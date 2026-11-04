import test from "node:test";
import assert from "node:assert/strict";
import { toGameText, fromGameText } from "./sanitize.mjs";

test("Discord messages cannot inject WoW texture, color, or hyperlink codes", () => {
  assert.equal(toGameText("Hello |Tfoo|t |Hitem:123|hClick|h"), "Hello Tfoot Hitem:123hClickh");
});

test("Discord messages are flattened, bounded, and stripped of non-BMP emoji", () => {
  assert.equal(toGameText("hello\nworld😀", 11), "hello world");
});

test("WoW formatting is removed before posting to Discord", () => {
  assert.equal(fromGameText("|cffFF0000Red|r |Hitem:1|h[Sword]|h"), "Red [Sword]");
});
