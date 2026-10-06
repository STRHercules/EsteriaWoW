ECProgressBarMixin = {}

function ECProgressBarMixin:OnLoad()
	BetterStatusBarMixin.OnLoad(self)
	self:Layout()
	self:SetMinMaxValues(0, 100)
	self:EnableMouse(true)
	self:SetValue(-1)

	self.valueStep = 0.05
end

function ECProgressBarMixin:OnEnter()
	GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
	GameTooltip:AddLine(string.format(MYSTIC_ENCHANTING_ALTAR.." "..(self.text or "")), 1, 1, 1, 1)
	GameTooltip:AddLine(MYSTIC_ENCHANT_EXP_BAR_DESC, 1, 0.82, 0, 1)
	GameTooltip:Show()
end

function ECProgressBarMixin:OnLeave()
	GameTooltip:Hide()
end

function ECProgressBarMixin:OnValueChanged(value)
	self:SetText(format((self.text or "").." (%s%%)", math.ceil(value)))
end

function ECProgressBarMixin:OnUpdateAnim()
	if ((self:GetValue()+self.valueStep) >= self.newValue) then
		self:SetValue(math.ceil(self.newValue))
		self:SetScript("OnUpdate", nil)
	end

	local valueDiff = self.newValue - self:GetValue()

	self:SetValue(self:GetValue()+(valueDiff*self.valueStep))
end

function ECProgressBarMixin:PlayUpdateValueAnim(oldValue, newValue)
	self.newValue = newValue
	self:SetValue(oldValue)
	self:SetScript("OnUpdate", self.OnUpdateAnim)
end

function ECProgressBarMixin:Layout()
	local atlasInfo = "skillbar_fill_flipbook_enchanting"
	local atlas = AtlasUtil:GetAtlasInfo(atlasInfo)

	-- TODO: Review later, copied from TradeSkillUI
	local frameWidth, frameHeight = 856, 34
	local frames = (atlas.height / frameHeight) * 2
	local fps = 26

	self:SetStatusBarFlipbookAtlas(atlasInfo, frameWidth, frameHeight, frames, fps, true)
	self:SetSize(332, 22)
	self.flipbook:Play()
		
	self:SetSparkAtlas("skillbar_flare_enchanting")
	self:SetSparkSize(50, 20)
	self:SetSparkPoint("RIGHT")

	self.BorderFrame = CreateFrame("FRAME", "$parent.BorderFrame", self, nil)
	self.BorderFrame:SetPoint("TOPLEFT", -5, 5)
	self.BorderFrame:SetPoint("BOTTOMRIGHT", 5, -5)
	self.BorderFrame:SetBackdrop(
		{
			edgeFile="Interface\\FriendsFrame\\UI-Toast-Border", 
			tile=true, 
			tileSize = 12, 
			edgeSize = 12,
		})
end