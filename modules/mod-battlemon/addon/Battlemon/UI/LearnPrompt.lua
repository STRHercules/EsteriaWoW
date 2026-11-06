Battlemon = Battlemon or {}

-- "<Pokémon> wants to learn <move>! Forget which move?" The server sends LEARNOFFER when a Pokémon that already
-- knows four moves reaches a level a fifth is learned at; we answer with LEARNREPLY (a slot 1-4 to forget, 0 to
-- decline). Closing the window without answering leaves the offer waiting: it is asked again next time.

local ui
local offer -- { ownedId, move }

local function moveDef(internal)
    return (Battlemon.MovesByInternal or {})[internal]
end

local function moveName(internal)
    local def = moveDef(internal)
    return (def and def.name) or internal
end

local function moveLine(internal)
    local def = moveDef(internal)
    if not def then
        return ""
    end
    return string.format("%s   ·   %s   ·   Pow %s   ·   Acc %s   ·   PP %s", def.type or "", def.category or "",
        tostring(def.power or "-"), tostring(def.accuracy or "-"), tostring(def.pp or "-"))
end

local function reply(slot)
    if not offer then
        return
    end
    Battlemon.Send("LEARNREPLY", string.format("%d\t%s\t%d", offer.ownedId, offer.move, slot))
    offer = nil
    ui.frame:Hide()
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonLearnFrame", 520, 330)
    local title = Battlemon.Font(f, 18, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -18)
    title:SetWidth(480)
    local detail = Battlemon.Font(f, 12, "", 0.80, 0.86, 0.94)
    detail:SetPoint("TOP", 0, -48)
    detail:SetWidth(480)
    local ask = Battlemon.Font(f, 13, "", 0.92, 0.94, 0.98)
    ask:SetPoint("TOP", 0, -76)
    ask:SetWidth(480)
    ask:SetText("It already knows four moves. Forget one to make room?")

    local buttons = {}
    for slot = 1, 4 do
        local b = Battlemon.MakeTextButton(f, 460, 40, "", function()
            reply(slot)
        end, 0.16, 0.20, 0.28)
        b:SetPoint("TOP", 0, -102 - (slot - 1) * 46)
        b.text:SetFont("Fonts\\FRIZQT__.TTF", 12, "")
        buttons[slot] = b
    end
    local decline = Battlemon.MakeTextButton(f, 460, 36, "", function()
        reply(0)
    end, 0.30, 0.18, 0.16)
    decline:SetPoint("BOTTOM", 0, 18)

    f:Hide()
    ui = { frame = f, title = title, detail = detail, buttons = buttons, decline = decline }
    return ui
end

function Battlemon.ShowLearnOffer(ownedId, move, known, pokemon)
    local w = build()
    -- One prompt at a time; the server sends the next after this one is answered.
    if offer and w.frame:IsShown() and (offer.ownedId ~= ownedId or offer.move ~= move) then
        return
    end
    offer = { ownedId = ownedId, move = move }
    w.title:SetText(string.format("%s wants to learn %s!", pokemon ~= "" and pokemon or "Your Pokémon", moveName(move)))
    w.detail:SetText(moveLine(move))
    for slot = 1, 4 do
        local current = known[slot] or ""
        w.buttons[slot].text:SetText(string.format("Forget %s     |cff9aa4b0%s|r", moveName(current),
            current ~= "" and moveLine(current) or ""))
    end
    w.decline.text:SetText(string.format("Don't learn %s", moveName(move)))
    w.frame:Show()
end
