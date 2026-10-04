"""Measure the persisted payload against the cvar storage budget.

The custom order has to survive a logout for a roster of up to 100 characters
(server cap). The store is percent-encoded and sharded across probed string
cvars, so the question "does a full roster even fit?" is arithmetic, not opinion.

This prints the real numbers from the REAL modules on Lua 5.1 rather than an
estimate: payload size, shards needed, and the shards available in the best case
(all six candidate cvars writable) versus the proven case (the first two, which
the existing Freeborn implementation demonstrates do persist).

Usage:
    python .agents/plans/character-select-redesign/tools/measure_capacity.py
"""

from __future__ import annotations

from pathlib import Path

from lupa.lua51 import LuaRuntime

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "GlueXML"

MODULES = [
    "ECS_Constants.lua",
    "ECS_Schema.lua",
    "ECS_Order.lua",
    "ECS_Data.lua",
    "ECS_Persistence.lua",
    "ECS_Notes.lua",
]

lua = LuaRuntime(unpack_returned_tuples=True)


def run(path: Path) -> None:
    lua.execute(path.read_text(encoding="utf-8"))


for name in MODULES:
    run(SRC / name)

MEASURE = r"""
local P = ECS.Persistence;

local function BuildStore(count, noteLength)
    local order, notes = {}, {};
    for index = 1, count do
        -- a realistic stable key: realm + ':' + character name
        local key = "esteria:character" .. tostring(index);
        order[index] = key;
        if noteLength and noteLength > 0 then
            notes[key] = string.rep("x", noteLength);
        end
    end
    return P.MakeStore("ZACHGM", "Esteria", order, notes);
end

local lines = {};
local full = nil;
for _, count in ipairs({ 10, 25, 50, 75, 100 }) do
    for _, noteLength in ipairs({ 0, 20, 40 }) do
        local payload = P.Serialise(BuildStore(count, noteLength));
        local shards = #P.Shard(payload);
        lines[#lines + 1] = string.format("%6d %5d %9d %7d", count, noteLength, #payload, shards);
        if ( count == 100 and noteLength == 0 ) then
            full = shards;
        end
    end
end

local maxChunk = P.MAX_CHUNK;
local candidates = #P.CANDIDATE_CVARS;
local keyCost = #P.Encode("esteria:character1");

local out = {};
out[#out + 1] = string.format("%6s %5s %9s %7s", "chars", "note", "payload", "shards");
for _, line in ipairs(lines) do out[#out + 1] = line; end
out[#out + 1] = "";
out[#out + 1] = string.format("MAX_CHUNK                : %d chars per cvar", maxChunk);
out[#out + 1] = string.format("candidate cvars          : %d", candidates);
out[#out + 1] = string.format("encoded key cost         : %d chars each", keyCost);
out[#out + 1] = string.format("capacity, all candidates : %d chars", maxChunk * candidates);
out[#out + 1] = string.format("capacity, proven two     : %d chars", maxChunk * 2);
out[#out + 1] = "";
out[#out + 1] = string.format("100 chars, order only    : %d shards needed", full);
out[#out + 1] = string.format("verdict (all candidates) : %s",
    full <= candidates and "FITS" or "DOES NOT FIT");
out[#out + 1] = string.format("verdict (proven two)     : %s",
    full <= 2 and "FITS" or "DOES NOT FIT");

-- The client now MEASURES the real per-cvar limit at discovery instead of assuming
-- MAX_CHUNK, so what matters is how much total room a roster needs. This projects
-- the 100-character order against plausible measured limits, to compare with what
-- the probe actually reports on the client.
out[#out + 1] = "";
out[#out + 1] = "100-character order, against measured per-cvar limits:";
out[#out + 1] = string.format("  %8s %10s %10s %8s", "limit", "room/slot", "slots", "verdict");
local needed100 = #P.Serialise(P.MakeStore("A", "esteria", (function()
    local keys = {};
    for index = 1, 100 do keys[index] = "esteria:character" .. tostring(index); end
    return keys;
end)(), {}));
for _, limit in ipairs({ 64, 120, 170, 200, 250 }) do
    local room = limit - P.PROBE_RESERVE;
    local slots = nil;
    if ( room > 0 ) then
        slots = math.ceil(needed100 / room);
    end
    out[#out + 1] = string.format("  %8d %10s %10s %8s",
        limit,
        room > 0 and tostring(room) or "-",
        slots and tostring(slots) or "-",
        (slots and slots <= candidates) and "FITS" or "DOES NOT FIT");
end
return table.concat(out, "\n");
"""

print(lua.eval("(function() " + MEASURE + " end)()"))
