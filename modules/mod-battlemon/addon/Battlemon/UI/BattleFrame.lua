Battlemon = Battlemon or {}

local ui
local queue = {}
-- busy: the message queue is animating. awaiting: we sent an action and are
-- waiting on the server. They are separate because incoming packets must still
-- drive the queue while an action is in flight, otherwise the UI locks up.
local busy = false
local awaiting = false
local busySince = 0
local awaitSince = 0
local displayed = { player = 0, enemy = 0 }
local pending = { catch = nil, catchThrows = 0, catchThrowsMax = 3, ending = nil, switchNeed = false }
-- A fight is live from the WILD packet until it ends. Neither of the obvious
-- proxies works: the battle page hides when you switch tabs in the main window,
-- and the server sends your party lead as a battler on login, so Battlemon.battle
-- is populated while you are just standing around.
function Battlemon.InBattle()
    return Battlemon.battleActive and true or false
end

-- Closing the window during a fight must RUN on the server, not just hide UI.
function Battlemon.ForfeitBattle()
    if not Battlemon.InBattle() then
        return false
    end
    if Battlemon.battle and Battlemon.battle.enemy then
        Battlemon.Send("RUN")
    end
    idle()
    closeBattle()
    return true
end

-- As a page inside the main window, hiding the battle would leave the shell on a
-- blank panel, so tell it to fall back to Home. Harmless in split mode.
local function closeBattle()
    Battlemon.battleActive = nil
    Battlemon.BattleMusic.Stop()
    -- A level-up with four moves known leaves an offer to forget one; the server only asks once the battle is over.
    Battlemon.Send("LEARNQ")
    if not ui then
        return
    end
    ui.frame:Hide()
    if Battlemon.PanelClosed then
        Battlemon.PanelClosed("battle")
    end
end

local STATUS_RGB = {
    BRN = { 0.95, 0.45, 0.25 },
    PAR = { 0.98, 0.85, 0.25 },
    SLP = { 0.70, 0.70, 0.78 },
    PSN = { 0.80, 0.45, 0.85 },
    TOX = { 0.72, 0.32, 0.80 },
    FRZ = { 0.55, 0.85, 1.00 },
}

local WEATHER_TEXT = {
    RAIN = "Rain is falling.",
    SUN = "The sunlight is harsh.",
    SAND = "A sandstorm rages.",
    HAIL = "Hail is falling.",
}

local function setBusy(state)
    busy = state
    busySince = state and GetTime() or 0
end

local function blocked()
    return busy or awaiting
end

local function idle()
    awaiting = false
    awaitSince = 0
    setBusy(false)
end

-- Anything that touches battle state runs protected. A single nil field used to
-- abort mid-refresh and leave busy = true, which is why the buttons went dead.
local function safe(fn, ...)
    local ok, err = pcall(fn, ...)
    if not ok then
        Battlemon.Print("|cffff4040battle UI error:|r " .. tostring(err))
    end
    return ok
end

local function tex(parent, layer)
    return parent:CreateTexture(nil, layer or "ARTWORK")
end

local function hpFillColor(pct)
    if pct > 0.5 then
        return 0.28, 0.82, 0.41
    elseif pct > 0.2 then
        return 0.91, 0.78, 0.19
    end
    return 0.91, 0.28, 0.25
end

-- StatusBar keeps the fill texture at its file width (128px) instead of the
-- frame width (168px), so a full bar stopped at ~75%. Drive width ourselves.
local function makeHPBar(parent, width, height)
    local wrap = CreateFrame("Frame", nil, parent)
    wrap:SetWidth(width)
    wrap:SetHeight(height)
    wrap.barWidth = width
    wrap.track = tex(wrap, "BACKGROUND")
    wrap.track:SetAllPoints()
    Battlemon.Fill(wrap.track, 0.16, 0.13, 0.19, 1)
    wrap.fill = tex(wrap, "ARTWORK")
    wrap.fill:SetPoint("TOPLEFT")
    wrap.fill:SetPoint("BOTTOMLEFT")
    wrap.fill:SetWidth(width)
    Battlemon.Fill(wrap.fill, 0.28, 0.82, 0.41, 1)
    return wrap
end

local function setHPBar(bar, current, maxhp)
    if not maxhp or maxhp < 1 then
        maxhp = 1
    end
    local pct = (current or 0) / maxhp
    if pct < 0 then pct = 0 elseif pct > 1 then pct = 1 end
    local w = bar.barWidth * pct
    if w < 1 then
        bar.fill:Hide()
        return
    end
    bar.fill:Show()
    bar.fill:SetWidth(w)
    local r, g, b = hpFillColor(pct)
    Battlemon.Fill(bar.fill, r, g, b, 1)
end

local function genderTex(gender)
    if gender == "M" then
        return Battlemon.Media("gender_m")
    elseif gender == "F" then
        return Battlemon.Media("gender_f")
    end
    return nil
end

local function setStatus(fs, status)
    if not status or status == "" then
        fs:SetText("")
        return
    end
    local c = STATUS_RGB[status] or { 0.9, 0.9, 0.9 }
    fs:SetTextColor(c[1], c[2], c[3])
    fs:SetText(status)
end

local function hideMenus()
    ui.commands:Hide()
    ui.moves:Hide()
    ui.bag:Hide()
    ui.party:Hide()
    ui.catch:Hide()
end

local function sendAction(cmd, arg)
    hideMenus()
    awaiting = true
    awaitSince = GetTime()
    Battlemon.Send(cmd, arg)
end

-- "Trash Cloak Wormadam" reads better stacked than run together on one line, so
-- the form words sit above the species. The shiny star stays on the species line
-- to match every other place a name is shown.
--
-- Both lines are placed against the painted plate rather than against each
-- other. Hanging the form off the top of the name pushed it above the artwork on
-- the enemy plate, which only has 5px of margin, so the species drops instead
-- when there is a form to show.
local function setPlateName(plate, battler)
    local prefix, base = Battlemon.SplitFormName(battler.name, battler.speciesId, battler.formId)
    plate.name:ClearAllPoints()
    plate.name:SetPoint("TOPLEFT", plate.x, prefix and plate.stackedY or plate.plainY)
    plate.name:SetJustifyH("LEFT")
    if prefix then
        plate.form:SetText(prefix)
        plate.form:Show()
    else
        plate.form:Hide()
    end
    plate.name:SetText(Battlemon.ShinyName(base, battler.shiny))
end

local function refreshHUD()
    local b = Battlemon.battle
    if not b or not ui then
        return
    end
    local e, p = b.enemy, b.player

    if e then
        setPlateName(ui.enemyPlate, e)
        ui.enemyLv:SetText("Lv. " .. (e.level or 1))
        setStatus(ui.enemyStatus, e.status)
        setHPBar(ui.enemyHP, displayed.enemy, e.maxhp)
        local g = genderTex(e.gender)
        if g then
            ui.enemyGender:SetTexture(g)
            ui.enemyGender:Show()
        else
            ui.enemyGender:Hide()
        end
        ui.enemyHud:Show()
        local species = e.species or Battlemon.Species[e.speciesId or 0]
        ui.bg:SetTexture(Battlemon.HabitatBackground(species and species.habitat))
    else
        ui.enemyHud:Hide()
    end

    if p then
        setPlateName(ui.playerPlate, p)
        ui.playerLv:SetText("Lv. " .. (p.level or 1))
        setStatus(ui.playerStatus, p.status)
        setHPBar(ui.playerHP, displayed.player, p.maxhp)
        ui.playerHPText:SetText(math.floor(displayed.player + 0.5) .. " / " .. (p.maxhp or 1))
        local g = genderTex(p.gender)
        if g then
            ui.playerGender:SetTexture(g)
            ui.playerGender:Show()
        else
            ui.playerGender:Hide()
        end
        ui.playerHud:Show()
    else
        ui.playerHud:Hide()
    end

    local w = WEATHER_TEXT[b.weather or ""]
    if w then
        ui.weather:SetText(w)
        ui.weather:Show()
    else
        ui.weather:Hide()
    end

    Battlemon.SetBattlerTextures(ui.playerSprite, ui.enemySprite, p, e)
end

local showPartyMenu

-- A switch the player cannot decline: the active Pokémon is down. U-turn also
-- prompts for a switch, but with a conscious battler still out, so backing out
-- of that one stays legal.
local function mustSwitch()
    if not pending.switchNeed then
        return false
    end
    local p = Battlemon.battle and Battlemon.battle.player
    return p ~= nil and (p.hp or 0) <= 0
end

local function showCommand()
    -- Offering FIGHT with a fainted lead lets the player spend a turn the server
    -- refuses, so send them back to the switch they still owe.
    if mustSwitch() then
        showPartyMenu()
        return
    end
    hideMenus()
    ui.commands:Show()
    local b = Battlemon.battle
    if b and b.player then
        ui.msg:SetText("What will " .. (b.player.name or "your Pokémon") .. " do?")
    end
    idle()
end

-- Throwable balls, best last so the cheap one stays under the cursor.
local BALLS = { "POKEBALL", "GREATBALL", "ULTRABALL", "MASTERBALL" }

local function itemName(internal)
    local def = (Battlemon.Items or {})[internal]
    return (def and def.name) or internal
end

local function showCatch()
    hideMenus()
    ui.catch:Show()
    local allowed = pending.catch == true
    local bag = Battlemon.state.bag or {}

    local n = 0
    if allowed then
        for i = 1, #BALLS do
            local count = bag[BALLS[i]] or 0
            if count > 0 then
                n = n + 1
                local btn = ui.catchBtns[n]
                btn:Show()
                btn.item = BALLS[i]
                btn.text:SetText(string.format("%s   x%d", itemName(BALLS[i]), count))
                Battlemon.SetButtonEnabled(btn, true)
            end
        end
    end
    for i = n + 1, #ui.catchBtns - 1 do
        ui.catchBtns[i]:Hide()
        ui.catchBtns[i].item = nil
    end

    local leave = ui.catchBtns[#ui.catchBtns]
    leave:Show()
    leave.item = nil
    leave.text:SetText(allowed and "|cffff8080LEAVE IT|r" or "|cffff8080LEAVE|r")

    if allowed then
        local left = pending.catchThrows or Battlemon.state.catchThrows or 0
        local maxT = pending.catchThrowsMax or Battlemon.state.catchThrowsMax or 3
        if n == 0 then
            ui.msg:SetText("You have no balls left!")
        else
            ui.msg:SetText(string.format("Throw which ball?\n%d/%d throws left", left, maxT))
        end
    else
        ui.msg:SetText("Leave the battle?")
    end
    idle()
end

-- X items boost the Pokémon that is out. The catalog marks them OnBattler, so they are named here;
-- keep in step with XItemStat() in the server's BattlemonMgr.cpp (tests/test_xitems_addon.py checks it).
local X_ITEMS = { XATTACK = true, XDEFENSE = true, XSPATK = true, XSPDEF = true, XSPEED = true, XACCURACY = true }

-- Potions are usable now; balls are listed so you can see the stock, but they
-- only get thrown once the foe faints.
local bagOffset = 0

local function showBagMenu(keepOffset)
    hideMenus()
    ui.bag:Show()
    local bag = Battlemon.state.bag or {}
    local usable, inert = {}, {}
    for internal, count in pairs(bag) do
        if count > 0 then
            local def = (Battlemon.Items or {})[internal]
            local use = def and def.battle_use or ""
            local entry = { internal = internal, count = count, name = itemName(internal) }
            if use == "OnPokemon" or X_ITEMS[internal] then
                table.insert(usable, entry)
            else
                table.insert(inert, entry)
            end
        end
    end
    table.sort(usable, function(a, b) return a.name < b.name end)
    table.sort(inert, function(a, b) return a.name < b.name end)

    -- Usable items first, then the greyed-out rest. Only six fit, so the mouse wheel scrolls the list.
    local all = {}
    for _, e in ipairs(usable) do
        e.canUse = true
        table.insert(all, e)
    end
    for _, e in ipairs(inert) do
        table.insert(all, e)
    end
    local shown = #ui.bagBtns
    if not keepOffset then
        bagOffset = 0
    end
    bagOffset = math.max(0, math.min(bagOffset, #all - shown))

    local n = 0
    for i = 1, shown do
        local e = all[bagOffset + i]
        local btn = ui.bagBtns[i]
        if e then
            n = n + 1
            btn:Show()
            btn.item = e.canUse and e.internal or nil
            btn.text:SetText(e.canUse
                and string.format("%s   x%d", e.name, e.count)
                or string.format("|cff9095a0%s   x%d|r", e.name, e.count))
            Battlemon.SetButtonEnabled(btn, e.canUse == true)
        else
            btn:Hide()
            btn.item = nil
        end
    end

    if #all == 0 then
        ui.msg:SetText("Your bag is empty.\nRight-click to go back.")
    elseif #all > shown then
        ui.msg:SetText(string.format("Using an item takes your turn.\nScroll for more (%d-%d of %d). Right-click to go back.",
            bagOffset + 1, bagOffset + n, #all))
    else
        ui.msg:SetText("Using an item takes your turn.\nRight-click to go back.")
    end
end

-- A revive is the one item that names a target other than the Pokémon that is
-- out, so picking one re-purposes the party list into a target picker.
local REVIVES = { REVIVE = true, MAXREVIVE = true, REVIVALHERB = true }
local reviveItem = nil

function showPartyMenu()
    hideMenus()
    ui.party:Show()
    -- Drawn strictly from the server's battle snapshot. Reading state.owned here
    -- was the old bug: that HP is whatever was last written to the database, so
    -- anything that had ever fainted stayed red and unclickable forever.
    local party = (Battlemon.battle and Battlemon.battle.party) or {}
    local slots = Battlemon.state.partySlots or {}
    local forced = mustSwitch()
    local any = false
    for i = 1, 6 do
        local btn = ui.partyBtns[i]
        local row = party[i]
        if row then
            any = true
            btn:Show()
            btn.slot = i
            local down = (row.hp or 0) <= 0
            if reviveItem then
                btn.usable = down
            else
                btn.usable = not down and not row.active
            end
            btn.text:SetText(string.format("%d.  %s   Lv.%d   %s", i,
                Battlemon.ShinyName(row.name or "???", row.shiny),
                row.level or 1,
                down and "|cffd05050FAINTED|r"
                    or string.format("%d/%d", row.hp or 0, row.maxhp or 1)))
            if btn.usable then
                btn.text:SetTextColor(0.96, 0.96, 0.98)
            elseif down then
                btn.text:SetTextColor(0.85, 0.35, 0.35)
            else
                btn.text:SetTextColor(0.60, 0.62, 0.68)
            end
            Battlemon.SetButtonEnabled(btn, btn.usable)
        elseif not Battlemon.battle or not Battlemon.battle.party then
            -- Before the first snapshot lands, fall back to the roster just so
            -- the menu is not blank. Nothing here is clickable.
            local owned = Battlemon.state.owned[slots[i] or 0]
            if owned then
                any = true
                btn:Show()
                btn.slot = nil
                btn.usable = false
                btn.text:SetText(string.format("%d.  %s   Lv.%d", i,
                    Battlemon.ShinyName(Battlemon.FormName(owned.formId, owned.name), owned.shiny),
                    owned.level or 1))
                btn.text:SetTextColor(0.60, 0.62, 0.68)
                Battlemon.SetButtonEnabled(btn, false)
            else
                btn:Hide()
                btn.slot = nil
                btn.usable = nil
            end
        else
            btn:Hide()
            btn.slot = nil
            btn.usable = nil
        end
    end

    -- Escape hatch. Without it, a switch prompt where every slot is refused
    -- traps the player in the battle window with nothing left to click.
    local escape = ui.partyEscape
    escape:Show()
    escape.run = forced and not reviveItem
    escape.text:SetText(escape.run and "|cffff8080RUN FROM BATTLE|r" or "|cffb0b6c2BACK|r")

    if not any then
        ui.msg:SetText("No Pokémon in your party. Set one in /bm party.")
    elseif reviveItem then
        ui.msg:SetText("Revive which Pokémon?\nRight-click to go back.")
    elseif forced then
        ui.msg:SetText("Choose your next Pokémon!")
    end
    idle()
end

local function showMoves()
    hideMenus()
    ui.moves:Show()
    local moves = (Battlemon.battle and Battlemon.battle.player and Battlemon.battle.player.moves) or {}
    for i = 1, 4 do
        local btn = ui.moveBtns[i]
        local slot = moves[i]
        if slot and slot.data then
            Battlemon.SetButtonEnabled(btn, true)
            btn.moveIndex = i
            btn.text:SetText(slot.data.name or "?")
            local moveType = slot.data.type or ""
            local t = Battlemon.Types[moveType]
            btn.sub:SetText(t and t.name or moveType)
            local tr, tg, tb = Battlemon.TypeRGB(moveType)
            btn.sub:SetTextColor(tr * 0.55 + 0.05, tg * 0.48 + 0.04, tb * 0.38 + 0.04)
            btn.pp:SetText("PP " .. (slot.pp or 0) .. "/" .. (slot.maxpp or 0))
            if (slot.pp or 0) <= 0 then
                btn.pp:SetTextColor(0.72, 0.16, 0.16)
            else
                btn.pp:SetTextColor(0.18, 0.18, 0.20)
            end
        else
            Battlemon.SetButtonEnabled(btn, false)
            btn.moveIndex = nil
            btn.text:SetText("—")
            btn.sub:SetText("")
            btn.pp:SetText("")
        end
    end
    if #moves == 0 then
        ui.msg:SetText("This Pokémon has no moves. Right-click to go back.")
    end
end

local function pump()
    if not ui then
        return
    end
    if #queue == 0 then
        if pending.ending then
            setBusy(true)
            Battlemon.After(0.8, function()
                pending.ending = nil
                idle()
                -- Cleared before the hide so the shell's BATTLE tab sees the
                -- fight is over and greys out as it returns to Home.
                Battlemon.battle = nil
                closeBattle()
                Battlemon.Send("STATUS")
            end)
            return
        end
        if pending.catch ~= nil then
            showCatch()
            return
        end
        if pending.switchNeed then
            -- A forced switch stays pending until a conscious Pokémon is out, so
            -- a refused pick re-opens this menu instead of falling through to the
            -- command menu. An optional one is satisfied by showing the offer.
            if not mustSwitch() then
                pending.switchNeed = false
            end
            showPartyMenu()
            return
        end
        if Battlemon.battle then
            showCommand()
        else
            idle()
        end
        return
    end
    setBusy(true)
    local item = table.remove(queue, 1)
    if item.text then
        ui.msg:SetText(item.text)
    end
    safe(refreshHUD)
    Battlemon.After(item.delay or 1.05, function()
        safe(pump)
    end)
end

local function say(text, delay)
    table.insert(queue, { text = text, delay = delay or 1.05 })
end

local function nudge()
    if ui and ui.frame:IsShown() and not busy then
        safe(pump)
    end
end

local function makeCommandButton(parent, texturePath, label, onClick)
    local b = CreateFrame("Button", nil, parent)
    b:SetSize(142, 68)
    b.bg = tex(b, "BACKGROUND")
    b.bg:SetAllPoints()
    b.bg:SetTexture(texturePath)
    b.bg:SetVertexColor(0.88, 0.88, 0.88)
    b.text = Battlemon.Font(b, 20, "", 1, 1, 1, "Fonts\\ARIALN.TTF")
    b.text:SetPoint("CENTER", 0, 1)
    b.text:SetText(label)
    b:SetScript("OnEnter", function(self) self.bg:SetVertexColor(1, 1, 1) end)
    b:SetScript("OnLeave", function(self) self.bg:SetVertexColor(0.88, 0.88, 0.88) end)
    b:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    b:SetScript("OnClick", function(self, button)
        pcall(PlaySound, "igMainMenuOptionCheckBoxOn")
        safe(onClick, self, button)
    end)
    return b
end

-- Light plates, so type/PP stay dark. ARIALN is the readable 3.3.5 UI font;
-- FRIZQT at 11px on these buttons was the "tiny Times New Roman" look.
local function makeMoveButton(parent, onClick)
    local b = CreateFrame("Button", nil, parent)
    b:SetSize(142, 68)
    b.bg = tex(b, "BACKGROUND")
    b.bg:SetAllPoints()
    b.bg:SetTexture(Battlemon.Media("btn_move"))
    b.bg:SetVertexColor(0.92, 0.92, 0.94)
    b.text = Battlemon.Font(b, 18, "", 0.08, 0.08, 0.10, "Fonts\\ARIALN.TTF")
    b.text:SetShadowOffset(0, 0)
    b.text:SetPoint("TOP", 0, -10)
    b.sub = Battlemon.Font(b, 13, "", 0.20, 0.20, 0.22, "Fonts\\ARIALN.TTF")
    b.sub:SetShadowOffset(0, 0)
    b.sub:SetPoint("BOTTOMLEFT", 12, 10)
    b.pp = Battlemon.Font(b, 13, "", 0.18, 0.18, 0.20, "Fonts\\ARIALN.TTF")
    b.pp:SetShadowOffset(0, 0)
    b.pp:SetPoint("BOTTOMRIGHT", -12, 10)
    b:SetScript("OnEnter", function(self) self.bg:SetVertexColor(1, 1, 1) end)
    b:SetScript("OnLeave", function(self) self.bg:SetVertexColor(0.92, 0.92, 0.94) end)
    b:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    b:SetScript("OnClick", function(self, button)
        pcall(PlaySound, "igMainMenuOptionCheckBoxOn")
        safe(onClick, self, button)
    end)
    return b
end

local function makeListButton(parent, index, onClick)
    local b = Battlemon.MakeTextButton(parent, 300, 24, "", onClick, 0.14, 0.15, 0.20)
    b:SetPoint("TOPLEFT", 0, -((index - 1) * 26))
    b.text:ClearAllPoints()
    b.text:SetPoint("LEFT", 10, 0)
    b.text:SetJustifyH("LEFT")
    b.text:SetFont("Fonts\\FRIZQT__.TTF", 13, "")
    return b
end

local function menuFrame(parent)
    local m = CreateFrame("Frame", nil, parent)
    m:SetSize(300, 150)
    m:SetPoint("BOTTOMRIGHT", parent, "BOTTOMRIGHT", -14, 14)
    m:EnableMouse(true)
    m:SetScript("OnMouseUp", function(_, button)
        if button == "RightButton" and not blocked() then
            safe(showCommand)
        end
    end)
    m:Hide()
    return m
end

local function build()
    if ui then
        return ui
    end
    -- Hand-rolled rather than MakeWindow: the scene paints its own full-bleed
    -- background, so it wants none of the panel chrome. It still carries bmName
    -- and bmClose so the main window can adopt it as a page.
    local f = CreateFrame("Frame", "BattlemonFrame", UIParent)
    f.bmName = "BattlemonFrame"
    f:SetSize(780, 540)
    f:SetPoint("CENTER")
    f:SetFrameStrata("DIALOG")
    f:SetToplevel(true)
    f:EnableMouse(true)
    f:SetMovable(true)
    f:SetClampedToScreen(true)
    f:RegisterForDrag("LeftButton")
    f:SetScript("OnDragStart", function(self) self:StartMoving() end)
    f:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    f:Hide()
    Battlemon.EscClose("BattlemonFrame", true)

    local bg = tex(f, "BACKGROUND")
    bg:SetPoint("TOPLEFT")
    bg:SetPoint("TOPRIGHT")
    bg:SetHeight(360)
    bg:SetTexture(Battlemon.Media("bg_grass"))

    local bottom = tex(f, "BACKGROUND")
    bottom:SetPoint("TOPLEFT", bg, "BOTTOMLEFT")
    bottom:SetPoint("BOTTOMRIGHT")
    Battlemon.Fill(bottom, 0.08, 0.09, 0.12, 1)

    local enemyPlat = tex(f, "ARTWORK")
    enemyPlat:SetSize(220, 70)
    enemyPlat:SetPoint("TOPRIGHT", f, "TOPRIGHT", -36, -150)
    enemyPlat:SetTexture(Battlemon.Media("platform"))

    -- Sprites sit centred in a 256px canvas with heavy transparent padding, so
    -- they anchor by CENTER above the platform rather than by BOTTOM.
    local enemySprite = tex(f, "OVERLAY")
    enemySprite:SetSize(320, 320)
    enemySprite:SetPoint("CENTER", enemyPlat, "CENTER", 0, 34)

    local playerPlat = tex(f, "ARTWORK")
    playerPlat:SetSize(240, 78)
    playerPlat:SetPoint("BOTTOMLEFT", bg, "BOTTOMLEFT", 28, 8)
    playerPlat:SetTexture(Battlemon.Media("platform"))

    local playerSprite = tex(f, "OVERLAY")
    playerSprite:SetSize(360, 360)
    playerSprite:SetPoint("CENTER", playerPlat, "CENTER", 0, 36)

    local eHud = CreateFrame("Frame", nil, f)
    eHud:SetSize(300, 78)
    eHud:SetPoint("TOPLEFT", f, "TOPLEFT", 18, -18)
    local eHudBg = tex(eHud, "BACKGROUND")
    eHudBg:SetAllPoints()
    eHudBg:SetTexture(Battlemon.Media("hud_enemy"))

    local enemyName = Battlemon.Font(eHud, 15, "", 1, 1, 1)
    enemyName:SetPoint("TOPLEFT", 22, -14)
    enemyName:SetJustifyH("LEFT")

    -- hud_enemy.tga is painted from y -5 down, so this is as high as a line can
    -- sit; setPlateName drops the species to -24 to make room for it.
    local enemyForm = Battlemon.Font(eHud, 10, "", 1, 0.90, 0.62)
    enemyForm:SetPoint("TOPLEFT", 22, -9)
    enemyForm:SetJustifyH("LEFT")
    enemyForm:Hide()

    local enemyGender = tex(eHud, "OVERLAY")
    enemyGender:SetSize(14, 14)
    enemyGender:SetPoint("LEFT", enemyName, "RIGHT", 5, 0)

    -- The plate tapers to its point on the right: at the name row the paint stops
    -- around x 255, so a level parked at x 260 was hanging off the artwork.
    local enemyLv = Battlemon.Font(eHud, 13, "", 1, 1, 1)
    enemyLv:SetPoint("TOPRIGHT", -62, -14)
    enemyLv:SetJustifyH("RIGHT")

    -- Sized to the groove painted into hud_enemy.tga (x 16..230, centre y -53),
    -- leaving room at the left for the HP label, so a full bar reads as full.
    local eHP = makeHPBar(eHud, 184, 10)
    eHP:SetPoint("BOTTOMLEFT", 42, 20)
    local eHPLabel = Battlemon.Font(eHud, 10, "", 1, 0.85, 0.2)
    eHPLabel:SetPoint("RIGHT", eHP, "LEFT", -6, 0)
    eHPLabel:SetText("HP")

    -- On the name row: the bar now runs to the edge of the plate art, so there
    -- is no longer a gap beside it to hold the ailment tag.
    local enemyStatus = Battlemon.Font(eHud, 11, "", 1, 1, 1)
    enemyStatus:SetPoint("RIGHT", enemyLv, "LEFT", -8, 0)

    local pHud = CreateFrame("Frame", nil, f)
    pHud:SetSize(320, 110)
    pHud:SetPoint("BOTTOMRIGHT", bg, "BOTTOMRIGHT", -12, 8)
    local pHudBg = tex(pHud, "BACKGROUND")
    pHudBg:SetAllPoints()
    pHudBg:SetTexture(Battlemon.Media("hud_player"))

    local playerName = Battlemon.Font(pHud, 15, "", 1, 1, 1)
    playerName:SetPoint("TOPLEFT", 78, -22)
    playerName:SetJustifyH("LEFT")

    -- hud_player.tga starts at y -3, so the form line clears the species here
    -- without the species needing to move.
    local playerForm = Battlemon.Font(pHud, 10, "", 1, 0.90, 0.62)
    playerForm:SetPoint("TOPLEFT", 78, -8)
    playerForm:SetJustifyH("LEFT")
    playerForm:Hide()

    local playerGender = tex(pHud, "OVERLAY")
    playerGender:SetSize(14, 14)
    playerGender:SetPoint("LEFT", playerName, "RIGHT", 5, 0)

    local playerLv = Battlemon.Font(pHud, 13, "", 1, 1, 1)
    playerLv:SetPoint("TOPRIGHT", -22, -22)
    playerLv:SetJustifyH("RIGHT")

    -- Matches the groove in hud_player.tga (x 69..303, centre y -60). This one
    -- was 43px short, which is what made a full bar look like chipped health.
    local pHP = makeHPBar(pHud, 204, 10)
    pHP:SetPoint("TOPLEFT", 95, -55)
    local pHPLabel = Battlemon.Font(pHud, 10, "", 1, 0.85, 0.2)
    pHPLabel:SetPoint("RIGHT", pHP, "LEFT", -6, 0)
    pHPLabel:SetText("HP")

    local playerStatus = Battlemon.Font(pHud, 11, "", 1, 1, 1)
    playerStatus:SetPoint("RIGHT", playerLv, "LEFT", -8, 0)

    local playerHPText = Battlemon.Font(pHud, 13, "", 1, 1, 1)
    playerHPText:SetPoint("TOPRIGHT", pHP, "BOTTOMRIGHT", 0, -6)
    playerHPText:SetJustifyH("RIGHT")

    local weather = Battlemon.Font(f, 13, "", 0.88, 0.95, 1)
    weather:SetPoint("TOP", f, "TOP", 0, -10)
    weather:Hide()

    local dialogue = CreateFrame("Frame", nil, f)
    dialogue:SetSize(430, 150)
    dialogue:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", 14, 14)
    local dBg = tex(dialogue, "BACKGROUND")
    dBg:SetAllPoints()
    dBg:SetTexture(Battlemon.Media("dialogue"))
    local msg = Battlemon.Font(dialogue, 16, "", 0.10, 0.10, 0.14)
    msg:SetShadowOffset(0, 0)
    msg:SetPoint("TOPLEFT", 26, -26)
    msg:SetPoint("BOTTOMRIGHT", -26, 22)
    msg:SetJustifyH("LEFT")
    msg:SetJustifyV("TOP")

    local commands = CreateFrame("Frame", nil, f)
    commands:SetSize(300, 150)
    commands:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -14, 14)

    local fight = makeCommandButton(commands, Battlemon.Media("btn_fight"), "FIGHT", function()
        if blocked() then return end
        showMoves()
    end)
    fight:SetPoint("TOPLEFT")

    local bagBtn = makeCommandButton(commands, Battlemon.Media("btn_bag"), "BAG", function()
        if blocked() then return end
        safe(showBagMenu)
    end)
    bagBtn:SetPoint("TOPRIGHT")

    local partyBtn = makeCommandButton(commands, Battlemon.Media("btn_party"), "POKéMON", function()
        if blocked() then return end
        showPartyMenu()
    end)
    partyBtn:SetPoint("BOTTOMLEFT")

    local runBtn = makeCommandButton(commands, Battlemon.Media("btn_run"), "RUN", function()
        if blocked() then return end
        if not Battlemon.battle or not Battlemon.battle.enemy then
            -- Nothing to run from (the window was opened by a status update).
            closeBattle()
            return
        end
        sendAction("RUN")
    end)
    runBtn:SetPoint("BOTTOMRIGHT")

    local moves = menuFrame(f)
    local moveBtns = {}
    local anchors = { "TOPLEFT", "TOPRIGHT", "BOTTOMLEFT", "BOTTOMRIGHT" }
    for i = 1, 4 do
        local btn = makeMoveButton(moves, function(self, button)
            if button == "RightButton" then
                showCommand()
                return
            end
            if blocked() or not self.moveIndex then
                return
            end
            sendAction("MOVE", tostring(self.moveIndex))
        end)
        btn:SetPoint(anchors[i])
        moveBtns[i] = btn
    end

    local bagFrame = menuFrame(f)
    bagFrame:EnableMouseWheel(true)
    bagFrame:SetScript("OnMouseWheel", function(_, delta)
        if not blocked() then
            bagOffset = bagOffset - delta
            safe(function() showBagMenu(true) end)
        end
    end)
    local bagBtns = {}
    for i = 1, 6 do
        bagBtns[i] = makeListButton(bagFrame, i, function(self, button)
            if button == "RightButton" then
                showCommand()
                return
            end
            if blocked() or not self.item then
                return
            end
            if REVIVES[self.item] then
                reviveItem = self.item
                safe(showPartyMenu)
                return
            end
            sendAction("USEITEM", self.item)
        end)
    end

    -- Taller than the other menus: six slots plus the escape row.
    local partyFrame = menuFrame(f)
    partyFrame:SetSize(300, 182)
    local partyBtns = {}
    for i = 1, 6 do
        partyBtns[i] = makeListButton(partyFrame, i, function(self, button)
            if button == "RightButton" then
                reviveItem = nil
                showCommand()
                return
            end
            if blocked() or not self.slot or not self.usable then
                return
            end
            if reviveItem then
                local item = reviveItem
                reviveItem = nil
                sendAction("USEITEM", item .. "," .. self.slot)
                return
            end
            sendAction("SWITCH", tostring(self.slot))
        end)
    end
    local partyEscape = makeListButton(partyFrame, 7, function(self, button)
        if blocked() then
            return
        end
        if self.run and button ~= "RightButton" then
            sendAction("RUN")
            return
        end
        reviveItem = nil
        showCommand()
    end)

    -- A list rather than icon buttons: there are four ball types and the old
    -- 2x2 command layout could only ever show one.
    local catchFrame = CreateFrame("Frame", nil, f)
    catchFrame:SetSize(300, 150)
    catchFrame:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -14, 14)
    catchFrame:Hide()
    local catchBtns = {}
    for i = 1, 5 do
        catchBtns[i] = makeListButton(catchFrame, i, function(self)
            if blocked() then
                return
            end
            if self.item then
                sendAction("BALL", self.item)
            else
                sendAction("SKIPCATCH")
            end
        end)
    end

    -- Closing the battle is a forfeit, not just a window dismissal.
    f.bmClose = CreateFrame("Button", nil, f, "UIPanelCloseButton")
    f.bmClose:SetPoint("TOPRIGHT", 6, 6)
    f.bmClose:SetScript("OnClick", function()
        Battlemon.ForfeitBattle()
    end)

    -- Packets keep arriving while the page is hidden behind another tab, but
    -- nudge() refuses to pump a hidden frame, so by the time you come back the
    -- queue is backed up and nothing is scheduled to drain it. Restarting it here
    -- is what keeps the command menu reachable after tabbing away mid-fight.
    f:SetScript("OnShow", function()
        if Battlemon.battle then
            safe(refreshHUD)
        end
        nudge()
    end)

    -- Eases the HP bars toward their real value and, more importantly, clears a
    -- stuck busy flag so a dropped packet can never leave the menus dead.
    f:SetScript("OnUpdate", function(_, dt)
        local b = Battlemon.battle
        if b then
            local changed = false
            if b.player then
                local target = b.player.hp or 0
                if math.abs(displayed.player - target) > 0.5 then
                    local step = math.max((b.player.maxhp or 1) * dt * 0.9, 1)
                    if displayed.player < target then
                        displayed.player = math.min(displayed.player + step, target)
                    else
                        displayed.player = math.max(displayed.player - step, target)
                    end
                    changed = true
                elseif displayed.player ~= target then
                    displayed.player = target
                    changed = true
                end
            end
            if b.enemy then
                local target = b.enemy.hp or 0
                if math.abs(displayed.enemy - target) > 0.5 then
                    local step = math.max((b.enemy.maxhp or 1) * dt * 0.9, 1)
                    if displayed.enemy < target then
                        displayed.enemy = math.min(displayed.enemy + step, target)
                    else
                        displayed.enemy = math.max(displayed.enemy - step, target)
                    end
                    changed = true
                elseif displayed.enemy ~= target then
                    displayed.enemy = target
                    changed = true
                end
            end
            if changed then
                safe(refreshHUD)
            end
        end
        -- Nothing queued and still blocked long after the last action means a
        -- reply never arrived; hand control back rather than sit dead.
        local since = math.max(busySince, awaitSince)
        if blocked() and #queue == 0 and since > 0 and (GetTime() - since) > 8 then
            idle()
            if Battlemon.battle then
                safe(showCommand)
            else
                closeBattle()
            end
        end
    end)

    ui = {
        frame = f,
        bg = bg,
        enemyHud = eHud,
        playerHud = pHud,
        enemySprite = enemySprite,
        playerSprite = playerSprite,
        enemyName = enemyName,
        enemyForm = enemyForm,
        enemyPlate = { name = enemyName, form = enemyForm, x = 22, plainY = -14, stackedY = -24 },
        enemyLv = enemyLv,
        enemyGender = enemyGender,
        enemyStatus = enemyStatus,
        enemyHP = eHP,
        playerName = playerName,
        playerForm = playerForm,
        playerPlate = { name = playerName, form = playerForm, x = 78, plainY = -22, stackedY = -22 },
        playerLv = playerLv,
        playerGender = playerGender,
        playerStatus = playerStatus,
        playerHP = pHP,
        playerHPText = playerHPText,
        weather = weather,
        msg = msg,
        commands = commands,
        moves = moves,
        moveBtns = moveBtns,
        bag = bagFrame,
        bagBtns = bagBtns,
        party = partyFrame,
        partyBtns = partyBtns,
        partyEscape = partyEscape,
        catch = catchFrame,
        catchBtns = catchBtns,
    }
    return ui
end

function Battlemon.BuildBattle()
    return build().frame
end

function Battlemon.ShowBattle()
    build()
    local b = Battlemon.battle
    if not b then
        return
    end
    displayed.player = b.player and b.player.hp or 0
    displayed.enemy = b.enemy and b.enemy.hp or 0
    queue = {}
    pending.catch = nil
    pending.catchThrows = 0
    pending.ending = nil
    -- switchNeed survives: re-opening the window does not settle a switch the
    -- player still owes, and showCommand routes back to the prompt.
    idle()
    hideMenus()
    Battlemon.OpenPanel("battle")
    safe(refreshHUD)
    safe(showCommand)
end

Battlemon.OnNet("WILD", function()
    build()
    Battlemon.battleActive = true
    Battlemon.BattleMusic.Start()
    Battlemon.battle = Battlemon.battle or {}
    Battlemon.battle.weather = ""
    Battlemon.battle.playerStatus = ""
    Battlemon.battle.enemyStatus = ""
    displayed.player = 0
    displayed.enemy = 0
    queue = {}
    pending.catch = nil
    pending.catchThrows = 0
    pending.ending = nil
    pending.switchNeed = false
    reviveItem = nil
    Battlemon.battle.party = nil
    idle()
    hideMenus()
    Battlemon.OpenPanel("battle")
end)

-- The server also sends the party lead on login/status, so this packet only
-- updates state. Only WILD opens the battle window.
Battlemon.OnNet("P", function(a)
    build()
    Battlemon.battle = Battlemon.battle or {}
    local p = Battlemon.ParseBattler(a)
    p.status = Battlemon.battle.playerStatus or ""
    Battlemon.battle.player = p
    if pending.switchNeed and (p.hp or 0) > 0 then
        pending.switchNeed = false
    end
    if displayed.player == 0 then
        displayed.player = p.hp
    end
    if ui.frame:IsShown() then
        refreshHUD()
    end
end)

Battlemon.OnNet("E", function(a)
    build()
    Battlemon.battle = Battlemon.battle or {}
    local e = Battlemon.ParseBattler(a)
    e.status = Battlemon.battle.enemyStatus or ""
    Battlemon.battle.enemy = e
    if displayed.enemy == 0 then
        displayed.enemy = e.hp
    end
    if ui.frame:IsShown() then
        refreshHUD()
    end
end)

Battlemon.OnNet("MSG", function(a)
    local text = table.concat(a, "\t", 2)
    if text == "" then
        return
    end
    say(text)
    nudge()
end)

Battlemon.OnNet("CATCH", function(a)
    pending.catch = (a[2] == "1")
    pending.catchThrows = tonumber(a[3]) or 0
    if a[4] and a[4] ~= "" then
        pending.catchThrowsMax = tonumber(a[4]) or pending.catchThrowsMax or 3
    end
    Battlemon.state.catchThrows = pending.catchThrows
    Battlemon.state.catchThrowsMax = pending.catchThrowsMax
    nudge()
end)

Battlemon.OnNet("END", function(a)
    pending.ending = a[2] or "WIN"
    pending.catch = nil
    pending.catchThrows = 0
    pending.switchNeed = false
    reviveItem = nil
    nudge()
end)

Battlemon.OnNet("SWITCHNEED", function()
    pending.switchNeed = true
    nudge()
end)

Battlemon.OnNet("AIL", function()
    if ui and ui.frame:IsShown() then
        refreshHUD()
    end
end)

Battlemon.OnNet("WEATHER", function()
    if ui and ui.frame:IsShown() then
        refreshHUD()
    end
end)
