Battlemon = Battlemon or {}

Battlemon.state = Battlemon.state or {
    ready = false,
    readyIn = 0,
    balls = 0,
    points = 0,
    catchThrows = 0,
    catchThrowsMax = 3,
    partySlots = { 0, 0, 0, 0, 0, 0 },
    owned = {},
    dexOwned = {},
    dexShiny = {},
    -- Move pool for the Pokemon the move manager currently has open.
    learnset = { ownedId = 0, cost = 0, moves = {}, ready = false },
    bag = {},
    shop = {},
}
Battlemon.state.dexShiny = Battlemon.state.dexShiny or {}
Battlemon.state.bag = Battlemon.state.bag or {}
Battlemon.state.shop = Battlemon.state.shop or {}
-- Spawn admin panel: server knobs, this zone's rule and the last spawn preview (administrators only).
Battlemon.state.admin = Battlemon.state.admin or { settings = {} }
Battlemon.state.learnset = Battlemon.state.learnset
    or { ownedId = 0, cost = 0, moves = {}, ready = false }

local handlers = {}

function Battlemon.OnNet(cmd, fn)
    handlers[cmd] = fn
end

function Battlemon.Send(cmd, arg)
    local payload = cmd
    if arg and arg ~= "" then
        payload = cmd .. "\t" .. arg
    end
    local me = UnitName("player")
    if not me then
        return
    end
    SendAddonMessage("BM", payload, "WHISPER", me)
end

local function splitTab(s)
    local out = {}
    local start = 1
    while true do
        local i = string.find(s, "\t", start, true)
        if not i then
            table.insert(out, string.sub(s, start))
            break
        end
        table.insert(out, string.sub(s, start, i - 1))
        start = i + 1
    end
    return out
end

function Battlemon.ParseBattler(a)
    -- a[1] = P|E
    local b = {
        ownedId = tonumber(a[2]) or 0,
        formId = tonumber(a[3]) or 0,
        speciesId = tonumber(a[4]) or 0,
        name = a[5] or "???",
        level = tonumber(a[6]) or 1,
        exp = tonumber(a[7]) or 0,
        gender = a[8] or "N",
        hp = tonumber(a[9]) or 0,
        maxhp = tonumber(a[10]) or 1,
        sprite = a[11] or "",
        backSprite = a[12] or "",
        partySlot = tonumber(a[13]) or 0,
        shiny = (a[14] == "1"),
        moves = {},
        fainted = (tonumber(a[9]) or 0) <= 0,
        species = (Battlemon.Species or {})[tonumber(a[4]) or 0],
    }
    local i = 15
    local idx = 1
    while a[i] and a[i] ~= "" do
        local internal = a[i]
        local mv = Battlemon.MovesByInternal and Battlemon.MovesByInternal[internal]
        table.insert(b.moves, {
            index = idx,
            data = mv or { name = a[i + 1] or internal, type = "", pp = a[i + 3] },
            pp = tonumber(a[i + 2]) or 0,
            maxpp = tonumber(a[i + 3]) or 5,
        })
        if mv and a[i + 1] then
            b.moves[#b.moves].data = Battlemon.Copy(mv)
            b.moves[#b.moves].data.name = a[i + 1]
        end
        idx = idx + 1
        i = i + 4
    end
    return b
end

local netFrame = CreateFrame("Frame")
netFrame:RegisterEvent("CHAT_MSG_ADDON")
netFrame:RegisterEvent("PLAYER_LOGIN")
netFrame:SetScript("OnEvent", function(_, event, ...)
    if event == "PLAYER_LOGIN" then
        Battlemon.After(1.0, function()
            Battlemon.Send("HELLO")
        end)
        Battlemon.After(3.0, function()
            Battlemon.Send("LEARNQ")
        end)
        return
    end
    local prefix, message, channel, sender = ...
    if prefix ~= "BM" then
        if type(prefix) == "string" and string.sub(prefix, 1, 3) == "BM\t" then
            message = string.sub(prefix, 4)
            prefix = "BM"
        elseif type(message) == "string" and string.sub(message, 1, 3) == "BM\t" then
            message = string.sub(message, 4)
            prefix = "BM"
        else
            return
        end
    end
    local me = UnitName("player")
    if sender and sender ~= me then
        return
    end
    local a = splitTab(message or "")
    local cmd = a[1]
    if not cmd or cmd == "" then
        return
    end
    if cmd == "HELLO" then
        Battlemon.state.owned = {}
        Battlemon.state.dexOwned = {}
        Battlemon.state.dexShiny = {}
        Battlemon.state.partySlots = { 0, 0, 0, 0, 0, 0 }
        Battlemon.state.followerId = nil
    elseif cmd == "ADMIN" then
        local admin = Battlemon.state.admin
        local sub = a[2]
        if sub == "SET" then
            admin.settings[a[3] or ""] = a[4] or ""
        elseif sub == "ZONE" then
            admin.zone = { id = tonumber(a[3]) or 0, min = tonumber(a[4]) or 0, max = tonumber(a[5]) or 0, types = a[6] or "" }
        elseif sub == "ODDS" then
            local list = {}
            for i = 4, #a do
                local name, pct = string.match(a[i], "^(.*)~([%d%.]+)$")
                if name then
                    table.insert(list, { name = name, pct = tonumber(pct) or 0 })
                end
            end
            admin.odds = { level = tonumber(a[3]) or 0, list = list }
        elseif sub == "END" and Battlemon.RefreshAdmin then
            Battlemon.RefreshAdmin()
        end
    elseif cmd == "LEARNOFFER" then
        if Battlemon.ShowLearnOffer then
            Battlemon.ShowLearnOffer(tonumber(a[2]) or 0, a[3] or "", { a[4] or "", a[5] or "", a[6] or "", a[7] or "" }, a[8] or "")
        end
    elseif cmd == "FOLLOW" then
        -- The Pokemon walking behind you (0 = none). Only announce a change, not the sync that follows login.
        local old = Battlemon.state.followerId
        local new = tonumber(a[2]) or 0
        Battlemon.state.followerId = new
        if old ~= nil and old ~= new then
            local row = Battlemon.state.owned[new]
            Battlemon.Print(new == 0 and "Your Pokémon stops following you."
                or ((row and Battlemon.FormName(row.formId, row.name) or "Your Pokémon") .. " follows you."))
        end
        if Battlemon.RefreshParty then
            Battlemon.RefreshParty()
        end
    elseif cmd == "CENTER" then
        if a[2] == "SHOP" and Battlemon.ShowShop then Battlemon.ShowShop()
        elseif a[2] == "PARTY" and Battlemon.ShowParty then Battlemon.ShowParty() end
    elseif cmd == "READY" then
        Battlemon.state.ready = (a[2] == "1")
        Battlemon.state.readyIn = tonumber(a[3]) or 0
    elseif cmd == "BALLS" then
        Battlemon.state.balls = tonumber(a[2]) or 0
    elseif cmd == "POINTS" then
        Battlemon.state.points = tonumber(a[2]) or 0
    elseif cmd == "CATCH" then
        Battlemon.state.catchThrows = tonumber(a[3]) or 0
        if a[4] and a[4] ~= "" then
            Battlemon.state.catchThrowsMax = tonumber(a[4]) or 3
        end
    elseif cmd == "PARTYSLOTS" then
        for i = 1, 6 do
            Battlemon.state.partySlots[i] = tonumber(a[i + 1]) or 0
        end
    elseif cmd == "OWNEDBEGIN" then
        Battlemon.state.owned = {}
    elseif cmd == "OWNEDEND" then
        if Battlemon.PruneRemovedOwned then Battlemon.PruneRemovedOwned() end
    elseif cmd == "OWNED" then
        local id = tonumber(a[2]) or 0
        Battlemon.state.owned[id] = {
            id = id,
            formId = tonumber(a[3]) or 0,
            level = tonumber(a[4]) or 1,
            exp = tonumber(a[5]) or 0,
            gender = a[6] or "N",
            hp = tonumber(a[7]) or 0,
            move = { a[8] or "", a[9] or "", a[10] or "", a[11] or "" },
            name = a[12] or "",
            sprite = a[13] or "",
            shiny = (a[14] == "1"),
            -- hp 0 means fainted; reviveIn counts down to the free revival.
            reviveIn = tonumber(a[15]) or 0,
            -- the item it is holding (battlemon_items.internal_name), empty for none
            held = a[16] or "",
        }
    elseif cmd == "BPARTY" then
        -- The battle's own view of the bench, one line per slot. The switch
        -- menu has to read this and never state.owned, whose HP is whatever was
        -- last written to the database and is stale the moment anything faints.
        local slot = tonumber(a[2]) or 0
        if slot >= 1 and slot <= 6 then
            Battlemon.battle = Battlemon.battle or {}
            Battlemon.battle.party = Battlemon.battle.party or {}
            local ownedId = tonumber(a[3]) or 0
            if ownedId > 0 then
                Battlemon.battle.party[slot] = {
                    slot = slot,
                    ownedId = ownedId,
                    hp = tonumber(a[4]) or 0,
                    maxhp = tonumber(a[5]) or 1,
                    level = tonumber(a[6]) or 1,
                    shiny = (a[7] == "1"),
                    active = (a[8] == "1"),
                    name = a[9] or "",
                }
            else
                Battlemon.battle.party[slot] = nil
            end
        end
    elseif cmd == "BAG" then
        -- Chunk 0 is always sent, even for an empty bag, so wiping on it is
        -- what makes a spent stack disappear.
        if a[2] == "0" then
            Battlemon.state.bag = {}
        end
        for i = 3, #a do
            local name, count = string.match(a[i], "^([^:]+):(%d+)$")
            if name then
                Battlemon.state.bag[name] = tonumber(count) or 0
            end
        end
    elseif cmd == "SHOP" then
        if a[2] == "0" then
            Battlemon.state.shop = {}
        end
        for i = 3, #a do
            local name, cost = string.match(a[i], "^([^:]+):(%d+)$")
            if name then
                table.insert(Battlemon.state.shop, { internal = name, cost = tonumber(cost) or 0 })
            end
        end
    elseif cmd == "LEARN" then
        Battlemon.state.learnset = {
            ownedId = tonumber(a[2]) or 0,
            cost = tonumber(a[3]) or 0,
            moves = {},
            ready = false,
        }
    elseif cmd == "LEARNADD" then
        local ls = Battlemon.state.learnset
        for i = 2, #a do
            -- INTERNAL:src:level, where src is L level-up, P paid, T for sale
            local name, src, level = string.match(a[i], "^([^:]+):([^:]*):(%d*)$")
            if name then
                table.insert(ls.moves, {
                    internal = name,
                    tutor = (src ~= "L"),
                    paid = (src == "P"),
                    level = tonumber(level) or 0,
                })
            end
        end
    elseif cmd == "LEARNEND" then
        Battlemon.state.learnset.ready = true
    elseif cmd == "DEXOWNED" or cmd == "DEXSHINY" then
        local set = (cmd == "DEXSHINY") and Battlemon.state.dexShiny or Battlemon.state.dexOwned
        for i = 2, #a do
            local fid = tonumber(a[i])
            if fid then
                set[fid] = true
            end
        end
    elseif cmd == "DEX" then
        local fid = tonumber(a[2])
        if fid then
            if a[3] == "1" then
                Battlemon.state.dexShiny[fid] = true
            else
                Battlemon.state.dexOwned[fid] = true
            end
        end
    elseif cmd == "AIL" then
        Battlemon.battle = Battlemon.battle or {}
        local side = a[2]
        local ail = a[3] or ""
        if side == "P" then
            Battlemon.battle.playerStatus = ail
            if Battlemon.battle.player then
                Battlemon.battle.player.status = ail
            end
        elseif side == "E" then
            Battlemon.battle.enemyStatus = ail
            if Battlemon.battle.enemy then
                Battlemon.battle.enemy.status = ail
            end
        end
    elseif cmd == "WEATHER" then
        Battlemon.battle = Battlemon.battle or {}
        Battlemon.battle.weather = a[2] or ""
    end
    -- Handlers run protected: a UI error must never stop the rest of the
    -- packet flow, or the battle frame ends up stuck waiting on input.
    local function run(fn)
        if not fn then
            return
        end
        local ok, err = pcall(fn, a)
        if not ok then
            Battlemon.Print("|cffff4040error in " .. tostring(cmd) .. ":|r " .. tostring(err))
        end
    end

    -- Optional alternate battle presentation; classic handlers remain the default.
    local routed = false
    if type(Battlemon.RouteBattlePacket) == "function" then
        local ok, result = pcall(Battlemon.RouteBattlePacket, cmd, a)
        if ok then
            routed = result and true or false
        else
            Battlemon.Print("Pet battle UI error: " .. tostring(result))
        end
    end
    if not routed then
        run(handlers[cmd])
    end
    run(Battlemon.RefreshMain)
    run(Battlemon.RefreshHub)
    run(Battlemon.RefreshParty)
    run(Battlemon.RefreshDex)
    run(Battlemon.RefreshMoves)
    run(Battlemon.RefreshShop)
    run(Battlemon.RefreshBag)
end)
