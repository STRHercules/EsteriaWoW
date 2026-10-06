local BONUS_PACK_MAX_PROGRESS = 400
-------------------------------------------------------------------------------
--                           Progress Bar Minimized                          --
-------------------------------------------------------------------------------
SkillCardProgressMinimizedBar = CreateFromMixins(CallbackRegistryMixin)

function SkillCardProgressMinimizedBar:OnLoad()
	CallbackRegistryMixin.OnLoad(self)
	BetterStatusBarMixin.OnLoad(self)

	self:GenerateCallbackEvents({
		"OnProgressUpdateFinished",
	})
	
	self:Layout()
	self:SetValue(0)
	self:SetMinMaxValues(0, 100)
	self:EnableMouse(true)

	self.newValue = nil
	self.valueStep = 0.05
end

function SkillCardProgressMinimizedBar:UpdateText(value)
	self:SetText(string.format("(%s%%)", math.ceil(value)))
end

function SkillCardProgressMinimizedBar:OnValueChanged(value)
	self:UpdateText(value)
end

function SkillCardProgressMinimizedBar:OnUpdateAnim()
	if math.NearlyEquals( (self:GetValue()+self.valueStep), self.newValue, 1) then
		self:SetValue(math.ceil(self.newValue))
		self:SetScript("OnUpdate", nil)
		self:TriggerEvent("OnProgressUpdateFinished")
	end

	local valueDiff = self.newValue - self:GetValue()

	self:SetValue(self:GetValue()+(valueDiff*self.valueStep))
end

function SkillCardProgressMinimizedBar:PlayUpdateValueAnim(oldValue, newValue)
	self.newValue = newValue
	self:SetValue(oldValue)
	self:SetScript("OnUpdate", self.OnUpdateAnim)
end

function SkillCardProgressMinimizedBar:OnShow()
	self:Update()
end

function SkillCardProgressMinimizedBar:Layout()
	self:SetStatusBarAtlas("ui-frame-bar-fill-white")
	self:SetStatusBarColor(0.6, 0.1, 0.85, 1)
	self:SetHeight(14)
	self:SetWidth(48)
		
	self:SetSparkAtlas("skillbar_flare_enchanting")
	self:SetSparkSize(8, 16)
	self:SetSparkPoint("RIGHT")

	self:SetBackdrop({
			bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
		})
	self:SetBackdropColor(0, 0, 0, 1)

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

-------------------------------------------------------------------------------
--                                Progress Bar                               --
-------------------------------------------------------------------------------
SkillCardFreeBoosterProgressBar = CreateFromMixins(SkillCardProgressMinimizedBar)

function SkillCardFreeBoosterProgressBar:UpdateText(value)
	self:SetText(format((self.text or "").." (%.2f%%)", value))
end

function SkillCardFreeBoosterProgressBar:PlayUpdateValueAnim()
	local progress = SkillCardUtil.GetBonusSealedCardPacksProgress()

	if self:GetScript("OnUpdate") then
		self.newValue = progress
	else
		SkillCardProgressMinimizedBar.PlayUpdateValueAnim(self, self:GetValue(), progress)
	end

	self:PlayFlipbook()
end

function SkillCardFreeBoosterProgressBar:Layout()
	local atlasInfo = "skillbar_fill_flipbook_alchemy"
	local atlas = AtlasUtil:GetAtlasInfo(atlasInfo)

	local frameWidth, frameHeight = 856, 34
	local frames = (atlas.height / frameHeight) * 2
	local fps = 26

	self:SetStatusBarFlipbookAtlas(atlasInfo, 856, 34, frames, fps, true)
	self:SetHeight(16)
	self.flipbook:Play()
		
	self:SetSparkAtlas("skillbar_flare_enchanting")
	self:SetSparkSize(50, 20)
	self:SetSparkPoint("RIGHT")

	self:SetBackdrop({
			bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
		})
	self:SetBackdropColor(0, 0, 0, 1)

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