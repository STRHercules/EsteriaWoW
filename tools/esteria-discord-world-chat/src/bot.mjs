import { createServer } from "node:http";
import { timingSafeEqual } from "node:crypto";
import { Client, Events, GatewayIntentBits, escapeMarkdown } from "discord.js";
import { fromGameText, toGameText } from "./sanitize.mjs";

const token = process.env.DISCORD_TOKEN;
const channelId = process.env.DISCORD_CHANNEL_ID;
const guildId = process.env.DISCORD_GUILD_ID || "";
const secret = process.env.BRIDGE_SECRET;
const port = Number(process.env.BRIDGE_PORT || 22150);

if (!token || !/^\d{15,22}$/.test(channelId || "")) {
  throw new Error("Set DISCORD_TOKEN and a valid DISCORD_CHANNEL_ID in .env");
}
if (!secret || secret.length < 32 || !Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("Set a random 32+ character BRIDGE_SECRET and a valid BRIDGE_PORT");
}

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent],
});

let ready = false;
const incoming = [];
const sent = new Map();
const rate = new Map();
const MAX_INCOMING = 512;
const WINDOW_MS = 10_000;
const MAX_MESSAGES_PER_WINDOW = 5;

function rememberIncoming(message) {
  incoming.push(message);
  const cutoff = Date.now() - 10 * 60_000;
  while (incoming.length > MAX_INCOMING || (incoming[0] && incoming[0].timestamp < cutoff)) {
    incoming.shift();
  }
}

function allowedToRelay(userId) {
  const now = Date.now();
  const entry = rate.get(userId);
  if (!entry || now - entry.started > WINDOW_MS) {
    rate.set(userId, { started: now, count: 1 });
    return true;
  }
  if (entry.count >= MAX_MESSAGES_PER_WINDOW) return false;
  entry.count += 1;
  return true;
}

client.on(Events.MessageCreate, (message) => {
  if (message.channelId !== channelId || message.author.bot || message.webhookId) return;
  if (guildId && message.guildId !== guildId) return;

  const text = toGameText(message.content, 220);
  if (!text || !allowedToRelay(message.author.id)) return;

  const name = toGameText(
    message.member?.displayName || message.author.globalName || message.author.username,
    48,
  );
  if (!name) return;
  rememberIncoming({ id: message.id, author: name, text, timestamp: Date.now() });
});

client.once(Events.ClientReady, () => {
  ready = true;
  console.log("Esteria World Chat connected to Discord as " + client.user.username);
});

client.on(Events.Error, (error) => console.error("Discord error:", error.message));

function authenticated(req) {
  const provided = req.headers["x-esteria-secret"];
  if (typeof provided !== "string") return false;
  const a = Buffer.from(provided);
  const b = Buffer.from(secret);
  return a.length === b.length && timingSafeEqual(a, b);
}

function reply(res, status, value) {
  const json = JSON.stringify(value);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Content-Length": Buffer.byteLength(json),
  });
  res.end(json);
}

async function readJson(req) {
  let size = 0;
  const parts = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 8192) throw new Error("Message too large");
    parts.push(chunk);
  }
  return JSON.parse(Buffer.concat(parts).toString("utf8"));
}

async function handleOutgoing(req, res) {
  if (!ready) return reply(res, 503, { error: "Discord is reconnecting" });
  let payload;
  try {
    payload = await readJson(req);
  } catch {
    return reply(res, 400, { error: "Invalid JSON" });
  }

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return reply(res, 400, { error: "Expected an object" });
  }

  const id = typeof payload.id === "string" ? payload.id : "";
  const author = toGameText(payload.author, 48);
  const text = fromGameText(payload.text, 500);
  if (!/^\d{10,24}-\d{1,12}$/.test(id) || !author || !text) {
    return reply(res, 400, { error: "Invalid message" });
  }
  if (sent.has(id)) return reply(res, 200, { ok: true, duplicate: true });

  const team = Number(payload.teamId);
  const faction = team === 0 ? "Alliance" : team === 1 ? "Horde" : "World";
  const content = "[" + faction + "] **" + escapeMarkdown(author) + "**: " + escapeMarkdown(text);

  try {
    const channel = await client.channels.fetch(channelId);
    if (!channel?.isTextBased() || typeof channel.send !== "function") {
      return reply(res, 503, { error: "Configured channel is not text-based" });
    }
    await channel.send({ content, allowedMentions: { parse: [] } });
    sent.set(id, Date.now());
    const cutoff = Date.now() - 10 * 60_000;
    for (const [key, timestamp] of sent) {
      if (timestamp < cutoff) sent.delete(key);
    }
    return reply(res, 200, { ok: true });
  } catch (error) {
    console.error("Discord send failed:", error.message);
    return reply(res, 503, { error: "Discord send failed" });
  }
}

function handleIncoming(req, res) {
  const after = new URL(req.url, "http://127.0.0.1").searchParams.get("after");
  if (after === "latest") {
    return reply(res, 200, { cursor: incoming.at(-1)?.id || "0", messages: [] });
  }
  if (!/^\d{1,20}$/.test(after || "")) {
    return reply(res, 400, { error: "Invalid cursor" });
  }
  const cursor = BigInt(after);
  const messages = incoming.filter((message) => BigInt(message.id) > cursor).slice(0, 16);
  return reply(res, 200, {
    cursor: messages.at(-1)?.id || after,
    messages: messages.map(({ id, author, text }) => ({ id, author, text })),
  });
}

const server = createServer(async (req, res) => {
  if (!authenticated(req)) return reply(res, 401, { error: "Unauthorized" });
  const path = new URL(req.url, "http://127.0.0.1").pathname;
  if (req.method === "POST" && path === "/outgoing") return handleOutgoing(req, res);
  if (req.method === "GET" && path === "/incoming") return handleIncoming(req, res);
  return reply(res, 404, { error: "Not found" });
});

server.listen(port, "127.0.0.1", () => {
  console.log("Esteria World Chat bridge listening on 127.0.0.1:" + port);
});

client.login(token).catch((error) => {
  console.error("Discord login failed:", error.message);
  server.close();
  process.exitCode = 1;
});

function shutdown() {
  ready = false;
  server.close();
  client.destroy();
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
