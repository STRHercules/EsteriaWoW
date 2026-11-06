Battlemon = Battlemon or {}

local timers = {}

function Battlemon.After(delay, fn)
    local f = CreateFrame("Frame")
    local elapsed = 0
    f:SetScript("OnUpdate", function(_, dt)
        elapsed = elapsed + dt
        if elapsed >= delay then
            f:SetScript("OnUpdate", nil)
            f:Hide()
            fn()
        end
    end)
    return f
end

function Battlemon.Print(msg)
    DEFAULT_CHAT_FRAME:AddMessage("|cffc45a9aBattlemon|r: " .. tostring(msg))
end

function Battlemon.Clamp(v, lo, hi)
    if v < lo then return lo end
    if v > hi then return hi end
    return v
end

function Battlemon.Copy(t)
    local n = {}
    for k, v in pairs(t) do
        n[k] = v
    end
    return n
end

function Battlemon.Media(name)
    return "Interface\\AddOns\\Battlemon\\assets\\ui\\" .. name
end
