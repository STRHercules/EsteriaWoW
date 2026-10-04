--[[ ECS_Order.lua --------------------------------------------------------------
    Esteria Character Select - the visual order / real index mapping (spec 24).

    THIS IS THE MOST IMPORTANT FILE IN THE PROJECT.

    Blizzard's character list is authoritative and is indexed 1..numChars. That
    index is what SelectCharacter / DeleteCharacter / EnterWorld all take. The
    roster, however, shows a *filtered, reordered* view. As soon as search or a
    custom order exists, the two stop agreeing.

    So every mapping is explicit and one-directional, and nothing may ever assume
    visualIndex == realIndex:

        ECS.Order.visible[i]        = realIndex of the i-th VISIBLE row
        ECS.Order.realToVisual[r]   = i, or nil when r is filtered out

    Pure Lua: no frame access, no client API. Loads before any XML and is fully
    unit-testable offline (see tests/test_order.lua).

    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Order = ECS.Order or {};

local O = ECS.Order;
local C = ECS.Const;

-- ---------------------------------------------------------------- state
O.characters   = O.characters or {};   -- realIndex -> CharacterData (dense, 1..n)
O.customOrder  = O.customOrder or {};  -- array of stableKey, persisted (spec 11)
O.filter       = O.filter or "";       -- normalised search text, "" = no filter
O.visible      = {};                   -- array of realIndex
O.realToVisual = {};                   -- realIndex -> position in visible
O.count        = 0;                    -- #visible

-- ---------------------------------------------------------------- helpers
local function Normalise(text)
    if ( type(text) ~= "string" ) then
        return "";
    end
    local value = string.lower(text);
    -- collapse surrounding whitespace so "  mage " matches "mage"
    value = string.gsub(value, "^%s+", "");
    value = string.gsub(value, "%s+$", "");
    return value;
end

O.Normalise = Normalise;

-- Build the searchable haystack for one character (spec 8).
local function SearchBlob(character)
    local parts = {
        character.name or "",
        character.raceName or "",
        character.className or "",
        character.zone or "",
        character.factionName or "",
    };
    if ( type(character.level) == "number" ) then
        parts[#parts + 1] = tostring(character.level);
    end
    return string.lower(table.concat(parts, "\1"));
end

O.SearchBlob = SearchBlob;

local function Matches(character, needle)
    if ( needle == "" ) then
        return true;
    end
    if ( not character ) then
        return false;
    end
    local blob = character.searchBlob;
    if ( not blob ) then
        blob = SearchBlob(character);
        character.searchBlob = blob;
    end
    return string.find(blob, needle, 1, true) ~= nil;
end

-- ---------------------------------------------------------------- inputs
-- characters: dense array of CharacterData with realIndex == array position.
function O.SetCharacters(list)
    O.characters = list or {};
    for index = 1, #O.characters do
        local character = O.characters[index];
        if ( character ) then
            character.realIndex = index;
            character.searchBlob = nil;   -- invalidate cached haystack
        end
    end
    O.Rebuild();
end

-- customOrder: array of stableKey. Anything malformed is ignored rather than
-- failing the roster (spec 11, 33).
function O.SetCustomOrder(order)
    local clean = {};
    if ( type(order) == "table" ) then
        for index = 1, #order do
            local key = order[index];
            if ( type(key) == "string" and key ~= "" ) then
                clean[#clean + 1] = key;
            end
        end
    end
    O.customOrder = clean;
    O.Rebuild();
end

function O.GetCustomOrder()
    return O.customOrder;
end

function O.SetFilter(text)
    O.filter = Normalise(text);
    O.Rebuild();
end

function O.GetFilter()
    return O.filter;
end

-- ---------------------------------------------------------------- ordering
-- Produce the ordered list of REAL indices: saved custom order first (dropping
-- keys for characters that no longer exist), then any character the saved order
-- has never seen, per C.NEW_CHARACTER_POSITION.
function O.ComputeOrder()
    local position = {};
    for index = 1, #O.customOrder do
        -- first occurrence wins, so a duplicated key cannot scramble the list
        local key = O.customOrder[index];
        if ( position[key] == nil ) then
            position[key] = index;
        end
    end

    local head, tail = {}, {};

    for realIndex = 1, #O.characters do
        local character = O.characters[realIndex];
        local key = character and character.stableKey;
        local slot = key and position[key];
        if ( slot ) then
            tail[#tail + 1] = { realIndex = realIndex, slot = slot };
        else
            head[#head + 1] = { realIndex = realIndex, slot = realIndex };
        end
    end

    local ordered = {};
    local function AppendKnown()
        table.sort(tail, function(a, b) return a.slot < b.slot; end);
        for index = 1, #tail do
            ordered[#ordered + 1] = tail[index].realIndex;
        end
    end
    local function AppendUnknown()
        -- unknowns keep server order
        table.sort(head, function(a, b) return a.realIndex < b.realIndex; end);
        for index = 1, #head do
            ordered[#ordered + 1] = head[index].realIndex;
        end
    end

    if ( C.NEW_CHARACTER_POSITION == "head" ) then
        AppendUnknown();
        AppendKnown();
    else
        -- default: known characters keep their saved order; newly created ones
        -- land at the end in server order (spec 11)
        AppendKnown();
        AppendUnknown();
    end

    -- Strip saved keys that no longer correspond to a character, so the stored
    -- order self-heals for deleted/renamed characters (spec 11).
    --
    -- CRITICAL: only prune when we actually HAVE a roster. At the login screen, or
    -- before the server answers, O.characters is empty -- pruning then would
    -- discard every saved key against nothing, silently losing the whole order.
    if ( #O.characters > 0 ) then
        local live = {};
        for realIndex = 1, #O.characters do
            local character = O.characters[realIndex];
            if ( character and character.stableKey ) then
                live[character.stableKey] = true;
            end
        end
        local pruned = {};
        for index = 1, #O.customOrder do
            if ( live[O.customOrder[index]] ) then
                pruned[#pruned + 1] = O.customOrder[index];
            end
        end
        O.customOrder = pruned;
    end

    return ordered;
end

-- ---------------------------------------------------------------- rebuild
-- Recompute visible[] and realToVisual[] from the current characters, custom
-- order and filter. Idempotent and cheap; call on invalidation only (spec 22),
-- never per frame.
function O.Rebuild()
    local ordered = O.ComputeOrder();

    local visible = {};
    local realToVisual = {};
    local needle = O.filter;

    for index = 1, #ordered do
        local realIndex = ordered[index];
        local character = O.characters[realIndex];
        if ( Matches(character, needle) ) then
            visible[#visible + 1] = realIndex;
            realToVisual[realIndex] = #visible;
        end
    end

    O.visible      = visible;
    O.realToVisual = realToVisual;
    O.count        = #visible;
    return visible;
end

-- ---------------------------------------------------------------- queries
function O.VisibleCount()
    return O.count;
end

-- visual position (1-based) -> real index, or nil when out of range.
function O.RealIndexAt(visualPos)
    if ( type(visualPos) ~= "number" ) then
        return nil;
    end
    return O.visible[visualPos];
end

-- real index -> visual position, or nil when filtered out.
function O.VisualPosOf(realIndex)
    if ( type(realIndex) ~= "number" ) then
        return nil;
    end
    return O.realToVisual[realIndex];
end

function O.CharacterAt(visualPos)
    local realIndex = O.RealIndexAt(visualPos);
    if ( not realIndex ) then
        return nil;
    end
    return O.characters[realIndex];
end

-- spec 8: is the selected character hidden by the active filter?
function O.IsFilteredOut(realIndex)
    if ( not realIndex or realIndex <= 0 ) then
        return false;
    end
    return O.realToVisual[realIndex] == nil;
end

-- ---------------------------------------------------------------- reordering
-- spec 10/11: move the character at visual position `fromPos` so that it lands
-- at visual position `toPos`. Works on stableKey, so the persisted order stays
-- valid across deletes and renames.
--
-- Returns true when the order actually changed.
function O.MoveCharacter(fromPos, toPos)
    local fromIndex = O.RealIndexAt(fromPos);
    local toIndex   = O.RealIndexAt(toPos);
    if ( not fromIndex or not toIndex or fromPos == toPos ) then
        return false;
    end

    -- Rebuild the full order first, then reorder by real index so a filtered
    -- view still produces a globally consistent saved order.
    local full = O.ComputeOrder();

    local fromSlot, toSlot = nil, nil;
    for slot = 1, #full do
        if ( full[slot] == fromIndex ) then fromSlot = slot; end
        if ( full[slot] == toIndex ) then toSlot = slot; end
    end
    if ( not fromSlot or not toSlot ) then
        return false;
    end

    local moved = table.remove(full, fromSlot);
    table.insert(full, toSlot, moved);

    local keys = {};
    for slot = 1, #full do
        local character = O.characters[full[slot]];
        local key = character and character.stableKey;
        if ( key ) then
            keys[#keys + 1] = key;
        end
    end

    O.customOrder = keys;
    O.Rebuild();
    return true;
end

-- Drop one character from the saved order (used after a confirmed delete).
function O.RemoveFromOrder(realIndex)
    local character = O.characters[realIndex];
    if ( not character or not character.stableKey ) then
        return false;
    end
    local key = character.stableKey;
    local kept = {};
    local removed = false;
    for index = 1, #O.customOrder do
        if ( O.customOrder[index] == key ) then
            removed = true;
        else
            kept[#kept + 1] = O.customOrder[index];
        end
    end
    O.customOrder = kept;
    return removed;
end

-- NOTE: there is deliberately no Serialise/Deserialise here.
--
-- ECS_Persistence owns the on-disk format because encoding a key is not a
-- property of the order: the record also carries a schema version, an account
-- and a realm, the keys have to be escaped, and the payload is sharded across
-- cvar slots. A second, unescaped "join the keys with commas" serialiser used to
-- live here. Nothing in production called it - the real round trip is
-- P.Serialise/P.Deserialise over store.order - but its Deserialise WAS covered by
-- tests, which made the order format look tested while the code that actually
-- ran went unexercised. Two serialisers for one field is a drift hazard, so the
-- unused pair was removed rather than kept "just in case".
--
-- O.GetCustomOrder / O.SetCustomOrder remain the correct way in and out.
