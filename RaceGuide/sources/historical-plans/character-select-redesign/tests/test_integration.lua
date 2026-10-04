--[==[ test_integration.lua --------------------------------------------------------
    End-to-end: order + notes + persistence across a simulated client restart
    (spec 11, 12, 41).

    Covers the checklist items that can only be proven by combining the layers:
      * reorder, then restart  -> order survives, and Enter World still targets
        the character that is visually selected
      * saved notes            -> survive restart, and stay attached to the right
        character
      * delete a character     -> its order entry AND its note are forgotten
      * rename                 -> the stale key is dropped, the character is kept
      * create a character     -> lands at the tail without disturbing the order
]==]

local O = ECS.Order;
local N = ECS.Notes;
local P = ECS.Persistence;
local D = ECS.Data;

-- ---------------------------------------------------------------- fake world
local function FakeBackend()
    local values = {};
    return {
        values = values,
        get = function(name) return values[name]; end,
        set = function(name, value) values[name] = value; return true; end,
    };
end

local SLOTS = {
    { name = "Sound_VoiceChatOutputDriverName", original = "1" },
    { name = "Sound_OutputDriverName",          original = "0" },
    { name = "lastCharacterDeleted",            original = "" },
};

local ACCOUNT = "ZACHGM";
local REALM   = "Esteria";

local function MakeCharacter(realIndex, name, model)
    return {
        realIndex   = realIndex,
        stableKey   = D.StableKey(REALM, name),
        name        = name,
        level       = 80,
        raceName    = "Human",
        className   = "Hero",
        zone        = "Stormwind",
        factionName = "Alliance",
        modelKey    = model,
    };
end

-- The server list is authoritative and dense; real index == position.
local function ServerList(names)
    local list = {}
    for index = 1, #names do
        list[index] = MakeCharacter(index, names[index]);
    end
    return list
end

-- Simulate one client session: fresh in-memory state, same cvar backend.
local function BootSession(backend, names)
    O.SetFilter("");
    O.SetCustomOrder({});
    N.Reset();

    O.SetCharacters(ServerList(names));

    local store, reason = P.Load(ACCOUNT, REALM, SLOTS, backend);
    if ( store ) then
        O.SetCustomOrder(store.order);
        N.Replace(store.notes);
        D.ApplyNotes(O.characters, N.Export());
    end
    return store, reason
end

local function SaveSession(backend)
    return P.Save(P.MakeStore(ACCOUNT, REALM, O.GetCustomOrder(), N.Export()), SLOTS, backend);
end

local function VisualNames()
    local out = {}
    for i = 1, O.VisibleCount() do
        out[i] = O.CharacterAt(i).name
    end
    return table.concat(out, ",")
end

local backend = FakeBackend();
P.SetBackend(backend);

-- ============================================================ 1. first session
local NAMES = { "Zach", "Auctioneer", "Clunt", "Nat", "Tubby", "Greg" };
BootSession(backend, NAMES);
ECS_EQ(O.VisibleCount(), 6, "1a: fresh session lists every character");
ECS_EQ(VisualNames(), "Zach,Auctioneer,Clunt,Nat,Tubby,Greg", "1b: server order initially");

-- reorder Nat (visual 4) to the front, and Greg (visual 6) to second
O.MoveCharacter(4, 1);
O.MoveCharacter(6, 2);
ECS_EQ(VisualNames(), "Nat,Greg,Zach,Auctioneer,Clunt,Tubby", "1c: reordered");
ECS_EQ(O.CharacterAt(1).realIndex, 4, "1d: visual 1 maps to real index 4 (Nat)");

-- add notes
N.Set(D.StableKey(REALM, "Nat"), "Main tank");
N.Set(D.StableKey(REALM, "Zach"), "Bank alt");

local saved, saveErr = SaveSession(backend);
ECS_CHECK(saved == true, "1e: session saved (" .. tostring(saveErr) .. ")");

-- ============================================================ 2. restart
BootSession(backend, NAMES);   -- new session, same backend: this is the "restart"
ECS_EQ(VisualNames(), "Nat,Greg,Zach,Auctioneer,Clunt,Tubby",
    "2a: custom order survived the restart");
ECS_EQ(O.CharacterAt(1).realIndex, 4, "2b: visual 1 still maps to real index 4");
ECS_EQ(N.Get(D.StableKey(REALM, "Nat")), "Main tank", "2c: note survived the restart");
ECS_EQ(N.Get(D.StableKey(REALM, "Zach")), "Bank alt", "2d: second note survived");

-- 2e: THE INVARIANT - whatever is visually selected must be what Enter World gets
local selectedVisual = 3;
local character = O.CharacterAt(selectedVisual);
ECS_EQ(character.name, "Zach", "2e: visual 3 is Zach");
ECS_EQ(character.realIndex, 1, "2f: and Enter World would use real index 1");
ECS_EQ(O.VisualPosOf(character.realIndex), selectedVisual, "2g: mapping is symmetric");

-- ============================================================ 3. delete a character
-- Nat is removed from the server list; everything else shifts down one real index.
local afterDelete = { "Zach", "Auctioneer", "Clunt", "Tubby", "Greg" };
O.SetCharacters(ServerList(afterDelete));
N.Forget(D.StableKey(REALM, "Nat"));
SaveSession(backend);

BootSession(backend, afterDelete);
ECS_EQ(O.VisibleCount(), 5, "3a: deleted character is gone");
ECS_EQ(VisualNames(), "Greg,Zach,Auctioneer,Clunt,Tubby",
    "3b: remaining order preserved after a delete");
ECS_CHECK(N.Get(D.StableKey(REALM, "Nat")) == nil,
    "3c: the deleted character's NOTE was forgotten");
ECS_EQ(N.Get(D.StableKey(REALM, "Zach")), "Bank alt",
    "3d: other notes untouched by the delete");
ECS_CHECK(table.concat(O.GetCustomOrder(), ",") ~= nil
    and string.find(table.concat(O.GetCustomOrder(), ","), "nat") == nil,
    "3e: the deleted character's order entry is gone from the saved order");

-- ============================================================ 4. rename
-- "Tubby" becomes "Tubbytwo": a NEW stable key, so the old one is stale. A rename
-- is indistinguishable from a delete+create at this layer, so per spec 11 the
-- character is adopted at the TAIL and the old note key is dropped.
local renamed = { "Zach", "Auctioneer", "Clunt", "Tubbytwo", "Greg" };
O.SetCharacters(ServerList(renamed));
SaveSession(backend);

BootSession(backend, renamed);
ECS_EQ(O.VisibleCount(), 5, "4a: renamed character is present");
ECS_CHECK(O.realToVisual[4] ~= nil, "4b: renamed character is visible");
ECS_CHECK(O.CharacterAt(O.VisibleCount()).name == "Tubbytwo",
    "4c: a renamed character lands at the tail (new stable key)");
-- 4d/4e: the other characters kept their saved relative order
ECS_EQ(O.CharacterAt(1).name, "Greg", "4d: previously ordered characters still lead");
ECS_CHECK(string.find(table.concat(O.GetCustomOrder(), ","), "tubbytwo") == nil,
    "4e: the renamed character is not yet in the saved order (it is appended by rule)");
ECS_EQ(N.Get(D.StableKey(REALM, "Tubby")), nil,
    "4f: the pre-rename note key is gone - notes do not follow a rename (documented)");

-- ============================================================ 5. create a character
local created = { "Zach", "Auctioneer", "Clunt", "Tubbytwo", "Greg", "Brandnew" };
BootSession(backend, created);
ECS_EQ(O.VisibleCount(), 6, "5a: new character appears");
ECS_EQ(O.RealIndexAt(O.VisibleCount()), 6, "5b: new character lands at the tail");
ECS_CHECK(O.CharacterAt(O.VisibleCount()).name == "Brandnew",
    "5c: the tail entry is the new character");
-- 5d: the saved order still leads the roster
ECS_CHECK(O.CharacterAt(1).name == "Greg",
    "5d: existing order still leads after a creation");

-- ============================================================ 6. filter + order together
-- With a custom order AND a filter active, selection must still resolve correctly.
BootSession(backend, created);
O.SetCustomOrder({ D.StableKey(REALM, "Brandnew"), D.StableKey(REALM, "Zach") });
O.SetFilter("g");
ECS_CHECK(O.VisibleCount() >= 1, "6a: filter matches something");
for i = 1, O.VisibleCount() do
    local c = O.CharacterAt(i);
    ECS_CHECK(string.find(string.lower(c.name), "g", 1, true) ~= nil
        or string.find(string.lower(c.zone or ""), "g", 1, true) ~= nil
        or string.find(string.lower(c.className or ""), "g", 1, true) ~= nil,
        "6b: filtered row '" .. c.name .. "' genuinely matches");
    ECS_EQ(O.realToVisual[c.realIndex], i, "6c: inverse mapping holds under filter+order");
end

-- ============================================================ 7. degraded capacity
-- A backend that can only hold one short value must still persist the ORDER,
-- even if notes cannot fit.
local tiny = FakeBackend();
local tinySlots = { { name = "Sound_VoiceChatOutputDriverName", original = "1" } };
P.SetBackend(tiny);

BootSession(tiny, created);
O.MoveCharacter(2, 1);
N.Set(D.StableKey(REALM, "Zach"), "This note is deliberately long enough to blow the budget "
    .. "when several of them exist together in one small storage slot");

local tinyStore = P.MakeStore(ACCOUNT, REALM, O.GetCustomOrder(), N.Export());
local tinySaved, tinyErr = P.Save(tinyStore, tinySlots, tiny);
ECS_CHECK(tinySaved == false,
    "7a: an over-capacity store is refused rather than half-written (" .. tostring(tinyErr) .. ")");

-- The caller degrades by dropping notes and keeping the order (spec 11/33).
local orderOnly = P.MakeStore(ACCOUNT, REALM, O.GetCustomOrder(), {});
local orderSaved = P.Save(orderOnly, tinySlots, tiny);
ECS_CHECK(orderSaved == true, "7b: the order alone still fits");

BootSession(tiny, created);
ECS_CHECK(O.CharacterAt(1).name == "Auctioneer",
    "7c: degraded save preserved the reordering");
ECS_EQ(N.Get(D.StableKey(REALM, "Zach")), nil,
    "7d: notes were lost as expected when capacity ran out");

-- ============================================================ 8. realm label
-- The ECS header replaces the stock label without losing the realm type or
-- disconnected status that the stock screen normally includes.
local I = ECS.Integrate;
local savedGetServerName = _G.GetServerName;
local savedGetRealmName = _G.GetRealmName;
local savedIsConnected = _G.IsConnectedToServer;
local savedPvp = _G.PVP_PARENTHESES;
local savedRp = _G.RP_PARENTHESES;
local savedRpPvp = _G.RPPVP_PARENTHESES;
local savedServerDown = _G.SERVER_DOWN;

_G.GetServerName = function() return "Zagan Realm", true, true end;
_G.IsConnectedToServer = function() return true end;
_G.RPPVP_PARENTHESES = "(RP-PvP)";
ECS_EQ(I.RealmLabel(), "Zagan Realm (RP-PvP)", "8a: realm label includes the combined RP-PvP marker");

_G.GetServerName = function() return "Zagan Realm", true, false end;
_G.PVP_PARENTHESES = "(PvP)";
ECS_EQ(I.RealmLabel(), "Zagan Realm (PvP)", "8b: realm label includes the PvP marker");

_G.GetServerName = function() return "Zagan Realm", false, true end;
_G.RP_PARENTHESES = "(RP)";
ECS_EQ(I.RealmLabel(), "Zagan Realm (RP)", "8c: realm label includes the RP marker");

_G.GetServerName = function() return "Zagan Realm", false, false end;
_G.IsConnectedToServer = function() return false end;
_G.SERVER_DOWN = "Offline";
ECS_EQ(I.RealmLabel(), "Zagan Realm (Offline)", "8d: server-down note stays on the single line");

_G.GetServerName = function() return "Zagan Realm", true, true end;
_G.RPPVP_PARENTHESES = nil;
_G.SERVER_DOWN = nil;
ECS_EQ(I.RealmLabel(), "Zagan Realm", "8e: missing locale strings safely omit only their labels");

_G.GetRealmName = function() return "Fallback Realm" end;
_G.GetServerName = function() error("server name unavailable") end;
ECS_EQ(I.RealmLabel(), "Fallback Realm", "8f: a failing server-name getter falls back to the realm name");

_G.GetServerName = nil;
ECS_EQ(I.RealmLabel(), "Fallback Realm", "8g: a missing server-name getter falls back to the realm name");

local savedGetSavedAccountName = _G.GetSavedAccountName;
_G.GetSavedAccountName = function()
    return "ZachGM#&|&#super-secret#&|&#1#&|&#ww";
end;
ECS_EQ(I.AccountName(), "ZachGM",
    "8h: ECS scopes persistence by username only, never by the packed credential payload");
_G.GetSavedAccountName = function() return "StockAccount" end;
ECS_EQ(I.AccountName(), "StockAccount", "8i: stock single-field saved account names still work");
_G.GetSavedAccountName = savedGetSavedAccountName;

_G.GetServerName = savedGetServerName;
_G.GetRealmName = savedGetRealmName;
_G.IsConnectedToServer = savedIsConnected;
_G.PVP_PARENTHESES = savedPvp;
_G.RP_PARENTHESES = savedRp;
_G.RPPVP_PARENTHESES = savedRpPvp;
_G.SERVER_DOWN = savedServerDown;

-- ============================================================ 9. stock refresh paths
-- The War Band list toggle shows CharacterSelectCharacterFrame directly, and
-- selection events can refresh the rows without traversing UpdateCharacterList.
local savedInstalled = I.installed;
local savedPostUpdate = I.PostUpdate;
local savedPostUpdateCount = I.postUpdateCount;
local savedUpdateCharacterList = _G.UpdateCharacterList;
local savedCharacterSelectEvent = _G.CharacterSelect_OnEvent;
local savedWarBandToggle = _G.CharacterSelect_OnEventO2;
local savedStyleToggle = _G.CharacterSelect_OnEventO;
local postUpdateCalls = 0;
local listUpdateCalls = 0;
local warBandToggleCalls = 0;
local styleToggleCalls = 0;

I.installed = false;
I.postUpdateCount = 0;
I.PostUpdate = function() postUpdateCalls = postUpdateCalls + 1 end;
_G.UpdateCharacterList = function() listUpdateCalls = listUpdateCalls + 1 end;
_G.CharacterSelect_OnEvent = function(_, event)
    if ( event == "CHARACTER_LIST_UPDATE" ) then
        _G.UpdateCharacterList();
    end
end;
_G.CharacterSelect_OnEventO2 = function() warBandToggleCalls = warBandToggleCalls + 1 end;
_G.CharacterSelect_OnEventO = function() styleToggleCalls = styleToggleCalls + 1 end;

ECS_CHECK(I.Install() == true, "9a: install wraps the stock refresh paths");
_G.CharacterSelect_OnEvent({}, "CHARACTER_LIST_UPDATE");
ECS_EQ(listUpdateCalls, 1, "9b: the stock character-list event still binds its rows");
ECS_EQ(postUpdateCalls, 1, "9c: a wrapped list update reconciles only once");

_G.CharacterSelect_OnEvent({}, "UPDATE_SELECTED_CHARACTER");
ECS_EQ(postUpdateCalls, 2, "9d: selection events reconcile when stock skips list update");

_G.CharacterSelect_OnEventO2();
ECS_EQ(warBandToggleCalls, 1, "9e: the War Band visibility toggle still runs");
ECS_EQ(postUpdateCalls, 3, "9f: showing the stock frame triggers an ECS reconciliation");

_G.CharacterSelect_OnEventO();
ECS_EQ(styleToggleCalls, 1, "9g: the stock style toggle still runs");
ECS_EQ(postUpdateCalls, 4, "9h: the style toggle reconciles after moving stock frames");

I.installed = savedInstalled;
I.PostUpdate = savedPostUpdate;
I.postUpdateCount = savedPostUpdateCount;
_G.UpdateCharacterList = savedUpdateCharacterList;
_G.CharacterSelect_OnEvent = savedCharacterSelectEvent;
_G.CharacterSelect_OnEventO2 = savedWarBandToggle;
_G.CharacterSelect_OnEventO = savedStyleToggle;

-- ============================================================ 10. live-list count fallback
local stockRowsParent = CreateFrame("Frame", "ECSStockRowsParent", UIParent);
for index = 1, 3 do
    local button = CreateFrame("Button", ECS.Roster.RowName(index), stockRowsParent);
    button:SetID(index);
end
_G.CharSelectCharacterButton3:Hide();
ECS_EQ(I.StockCharacterCount(), 2,
    "10a: visible stock row IDs recover the list count while the getter is stale");

-- ============================================================ 11. roster wheel routing
local savedSelect = _G.CharacterSelect;
SHIM.Reset();
SHIM.Install();
ECS.Search.Reset();
O.SetCustomOrder({});
O.SetCharacters(ServerList({ "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L" }));
ECS.Roster.Reset();
local wheelParent = CreateFrame("Frame", "ECSWheelParent", UIParent);
local wheelScroll = CreateFrame("ScrollFrame", "ECSWheelScroll", UIParent);
local wheelChild = CreateFrame("Frame", "ECSWheelChild", wheelScroll);
wheelScroll:SetScrollChild(wheelChild);
for index = 1, ECS.Const.POOL_SIZE do
    local button = CreateFrame("Button", ECS.Roster.RowName(index), wheelParent);
    button:SetSize(ECS.Const.ROSTER_WIDTH, ECS.Const.ROW_HEIGHT);
end
ECS.Roster.BuildPool(wheelParent, ECS.Const.POOL_SIZE);
ECS.Roster.SetLayoutParent(wheelParent);
ECS.Roster.SetScrollFrame(wheelScroll);
ECS_CHECK(I.HookScrollFrame(wheelScroll) == true, "11e0: scroll-frame handlers are installed");
_G.CharacterSelect = { scrollOffset = 0, scrollMax = 0 };
I.HookRows();
ECS.Roster.Refresh();

local rowWheel = ECS.Roster.pool[1].__scripts.OnMouseWheel;
ECS_CHECK(type(rowWheel) == "function", "11a: visible roster rows own an explicit wheel handler");
rowWheel(ECS.Roster.pool[1], -1);
ECS_EQ(ECS.Roster.GetOffset(), 1, "11b: one down-wheel notch advances one visual row");
ECS_EQ(ECS.Roster.pool[1]:GetID(), 2, "11c: the visible list rebinds after wheel scrolling");
ECS_EQ(_G.CharacterSelect.scrollOffset, 1, "11d: stock selection offset mirrors the virtual roster");

local frameWheel = wheelScroll.__scripts.OnMouseWheel;
ECS_CHECK(type(frameWheel) == "function", "11e: the scroll frame routes wheel to ECS too");
frameWheel(wheelScroll, 1);
ECS_EQ(ECS.Roster.GetOffset(), 0, "11f: one up-wheel notch returns one visual row");
ECS_EQ(_G.CharacterSelect.scrollMax, 4, "11g: scrollbar range uses the eight-row viewport");

_G.CharacterSelect = savedSelect;
ECS.Roster.Reset();
