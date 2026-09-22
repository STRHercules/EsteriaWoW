local function UpdateIcon(button)
    if not button then return end
    local slot = button.action
    if not slot then return end
    local kind, id = GetActionInfo(slot)
    if kind ~= "spell" or id ~= 970100 then return end
    local texture = GetInventoryItemTexture("player", 18)
    local icon = button.icon or _G[button:GetName() .. "Icon"]
    if icon and texture then icon:SetTexture(texture) end
end
if hooksecurefunc then hooksecurefunc("ActionButton_Update", UpdateIcon) end
local frame = CreateFrame("Frame")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
frame:RegisterEvent("UNIT_INVENTORY_CHANGED")
frame:RegisterEvent("ACTIONBAR_SLOT_CHANGED")
frame:SetScript("OnEvent", function(self, event, unit)
    if event == "UNIT_INVENTORY_CHANGED" and unit ~= "player" then return end
    for _, prefix in ipairs({"ActionButton", "MultiBarBottomLeftButton", "MultiBarBottomRightButton", "MultiBarRightButton", "MultiBarLeftButton"}) do
        for i=1,12 do UpdateIcon(_G[prefix .. i]) end
    end
end)
