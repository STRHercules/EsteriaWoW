local PAID_RACE_SERVICE_OVERRIDE_FACTIONS = {
	[FACTION_HORDE]		= PLAYER_FACTION_GROUP.Alliance,
	[FACTION_ALLIANCE]	= PLAYER_FACTION_GROUP.Horde,
}

local PAID_SERVICE_ORIGINAL_FACTION = {
	[FACTION_HORDE]		= PLAYER_FACTION_GROUP.Horde,
	[FACTION_ALLIANCE]	= PLAYER_FACTION_GROUP.Alliance,
	[FACTION_NEUTRAL]	= PLAYER_FACTION_GROUP.Neutral,
}

local PAID_RACE_SERVICE_DYNAMIC = {
	[E_CHARACTER_RACES.RACE_DRACTHYR]				= E_CHARACTER_RACES.RACE_DRACTHYR,
}

local PAID_SERVICE_ORIGINAL_RACE = {
	[E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE]		= E_CHARACTER_RACES.RACE_PANDAREN_NEUTRAL,
	[E_CHARACTER_RACES.RACE_PANDAREN_HORDE]			= E_CHARACTER_RACES.RACE_PANDAREN_NEUTRAL,
	[E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE]		= E_CHARACTER_RACES.RACE_VULPERA_NEUTRAL,
	[E_CHARACTER_RACES.RACE_VULPERA_HORDE]			= E_CHARACTER_RACES.RACE_VULPERA_NEUTRAL,
}

local PAID_FACTION_SERVICE_OVERRIDE_RACES = {
	[FACTION_ALLIANCE] = {
		[E_CHARACTER_RACES.RACE_PANDAREN_NEUTRAL]	= E_CHARACTER_RACES.RACE_PANDAREN_HORDE,
		[E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE]	= E_CHARACTER_RACES.RACE_PANDAREN_HORDE,
		[E_CHARACTER_RACES.RACE_VULPERA_NEUTRAL]	= E_CHARACTER_RACES.RACE_VULPERA_HORDE,
		[E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE]	= E_CHARACTER_RACES.RACE_VULPERA_HORDE,
	},
	[FACTION_HORDE] = {
		[E_CHARACTER_RACES.RACE_PANDAREN_NEUTRAL]	= E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE,
		[E_CHARACTER_RACES.RACE_PANDAREN_HORDE]		= E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE,
		[E_CHARACTER_RACES.RACE_VULPERA_NEUTRAL]	= E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE,
		[E_CHARACTER_RACES.RACE_VULPERA_HORDE]		= E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE,
	}
}

local PAID_RACE_SERVICE_OVERRIDE_RACES = {
	[FACTION_ALLIANCE] = {
		[E_CHARACTER_RACES.RACE_PANDAREN_HORDE]		= E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE,
		[E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE]	= E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE,
		[E_CHARACTER_RACES.RACE_PANDAREN_NEUTRAL]	= E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE,
		[E_CHARACTER_RACES.RACE_VULPERA_HORDE]		= E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE,
		[E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE]	= E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE,
		[E_CHARACTER_RACES.RACE_VULPERA_NEUTRAL]	= E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE,
	},
	[FACTION_HORDE] = {
		[E_CHARACTER_RACES.RACE_PANDAREN_HORDE]		= E_CHARACTER_RACES.RACE_PANDAREN_HORDE,
		[E_CHARACTER_RACES.RACE_PANDAREN_ALLIANCE]	= E_CHARACTER_RACES.RACE_PANDAREN_HORDE,
		[E_CHARACTER_RACES.RACE_PANDAREN_NEUTRAL]	= E_CHARACTER_RACES.RACE_PANDAREN_HORDE,
		[E_CHARACTER_RACES.RACE_VULPERA_HORDE]		= E_CHARACTER_RACES.RACE_VULPERA_HORDE,
		[E_CHARACTER_RACES.RACE_VULPERA_ALLIANCE]	= E_CHARACTER_RACES.RACE_VULPERA_HORDE,
		[E_CHARACTER_RACES.RACE_VULPERA_NEUTRAL]	= E_CHARACTER_RACES.RACE_VULPERA_HORDE,
	}
}

local CREATION_STATES = {
	DEFAULT = 0,
	SIGN_SELECTION = 1,
}
local CREATION_STATE = 0

local VIEW_STATES = {
	RACE_CLASS = 0,
	CUSTOMIZATIONS = 1,
	ZODIAC_SIGNS = 2,
}
local VIEW_STATE = 0

local CAMERA_ZOOM_LEVEL_AMOUNT = 80

local TOOLTIP_MAX_CLASS_ABLILITIES = 5
local TOOLTIP_MAX_RACE_ABLILITIES_PASSIVE = 4
local TOOLTIP_MAX_RACE_ABLILITIES_ACTIVE = 3
local TOOLTIPS_EXPANDED = false

CharacterCreateMixin = {}

local pullButtonReset = function(framePool, frame)
	FramePool_HideAndClearAnchors(framePool, frame)
	frame:Enable()
	frame:SetAlpha(1)
end

function CharacterCreateMixin:OnLoad()
	self.VignetteTop:SetAtlas("charactercreate-vignette-top", true)
	self.VignetteBottom:SetAtlas("charactercreate-vignette-bottom", true)
	self.VignetteLeft:SetAtlas("charactercreate-vignette-sides", true)
	self.VignetteRight:SetAtlas("charactercreate-vignette-sides", true)
	self.VignetteRight:SetSubTexCoord(1, 0, 0, 1)

	self:RegisterCustomEvent("GLUE_CHARACTER_CREATE_UPDATE_CLASSES")
	self:RegisterCustomEvent("GLUE_CHARACTER_CREATE_FORCE_RACE_CHANGE")
	self:RegisterCustomEvent("GLUE_CHARACTER_CREATE_ZOOM_UPDATE")
	self:RegisterCustomEvent("GLUE_CHARACTER_CREATE_ZODIAC_SELECTED")

	self.raceButtonPerLine = 5

	self.clientRaceData = {}
	self.clientClassData = {}

	self.raceButtonPool = CreateFramePool("CheckButton", self, "CharacterCreateRaceButtonTemplate", pullButtonReset)
	self.classButtonPool = CreateFramePool("CheckButton", self.ClassesFrame, "CharacterCreateClassButtonTemplate", pullButtonReset)
	self.genderButtonPool = CreateFramePool("CheckButton", self.GenderFrame, "CharacterCreateGenderButtonTemplate", pullButtonReset)

	self.NavigationFrame.CreateNameEditBox:SetPoint("BOTTOM", self.GenderFrame.CustomizationButton, "TOP", 0, 5)
	self.NavigationFrame.HardcoreButton:SetPoint("RIGHT", self.GenderFrame, "RIGHT", -67, 0)
end

function CharacterCreateMixin:OnShow()
	C_CharacterCreation.SetInCharacterCreate(true)

	if C_CharacterCreation.PaidChange_IsActive(true) and self:CanSetZodiacSignState() then
		CREATION_STATE = CREATION_STATES.SIGN_SELECTION
		VIEW_STATE = VIEW_STATES.ZODIAC_SIGNS
	else
		CREATION_STATE = CREATION_STATES.DEFAULT
		VIEW_STATE = VIEW_STATES.RACE_CLASS
	end

	if C_CharacterCreation.PaidChange_IsActive(true) then
		self:UpdateCreationState()
		self.NavigationFrame.CreateNameEditBox:SetText(C_CharacterCreation.PaidChange_GetName())
		self.NavigationFrame.HardcoreButton:Hide()
	else
		C_CharacterCreation.ResetCharCustomize()
		self:UpdateCreationState()
		self.NavigationFrame.CreateNameEditBox:SetText("")
		if C_CharacterCreation.CanCreateHardcoreCharacter() then
			self.NavigationFrame.HardcoreButton:SetChecked(C_CharacterCreation.GetHardcoreFlag())
			self.NavigationFrame.HardcoreButton:Show()
		else
			self.NavigationFrame.HardcoreButton:Hide()
		end
	end

	self.NavigationFrame.CreateNameEditBox:Show()
	self.NavigationFrame.RandomNameButton:Show()
	self.CustomizationFrame.DressCheckButton:SetChecked(C_CharacterCreation.IsDressed())

	self:UpdateBackground()

	if PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_FACTION and select(3, C_CharacterCreation.PaidChange_GetCurrentFaction()) == SERVER_PLAYER_FACTION_GROUP.Neutral then
		self.NavigationFrame.CreateNameEditBox:SetAutoFocus(false)
		self.NavigationFrame.CreateNameEditBox:ClearFocus()
		self.NavigationFrame:Hide()
		self.AllianceRacesFrame:Hide()
		self.HordeRacesFrame:Hide()
		self.NeutralRacesFrame:Hide()
		self.GenderFrame:Hide()
		self.ClassesFrame:Hide()

		PlaySound(SOUNDKIT.GS_TITLE_OPTIONS)
		GlueDialog:ShowDialog("FORCE_CHOOSE_FACTION")

		return
	end

	self.GenderFrame.CustomizationButton:SetText(CHARACTER_CREATE_CUSTOMIZATION_LABEL)
	self:CreateUpdateButtons()
	self:UpdateCharacterCreateButton()
	self.skipCustomizationConfirmation = false

	C_CharacterCreation.EnableMouseWheel(true)
end

function CharacterCreateMixin:OnHide()
	C_CharacterCreation.SetInCharacterCreate(false)
	self.CustomizationFrame:Hide()
	self.CustomizationFrame:Reset()
	self.ZodiacSignFrame:Hide()
	self.ZodiacSignFrame:Reset()
	self:ResetSelectRaceAndClassAnim()
	C_CharacterCreation.EnableMouseWheel(false)
end

function CharacterCreateMixin:OnEvent(event, ...)
	if event == "GLUE_CHARACTER_CREATE_FORCE_RACE_CHANGE" then
		self.NavigationFrame:Show()
		self.NavigationFrame.CreateNameEditBox:SetAutoFocus(true)
		self.NavigationFrame.CreateNameEditBox:SetFocus()
		self.NavigationFrame.CreateNameEditBox:HighlightText(0, 0)
		self.AllianceRacesFrame:Show()
		self.HordeRacesFrame:Show()
		self.NeutralRacesFrame:Show()
		self.GenderFrame:Show()
		self.ClassesFrame:Show()

		self:CreateUpdateButtons()
	elseif event == "GLUE_CHARACTER_DRESS_STATE_UPDATE" then
		local isDressed = ...
		self.CustomizationFrame.DressCheckButton:SetChecked(isDressed)
	elseif event == "GLUE_CHARACTER_CREATE_ZOOM_UPDATE" then
		if self.CustomizationFrame:IsVisible() then
			self.CustomizationFrame:UpdateZoomButtonStates()
		end
	elseif event == "GLUE_CHARACTER_CREATE_ZODIAC_SELECTED" then
		self:UpdateCharacterCreateButton()
	elseif event == "GLUE_CHARACTER_CREATE_UPDATE_CLASSES" then
		self:UpdateClassButtons()
		self:UpdateCharacterCreateButton()
	end
end

local RESET_ROTATION_TIME = 0.5
function CharacterCreateMixin:OnUpdate(elapsed)
	if self.rotationStartX then
		local x = GetScaledCursorPosition()
		local diff = (x - self.rotationStartX) * 0.6
		self.rotationStartX = x
		C_CharacterCreation.SetCharacterCreateFacing(C_CharacterCreation.GetCharacterCreateFacing() + diff)
	elseif self.rotationResetStep then
		self.elapsed = self.elapsed + elapsed
		if self.elapsed < self.rotationResetTime then
			C_CharacterCreation.SetCharacterCreateFacing(self.rotationResetCur + self.rotationResetStep * self.elapsed)
		else
			self.elapsed = 0
			self.rotationResetTime = nil
			self.rotationResetCur = nil
			self.rotationResetStep = nil
			C_CharacterCreation.SetCharacterCreateFacing(C_CharacterCreation.GetDefaultCharacterCreateFacing())
		end
	end
end

function CharacterCreateMixin:OnKeyDown(key)
	if key == "ESCAPE" then
		self:SetPreviousCreationState()
		PlaySound(SOUNDKIT.GS_CHARACTER_CREATION_LOOK)
	elseif key == "ENTER" then
		self.NavigationFrame.CreateButton:Click()
	elseif key == "PRINTSCREEN" then
		Screenshot()
	end
end

function CharacterCreateMixin:OnMouseUp(button)
	if button == "LeftButton" then
		self.rotationStartX = nil
		self.rotationResetTime = nil
		self.rotationResetCur = nil
		self.rotationResetStep = nil
	elseif button == "RightButton" and not self.rotationStartX then
		local defaultDeg = C_CharacterCreation.GetDefaultCharacterCreateFacing()
		local deg = C_CharacterCreation.GetCharacterCreateFacing()
		if deg ~= defaultDeg then
			local change = (defaultDeg - deg + 540) % 360 - 180
			self.elapsed = 0
			self.rotationResetTime = math.abs(change / 180 * RESET_ROTATION_TIME)
			self.rotationResetCur = deg
			self.rotationResetStep = change / self.rotationResetTime
		end
	end
end

function CharacterCreateMixin:OnMouseDown(button)
	if button == "LeftButton" then
		self.rotationResetX = nil
		self.rotationResetCur = nil
		self.rotationStartX = GetScaledCursorPosition()
	end
end

function CharacterCreateMixin:CanSetZodiacSignState()
	return C_CharacterCreation.IsZodiacSignsEnabled() and C_CharacterCreation.CanChangeZodiacSign()
end

function CharacterCreateMixin:GetFirstCreationState()
	local canOpenZodiacSignView = self:CanSetZodiacSignState()
	if C_CharacterCreation.PaidChange_IsActive(true) and C_CharacterCreation.PaidChange_CanChangeZodiac() then
		return CREATION_STATES.SIGN_SELECTION
	elseif canOpenZodiacSignView then
		return CREATION_STATES.DEFAULT
	else
		return CREATION_STATES.DEFAULT
	end
end

function CharacterCreateMixin:GetFinalCreationState()
	if self:CanSetZodiacSignState() then
		return CREATION_STATES.SIGN_SELECTION
	else
		return CREATION_STATES.DEFAULT
	end
end

function CharacterCreateMixin:IsInFirstCreationState()
	return CREATION_STATE == self:GetFirstCreationState()
end

function CharacterCreateMixin:IsInFinalCreationState()
	return CREATION_STATE == self:GetFinalCreationState()
end

function CharacterCreateMixin:UpdateCreationState()
	if self:IsInFinalCreationState() then
		if C_CharacterCreation.PaidChange_IsActive(true) then
			self.NavigationFrame.CreateButton:SetText(CHARACTER_CREATE_ACCEPT)
		else
			self.NavigationFrame.CreateButton:SetText(CHARACTER_CREATE)
		end
	else
		self.NavigationFrame.CreateButton:SetText(NEXT)
	end

	if VIEW_STATE == VIEW_STATES.CUSTOMIZATIONS then
		if CREATION_STATE == CREATION_STATES.DEFAULT then
			self.GenderFrame.CustomizationButton:SetText(CHARACTER_CREATE_RACE_LABEL)
		elseif CREATION_STATE == CREATION_STATES.SIGN_SELECTION then
			self.GenderFrame.CustomizationButton:SetText(CHARACTER_CREATE_ZODIAC_SIGN_LABEL)
		end
		self.CustomizationFrame:UpdateCustomizationButtonFrame()
	else
		self.GenderFrame.CustomizationButton:SetText(CHARACTER_CREATE_CUSTOMIZATION_LABEL)
	end

	self:UpdateCharacterCreateButton()
end

function CharacterCreateMixin:SetPreviousCreationState()
	if self:IsInFirstCreationState() and VIEW_STATE ~= VIEW_STATES.CUSTOMIZATIONS then
		self:BackToCharacterSelect()
	else
		if VIEW_STATE == VIEW_STATES.CUSTOMIZATIONS then
			if self.CustomizationFrame:IsShown() and not self.CustomizationFrame:IsAnimPlayingReverse() then
				self.CustomizationFrame:PlayToggleAnim(CREATION_STATE == CREATION_STATES.DEFAULT)
			end

			if CREATION_STATE == CREATION_STATES.DEFAULT then
				VIEW_STATE = VIEW_STATES.RACE_CLASS
				self:PlayDefaultViewAnim()
			elseif CREATION_STATE == CREATION_STATES.SIGN_SELECTION then
				VIEW_STATE = VIEW_STATES.ZODIAC_SIGNS
				self.ZodiacSignFrame:PlayToggleAnim()
			end

			self:UpdateCreationState()
		else
			if CREATION_STATE == CREATION_STATES.SIGN_SELECTION then
				CREATION_STATE = CREATION_STATES.DEFAULT
				VIEW_STATE = VIEW_STATES.RACE_CLASS

				if self.ZodiacSignFrame:IsShown() and not self.ZodiacSignFrame:IsAnimPlayingReverse() then
					self.ZodiacSignFrame:PlayToggleAnim(true)
				end
			end

			self:PlayDefaultViewAnim()
			self:UpdateCreationState()
		end
	end
end

function CharacterCreateMixin:SetNextCreationState()
	if self:IsInFinalCreationState() then
		self:CreateCharacter()
	else
		local wasInCustomizationView = VIEW_STATE == VIEW_STATES.CUSTOMIZATIONS
		CREATION_STATE = CREATION_STATES.SIGN_SELECTION
		VIEW_STATE = VIEW_STATES.ZODIAC_SIGNS

		if self.CustomizationFrame:IsShown() and not self.CustomizationFrame:IsAnimPlayingReverse() then
			self.CustomizationFrame:PlayToggleAnim()
		end

		self:PlayDefaultViewAnim(true)
		self.ZodiacSignFrame:PlayToggleAnim(not wasInCustomizationView)
		self:UpdateCreationState()
	end
end

function CharacterCreateMixin:ToggleCustomications()
	if VIEW_STATE == VIEW_STATES.CUSTOMIZATIONS then
		if CREATION_STATE == CREATION_STATES.DEFAULT then
			VIEW_STATE = VIEW_STATES.RACE_CLASS
			self:PlayDefaultViewAnim()
		elseif CREATION_STATE == CREATION_STATES.SIGN_SELECTION then
			VIEW_STATE = VIEW_STATES.ZODIAC_SIGNS
			self.ZodiacSignFrame:PlayToggleAnim()
		end

		if self.CustomizationFrame:IsShown() and not self.CustomizationFrame:IsAnimPlayingReverse() then
			self.CustomizationFrame:PlayToggleAnim(CREATION_STATE == CREATION_STATES.DEFAULT)
		end
	else
		VIEW_STATE = VIEW_STATES.CUSTOMIZATIONS

		if CREATION_STATE == CREATION_STATES.DEFAULT then
			self:PlayDefaultViewAnim(true)
		elseif CREATION_STATE == CREATION_STATES.SIGN_SELECTION then
			if self.ZodiacSignFrame:IsShown() and not self.ZodiacSignFrame:IsAnimPlayingReverse() then
				self.ZodiacSignFrame:PlayToggleAnim()
			end
		end

		self.CustomizationFrame:PlayToggleAnim(CREATION_STATE == CREATION_STATES.DEFAULT)
	end

	self:UpdateCreationState()
end

function CharacterCreateMixin:BackToCharacterSelect()
	self.BlockingFrame:Show()
	self.Overlay.hideAnim:Play()
	PlaySound("gsCharacterCreationCancel")
	if self:GetFirstCreationState() == CREATION_STATES.DEFAULT then
		self:PlaySelectRaceAndClassAnim(true, function()
			self.BlockingFrame:Hide()
			SetGlueScreen("charselect")
		end)
	else
		self.ZodiacSignFrame:PlayToggleAnim(true, function()
			self.BlockingFrame:Hide()
			SetGlueScreen("charselect")
		end)
	end
end

function CharacterCreateMixin:CreateCharacter()
	local name = self.NavigationFrame.CreateNameEditBox:GetText()
	if name == "" then
		GlueDialog:ShowDialog("OKAY", CHAR_NAME_NO_NAME)
	else
		local class = select(2, C_CharacterCreation.GetSelectedClass())
		local _, _, _, hexColor = GetClassColor(class)
		local skipCustomization = self.skipCustomizationConfirmation or (C_CharacterCreation.PaidChange_IsActive(true) and self:CanSetZodiacSignState())

		local customization = C_CharacterCreation.PaidChange_IsActive(true)
		local buttonText = customization and ACCEPT or nil
		local text = customization and CONFIRM_PAID_SERVICE or CONFIRM_CHARACTER_CREATE
		local confirmation = skipCustomization and "" or CONFIRM_CHARACTER_CREATE_CUSTOMIZATION

		text = string.format(text, hexColor or "ffffff", name or CHARACTER_NO_NAME)
		text = string.format("%s%s", text, confirmation)

		GlueDialog:ShowDialog(skipCustomization and "CONFIRM_CHARACTER_CREATE" or "CONFIRM_CHARACTER_CREATE_CUSTOMIZATION", text, {name, buttonText})
	end
end

local setActiveRaceClassButtonState = function(framePool, state)
	for frame in framePool:EnumerateActive() do
		if state then
			frame:SetEnabled(frame.animDisable)
			frame.animDisable = false
			frame:InFade()
		else
			if frame:IsEnabled() == 1 then
				frame.animDisable = true
			end
			frame:Disable()
			frame:OutFade()
		end
	end
end

function CharacterCreateMixin:PlayDefaultViewAnim(reverse)
	if not reverse then
		if self.AllianceRacesFrame:IsShown() or self.AllianceRacesFrame:IsAnimPlayingNonReverse() then
			return
		end

		self:PlaySelectRaceAndClassAnim(false, function()
			self.AllianceRacesFrame:Show()
			self.HordeRacesFrame:Show()
			self.NeutralRacesFrame:Show()
			self.ClassesFrame:Show()
		end)

		setActiveRaceClassButtonState(self.classButtonPool, true)
		setActiveRaceClassButtonState(self.raceButtonPool, true)

		C_CharacterCreation.ZoomCamera(C_CharacterCreation.GetMaxCameraZoom() * -1, nil, true)
	else
		if not self.AllianceRacesFrame:IsShown() or self.AllianceRacesFrame:IsAnimPlayingReverse() then
			return
		end

		setActiveRaceClassButtonState(self.classButtonPool, false)
		setActiveRaceClassButtonState(self.raceButtonPool, false)

		self:PlaySelectRaceAndClassAnim(true, function()
			self.AllianceRacesFrame:Hide()
			self.HordeRacesFrame:Hide()
			self.NeutralRacesFrame:Hide()
			self.ClassesFrame:Hide()
		end)

		C_CharacterCreation.ZoomCamera(CAMERA_ZOOM_LEVEL_AMOUNT - C_CharacterCreation.GetCurrentCameraZoom(), nil, true)
	end
end

function CharacterCreateMixin:PlaySelectRaceAndClassAnim(isReverce, callback)
	self.AllianceRacesFrame:PlayAnim(isReverce, callback)
	self.HordeRacesFrame:PlayAnim(isReverce)
	self.NeutralRacesFrame:PlayAnim(isReverce)
	self.ClassesFrame:PlayAnim(isReverce)
	self.GenderFrame:PlayAnim(isReverce)
	self.NavigationFrame:PlayAnim(isReverce)
end

function CharacterCreateMixin:ResetSelectRaceAndClassAnim()
	self.AllianceRacesFrame:Reset()
	self.HordeRacesFrame:Reset()
	self.NeutralRacesFrame:Reset()
	self.ClassesFrame:Reset()
	self.GenderFrame:Reset()
	self.NavigationFrame:Reset()
end

function CharacterCreateMixin:UpdateCharacterCreateButton()
	if C_CharacterCreation.PaidChange_IsActive(true) and self:CanSetZodiacSignState() then
		local isValid, disabledReason, disableReasonInfo = C_CharacterCreation.IsSignAvailable(C_CharacterCreation.GetSelectedZodiacSign())
		self.NavigationFrame.CreateButton.disabledReason = disabledReason
		self.NavigationFrame.CreateButton.disableReasonInfo = disableReasonInfo
		self.NavigationFrame.CreateButton:SetEnabled(isValid)
	else
		local _, _, classID = C_CharacterCreation.GetSelectedClass()
		local raceID = C_CharacterCreation.GetSelectedRace()
		local isValid, disabledReason, disableReasonInfo = C_CharacterCreation.IsRaceClassValid(raceID, classID)
		if isValid then
			isValid, disabledReason, disableReasonInfo = C_CharacterCreation.IsRaceAvailable(raceID)
		end
		if isValid and CREATION_STATE == CREATION_STATES.SIGN_SELECTION then
			isValid, disabledReason, disableReasonInfo = C_CharacterCreation.IsSignAvailable(C_CharacterCreation.GetSelectedZodiacSign())
		end

		self.NavigationFrame.CreateButton.disabledReason = disabledReason
		self.NavigationFrame.CreateButton.disableReasonInfo = disableReasonInfo
		self.NavigationFrame.CreateButton:SetEnabled(isValid)
		self.NavigationFrame.CreateNameEditBox:SetShown(isValid)
		self.NavigationFrame.RandomNameButton:SetShown(isValid)
	end
end

function CharacterCreateMixin:UpdateBackground()
	CharacterModelManager.SetBackground(C_CharacterCreation.GetSelectedModelName())
end

function CharacterCreateMixin:CreateUpdateButtons()
	local firstCreationState = self:GetFirstCreationState()
	if firstCreationState == CREATION_STATES.DEFAULT then
		self:BuildRaceData()
		self:CreateRaceButtons()
		self:UpdateRaceButtons()
		self:UpdateFactionTenacity()

		self:BuildClassData()
		self:CreateClassButtons()
		self:UpdateClassButtons()

		self:CreateGenderButtons()
		self:UpdateGenderButtons()

		self.GenderFrame:Show()

		self:PlaySelectRaceAndClassAnim()
	elseif firstCreationState == CREATION_STATES.SIGN_SELECTION then
		self.NavigationFrame.CreateNameEditBox:Hide()
		self.NavigationFrame.RandomNameButton:Hide()
		self.AllianceRacesFrame:Hide()
		self.HordeRacesFrame:Hide()
		self.NeutralRacesFrame:Hide()
		self.GenderFrame:Hide()
		self.ClassesFrame:Hide()

		self.ZodiacSignFrame:PlayToggleAnim(true)
	end

	self.Overlay.showAnim:Play()
end

function CharacterCreateMixin:CreateGenderButtons()
	self.genderButtonPool:ReleaseAll()

	local lastButton
	for _, genderID in ipairs(C_CharacterCreation.GetAvailableGenders()) do
		local button = self.genderButtonPool:Acquire()
		button.index = genderID
		button.Icon:SetAtlas("GLUE-GENDER-"..E_SEX[genderID])
		if genderID == E_SEX.MALE then
			button:SetPoint("LEFT", 0, 0)
		else
			if C_CharacterCreation.CanCreateHardcoreCharacter() then
				button:SetPoint("LEFT", lastButton, "RIGHT", 15, 0)
			else
				button:SetPoint("RIGHT", 0, 0)
			end
		end
		button:Show()
		lastButton = button
	end
end

function CharacterCreateMixin:BuildClassData()
	self.clientClassData = C_CharacterCreation.GetAvailableClasses()
end

function CharacterCreateMixin:CreateClassButtons()
	self.classButtonPool:ReleaseAll()

	local prevButton

	for index, data in ipairs(self.clientClassData) do
		local button = self.classButtonPool:Acquire()
		button:SetID(data.classID)
		button.index = index
		button.Icon:SetAtlas("CLASS_ICON_ROUND_"..data.clientFileString)
		if not prevButton then
			button:SetPoint("LEFT", 47, 0)
		else
			button:SetPoint("LEFT", prevButton, "RIGHT", 15, 0)
		end
		button:Show()

		prevButton = button
	end
end

function CharacterCreateMixin:GetClientRaceInfo(raceIndex)
	return self.clientRaceData[raceIndex]
end

function CharacterCreateMixin:BuildRaceData()
	self.clientRaceData = C_CharacterCreation.GetAvailableRaces()
end

function CharacterCreateMixin:CreateRaceButtons()
	local factionButtons = {
		[PLAYER_FACTION_GROUP.Horde] = {},
		[PLAYER_FACTION_GROUP.Alliance] = {},
		[PLAYER_FACTION_GROUP.Neutral] = {},
	}

	self.raceButtonPool:ReleaseAll()

	for index, data in ipairs(C_CharacterCreation.GetAvailableRacesForCreation()) do
		local button = self.raceButtonPool:Acquire()
		button.data = data

		local isNeutralFaction = data.factionID == PLAYER_FACTION_GROUP.Neutral or not not PAID_SERVICE_ORIGINAL_RACE[data.raceID]
		local factionID = isNeutralFaction and PLAYER_FACTION_GROUP.Neutral or data.factionID

		if factionID == PLAYER_FACTION_GROUP.Alliance then
			button:SetParent(self.AllianceRacesFrame)
		elseif factionID == PLAYER_FACTION_GROUP.Horde then
			button:SetParent(self.HordeRacesFrame)
		elseif factionID == PLAYER_FACTION_GROUP.Neutral then
			button:SetParent(self.NeutralRacesFrame)

			if PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_RACE or PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_FACTION then
				local faction = C_CharacterCreation.PaidChange_GetCurrentFaction()

				if PAID_RACE_SERVICE_DYNAMIC[data.raceID] then
					if PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_FACTION and PAID_SERVICE_ORIGINAL_FACTION[faction] ~= PLAYER_FACTION_GROUP.Neutral then
						data.factionID = PAID_RACE_SERVICE_OVERRIDE_FACTIONS[faction]
					else
						data.factionID = PAID_SERVICE_ORIGINAL_FACTION[faction]
					end
				else
					local overrideRaceID
					local overrideFactionID

					if PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_FACTION then
						overrideRaceID = PAID_FACTION_SERVICE_OVERRIDE_RACES[faction] and PAID_FACTION_SERVICE_OVERRIDE_RACES[faction][data.raceID]
						overrideFactionID = PAID_RACE_SERVICE_OVERRIDE_FACTIONS[faction]
					else
						overrideRaceID = PAID_RACE_SERVICE_OVERRIDE_RACES[faction] and PAID_RACE_SERVICE_OVERRIDE_RACES[faction][data.raceID]
						overrideFactionID = PAID_SERVICE_ORIGINAL_FACTION[faction]
					end

					if overrideRaceID and overrideFactionID then
						data.raceID = overrideRaceID
						data.factionID = overrideFactionID
					end
				end
			else
				local raceID = PAID_SERVICE_ORIGINAL_RACE[data.raceID]
				if raceID then
					data.raceID = raceID
					data.factionID = PLAYER_FACTION_GROUP.Neutral
				end
			end
		end

		table.insert(factionButtons[factionID], button)

		local buttonCount = #factionButtons[factionID]

		if mod(buttonCount - 1, self.raceButtonPerLine) == 0 then
			if buttonCount == 1 then
				if factionID == PLAYER_FACTION_GROUP.Alliance then
					button:SetPoint("TOPLEFT", 40, -40)
				elseif factionID == PLAYER_FACTION_GROUP.Horde then
					button:SetPoint("TOPRIGHT", -40, -40)
				else
					button:SetPoint("LEFT", 0, 0)
				end
			else
				if factionID == PLAYER_FACTION_GROUP.Alliance then
					button:SetPoint("LEFT", factionButtons[factionID][buttonCount - self.raceButtonPerLine], "RIGHT", 26, -30)
				elseif factionID == PLAYER_FACTION_GROUP.Horde then
					button:SetPoint("RIGHT", factionButtons[factionID][buttonCount - self.raceButtonPerLine], "LEFT", -26, -30)
				end
			end
		else
			if factionID == PLAYER_FACTION_GROUP.Neutral then
				button:SetPoint("LEFT", factionButtons[factionID][buttonCount - 1], "RIGHT", 40, 0)
			else
				button:SetPoint("TOP", factionButtons[factionID][buttonCount - 1], "BOTTOM", 0, -30)
			end
		end

		if C_CharacterCreation.IsAlliedRace(data.raceID) then
			button.alliedRace = true
			button.AlliedBorder1:Show()
			button.AlliedBorder1.Anim.Rotation:SetDegrees((index % 2 == 0) and -360 or 360)
			button.AlliedBorder1.Anim:Play()
			button.AlliedBorder2:Show()
			button.AlliedBorder2.Anim:Play()
			button.AlliedBorder2.Pulse:Play()
		else
			button.alliedRace = nil
			button.AlliedBorder1.Anim:Stop()
			button.AlliedBorder1:Hide()
			button.AlliedBorder2.Anim:Stop()
			button.AlliedBorder2.Pulse:Stop()
			button.AlliedBorder2:Hide()
		end

		button.ArtFrame.RaceID:SetText(data.raceID)
		button:Show()
	end

	local buttonOffset = 40
	local buttonsSize = 50
	for factionID, buttons in pairs(factionButtons) do
		local buttonCount = #buttons
		if factionID == PLAYER_FACTION_GROUP.Neutral then
			local width = buttonsSize * buttonCount + buttonOffset * (buttonCount - 1)
			self.NeutralRacesFrame:SetSize(width, buttonsSize)
		end
	end
end

local function updateButtonMacro(frame, onlyDeselected, ignoredButton)
	if onlyDeselected then
		if frame ~= ignoredButton then
			frame:SetChecked(false)
			frame:UpdateChecked()
		end
	else
		frame:UpdateButton()
	end
end

function CharacterCreateMixin:UpdateRaceButtons(onlyDeselected, ignoredButton)
	for frame in self.raceButtonPool:EnumerateActive() do
		updateButtonMacro(frame, onlyDeselected, ignoredButton)
	end
end

function CharacterCreateMixin:UpdateClassButtons(onlyDeselected, ignoredButton)
	for frame in self.classButtonPool:EnumerateActive() do
		updateButtonMacro(frame, onlyDeselected, ignoredButton)
	end
end

function CharacterCreateMixin:UpdateGenderButtons(onlyDeselected, ignoredButton)
	for frame in self.genderButtonPool:EnumerateActive() do
		updateButtonMacro(frame, onlyDeselected, ignoredButton)
	end
end

function CharacterCreateMixin:UpdateFactionTenacity()
	local factionID, timeLeft = C_CharacterList.GetFactionTenacityInfo()
	if factionID then
		self.AllianceRacesFrame.Tenacity:SetShown(factionID == PLAYER_FACTION_GROUP.Alliance)
		self.HordeRacesFrame.Tenacity:SetShown(factionID == PLAYER_FACTION_GROUP.Horde)
	end
end

CharacterCreateRaceButtonMixin = {}

function CharacterCreateRaceButtonMixin:OnLoad()
	self.mainFrame = CharacterCreate

	self.Border:SetAtlas("UI-Frame-jailerstower-Portrait")
	self.FactionBorder:SetAtlas("UI-Frame-jailerstower-Portrait-border")
	self.ArtFrame.CheckedTexture:SetAtlas("charactercreate-ring-select")
	self.ArtFrame.HighlightTexture:SetAtlas("UI-Frame-jailerstower-Portrait-border")
	self.ArtFrame.Border2:SetAtlas("UI-Frame-jailerstower-Portrait")
	self.ArtFrame.Border3:SetAtlas("UI-Frame-jailerstower-Portrait")

	self.AlliedBorder1:SetAtlas("services-ring-large-glowpulse")
	self.AlliedBorder2:SetAtlas("Roulette-item-jackpot-light-center")
end

function CharacterCreateRaceButtonMixin:UpdateChecked()
	self.ArtFrame.CheckedTexture:SetShown(self:GetChecked())
end

function CharacterCreateRaceButtonMixin:OnMouseDown(button)
	if self:IsEnabled() == 1 then
		self.Icon:SetPoint("CENTER", 1, -1)
		self.Border:SetPoint("CENTER", 1, -1)
		self.FactionBorder:SetPoint("CENTER", 1, -1)
		self.ArtFrame:SetPoint("TOPLEFT", 1, -1)
		self.ArtFrame:SetPoint("BOTTOMRIGHT", 1, -1)
	end
end

function CharacterCreateRaceButtonMixin:OnMouseUp(button)
	self.Icon:SetPoint("CENTER", 0, 0)
	self.Border:SetPoint("CENTER", 0, 0)
	self.FactionBorder:SetPoint("CENTER", 0, 0)
	self.ArtFrame:SetPoint("TOPLEFT", 0, 0)
	self.ArtFrame:SetPoint("BOTTOMRIGHT", 0, 0)

	if button == "LeftButton" then
		if self:IsEnabled() == 1 or self.alliedRaceLocked then
			PlaySound("gsCharacterCreationClass")

			local isSet = C_CharacterCreation.SetSelectedRace(self.index)
			if not isSet then return end

			self:SetChecked(true)

			self.mainFrame:UpdateRaceButtons(true, self)
			self:UpdateChecked()

			self.mainFrame:UpdateClassButtons()
			self.mainFrame:UpdateBackground()
			self.mainFrame.CustomizationFrame:UpdateCustomizationButtonFrame(true)
			self.mainFrame.skipCustomizationConfirmation = self.mainFrame.CustomizationFrame:IsShown()

			self.mainFrame:UpdateCharacterCreateButton()
		end
	elseif button == "RightButton" and self:IsMouseOver() and self.tooltip and not C_CharacterCreation.IsZodiacSignsEnabled() then
		TOOLTIPS_EXPANDED = not TOOLTIPS_EXPANDED
		CharCreateRaceButtonTemplate_OnEnter(self)
	end
end

function CharacterCreateRaceButtonMixin:OnEnter()
	if IsInterfaceDevClient() then
		self.ArtFrame.RaceID:Show()
	end

	for i = 2, 3 do
		self.ArtFrame["Border"..i].HideAnim:Stop()
		self.ArtFrame["Border"..i]:Show()

		self.ArtFrame["Border"..i].Anim:Play()
		self.ArtFrame["Border"..i].ShowAnim:Play()
	end

	self.ArtFrame.HighlightTexture:Show()

	if self:IsEnabled() == 1 then
		self.tooltip = true
	elseif PAID_SERVICE_TYPE == E_PAID_SERVICE.CUSTOMIZATION then
		self.tooltip = nil
	elseif C_CharacterCreation.IsAlliedRace(self.index) then
		if PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_FACTION or PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_RACE then
			local currentFaction = C_CharacterCreation.PaidChange_GetCurrentFaction()
			local factionID = S_CHARACTER_RACES_INFO[self.index].factionID

			if PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_FACTION then
				self.tooltip = factionID == PAID_RACE_SERVICE_OVERRIDE_FACTIONS[currentFaction]
			else
				self.tooltip = factionID == PAID_SERVICE_ORIGINAL_FACTION[currentFaction] or C_CharacterCreation.IsNeutralBaseRace(C_CharacterCreation.PaidChange_GetCurrentRaceIndex())
			end
		else
			self.tooltip = true
		end
	end

	if self.tooltip then
		CharCreateRaceButtonTemplate_OnEnter(self)
	end
end

function CharacterCreateRaceButtonMixin:OnLeave()
	self.ArtFrame.RaceID:Hide()

	for i = 2, 3 do
		self.ArtFrame["Border"..i].HideAnim:Play()
		self.ArtFrame["Border"..i].ShowAnim:Stop()
	end

	self.ArtFrame.HighlightTexture:Hide()

	if self.tooltip then
		self.tooltip = nil
		CharCreateRaceButtonTemplate_OnLeave(self)
	end
end

function CharacterCreateRaceButtonMixin:OnDisable()
	self.FactionBorder:SetDesaturated(true)
	self.ArtFrame.HighlightTexture:SetDesaturated(true)
	self.ArtFrame.Border2:SetDesaturated(true)
	self.ArtFrame.Border3:SetDesaturated(true)
	self.Icon:SetDesaturated(true)
	self.alliedRaceDisabled = C_CharacterCreation.IsAlliedRace(self.index)
end

function CharacterCreateRaceButtonMixin:OnEnable()
	self.FactionBorder:SetDesaturated(false)
	self.ArtFrame.HighlightTexture:SetDesaturated(false)
	self.ArtFrame.Border2:SetDesaturated(false)
	self.ArtFrame.Border3:SetDesaturated(false)
	self.Icon:SetDesaturated(false)
	self.alliedRaceDisabled = nil
end

function CharacterCreateRaceButtonMixin:UpdateButton()
	local clientData = self.mainFrame:GetClientRaceInfo(self.data.raceID)
	if C_CharacterCreation.IsPandarenRace(clientData.index) or C_CharacterCreation.IsVulperaRace(clientData.index) then
		if C_CharacterCreation.GetSelectedSex() == E_SEX.FEMALE then
			self.data.name = _G[string.upper(clientData.clientFileString).."_FEMALE"] or _G[string.upper(clientData.clientFileString)]
		else
			self.data.name = _G[string.upper(clientData.clientFileString)]
		end
	else
		self.data.name = clientData.name
	end

	self.data.clientFileString = clientData.clientFileString

	local atlas = string.format("RACE_ICON_ROUND_%s_%s_%s", string.upper(clientData.clientFileString), E_SEX[C_CharacterCreation.GetSelectedSex()], string.upper(PLAYER_FACTION_GROUP[self.data.factionID]))

	if not C_Texture.HasAtlasInfo(atlas) then
		atlas = "RACE_ICON_ROUND_HUMAN_MALE_HORDE"
	end

	self.Icon:SetAtlas(atlas)

	self.index = clientData.index

	local allow = false
	local factionIDOverride
	local alliedRaceLocked

	if C_CharacterCreation.PaidChange_IsActive(true) then
		local faction, _, _, factionID = C_CharacterCreation.PaidChange_GetCurrentFaction()
		local raceID = C_CharacterCreation.PaidChange_GetCurrentRaceIndex()

		if PAID_SERVICE_TYPE == E_PAID_SERVICE.CUSTOMIZATION then
			allow = self.index == raceID
		elseif PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_RACE then
			if C_CharacterCreation.IsNeutralBaseRace(raceID) then
				local overrideFactionID = C_CharacterList.GetCharacterFactionOverride(C_CharacterCreation.PaidChange_GetCharacterID())
				if overrideFactionID == PLAYER_FACTION_GROUP.Renegade then
					factionIDOverride = overrideFactionID
					allow = true
				else
					allow = C_CharacterCreation.IsNeutralBaseRace(self.index) or faction == C_CharacterCreation.GetFactionForRace(self.index)
				end
			else
				allow = (PAID_RACE_SERVICE_DYNAMIC[self.index] or faction == C_CharacterCreation.GetFactionForRace(self.index) or self.index == C_CharacterCreation.PaidChange_GetCurrentRaceIndex())
			end
		elseif PAID_SERVICE_TYPE == E_PAID_SERVICE.CHANGE_FACTION then
			allow = C_CharacterCreation.IsNeutralBaseRace(self.index) or (PAID_RACE_SERVICE_DYNAMIC[self.index] or faction ~= C_CharacterCreation.GetFactionForRace(self.index) or self.index == C_CharacterCreation.PaidChange_GetCurrentRaceIndex())
		end
	else
		allow = true
	end

	if allow then
		if PAID_SERVICE_TYPE and not C_CharacterCreation.IsServicesAvailableForRace(PAID_SERVICE_TYPE, self.index) then
			allow = false
		elseif C_CharacterCreation.IsAlliedRace(self.index) and not C_CharacterCreation.IsAlliedRacesUnlocked(self.index) then
			allow = false
			alliedRaceLocked = true
		end
	end

	local factionColor = PLAYER_FACTION_COLORS[factionIDOverride or self.data.factionID]

	self.Border:SetVertexColor(factionColor.r, factionColor.g, factionColor.b)
	self.FactionBorder:SetVertexColor(factionColor.r, factionColor.g, factionColor.b)
	self.ArtFrame.Border2:SetVertexColor(factionColor.r, factionColor.g, factionColor.b)
	self.ArtFrame.Border3:SetVertexColor(factionColor.r, factionColor.g, factionColor.b)

	self.alliedRaceGMAllowed = not C_CharacterCreation.IsAlliedRacesUnlocked(self.index, true)
	self.alliedRaceLocked = alliedRaceLocked
	self:SetEnabled(allow)

	self:SetChecked(C_CharacterCreation.GetSelectedRace() == self.index)
	self:UpdateChecked()
end

CharacterCreateClassButtonMixin = {}

function CharacterCreateClassButtonMixin:OnLoad()
	self.mainFrame = CharacterCreate

	self.Border:SetAtlas("charactercreate-ring-metaldark")
	self.HighlightTexture:SetAtlas("charactercreate-ring-metallight")
	self.CheckedTexture:SetAtlas("charactercreate-ring-select")
end

function CharacterCreateClassButtonMixin:OnEnter()
	self.HighlightTexture:Show()

	self.tooltip = self:IsEnabled() == 1 or self.disabledReason
	if self.tooltip then
		CharCreateClassButtonTemplate_OnEnter(self)
	end
end

function CharacterCreateClassButtonMixin:OnLeave()
	self.HighlightTexture:Hide()

	if self.tooltip then
		self.tooltip = nil
		CharCreateClassButtonTemplate_OnLeave(self)
	end
end

function CharacterCreateClassButtonMixin:UpdateChecked()
	self.CheckedTexture:SetShown(self:GetChecked())
end

function CharacterCreateClassButtonMixin:OnDisable()
	self.Icon:SetDesaturated(true)
	self.Border:SetDesaturated(true)
	self.HighlightTexture:SetDesaturated(true)
	self.CheckedTexture:SetDesaturated(true)
end

function CharacterCreateClassButtonMixin:OnEnable()
	self.Icon:SetDesaturated(false)
	self.Border:SetDesaturated(false)
	self.HighlightTexture:SetDesaturated(false)
	self.CheckedTexture:SetDesaturated(false)
end

function CharacterCreateClassButtonMixin:OnMouseDown(button)
	if self:IsEnabled() == 1 then
		self.Icon:SetPoint("CENTER", 1, -1)
		self.Border:SetPoint("CENTER", 1, -1)
		self.HighlightTexture:SetPoint("CENTER", 1, -1)
		self.CheckedTexture:SetPoint("CENTER", 1, -1)
	end
end

function CharacterCreateClassButtonMixin:OnMouseUp(button)
	self.Icon:SetPoint("CENTER", 0, 0)
	self.Border:SetPoint("CENTER", 0, 0)
	self.HighlightTexture:SetPoint("CENTER", 0, 0)
	self.CheckedTexture:SetPoint("CENTER", 0, 0)

	if button == "LeftButton" then
		if self:IsEnabled() == 1 or self.disabledReason then
			PlaySound("gsCharacterCreationClass")

			local isSet = C_CharacterCreation.SetSelectedClass(self:GetID())
			if not isSet then return end

			self:SetChecked(true)

			self.mainFrame:UpdateClassButtons(true, self)
			self:UpdateChecked()

			self.mainFrame:UpdateBackground()
			self.mainFrame.CustomizationFrame:UpdateCustomizationButtonFrame(true)
			self.mainFrame.skipCustomizationConfirmation = self.mainFrame.CustomizationFrame:IsShown()

			self.mainFrame:UpdateCharacterCreateButton()
		end
	elseif button == "RightButton" and self:IsMouseOver() and self.tooltip then
		TOOLTIPS_EXPANDED = not TOOLTIPS_EXPANDED
		CharCreateClassButtonTemplate_OnEnter(self)
	end
end

function CharacterCreateClassButtonMixin:UpdateButton()
	local _, _, classID = C_CharacterCreation.GetSelectedClass()

	local clientClassData = self.index and self.mainFrame.clientClassData[self.index]
	if clientClassData then
		self.name = clientClassData.name
		self.clientFileString = clientClassData.clientFileString
	end

	if C_CharacterCreation.PaidChange_IsActive(true) then
		self:SetEnabled(self:GetID() == classID)
		self.disabledReason = nil
		self.disableReasonInfo = nil
	else
		local isValid, disabledReason, disableReasonInfo = C_CharacterCreation.IsRaceClassValid(C_CharacterCreation.GetSelectedRace(), self:GetID())
		self:SetEnabled(isValid)
		self.disabledReason = disabledReason
		self.disableReasonInfo = disableReasonInfo
	end

	self:SetChecked(self:GetID() == classID)
	self:UpdateChecked()
end

CharacterCreateGenderButtonMixin = {}

function CharacterCreateGenderButtonMixin:OnLoad()
	self.mainFrame = CharacterCreate

	self.Border:SetAtlas("charactercreate-ring-metaldark")
	self.HighlightTexture:SetAtlas("charactercreate-ring-metallight")
	self.CheckedTexture:SetAtlas("charactercreate-ring-select")
end

function CharacterCreateGenderButtonMixin:OnMouseDown(button)
	if self:IsEnabled() == 1 then
		self.Icon:SetPoint("CENTER", 1, -1)
		self.Border:SetPoint("CENTER", 1, -1)
		self.HighlightTexture:SetPoint("CENTER", 1, -1)
		self.CheckedTexture:SetPoint("CENTER", 1, -1)
	end
end

function CharacterCreateGenderButtonMixin:OnMouseUp(button)
	self.Icon:SetPoint("CENTER", 0, 0)
	self.Border:SetPoint("CENTER", 0, 0)
	self.HighlightTexture:SetPoint("CENTER", 0, 0)
	self.CheckedTexture:SetPoint("CENTER", 0, 0)

	if button == "LeftButton" then
		PlaySound("gsCharacterCreationClass")

		local isSet = C_CharacterCreation.SetSelectedSex(self.index)
		if not isSet then return end

		self:SetChecked(true)

		self.mainFrame:UpdateGenderButtons(true, self)
		self:UpdateChecked()

		self.mainFrame:BuildRaceData()
		self.mainFrame:UpdateRaceButtons()
		self.mainFrame:BuildClassData()
		self.mainFrame:UpdateClassButtons()

		self.mainFrame.CustomizationFrame:UpdateCustomizationButtonFrame(true)
		self.mainFrame.skipCustomizationConfirmation = self.mainFrame.CustomizationFrame:IsShown()

		C_CharacterCreation.ZoomCamera(0, nil, true)
	end
end

function CharacterCreateGenderButtonMixin:OnEnter()
	self.HighlightTexture:Show()

	GlueTooltip:SetOwner(self, "ANCHOR_TOP")
	GlueTooltip:SetText(_G[E_SEX[self.index]], 1, 1, 1)
	GlueTooltip:Show()
end

function CharacterCreateGenderButtonMixin:OnLeave()
	self.HighlightTexture:Hide()

	GlueTooltip:Hide()
end

function CharacterCreateGenderButtonMixin:UpdateChecked()
	self.CheckedTexture:SetShown(self:GetChecked())
end

function CharacterCreateGenderButtonMixin:UpdateButton()
	self:SetChecked(C_CharacterCreation.GetSelectedSex() == self.index)
	self:UpdateChecked()
end

CharacterCreateFactionTenacityMixin = {}

function CharacterCreateFactionTenacityMixin:OnLoad()
	self.Icon:SetAtlas("PKBT-Icon-Arrow", true)
	self.UpdateTooltip = self.OnEnter
end

function CharacterCreateFactionTenacityMixin:OnShow()
	self.Icon.Anim:Restart()
end

function CharacterCreateFactionTenacityMixin:OnHide()
	self.Icon.Anim:Stop()
end

function CharacterCreateFactionTenacityMixin:OnEnter()
	local parent = self:GetParent()

	local factionID, timeLeft = C_CharacterList.GetFactionTenacityInfo()
	if factionID and factionID == parent:GetID() then
		if parent.tooltipAnchor == "ANCHOR_RIGHT" then
			GlueTooltip:SetOwner(self, "ANCHOR_RIGHT", 40, 0)
		elseif parent.tooltipAnchor == "ANCHOR_LEFT" then
			GlueTooltip:SetOwner(self, "ANCHOR_LEFT", -40, 0)
		else
			GlueTooltip:SetOwner(self, "ANCHOR_TOP")
		end
		GlueTooltip:AddLine(TENACITY_FACTION_BONUS_TITLE)
		GlueTooltip:AddLine(" ")
		GlueTooltip:AddLine(TENACITY_FACTION_BONUS_DESCRIPTION, 1, 1, 1, 1, true)
		GlueTooltip:AddLine(" ")
		GlueTooltip:AddLine(string.format(TENACITY_FACTION_TIMELEFT, GetRemainingTime(timeLeft)), 0, 1, 0, 1, true)
		GlueTooltip:Show()
	end
end

function CharacterCreateFactionTenacityMixin:OnLeave()
	if GlueTooltip:IsOwned(self) then
		GlueTooltip:Hide()
	end
end

CharacterCreateAllianceRacesFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateAllianceRacesFrameMixin:OnLoad()
	self.Logo:SetAtlas("charactercreate-icon-alliance")
	self:SetID(PLAYER_FACTION_GROUP.Alliance)

	self.tooltipAnchor = "ANCHOR_RIGHT"
	self.startPoint = -400
	self.endPoint = 10
	self.duration = 0.500
end

function CharacterCreateAllianceRacesFrameMixin:SetPosition(easing)
	if easing then
		self:ClearAndSetPoint("TOPLEFT", easing, -70)
	else
		self:ClearAndSetPoint("TOPLEFT", self.isRevers and self.startPoint or self.endPoint, -70)
	end
end

CharacterCreateHordeRacesFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateHordeRacesFrameMixin:OnLoad()
	self.Logo:SetAtlas("charactercreate-icon-horde")
	self:SetID(PLAYER_FACTION_GROUP.Horde)

	self.tooltipAnchor = "ANCHOR_LEFT"
	self.startPoint = 400
	self.endPoint = -10
	self.duration = 0.500
end

function CharacterCreateHordeRacesFrameMixin:SetPosition(easing)
	if easing then
		self:ClearAndSetPoint("TOPRIGHT", easing, -70)
	else
		self:ClearAndSetPoint("TOPRIGHT", self.isRevers and self.startPoint or self.endPoint, -70)
	end
end

CharacterCreateNeutralRacesFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateNeutralRacesFrameMixin:OnLoad()
	self:SetID(PLAYER_FACTION_GROUP.Neutral)

	self.startPoint = 100
	self.endPoint = -30
	self.duration = 0.500
end

function CharacterCreateNeutralRacesFrameMixin:SetPosition(easing)
	if easing then
		self:ClearAndSetPoint("TOP", 0, easing)
	else
		self:ClearAndSetPoint("TOP", 0, self.isRevers and self.startPoint or self.endPoint)
	end
end

CharacterCreateClassesFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateClassesFrameMixin:OnLoad()
	self.startPoint = -80
	self.endPoint = 10
	self.duration = 0.500
end

function CharacterCreateClassesFrameMixin:SetPosition(easing)
	if easing then
		self:ClearAndSetPoint("BOTTOM", 0, easing)
	else
		self:ClearAndSetPoint("BOTTOM", 0, 10)
	end
end

CharacterCreateGenderFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateGenderFrameMixin:OnLoad()
	self.startPoint = 20
	self.endPoint = 70
	self.duration = 0.500
end

function CharacterCreateGenderFrameMixin:SetPosition(easing)
	if easing then
		self:ClearAndSetPoint("BOTTOM", 0, easing)
	else
		self:ClearAndSetPoint("BOTTOM", 0, self.isRevers and self.startPoint or self.endPoint)
	end
end

CharacterCreateInteractiveButtonAlphaAnimMixin = {}

function CharacterCreateInteractiveButtonAlphaAnimMixin:InitAlpha()
	self.initMinAlpha 	= 0.4
	self.initMaxAlpha 	= 1

	self.elapsed 		= 0
	self.animationTime 	= 0.4

	self.startAlpha 	= nil
	self.endAlpha 		= nil
end

function CharacterCreateInteractiveButtonAlphaAnimMixin:InFade()
	self.startAlpha 	= self.initMinAlpha
	self.endAlpha 		= self.initMaxAlpha
end

function CharacterCreateInteractiveButtonAlphaAnimMixin:OutFade()
	self.startAlpha 	= self.initMaxAlpha
	self.endAlpha 		= self.initMinAlpha
end

function CharacterCreateInteractiveButtonAlphaAnimMixin:UpdateAlpha(elapsed)
	if not self.startAlpha or not self.endAlpha then
		return
	end

	self.elapsed = self.elapsed + elapsed

	local easing = EasingUtil.OutCirc2(self.elapsed, self.startAlpha, self.endAlpha, self.animationTime)

	self:SetAlpha(easing)

	if self.elapsed > self.animationTime then
		self:SetAlpha(self.endAlpha)

		self.elapsed 		= 0
		self.animationState = nil

		self.startAlpha 	= nil
		self.endAlpha 		= nil
	end
end

CharacterCreateCreateButtonMixin = {}

function CharacterCreateCreateButtonMixin:OnEnter()
	GlueDark_ButtonMixin.OnEnter(self)

	if self:IsEnabled() ~= 1 and self.disabledReason then
		GlueTooltip:SetOwner(self, "ANCHOR_TOP", 0, 10)
		GlueTooltip:SetMaxWidth(350)
		GlueTooltip:AddLine(self.disabledReason, 1, 0, 0)
		if self.disableReasonInfo then
			GlueTooltip:AddLine(self.disableReasonInfo, 1, 0.82, 0)
		end
		GlueTooltip:Show()
	end
end

function CharacterCreateCreateButtonMixin:OnLeave()
	GlueDark_ButtonMixin.OnLeave(self)
	GlueTooltip:Hide()
end

function CharacterCreateCreateButtonMixin:OnClick(button)
	self:GetParent():GetParent():SetNextCreationState()
	PlaySound("igMainMenuOptionCheckBoxOn")
end

CharacterCreateDressStateCheckButtonMixin = {}

function CharacterCreateDressStateCheckButtonMixin:OnClick(button)
	if button ~= "LeftButton" then return end
	C_CharacterCreation.SetDressState(self:GetChecked())
	PlaySound("igMainMenuOptionCheckBoxOn")
end

CharacterCreateHardcoreCheckButtonMixin = {}

function CharacterCreateHardcoreCheckButtonMixin:OnLoad()
	self:SetNormalAtlas("Custom-Challenges-Button-Round-Hardcore-Up", true)
	self:SetDisabledAtlas("Custom-Challenges-Button-Round-Hardcore-Up", true)
	self:GetDisabledTexture():SetDesaturated(true)
	self:SetPushedAtlas("Custom-Challenges-Button-Round-Hardcore-Down", true)
	self:SetHighlightAtlas("Custom-Challenges-Button-Round-Border", true)
	self:SetCheckedAtlas("Custom-Challenges-Button-Round-Border", true)

	self.AnimFrame.Spinner1:SetAtlas("Custom-Challenges-LoadingSpinner", true)
	self.AnimFrame.Spinner1:SetSubTexCoord(1, 0, 0, 1)
	self.AnimFrame.Spinner2:SetAtlas("Custom-Challenges-LoadingSpinner", true)
	self.AnimFrame.Spinner1.AnimRotation:Play()
	self.AnimFrame.Spinner2.AnimRotation:Play()
end

function CharacterCreateHardcoreCheckButtonMixin:OnShow()
	self.AnimFrame:SetShown(C_CharacterCreation.GetHardcoreFlag())
end

function CharacterCreateHardcoreCheckButtonMixin:OnEnter()
	GlueTooltip:SetOwner(self, "ANCHOR_LEFT")
	GlueTooltip:SetMaxWidth(350)
	GlueTooltip:AddLine(CHARACTER_CREATE_HARDCORE_LABEL, 1, 1, 1)
	GlueTooltip:AddLine(CHARACTER_CREATE_HARDCORE_TIP, 1, 0.82, 0)
	GlueTooltip:Show()
end

function CharacterCreateHardcoreCheckButtonMixin:OnLeave()
	GlueTooltip:Hide()
end

function CharacterCreateHardcoreCheckButtonMixin:OnClick(button)
	if button ~= "LeftButton" then return end

	local enabled = not C_CharacterCreation.GetHardcoreFlag()
	C_CharacterCreation.SetHardcoreFlag(enabled)

	if enabled then
		self.AnimFrame:Show()
		self.AnimFrame.AnimFadeOut:Stop()
		self.AnimFrame.AnimFadeIn:Play()
	else
		self.AnimFrame.AnimFadeIn:Stop()
		self.AnimFrame.AnimFadeOut:Play()
	end

	PlaySound("igMainMenuOptionCheckBoxOn")
end

CharacterCreateCustomizationButtonMixin = {}

function CharacterCreateCustomizationButtonMixin:OnLoad()
	self.parentFrame = self:GetParent():GetParent()
end

function CharacterCreateCustomizationButtonMixin:OnClick()
	self.parentFrame:ToggleCustomications()
	PlaySound(SOUNDKIT.GS_CHARACTER_CREATION_LOOK)
end

CharacterCreateCustomizationFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateCustomizationFrameMixin:OnLoad()
	self.parentFrame = self:GetParent()
	self.customizationButtonFramePool = CreateFramePool("Frame", self, "CharacterCreateCustomizationButtonFrameTemplate")

	self.sourceXOffset = 200
	self.startPoint = -200
	self.endPoint = self.sourceXOffset
	self.duration = 0.500
end

function CharacterCreateCustomizationFrameMixin:SetPosition(easing, progress)
	if easing then
		if self.animVignetteAlpha then
			self.parentFrame.CustomizationVignette:SetAlpha(self.isRevers and ((1 - progress) * 0.75) or (progress * 0.75))
		end
		self:SetAlpha(self.isRevers and (1 - progress) or progress)
		self:SetPoint("LEFT", easing, 200)
	else
		if self.animVignetteAlpha then
			self.parentFrame.CustomizationVignette:SetAlpha(self.isRevers and 0 or 0.75)
		end
		self:SetAlpha(self.isRevers and 0 or 1)
		self:SetPoint("LEFT", self.isRevers and self.startPoint or self.sourceXOffset, 200)
	end
end

function CharacterCreateCustomizationFrameMixin:UpdateCustomizationButtonFrame(selectedChanged)
	if selectedChanged and not self:IsShown() == 1 then return end

	self.customizationButtonFramePool:ReleaseAll()

	local prevFrame

	for _, style in ipairs(C_CharacterCreation.GetAvailableCustomizations()) do
		local frame = self.customizationButtonFramePool:Acquire()

		if not prevFrame then
			frame:SetPoint("LEFT", 0, 200)
		else
			frame:SetPoint("TOP", prevFrame, "BOTTOM", 0, -20)
		end

		prevFrame = frame

		frame.CustomizationIndex = style.orderIndex
		frame.CustomizationName:SetText(style.name)
		frame:Show()
	end

	self.RandomizeCustomizationButton:ClearAndSetPoint("TOP", prevFrame, "BOTTOM", 0, -40)
end

function CharacterCreateCustomizationFrameMixin:PlayToggleAnim(animVignetteAlpha, callback)
	self.show = not self.show

	if self.show then
		self:Show()
		self.sourceXOffset = not IsWideScreen() and 100 or 200
		self.endPoint = self.sourceXOffset

		self.animVignetteAlpha = animVignetteAlpha
		self:PlayAnim(false, callback)
	else
		self.animVignetteAlpha = animVignetteAlpha
		self:PlayAnim(true, function()
			if type(callback) == "function" then
				callback()
			else
				self:Hide()
			end
		end)
	end
end

function CharacterCreateCustomizationFrameMixin:OnShow()
	self.parentFrame.skipCustomizationConfirmation = true
	self:UpdateZoomButtonStates()
end

function CharacterCreateCustomizationFrameMixin:OnHide()
	self:Reset()

	if self.show then
		self.show = false
		self:SetPoint("LEFT", self.startPoint, 200)
		self:SetAlpha(0)
		self.parentFrame.CustomizationVignette:SetAlpha(0)
	end
end

function CharacterCreateCustomizationFrameMixin:UpdateZoomButtonStates()
	local currentZoom = C_CharacterCreation.GetCurrentCameraZoom();

	local zoomOutEnabled = (currentZoom > 0);
	self.SmallButtons.ZoomOutButton:SetEnabled(zoomOutEnabled);
	self.SmallButtons.ZoomOutButton.Icon:SetAtlas(zoomOutEnabled and "common-icon-zoomout" or "common-icon-zoomout-disable");

	local zoomInEnabled = (currentZoom < C_CharacterCreation.GetMaxCameraZoom());
	self.SmallButtons.ZoomInButton:SetEnabled(zoomInEnabled);
	self.SmallButtons.ZoomInButton.Icon:SetAtlas(zoomInEnabled and "common-icon-zoomin" or "common-icon-zoomin-disable");
end

CharacterCreateZodiacSignFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateZodiacSignFrameMixin:OnLoad()
	self.parentFrame = self:GetParent()

	self.sourceXOffset = 0
	self.startPoint = 450
	self.endPoint = self.sourceXOffset
	self.duration = 0.500

	self.Description.Text:SetWidth(self:GetWidth() - 60)
	self.SignLock.Lock:SetAtlas("BonusChest-Lock", true)

	self.signButtonPool = CreateFramePool("Button", self.Sign, "CharacterCreateZodiacSignButtonTemplate")
	self.spellButtonPool = CreateFramePool("Frame", self.SpellHolder, "CharacterCreateZodiacSignSpellTemplate")

	self:RegisterCustomEvent("GLUE_CHARACTER_CREATE_ZODIAC_SELECTED")
end

function CharacterCreateZodiacSignFrameMixin:OnEvent(event, ...)
	if event == "GLUE_CHARACTER_CREATE_ZODIAC_SELECTED" then
		if self:IsVisible() then
			self.Sign.ArtworkGlow.Pulse:Restart()
		end
		self:UpdateSignView()
	end
end

function CharacterCreateZodiacSignFrameMixin:OnShow()
	SetParentFrameLevel(self.Sign, 1)
	SetParentFrameLevel(self.SignLock, 2)
	self:UpdateSignView()
end

function CharacterCreateZodiacSignFrameMixin:OnHide()
	self:Reset()

	if self.show then
		self.show = false
		self:SetPoint("RIGHT", self.startPoint, 0)
		self:SetAlpha(0)
		self.parentFrame.CustomizationVignette:SetAlpha(0)
	end
end

local PI180 = math.pi / 180

function CharacterCreateZodiacSignFrameMixin:UpdateCircle()
	local rotation = 90
	local arcLength = 360
	local radius = 190

	local theta = (rotation or 0) * PI180
	local arc = (arcLength or 0) * PI180
	local dAngle

	local numSigns = C_CharacterCreation.GetNumZodiacSigns()

	if numSigns <= 1 then
		dAngle = 0
	else
		dAngle = arc / -numSigns
	end

	self.signButtonPool:ReleaseAll()

	for index = 1, numSigns do
		local sign = self.signButtonPool:Acquire()
		sign:SetID(index)
		sign.dAngle = dAngle * (index - 1)
		sign:SetPoint("CENTER", radius * math.cos(theta), radius * math.sin(theta))
		sign:Show()
		theta = theta + dAngle
	end
end

local sqrt2 = math.sqrt(2)
local calculateCorner = function(angle)
	local r = math.rad(angle)
	return 0.5 + math.cos(r) / sqrt2, 0.5 + math.sin(r) / sqrt2
end
local getRotatedTexCoord = function(angle)
	local ULx, ULy = calculateCorner(angle + 225)
	local LLx, LLy = calculateCorner(angle + 135)
	local URx, URy = calculateCorner(angle - 45)
	local LRx, LRy = calculateCorner(angle + 45)
	return ULx, ULy, LLx, LLy, URx, URy, LRx, LRy
end

local ALLIED_SIGN_COLOR = {0.929, 0.766, 0.512}
local ALLIED_SIGN_GLOW_COLOR = {0.929, 0.586, 0.812}

function CharacterCreateZodiacSignFrameMixin:UpdateSignView()
	local selectedSignIndex = C_CharacterCreation.GetSelectedZodiacSign()
	local numSigns = C_CharacterCreation.GetNumZodiacSigns()
	if self.signButtonPool:GetNumActive() ~= numSigns then
		self:UpdateCircle()
	end

	for sign in self.signButtonPool:EnumerateActive() do
		local signIndex = sign:GetID()
		local zodiacRaceID, name, description, icon, atlas, available = C_CharacterCreation.GetZodiacSignInfo(signIndex)

		sign.Artwork:SetAtlas(atlas.."-Medium", true)
		sign.ArtworkGlow:SetAtlas(atlas.."-Medium-Glow", true)

		if signIndex == selectedSignIndex then
			self.Sign.CircleSelection:SetTexCoord(getRotatedTexCoord(math.deg(sign.dAngle)))
		end

		if C_CharacterCreation.IsAlliedRace(zodiacRaceID) then
			sign.Artwork:SetVertexColor(unpack(ALLIED_SIGN_COLOR, 1, 3))
			sign.ArtworkGlow:SetVertexColor(unpack(ALLIED_SIGN_GLOW_COLOR, 1, 3))
		else
			sign.Artwork:SetVertexColor(1, 1, 1)
			sign.ArtworkGlow:SetVertexColor(1, 1, 1)
		end

		sign.Lock:SetShown(not available)
	end

	local zodiacRaceID, name, description, icon, atlas, available = C_CharacterCreation.GetZodiacSignInfo(selectedSignIndex)
	local activeSpellList, passiveSpellList = C_ZodiacSign.GetZodiacSignSpells(zodiacRaceID)

	self.SignLock:SetShown(not available)
	self.Sign.Artwork:SetAtlas(atlas, true)
	self.Sign.ArtworkGlow:SetAtlas(atlas.."-Glow", true)

	if C_CharacterCreation.IsAlliedRace(zodiacRaceID) then
		self.Sign.Artwork:SetVertexColor(unpack(ALLIED_SIGN_COLOR, 1, 3))
		self.Sign.ArtworkGlow:SetVertexColor(unpack(ALLIED_SIGN_GLOW_COLOR, 1, 3))
	else
		self.Sign.Artwork:SetVertexColor(1, 1, 1)
		self.Sign.ArtworkGlow:SetVertexColor(1, 1, 1)
	end

	self.SelectorFrame.Text:SetText(name)
	self.Description.Text:SetText(description)

	self.spellButtonPool:ReleaseAll()

	local firstButtonOffsetX = 10 + math.max(self.SpellHolder.ActiveSpells.Label:GetStringWidth(), self.SpellHolder.PassiveSpells.Label:GetStringWidth())
	self:CreateSpellButtons(self.SpellHolder.ActiveSpells, activeSpellList, firstButtonOffsetX)
	self:CreateSpellButtons(self.SpellHolder.PassiveSpells, passiveSpellList, firstButtonOffsetX)

	if self.SpellHolder.ActiveSpells:GetWidth() < self.SpellHolder.PassiveSpells:GetWidth() then
		self.SpellHolder.ActiveSpells:SetWidth(self.SpellHolder.PassiveSpells:GetWidth())
	end
end

function CharacterCreateZodiacSignFrameMixin:CreateSpellButtons(parent, spellList, firstButtonOffsetX, offsetX)
	if not offsetX then
		offsetX = 10
	end
	local buttonSize = 0

	local lastSpell
	for index, spellInfo in ipairs(spellList) do
		local spell = self.spellButtonPool:Acquire()
		spell:SetID(index)
		spell:SetParent(parent)

		if not lastSpell then
			spell:SetPoint("LEFT", firstButtonOffsetX or 0, 0)
		else
			spell:SetPoint("LEFT", lastSpell, "RIGHT", offsetX, 0)
		end

		spell.Icon:SetTexture(spellInfo.icon)
		spell.id = spellInfo.id
		spell.iconName = spellInfo.iconName
		spell.name = spellInfo.name
		spell.description = spellInfo.description
		spell:Show()

		lastSpell = spell
		if buttonSize == 0 then
			buttonSize = spell:GetWidth()
		end
	end

	parent:SetSize(firstButtonOffsetX + buttonSize * #spellList + offsetX * (#spellList - 1), buttonSize)
end

function CharacterCreateZodiacSignFrameMixin:SelectSignIndex(index)
	C_CharacterCreation.SetSelectedZodiacSign(index)
end

function CharacterCreateZodiacSignFrameMixin:NextSign()
	local signIndex = C_CharacterCreation.GetSelectedZodiacSign()
	if signIndex >= C_CharacterCreation.GetNumZodiacSigns() then
		self:SelectSignIndex(1)
	else
		self:SelectSignIndex(signIndex + 1)
	end

end

function CharacterCreateZodiacSignFrameMixin:PreviousSign()
	local signIndex = C_CharacterCreation.GetSelectedZodiacSign()
	if signIndex <= 1 then
		self:SelectSignIndex(C_CharacterCreation.GetNumZodiacSigns())
	else
		self:SelectSignIndex(signIndex - 1)
	end
end

function CharacterCreateZodiacSignFrameMixin:SetPosition(easing, progress)
	if easing then
		if self.animVignetteAlpha then
			self.parentFrame.CustomizationVignette:SetAlpha(self.isRevers and ((1 - progress) * 0.75) or (progress * 0.75))
		end
		self.parentFrame.VignetteRight:SetAlpha(self.isRevers and ((1 - progress) * 0.75) or (progress * 0.75))
		self:SetAlpha(self.isRevers and (1 - progress) or progress)
		self:SetPoint("RIGHT", easing, 200)
	else
		if self.animVignetteAlpha then
			self.parentFrame.CustomizationVignette:SetAlpha(self.isRevers and 0 or 0.75)
		end
		self.parentFrame.VignetteRight:SetAlpha(self.isRevers and 0 or 0.75)
		self:SetAlpha(self.isRevers and 0 or 1)
		self:SetPoint("RIGHT", self.isRevers and self.startPoint or self.sourceXOffset, 200)
	end
end

function CharacterCreateZodiacSignFrameMixin:PlayToggleAnim(animVignetteAlpha, callback)
	self.show = not self.show

	if self.show then
		self:Show()
		self.sourceXOffset = 0
		self.endPoint = self.sourceXOffset

		self.animVignetteAlpha = animVignetteAlpha
		self:PlayAnim(false, callback)
	else
		self.animVignetteAlpha = animVignetteAlpha
		self:PlayAnim(true, function()
			if type(callback) == "function" then
				callback()
			else
				self:Hide()
			end
		end)
	end
end

CharacterCreateZodiacSignEffectMixin = {}

function CharacterCreateZodiacSignEffectMixin:OnLoad()
	self:SetScale(1)
	self.StarsB:SetAlpha(0.8)
	self.StarsB:SetVertexColor(0.7, 0.7, 0.1)
	self.Galaxy:SetAlpha(0.0)

--	self.Shadow:SetAtlas("CovenantSanctum-Reservoir-Shadow", true)
--	self.Shadow:SetSize(516, 504)

	self.drag = 90
	self.rDrag = 120
	self.angle = 25

	self.stars = {}

	local panel = self:GetParent()
	for i = 1, 20 do
		local star = self:CreateTexture(("$parentStart%u"):format(i), "ARTWORK", "CharacterCreateZodiacStarsATemplate")
		star.baseAlpha = 1 - 0.08 * (i - 1)
		star.angle = math.rad(math.random(150, 170))
		star.dragE = 0
		star.drag = self.drag * (i + 1) / 2
		star.rDragE = 0
		star.rDrag = self.rDrag
		star.flashNext = math.random(500, 2500) / 1000
		star.flashT = 0
		star.flashTleft = 0

		star:SetAlpha(star.baseAlpha)
		star:SetPoint("TOPRIGHT", panel, 0, 0)
		star:SetPoint("BOTTOMRIGHT", panel, 0, 0)

		local starMode = self:CreateTexture(("$parentStartMode%u"):format(i), "ARTWORK", "CharacterCreateZodiacStarsATemplate")
		starMode:SetBlendMode("ADD")
		star.starMode = starMode

		self.stars[i] = star
	end
end

function CharacterCreateZodiacSignEffectMixin:SetSignTexCoord(star, radians, l, r, t, b)
	local cX, cY = (l + r) / 2, (t + b) / 2
	local z = math.sqrt((r - cX) ^ 2 + (b - cY) ^ 2)
	local zCos, zSin = z * math.cos(radians), z * math.sin(radians)
	star:SetTexCoord(cX - zSin, cY - zCos, cX - zCos, cY + zSin, cX + zCos, cY - zSin, cX + zSin, cY + zCos)
	star.starMode:SetTexCoord(star:GetTexCoord())
end

function CharacterCreateZodiacSignEffectMixin:OnShow()
	SetParentFrameLevel(self)
end

function CharacterCreateZodiacSignEffectMixin:OnUpdate(elapsed)
	for index, star in ipairs(self.stars) do
		star.dragE = (star.dragE + elapsed) % star.drag
		local m = star.dragE / star.drag
		local x = index * 0.35
		local y = index * 0.25
		local angle
		if index > 1 and index % 3 == 0 then
			star.rDragE = (star.rDragE + elapsed) % star.rDrag
			if index % 6 == 0 then
				angle = (star.angle * star.rDragE / star.rDrag) % (math.pi * 2)
			else
				angle = -(star.angle * star.rDragE / star.rDrag) % (math.pi * 2)
			end
		else
			angle = star.angle
		end
		if star.baseAlpha < 1 then
			star.flashNext = star.flashNext - elapsed
			if star.flashNext <= 0 and star.flashTleft <= 0 then
				star.flashNext = math.random(1500, 5000) / 1000
				star.flashT = math.random(600, 1000) / 1000
				star.flashTleft = star.flashT
			end
			star.flashTleft = star.flashTleft - elapsed
			if star.flashTleft > 0 then
				local flashElapsed = star.flashT - star.flashTleft
				local halfTime = star.flashT / 2
				local progress
				if flashElapsed < halfTime then
					progress = EasingUtil.InOutQuad(flashElapsed, 0, 1, halfTime)
				else
					progress = EasingUtil.OutQuad(flashElapsed - halfTime, 1, -1, halfTime)
				end
				if progress <= 1 then
					star:SetAlpha(star.baseAlpha + ((1 - star.baseAlpha) * progress))
					star.starMode:SetAlpha(progress)
				end
			else
				star.flashTleft = 0
				star:SetAlpha(star.baseAlpha)
				star.starMode:SetAlpha(0)
			end
		end
		self:SetSignTexCoord(star, angle, 0 + x + m, 1 + x + m, 0 + y + m, 1 + y + m)
	end
end

CharacterCreateZodiacSignSelectorMixin = {}

function CharacterCreateZodiacSignSelectorMixin:OnLoad()
	self.parent = self:GetParent()

	self.Background:SetAtlas("charactercreate-customize-dropdownbox")
	self.Highlight:SetAtlas("charactercreate-customize-dropdownbox-open")

	self.IncrementButton:SetNormalAtlas("charactercreate-customize-nextbutton")
	self.IncrementButton:SetPushedAtlas("charactercreate-customize-nextbutton-down")
	self.IncrementButton:SetDisabledAtlas("charactercreate-customize-nextbutton-disabled")

	self.DecrementButton:SetNormalAtlas("charactercreate-customize-backbutton")
	self.DecrementButton:SetPushedAtlas("charactercreate-customize-backbutton-down")
	self.DecrementButton:SetDisabledAtlas("charactercreate-customize-backbutton-disabled")

	local xOffset = self.incrementOffsetX or 4
	self.IncrementButton:SetPoint("LEFT", self, "RIGHT", xOffset, 0)
	self.IncrementButton:SetScript("OnClick", GenerateClosure(self.OnIncrementClicked, self))

	xOffset = self.decrementOffsetX or -5
	self.DecrementButton:SetPoint("RIGHT", self, "LEFT", xOffset, 0)
	self.DecrementButton:SetScript("OnClick", GenerateClosure(self.OnDecrementClicked, self))
end

function CharacterCreateZodiacSignSelectorMixin:OnIncrementClicked(button)
	self.parent:NextSign()
	PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
end

function CharacterCreateZodiacSignSelectorMixin:OnDecrementClicked(button)
	self.parent:PreviousSign()
	PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
end

function CharacterCreateZodiacSignSelectorMixin:OnMouseWheel(delta)
	if delta > 0 then
		self.parent:PreviousSign()
	else
		self.parent:NextSign()
	end
	PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
end

function CharacterCreateZodiacSignSelectorMixin:OnEnter()
	if self.parent.OnEnter then
		self.parent:OnEnter()
	end
end

function CharacterCreateZodiacSignSelectorMixin:OnLeave()
	if self.parent.OnLeave then
		self.parent:OnLeave()
	end
end

function CharacterCreateZodiacSignSelectorMixin:SetEnabled(enabled)
	self.DecrementButton:SetEnabled(enabled)
	self.IncrementButton:SetEnabled(enabled)
end

CharacterCreateZodiacSignIconButtonMixin = {}

function CharacterCreateZodiacSignIconButtonMixin:OnLoad()
	self.Lock:SetSize(33, 42)
	self.Lock:SetAtlas("BonusChest-Lock")
end

function CharacterCreateZodiacSignIconButtonMixin:OnClick(button)
	self:GetParent():GetParent():SelectSignIndex(self:GetID())
	PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
end

function CharacterCreateZodiacSignIconButtonMixin:OnEnter()
	self.ArtworkGlow:Show()

	local isValid, disabledReason, disableReasonInfo = C_CharacterCreation.IsSignAvailable(self:GetID())
	if not isValid and disabledReason then
		GlueTooltip:SetOwner(self)
		GlueTooltip:SetMaxWidth(325)
		GlueTooltip:AddLine(disabledReason, 1, 0, 0)
		if disableReasonInfo then
			GlueTooltip:AddLine(disableReasonInfo, 1, 0.82, 0)
		end
		GlueTooltip:Show()
	end
	if IsInterfaceDevClient() then
		local zodiacRaceID = C_CharacterCreation.GetZodiacSignInfo(self:GetID())
		if not GlueTooltip:IsShown() or GlueTooltip:GetOwner() ~= self then
			GlueTooltip:SetOwner(self)
		end
		GlueTooltip:AddLine(string.format("RaceID: |cffFFFFFF%u|r", zodiacRaceID), 0.5, 0.5, 0.5)
		GlueTooltip:AddLine(string.format("RaceID DBC: |cffFFFFFF%u|r", E_CHARACTER_RACES_DBC[E_CHARACTER_RACES[zodiacRaceID]]), 0.5, 0.5, 0.5)
		GlueTooltip:Show()
	end
end

function CharacterCreateZodiacSignIconButtonMixin:OnLeave()
	self.ArtworkGlow:Hide()
	GlueTooltip:Hide()
end

function CharacterCreateZodiacSignIconButtonMixin:OnHide()
	self.ArtworkGlow:Hide()
end

CharacterCreateZodiacSignSpellMixin = {}

function CharacterCreateZodiacSignSpellMixin:OnLoad()
	self.Border:SetAtlas("PKBT-ItemBorder-Default")
end

function CharacterCreateZodiacSignSpellMixin:OnEnter()
	if self.description then
		GlueTooltip:SetOwner(self, "ANCHOR_TOP")
		GlueTooltip:SetMaxWidth(330)
		GlueTooltip:AddLine(self.name, 1, 1, 1)
		GlueTooltip:AddLine(self.description, 1, 0.82, 0)
		if IsGMAccount() then
			GlueTooltip:AddLine(string.format("SpellID: |cffFFFFFF%u|r", self.id), 0.5, 0.5, 0.5)
			GlueTooltip:AddLine(string.format("Icon: |cffFFFFFF%s|r", self.iconName), 0.5, 0.5, 0.5)
		end
		GlueTooltip:Show()
	end
end

function CharacterCreateZodiacSignSpellMixin:OnLeave()
	GlueTooltip:Hide()
end

CharacterCreateCustomizationButtonFrameTemplateMixin = {}

function CharacterCreateCustomizationButtonFrameTemplateMixin:OnLoad()
	self.Background:SetAtlas("Glue-Shadow-Button-Normal")
end

CharCustomizeBaseButtonMixin = {};

function CharCustomizeBaseButtonMixin:OnBaseButtonClick()
	CharCustomizeFrame:OnButtonClick();
end

CharCustomizeSmallButtonMixin = CreateFromMixins();

function CharCustomizeSmallButtonMixin:OnLoad()
	self.NormalTexture:SetAtlas("common-button-square-gray-up")
	self.PushedTexture:SetAtlas("common-button-square-gray-down")

	self.HighlightTexture:ClearAllPoints()
	self.HighlightTexture:SetPoint("TOPLEFT", self.Icon)
	self.HighlightTexture:SetPoint("BOTTOMRIGHT", self.Icon)

	self.tooltipMinWidth = nil

	self.Icon:SetAtlas(self.iconAtlas);
	self.HighlightTexture:SetAtlas(self.iconAtlas);
end

function CharCustomizeSmallButtonMixin:OnEnter()
	if self.simpleTooltipLine then
		GlueTooltip:SetOwner(self, "ANCHOR_RIGHT", self:GetAttribute("tooltipXOffset"), self:GetAttribute("tooltipYOffset"))
		GlueTooltip:SetText(self.simpleTooltipLine, 1, 1, 1)
		GlueTooltip:Show()
	end
end

function CharCustomizeSmallButtonMixin:OnLeave()
	if self.simpleTooltipLine then
		GlueTooltip:Hide();
	end
end

function CharCustomizeSmallButtonMixin:OnMouseDown()
	if self:IsEnabled() then
		self.Icon:SetPoint("CENTER", self.PushedTexture);
	end
end

function CharCustomizeSmallButtonMixin:OnMouseUp()
	self.Icon:SetPoint("CENTER");
end

function CharCustomizeSmallButtonMixin:OnClick()
	PlaySound(SOUNDKIT.GS_CHARACTER_CREATION_LOOK);
end

CharCustomizeClickOrHoldButtonMixin = {};

function CharCustomizeClickOrHoldButtonMixin:OnLoad()
	self.holdWaitTimeSeconds = self:GetAttribute("holdWaitTimeSeconds")

	CharCustomizeSmallButtonMixin.OnLoad(self)
end

function CharCustomizeClickOrHoldButtonMixin:OnHide()
	self.waitTimerSeconds = nil;
	self:SetScript("OnUpdate", nil);
end

function CharCustomizeClickOrHoldButtonMixin:DoClickAction()
end

function CharCustomizeClickOrHoldButtonMixin:DoHoldAction(elapsed)
end

function CharCustomizeClickOrHoldButtonMixin:OnClick()
	CharCustomizeSmallButtonMixin.OnClick(self);

	if not self.wasHeld then
		self:DoClickAction();
	end
end

function CharCustomizeClickOrHoldButtonMixin:OnUpdate(elapsed)
	if self.waitTimerSeconds then
		self.waitTimerSeconds = self.waitTimerSeconds - elapsed;
		if self.waitTimerSeconds >= 0 then
			return;
		else
			-- waitTimerSeconds is now negative, so add it to elapsed to remove any leftover wait time
			elapsed = elapsed + self.waitTimerSeconds;
			self.waitTimerSeconds = nil;
		end
	end

	self.wasHeld = true;
	self:DoHoldAction(elapsed);
end

function CharCustomizeClickOrHoldButtonMixin:OnMouseDown()
	CharCustomizeSmallButtonMixin.OnMouseDown(self);
	self.wasHeld = false;
	self.waitTimerSeconds = self.holdWaitTimeSeconds;
	self:SetScript("OnUpdate", self.OnUpdate);
end

function CharCustomizeClickOrHoldButtonMixin:OnMouseUp()
	CharCustomizeSmallButtonMixin.OnMouseUp(self);
	self.waitTimerSeconds = nil;
	self:SetScript("OnUpdate", nil);
end

CharCustomizeResetCameraButtonMixin = {};

function CharCustomizeResetCameraButtonMixin:OnLoad()
	self.layoutIndex = self:GetAttribute("layoutIndex")
	self.iconAtlas = self:GetAttribute("iconAtlas")

	CharCustomizeSmallButtonMixin.OnLoad(self)
end

local RESET_ROTATION_TIME2 = 0.55
function CharCustomizeResetCameraButtonMixin:OnUpdate(elapsed)
	if self.rotationResetStep then
		self.elapsed = self.elapsed + elapsed
		if self.elapsed < self.rotationResetTime then
			C_CharacterCreation.SetCharacterCreateFacing(self.rotationResetCur + self.rotationResetStep * self.elapsed)
		else
			self:StopRotation()
		end
	end
end

function CharCustomizeResetCameraButtonMixin:StopRotation()
	self:SetScript("OnUpdate", nil)
	self.elapsed = 0
	self.rotationResetTime = nil
	self.rotationResetCur = nil
	self.rotationResetStep = nil
	C_CharacterCreation.SetCharacterCreateFacing(C_CharacterCreation.GetDefaultCharacterCreateFacing())
end

function CharCustomizeResetCameraButtonMixin:OnHide()
	self:StopRotation()
end

function CharCustomizeResetCameraButtonMixin:OnClick()
	CharCustomizeSmallButtonMixin.OnClick(self);

	C_CharacterCreation.ZoomCamera(CAMERA_ZOOM_LEVEL_AMOUNT - C_CharacterCreation.GetCurrentCameraZoom(), nil, true)
--	C_CharacterCreation.SetCharacterCreateFacing(0)

	local defaultDeg = C_CharacterCreation.GetDefaultCharacterCreateFacing()
	local deg = C_CharacterCreation.GetCharacterCreateFacing()
	if deg ~= defaultDeg then
		local change = (defaultDeg - deg + 540) % 360 - 180
		self.elapsed = 0
		self.rotationResetTime = math.abs(change / 180 * RESET_ROTATION_TIME2)
		self.rotationResetCur = deg
		self.rotationResetStep = change / self.rotationResetTime
		self:SetScript("OnUpdate", self.OnUpdate)
	end
end

CharCustomizeZoomButtonMixin = CreateFromMixins(CharCustomizeClickOrHoldButtonMixin);

function CharCustomizeZoomButtonMixin:OnLoad()
	self.layoutIndex = self:GetAttribute("layoutIndex")
	self.iconAtlas = self:GetAttribute("iconAtlas")
	self.clickAmount = self:GetAttribute("clickAmount")
	self.holdAmountPerSecond = self:GetAttribute("holdAmountPerSecond")

	CharCustomizeClickOrHoldButtonMixin.OnLoad(self)
end

function CharCustomizeZoomButtonMixin:DoClickAction()
	C_CharacterCreation.SetCameraZoomLevel(C_CharacterCreation.GetCurrentCameraZoom() + self.clickAmount, nil, true)
	self:GetParent():GetParent():UpdateZoomButtonStates()
end

function CharCustomizeZoomButtonMixin:DoHoldAction(elapsed)
	C_CharacterCreation.SetCameraZoomLevel(C_CharacterCreation.GetCurrentCameraZoom() + self.holdAmountPerSecond * elapsed)
	self:GetParent():GetParent():UpdateZoomButtonStates()
end

CharCustomizeRotateButtonMixin = CreateFromMixins(CharCustomizeClickOrHoldButtonMixin);

function CharCustomizeRotateButtonMixin:OnLoad()
	self.layoutIndex = self:GetAttribute("layoutIndex")
	self.iconAtlas = self:GetAttribute("iconAtlas")
	self.leftPadding = self:GetAttribute("leftPadding")
	self.clickAmount = self:GetAttribute("clickAmount")
	self.holdAmountPerSecond = self:GetAttribute("holdAmountPerSecond")

	CharCustomizeClickOrHoldButtonMixin.OnLoad(self)
end

function CharCustomizeRotateButtonMixin:DoClickAction()
	C_CharacterCreation.SetCharacterCreateFacing(C_CharacterCreation.GetCharacterCreateFacing() + self.clickAmount)
end

function CharCustomizeRotateButtonMixin:DoHoldAction(elapsed)
	C_CharacterCreation.SetCharacterCreateFacing(C_CharacterCreation.GetCharacterCreateFacing() + self.holdAmountPerSecond * elapsed);
end

CharacterCreateNavigationFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterCreateNavigationFrameMixin:OnLoad()
	self.sourceYOffset = 0
	self.startPoint = 0
	self.endPoint = self.sourceXOffset
	self.duration = 0.500
end

function CharacterCreateNavigationFrameMixin:OnShow()
	if not IsWideScreen() and PAID_SERVICE_TYPE ~= E_PAID_SERVICE.CHANGE_ZODIAC then
		self.sourceYOffset = 58
	else
		self.sourceYOffset = 0
	end
	self.endPoint = self.sourceYOffset

	self:SetPoint("BOTTOMLEFT", 0, self.sourceYOffset)
	self:SetPoint("BOTTOMRIGHT", 0, self.sourceYOffset)
end

function CharacterCreateNavigationFrameMixin:PlayAnim(...)
	if not IsWideScreen() then
		GlueEasingAnimMixin.PlayAnim(self, ...)
	end
end

function CharacterCreateNavigationFrameMixin:SetPosition(easing, progress)
	if easing then
		self:SetPoint("BOTTOMLEFT", 0, easing)
		self:SetPoint("BOTTOMRIGHT", 0, easing)
	else
		self:SetPoint("BOTTOMLEFT", 0, self.isRevers and self.startPoint or self.sourceYOffset)
		self:SetPoint("BOTTOMRIGHT", 0, self.isRevers and self.startPoint or self.sourceYOffset)
	end
end

CharacterCreateCircleShadowButtonTemplateMixin = {}

function CharacterCreateCircleShadowButtonTemplateMixin:OnLoad()
	self.normalTextureH = self:GetAttribute("normalTextureSizeH")
	self.normalTextureW = self:GetAttribute("normalTextureSizeW")

	self.PushedTexture:SetSize(self.normalTextureH, self.normalTextureW)
end

function CharCreateRaceButtonTemplate_OnEnter(self)
	if not self.data then return end

	local factionID = self.data.factionID
	if not factionID or not PLAYER_FACTION_GROUP[factionID] then
		error(string.format("CharCreateRaceButtonTemplate_OnEnter: Unknown faction (%i, %i, %i)", self.index, factionID or -1, PAID_SERVICE_TYPE or -1), 1)
	end

	local factionColor = PLAYER_FACTION_COLORS[factionID] or CreateColor(1, 1, 1)
	local raceFileString = string.upper(self.data.clientFileString)

	local tooltip = GlueRaceTooltip
	local alliedRaceText

	if self.alliedRace then
		if self.alliedRaceDisabled or self.alliedRaceGMAllowed then
			alliedRaceText = string.format("%s - %s", ALLIED_RACE_DISABLE, _G[string.format("ALLIED_RACE_DISABLE_REASON_%s", raceFileString:upper())])
		else
			alliedRaceText = _G[string.format("ALLIED_RACE_UNLOCKED_%s", raceFileString)] or string.format(_G["ALLIED_RACE_UNLOCKED"], self.data.name)
		end
	end

	tooltip:Hide()
	tooltip:SetBackdropBorderColor(factionColor.r, factionColor.g, factionColor.b)

	local tooltipHeight = 10

	tooltip.Header:SetText(self.data.name)
	tooltip.Description:SetText(_G[string.format("CHAR_INFO_RACE_%s_DESC", raceFileString)])

	tooltip.Header:SetWidth(tooltip:GetWidth() - 20)
	tooltip:SetWidth(math.max(tooltip:GetWidth(), tooltip.Header:GetWidth() + 20))

	tooltip.Description:SetWidth(tooltip:GetWidth() - 20)
	tooltip:SetWidth(math.max(tooltip:GetWidth(), tooltip.Description:GetWidth() + 20))

	tooltipHeight = tooltipHeight + tooltip.Description:GetHeight() + tooltip.Header:GetHeight() + 30

	if C_CharacterCreation.IsZodiacSignsEnabled() then
		tooltip.AbilityList:Hide()
		tooltipHeight = tooltipHeight - 10
	else
		if TOOLTIPS_EXPANDED then
			local abilities = {}
			local abilitiesPassive = {}

			for abilityIndex = 1, TOOLTIP_MAX_RACE_ABLILITIES_PASSIVE do
				local ability = _G[string.format("CHAR_INFO_RACE_%s_SPELL_PASSIVE%i_SHORT", raceFileString, abilityIndex)]
				if ability then
					local icon, desc = string.match(ability, "([^|]*)|(.+)")
					abilitiesPassive[#abilitiesPassive + 1] = {
						icon = string.format("Interface/Icons/%s", icon or "INV_Misc_QuestionMark"),
						description = desc,
					}
				end
			end

			for abilityIndex = 1, TOOLTIP_MAX_RACE_ABLILITIES_ACTIVE do
				local ability = _G[string.format("CHAR_INFO_RACE_%s_SPELL_ACTIVE%i_DESC_SHORT", raceFileString, abilityIndex)]
				if ability then
					local icon, desc = string.match(ability, "([^|]*)|(.+)")
					abilities[#abilities + 1] = {
						icon = string.format("Interface/Icons/%s", icon or "INV_Misc_QuestionMark"),
						description = desc,
					}
				end
			end

			tooltip.PassiveList:SetupAbilties(abilitiesPassive)
			tooltip.PassiveList:Show()
			tooltip.AbilityList:SetupAbilties(abilities)
			tooltip.AbilityList:Show()

			tooltip.ClickInfo:SetText(RIGHT_CLICK_FOR_LESS)
			tooltip.ClickInfo:SetPoint("TOPLEFT", alliedRaceText and tooltip.Warning or tooltip.AbilityList, "BOTTOMLEFT", 0, -15)

			tooltipHeight = tooltipHeight + tooltip.PassiveList:GetHeight() + 15 + tooltip.AbilityList:GetHeight() + tooltip.ClickInfo:GetHeight() + 20
		else
			tooltip.PassiveList:Hide()
			tooltip.AbilityList:Hide()
			tooltip.ClickInfo:SetText(RIGHT_CLICK_FOR_MORE)
			tooltip.ClickInfo:SetPoint("TOPLEFT", alliedRaceText and tooltip.Warning or tooltip.Description, "BOTTOMLEFT", 0, -15)

			tooltipHeight = tooltipHeight + tooltip.ClickInfo:GetHeight() + 5
		end
	end

	if alliedRaceText then
		tooltip.Warning:SetText(alliedRaceText)
		tooltip.Warning:SetWidth(tooltip:GetWidth() - 20)
		tooltip.Warning:SetPoint("TOPLEFT", tooltip.AbilityList:IsShown() and tooltip.AbilityList or tooltip.Description, "BOTTOMLEFT", 0, -15)
		tooltip.Warning:Show()

		tooltipHeight = tooltipHeight + tooltip.Warning:GetHeight() + 15
	else
		tooltip.Warning:Hide()
	end

	if self:GetParent() == self.mainFrame.AllianceRacesFrame then
		tooltip:ClearAndSetPoint("LEFT", self.mainFrame.AllianceRacesFrame, "RIGHT", 0, 0)
	elseif self:GetParent() == self.mainFrame.HordeRacesFrame then
		tooltip:ClearAndSetPoint("RIGHT", self.mainFrame.HordeRacesFrame, "LEFT", 0, 0)
	else
		tooltip:ClearAndSetPoint("TOP", self, "BOTTOM", 0, -10)
	end

	tooltip:SetHeight(tooltipHeight)
	tooltip:Show()
end

function CharCreateRaceButtonTemplate_OnLeave(self)
	GlueRaceTooltip:Hide()
end

function CharCreateClassButtonTemplate_OnEnter(self)
	if not self.name then return end

	local classTag = self.clientFileString and string.upper(self.clientFileString)
	if not classTag then return end

	local tooltip = GlueClassTooltip
	tooltip:Hide()

	if self.Tcolor then
		tooltip:SetBackdropBorderColor(self.Tcolor[1], self.Tcolor[2], self.Tcolor[3])
	end

	local tooltipHeight = 10

	tooltip.Header:SetText(self.name)
	tooltip.Description:SetText(_G[string.format("CHAR_INFO_CLASS_%s_DESC", classTag)])
	tooltip.Role:SetText(_G[string.format("CHAR_INFO_CLASS_%s_ROLE", classTag)])

	tooltip.Header:SetWidth(tooltip:GetWidth() - 20)
	tooltip:SetWidth(math.max(tooltip:GetWidth(), tooltip.Header:GetWidth() + 20))

	tooltip.Description:SetWidth(tooltip:GetWidth() - 20)
	tooltip:SetWidth(math.max(tooltip:GetWidth(), tooltip.Description:GetWidth() + 20))

	tooltip.Role:SetWidth(tooltip:GetWidth() - 20)
	tooltip:SetWidth(math.max(tooltip:GetWidth(), tooltip.Role:GetWidth() + 20))

	tooltipHeight = tooltipHeight + tooltip.Header:GetHeight() + tooltip.Description:GetHeight() + tooltip.Role:GetHeight() + 40

	if TOOLTIPS_EXPANDED then
		local abilities = {}

		for abilityIndex = 1, TOOLTIP_MAX_CLASS_ABLILITIES do
			local ability = _G[string.format("CHAR_INFO_CLASS_%s_SPELL%i", classTag, abilityIndex)]
			if ability then
				local icon, desc = string.match(ability, "([^|]*)|(.+)")
				abilities[#abilities + 1] = {
					icon = string.format("Interface/Icons/%s", icon or "INV_Misc_QuestionMark"),
					description = desc,
				}
			end
		end

		tooltip.AbilityList:SetupAbilties(abilities)
		tooltip.AbilityList:Show()

		tooltip.ClickInfo:SetText(RIGHT_CLICK_FOR_LESS)
		tooltip.ClickInfo:SetPoint("TOPLEFT", self:IsEnabled() ~= 1 and tooltip.Warning or tooltip.AbilityList, "BOTTOMLEFT", 0, -15)

		tooltipHeight = tooltipHeight + tooltip.AbilityList:GetHeight() + tooltip.ClickInfo:GetHeight() + 20
	else
		tooltip.AbilityList:Hide()
		tooltip.ClickInfo:SetText(RIGHT_CLICK_FOR_MORE)
		tooltip.ClickInfo:SetPoint("TOPLEFT", self:IsEnabled() ~= 1 and tooltip.Warning or tooltip.Role, "BOTTOMLEFT", 0, -15)

		tooltipHeight = tooltipHeight + tooltip.ClickInfo:GetHeight() + 5
	end

	if self:IsEnabled() ~= 1 then
		tooltip.Warning:SetText(self.disabledReason)
		tooltip.Warning:SetWidth(tooltip:GetWidth() - 20)
		tooltip:SetWidth(math.max(tooltip:GetWidth(), tooltip.Warning:GetWidth() + 20))
		tooltip.Warning:SetPoint("TOPLEFT", tooltip.AbilityList:IsShown() and tooltip.AbilityList or tooltip.Role, "BOTTOMLEFT", 0, -15)
		tooltip.Warning:Show()

		tooltipHeight = tooltipHeight + tooltip.Warning:GetHeight() + 15
	else
		tooltip.Warning:Hide()
	end

	tooltip:SetHeight(tooltipHeight)
	tooltip:ClearAllPoints()
	tooltip:SetPoint("BOTTOM", self, "TOP", 0, 10)
	tooltip:Show()
end

function CharCreateClassButtonTemplate_OnLeave(self)
	GlueClassTooltip:Hide()
end