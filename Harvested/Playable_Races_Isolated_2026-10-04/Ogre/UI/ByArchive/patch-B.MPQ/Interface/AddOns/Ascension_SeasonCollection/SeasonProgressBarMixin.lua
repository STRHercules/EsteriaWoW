SeasonProgressBarMixin = {}

local TierEvents = {
	[1] = {
		Enum.GameEvent.Chapter1Tier1,
		Enum.GameEvent.Chapter1Tier2,
		Enum.GameEvent.Chapter1Tier3,
		Enum.GameEvent.Chapter1Tier4,
		Enum.GameEvent.Chapter1Tier5,
		Enum.GameEvent.Chapter1Tier6,
		Enum.GameEvent.Chapter1Tier7
	},
	[2] = {
		Enum.GameEvent.Chapter2Tier1,
		Enum.GameEvent.Chapter2Tier2,
		Enum.GameEvent.Chapter2Tier3,
		Enum.GameEvent.Chapter2Tier4,
		Enum.GameEvent.Chapter2Tier5,
		Enum.GameEvent.Chapter2Tier6,
		Enum.GameEvent.Chapter2Tier7
	},
	[3] = {
		Enum.GameEvent.Chapter3Tier1,
		Enum.GameEvent.Chapter3Tier2,
		Enum.GameEvent.Chapter3Tier3,
		Enum.GameEvent.Chapter3Tier4,
		Enum.GameEvent.Chapter3Tier5,
		Enum.GameEvent.Chapter3Tier6,
		Enum.GameEvent.Chapter3Tier7
	},
	[4] = {
		Enum.GameEvent.Chapter4Tier1,
		Enum.GameEvent.Chapter4Tier2,
		Enum.GameEvent.Chapter4Tier3,
		Enum.GameEvent.Chapter4Tier4,
		Enum.GameEvent.Chapter4Tier5,
		Enum.GameEvent.Chapter4Tier6,
		Enum.GameEvent.Chapter4Tier7
	},
}

-- achievement ID, criteria ID
local AchievementIDs = {
	[Enum.GameEvent.Chapter1Tier1] = { 10324, 10007 },
	[Enum.GameEvent.Chapter1Tier2] = { 10325, 10009 },
	[Enum.GameEvent.Chapter1Tier3] = { 10326, 10011 },
	[Enum.GameEvent.Chapter1Tier4] = { 10327, 10012 },
	[Enum.GameEvent.Chapter1Tier5] = { 10333, 10013 },
	[Enum.GameEvent.Chapter1Tier6] = { 10349, 10015 },
	[Enum.GameEvent.Chapter1Tier7] = { 10350, 10017 },

	[Enum.GameEvent.Chapter2Tier1] = { 10351, 10019 },
	[Enum.GameEvent.Chapter2Tier2] = { 10352, 10020 },
	[Enum.GameEvent.Chapter2Tier3] = { 10353, 10021 },
	[Enum.GameEvent.Chapter2Tier4] = { 10354, 10022 },
	[Enum.GameEvent.Chapter2Tier5] = { 10365, 10043 },
	[Enum.GameEvent.Chapter2Tier6] = { 10371, 10052 },
	[Enum.GameEvent.Chapter2Tier7] = { 10377, 10053 },

	[Enum.GameEvent.Chapter3Tier1] = { 10383, 10064 },
	[Enum.GameEvent.Chapter3Tier2] = { 10389, 10065 },
	[Enum.GameEvent.Chapter3Tier3] = { 10395, 10070 },
	[Enum.GameEvent.Chapter3Tier4] = { 10401, 10071 },
	[Enum.GameEvent.Chapter3Tier5] = { 10407, 10076 },
	[Enum.GameEvent.Chapter3Tier6] = { 10413, 10078 },
	[Enum.GameEvent.Chapter3Tier7] = { 10419, 10092 },

	[Enum.GameEvent.Chapter4Tier1] = { 10425, 10093 },
	[Enum.GameEvent.Chapter4Tier2] = { 10431, 10094 },
	[Enum.GameEvent.Chapter4Tier3] = { 10437, 10096 },
	[Enum.GameEvent.Chapter4Tier4] = { 10626, 10097 },
	[Enum.GameEvent.Chapter4Tier5] = { 10634, 10098 },
	[Enum.GameEvent.Chapter4Tier6] = { 10636, 10109 },
	[Enum.GameEvent.Chapter4Tier7] = { 10680, 10113 },
}

function SeasonProgressBarMixin:OnLoad()
	self:SetSparkColor(1, 0.82, 0)
	self:SetValue(0)
end

function SeasonProgressBarMixin:OnShow()
	self:HookEvent("ACHIEVEMENT_EARNED")
	self:HookBucketEvent("CRITERIA_UPDATE", 0.1)
	self:UpdateProgress()
end

function SeasonProgressBarMixin:OnHide()
	C_Hook:Unregister(self)
end

function SeasonProgressBarMixin:CRITERIA_UPDATE()
	self:UpdateProgress()
end

function SeasonProgressBarMixin:ACHIEVEMENT_EARNED()
	self:UpdateProgress()
end

local tierStep = 0.14285 -- 1/7
function SeasonProgressBarMixin:UpdateProgress()
	self.LastValue = self:GetValue()

	local minValue, maxValue = 0, 0
	local maxQuantity, maxReqQuantity = 0, 0
	local percent = 0
	local lastCompleteFound

	-- find latest tier unlocked
	-- highlight last completed achievement node
	for i = #self.Tiers, 1, -1 do
		local tier = self.Tiers[i]
		if GameEventUtil.IsEventActive(tier.Event) then
			local isComplete = select(4, GetAchievementInfo(tier.AchievementID))
			local _, _, _, quantity, reqQuantity = GetAchievementCriteriaInfo(tier.CriteriaID)

			if not isComplete and not lastCompleteFound then
				maxQuantity = quantity
				maxReqQuantity = reqQuantity
				maxValue = i * tierStep * 100
			end

			if isComplete and not lastCompleteFound then
				lastCompleteFound = true
				if i == #self.Tiers then
					minValue = 100
				else
					minValue = i * tierStep * 100
				end
				maxQuantity = maxQuantity - reqQuantity
				maxReqQuantity = maxReqQuantity - reqQuantity
				
				percent = MClamp(maxQuantity / maxReqQuantity, 0, 1)
				self:SelectTier(i)
			end
		end
	end

	if minValue > maxValue then
		self.TargetValue = minValue
	else
		self.TargetValue = ((maxValue - minValue) * percent) + minValue
	end

	if not lastCompleteFound then
		self.Tier0.Selected:Show()
	end

	-- slide bar to current progress
	if self.LastValue < self.TargetValue then
		-- upvalue these so next open will just snap to complete
		-- dont want some long animation EVERY time
		local lastValue = self.LastValue
		local targetValue = self.TargetValue
		self.LastValue = targetValue
		self.lerp = 0

		self:SetScript("OnUpdate", function(self, elapsed)
			if MApprox(self:GetValue(), targetValue, 0.1) then
				self:SetScript("OnUpdate", nil)
				self:SetValue(targetValue)
				self:CheckCompleteTiers()
				self.lerp = nil
				self.targetValue = nil
				return
			end
			
			self:SetValue(math.lerp(lastValue, targetValue, EaseOut(self.lerp)))
			self:CheckCompleteTiers()
			self.lerp = self.lerp + (elapsed / 2)
		end)
	end
end

function SeasonProgressBarMixin:CheckCompleteTiers()
	local value = self:GetValue()
	local tier = self:GetLastTierForProgress(value)
	if tier then
		tier:CompleteTier(true)
	end
end

function SeasonProgressBarMixin:GetLastTierForProgress(value)
	local tier = floor((value / 100) / tierStep)
	return self.Tiers[tier]
end

function SeasonProgressBarMixin:SelectTier(tierID)
	self:GetParent():SelectTier(tierID)
	self.Tier0:SetSelected(false)

	for id, button in ipairs(self.Tiers) do
		button:SetSelected(tierID == id)
	end
end

--
-- Season Tier Mixin
--
SeasonTierMixin = {}

function SeasonTierMixin:OnLoad()
	self.Selected:SetAtlas("season-collection-tier-selected", Const.TextureKit.UseAtlasSize)
	self.Icon:SetPortraitTexture("Interface\\Icons\\seasonal_blank")
	self.MetalBorder:SetAtlas("season-collection-tier-border", Const.TextureKit.UseAtlasSize)
	self.Locked:SetAtlas("communities-icon-lock", Const.TextureKit.UseAtlasSize)
	self.UnlockedBorder:SetAtlas("season-collection-tier-unlocked", Const.TextureKit.UseAtlasSize)
	self.UnlockSpark:SetAtlas("MissionFX-SparkLines", Const.TextureKit.IgnoreAtlasSize)
	self.UnlockGlow:SetAtlas("Garr_BuildingTimerGlow", Const.TextureKit.IgnoreAtlasSize)

	if self:GetID() > 0 then
		SetParentArray(self, "Tiers", self:GetID())
		self.RewardOverlay.Background.Anim:Play()
	else
		self.IsBaseTier = true
		self.RewardOverlay:Hide()
	end
end

function SeasonTierMixin:OnShow()
	if self.IsBaseTier then
		self:SetEnabled(IsSeasonalCollectionUnlocked())
	else
		self.Event = TierEvents[self:GetCurrentChapter()][self:GetID()]
		self.AchievementID, self.CriteriaID = unpack(AchievementIDs[self.Event])

		self.Icon:SetPortraitTexture(select(10, GetAchievementInfo(self.AchievementID)))

		if not self.Complete then
			local points = self:GetRewardPoints()
			if points then
				self.RewardOverlay.Text:SetFormattedText("x%d", points)
			else
				self.RewardOverlay.Text:SetText("")
			end
			self.RewardOverlay:Show()
		end
		
		self:SetEnabled(GameEventUtil.IsEventActive(self.Event))
	end
end

function SeasonTierMixin:OnEnable()
	self.Locked:Hide()
	self.Icon:SetVertexColor(1, 1, 1)
end

function SeasonTierMixin:OnDisable()
	self.Locked:Show()
	self.UnlockedBorder:Hide()
	self.Selected:Hide()
	self.Icon:SetVertexColor(0.4, 0.4, 0.4)
end

function SeasonTierMixin:GetRewardPoints()
	local rewardText = select(11, GetAchievementInfo(self.AchievementID))
	if not rewardText then
		dprint("SeasonTier", self:GetID(), "No Reward Text for", self.AchievementID)
		return
	end

	local rewardPoints = string.match(rewardText, "(%d+)")
	if not rewardPoints or not tonumber(rewardPoints) then
		dprint("SeasonTier", self:GetID(), "Could not find reward amount in", rewardText)
		return
	end

	return tonumber(rewardPoints)
end

function SeasonTierMixin:CompleteTier()
	if self.Complete then return end
	self.UnlockedBorder:Show()
	self.RewardOverlay:Hide()
	self.UnlockSpark.Anim:Play()
	self.UnlockGlow.Anim:Play()
	self.MetalBorder:SetVertexColor(1, 1, 1)
	PlaySound(SOUNDKIT.UI_70_ARTIFACT_FORGE_TRAIT_UNLOCK)
	self.Complete = true
end

function SeasonTierMixin:SetSelected(selected)
	self.Selected:SetShown(selected)
end

function SeasonTierMixin:OnEnter()
	GameTooltip:SetOwner(self, "ANCHOR_TOP")
	if self.IsBaseTier then
		GameTooltip:SetText(UNLOCK_SEASONAL_COLLECTION, 1, 1, 1, 1, false)
		if not IsSeasonalCollectionUnlocked() then
			GameTooltip:AddLine(OBTAIN_ITEM_TO_EARN_COSMETICS:format(GetItemName(ItemData.SEASONAL_PASS)), 1, 0.82, 0, true)
		else
			GameTooltip:AddLine(ITEM_EARNED:format(GetItemName(ItemData.SEASONAL_PASS)), 0.1, 1, 0.1, true)
		end
	else
		GameTooltip:SetText(TIER_D:format(self:GetID()), 1, 1, 1, false)
		if not GameEventUtil.IsEventActive(self.Event) then
			GameTooltip:AddLine(UNLOCKS_IN_TIME:format(SecondsToTime(GameEventUtil.GetTimeUntil(self.Event))), 1, 0.1, 0.1, false)
		else
			local _, _, _, quantity, reqQuantity = GetAchievementCriteriaInfo(self.CriteriaID)
			local color = quantity >= reqQuantity and GREEN_FONT_COLOR or NORMAL_FONT_COLOR
			local rewardPoints = self:GetRewardPoints()
			GameTooltip:AddLine(EARNED_S_OF_S_ACHIEVEMENT_POINTS:format("|cffFFFFFF" .. quantity .. "|r", "|cffFFFFFF" .. reqQuantity.."|r"), color.r, color.g, color.b, true)
			if (rewardPoints) then
				GameTooltip_AddSpacer(GameTooltip)
				GameTooltip:AddLine(REWARDS_S_SEASONAL_POINTS:format("|cffFFFFFF"..rewardPoints.."|r"), color.r, color.g, color.b, true)
			end
		end
	end
	GameTooltip:Show()
end 

function SeasonTierMixin:GetCurrentChapter()
	if GameEventUtil.IsEventActive(Enum.GameEvent.Chapter4Tier1) then
		return 4
	end

	if GameEventUtil.IsEventActive(Enum.GameEvent.Chapter3Tier1) then
		return 3
	end

	if GameEventUtil.IsEventActive(Enum.GameEvent.Chapter2Tier1) then
		return 2
	end

	return 1
end 