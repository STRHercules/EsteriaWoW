Battlemon = Battlemon or {}

local function slash(msg)
    msg = string.lower(string.gsub(msg or "", "^%s*(.-)%s*$", "%1"))
    local cmd = string.match(msg, "^(%S*)") or ""

    if cmd == "" or cmd == "open" then
        Battlemon.ShowHub()
        return
    end
    if cmd == "wild" or cmd == "fight" then
        Battlemon.Send("WILD")
        return
    end
    if cmd == "party" then
        Battlemon.Send("PARTY")
        Battlemon.ShowParty()
        return
    end
    if cmd == "teams" then
        Battlemon.Send("PARTY")
        Battlemon.ShowTeams()
        return
    end
    if cmd == "dex" then
        Battlemon.ShowDex()
        return
    end
    if cmd == "bag" then
        Battlemon.Send("PARTY")
        Battlemon.ShowBag()
        return
    end
    if cmd == "music" then
        local arg = string.match(msg, "^%S+%s+(.-)%s*$") or ""
        if arg == "" then
            local choices = "|cffffff00random|r"
            for _, t in ipairs(Battlemon.BattleMusic.tracks) do
                choices = choices .. ", |cffffff00" .. t.key .. "|r (" .. t.name .. ")"
            end
            Battlemon.Print("Battle music: |cffffff00" .. Battlemon.BattleMusic.GetTheme() .. "|r. Choices: " .. choices)
            return
        end
        if Battlemon.BattleMusic.SetTheme(arg) then
            Battlemon.Print("Battle music set to |cffffff00" .. arg .. "|r.")
        else
            Battlemon.Print("|cffff4040Unknown theme:|r " .. arg .. ". Type |cffffff00/bm music|r to see choices.")
        end
        return
    end
    if cmd == "trade" then
        Battlemon.StartTrade(string.match(msg, "^%S+%s+(.-)%s*$"))
        return
    end
    if cmd == "admin" then
        Battlemon.ShowAdmin()
        return
    end
    if cmd == "status" then
        Battlemon.Send("STATUS")
        Battlemon.Print("Asked the server for status. Open /bm to see it.")
        return
    end
    if cmd == "debug" then
        Battlemon.PrintDataReport()
        return
    end
    if cmd == "reload" then
        Battlemon.LoadData()
        Battlemon.PrintDataReport()
        return
    end

    Battlemon.Print("Commands: /bm  |  /bm fight  |  /bm party  |  /bm bag  |  /bm dex  |  /bm music [theme]  |  /bm status  |  /bm debug")
end

-- Each init step is isolated. Previously one failing step (the minimap button)
-- aborted the whole handler and the catalog never loaded.
local function step(label, fn)
    local ok, err = pcall(fn)
    if not ok then
        Battlemon.Print("|cffff4040" .. label .. " failed:|r " .. tostring(err))
    end
    return ok
end

local eventFrame = CreateFrame("Frame")
eventFrame:RegisterEvent("ADDON_LOADED")
eventFrame:RegisterEvent("PLAYER_LOGIN")
eventFrame:SetScript("OnEvent", function(_, event, name)
    if event == "ADDON_LOADED" and name == "Battlemon" then
        BattlemonDB = BattlemonDB or {}
        if Battlemon.EnsureProfileDB then
            Battlemon.EnsureProfileDB()
        end
        -- Not every 3.3.5 client exposes math.randomseed, and nothing on this
        -- side needs a particular sequence: the server rolls everything that
        -- decides a battle. Seed when the client allows it, skip it when not.
        if type(math.randomseed) == "function" then
            math.randomseed(math.floor((GetTime() or 1) * 1000))
        end
        step("data load", Battlemon.LoadData)

        local species = #(Battlemon.SpeciesList or {})
        if species == 0 then
            Battlemon.Print("|cffff4040No species data loaded.|r Run |cffffff00/bm debug|r for details.")
        else
            Battlemon.Print(string.format("Loaded %d Pokémon. Click the Pikachu on the minimap, or type |cffffff00/bm|r.", species))
        end
        step("minimap button", Battlemon.CreateMinimapButton)
    elseif event == "PLAYER_LOGIN" then
        -- Retry: some UI replacements create the Minimap after ADDON_LOADED.
        if not Battlemon.minimapButton then
            step("minimap button", Battlemon.CreateMinimapButton)
        end
        if #(Battlemon.SpeciesList or {}) == 0 then
            step("data load", Battlemon.LoadData)
        end
    end
end)

SLASH_BATTLEMON1 = "/battlemon"
SLASH_BATTLEMON2 = "/bm"
SlashCmdList["BATTLEMON"] = slash
