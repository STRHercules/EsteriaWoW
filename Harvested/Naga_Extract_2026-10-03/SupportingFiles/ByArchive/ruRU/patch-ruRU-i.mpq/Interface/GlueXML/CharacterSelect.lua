local CHARACTER_SELECT_ROTATION_START_X = nil;
local CHARACTER_SELECT_INITIAL_FACING = nil;

local CHARACTER_ROTATION_CONSTANT = 0.6;

local DRAG_ACTIVE = false
local DRAG_BUTTON_INDEX = nil
local DRAG_HOLD_BUTTON = nil
local DRAG_HOLD_BUTTON_TIME = 0
local DRAG_HOLD_DELAY_TIME = 0.5

local DEFAULT_TEXT_OFFSET_X = 4
local DEFAULT_TEXT_OFFSET_Y = 0

local MOVING_TEXT_OFFSET_X = 12
local MOVING_TEXT_OFFSET_Y = 0

local DEFAULT_PRETEXT_ICON_OFFSET_X = 0
local DEFAULT_PRETEXT_ICON_OFFSET_Y = 5

local MOVING_PRETEXT_ICON_OFFSET_X = 8
local MOVING_PRETEXT_ICON_OFFSET_Y = 5

local translationTable = {};	-- for character reordering: key = button index, value = character ID

local FORCE_CHANGE_FACTION_TEXT = {
	[0] = FORCE_CHANGE_FACTION_EVENT_PANDA,
	[1] = FORCE_CHANGE_FACTION_EVENT_VULPERA,
	[2] = FORCE_CHANGE_FACTION_EVENT_COMMON
}

local SERVICE_BUTTON_ACTIVATION_DELAY = 0.400

function CharacterSelect_OnLoad(self)
	CharSelectChangeListStateButton:SetFrameLevel(self:GetFrameLevel() + 4)
	CharSelectEnterWorldButton:SetAutoSize(true, 10, 200)

	self.createIndex = 0;
	self.selectedIndex = 0;
	self.selectLast = 0;
	self:RegisterEvent("ADDON_LIST_UPDATE");
	self:RegisterEvent("CHARACTER_LIST_UPDATE");
	self:RegisterCustomEvent("CUSTOM_UPDATE_SELECTED_CHARACTER");
	self:RegisterEvent("SELECT_LAST_CHARACTER");
	self:RegisterEvent("SELECT_FIRST_CHARACTER");
	self:RegisterEvent("SUGGEST_REALM");
	self:RegisterEvent("FORCE_RENAME_CHARACTER");
	self:RegisterCustomEvent("SERVICE_DATA_UPDATE")
	self:RegisterCustomEvent("CHARACTER_LIST_PAGE_CHANGED")
	self:RegisterCustomEvent("CUSTOM_CHARACTER_LIST_UPDATE")
	self:RegisterCustomEvent("CUSTOM_CHARACTER_INFO_UPDATE")
	self:RegisterCustomEvent("CHARACTER_ORDER_SAVED")
	self:RegisterCustomEvent("CUSTOM_CHARACTER_FIXED")
	self:RegisterCustomEvent("CONNECTION_REALM_CONNECT")
	self:RegisterCustomEvent("CONNECTION_REALM_DISCONNECT")
	self:RegisterCustomEvent("CONNECTION_REALM_CHANGED")

	if IsConnectedToServer() then
		C_CharacterServices.RequestServiceInfo()
	end
end

function CharacterSelect_OnShow()
	if GlueFFXModel.ghostBugWorkaround then
		return
	end

	AccountLoginConnectionErrorFrame:Hide()

	FireCustomClientEvent("CUSTOM_CHARACTER_SELECT_SHOWN")

	-- request account data times from the server (so we know if we should refresh keybindings, etc...)
	ReadyForAccountDataTimes()
	GlueDialog:HideDialog("SERVER_WAITING")
	CharacterServiceBoostFlowFrame:Hide()
	CharacterServiceGearBoostFlowFrame:Hide()
	BoostServiceItemBrowserFrame:Hide()
	CharacterBoostBuyFrame:Hide()
	CharacterBoostRefundDialog:Hide()
	CharacterSelect.AutoEnterWorldCharacterGUID = nil

	if not C_GlobalStorageSecure.GetGlobalVar("GLUE_CHAR_FACTION_CHANGE_EVENT") and not C_Service.GetAccountID() then
		GlueDialog:ShowDialog("SERVER_WAITING")
	else
		GlueDialog:HideDialog("SERVER_WAITING")
	end

	BuildCharIndexToIDMapping();

	UpdateAddonButton();

	CharacterSelect_UpdateRealmButton()

	if IsConnectedToServer() then
		C_CharacterList.GetCharacterListUpdate();
	else
		UpdateCharacterList();
	end

	-- fadein the character select ui
	GlueFrameFadeIn(CharacterSelectUI, CHARACTER_SELECT_FADE_IN)

	RealmSplitCurrentChoice:Hide();
	RequestRealmSplitInfo();

	--Clear out the addons selected item
	GlueDark_DropDownMenu_SetSelectedValue(AddonCharacterDropDown, ALL);

	CharacterBoostButton:Show()
	CharacterBoostRefundButton:SetShown(C_CharacterServices.IsBoostRefundAvailable())

	CharacterSelectLogoFrameLogo:SetAtlas(C_RealmInfo.GetServerLogo(C_RealmInfo.GetServerIDByName(GetServerName())))

	CharacterSelectCharacterFrame:Hide()
	CharacterSelectLeftPanel:Hide()
	CharacterSelectPlayerNameFrame:Hide()
	CharacterSelectBottomLeftPanel:Hide()
	CharSelectChangeRealmButton:Hide()
	CharSelectChangeListStateButton:Hide()
end

function CharacterSelect_OnHide()
	if GlueFFXModel.ghostBugWorkaround then
		return
	end

	GlueDialog:HideDialog("ADDON_INVALID_VERSION_DIALOG")
	CharacterSelect_CloseDropdowns()

	if DRAG_ACTIVE then
		DRAG_ACTIVE = false
		DRAG_HOLD_BUTTON = nil
		DRAG_HOLD_BUTTON_TIME = 0

		if DRAG_BUTTON_INDEX then
			_G["CharSelectCharacterButton"..DRAG_BUTTON_INDEX]:OnDragStop()
			DRAG_BUTTON_INDEX = nil
		end
	end

	C_CharacterList.ForceSetPlayableMode()

	CharacterDeleteDialog:Hide()
	CharacterRenameDialog:Hide()
	CharacterFixDialog:Hide()
	CharacterBoostBuyFrame:Hide()
	CharacterBoostRefundDialog:Hide()
	CharacterServicePagePurchaseFrame:Hide()
	CharacterServiceRestoreCharacterFrame:Hide()

	if ( DeclensionFrame ) then
		DeclensionFrame:Hide();
	end
	SERVER_SPLIT_STATE_PENDING = -1;

	C_GlobalStorageSecure.SetGlobalVar("GLUE_CHAR_FACTION_CHANGE_EVENT", nil)
	C_GlobalStorageSecure.SetGlobalVar("GLUE_CHAR_FORCE_CUSTOMIZATION", nil)

	CharacterSelect_UIResetAnim()
end

function CharacterSelect_OnUpdate(self, elapsed)
	if DRAG_HOLD_BUTTON then
		DRAG_HOLD_BUTTON_TIME = DRAG_HOLD_BUTTON_TIME + elapsed
		if DRAG_HOLD_BUTTON_TIME >= DRAG_HOLD_DELAY_TIME then
			DRAG_HOLD_BUTTON:OnDragStart()
		end
	end

	if self.serviceButtonDelay then
		self.serviceButtonDelay = self.serviceButtonDelay - elapsed

		if self.serviceButtonDelay <= 0 then
			self.serviceButtonDelay = nil

			local button = CharacterSelectCharacterFrame.characterSelectButtons[CharacterSelect.selectedIndex]
			for _, serviceButton in ipairs(button.serviceButtons) do
				serviceButton:EnableMouse(true)
			end
		end
	end

	if ( SERVER_SPLIT_STATE_PENDING > 0 ) then
		CharacterSelectRealmSplitButton:Show();

		if ( SERVER_SPLIT_CLIENT_STATE > 0 ) then
			RealmSplit_SetChoiceText();
			RealmSplitPending:SetPoint("TOP", RealmSplitCurrentChoice, "BOTTOM", 0, -10);
		else
			RealmSplitPending:SetPoint("TOP", CharacterSelectRealmSplitButton, "BOTTOM", 0, 0);
			RealmSplitCurrentChoice:Hide();
		end

		if ( SERVER_SPLIT_STATE_PENDING > 1 ) then
			CharacterSelectRealmSplitButton:Disable();
			CharacterSelectRealmSplitButtonGlow:Hide();
			RealmSplitPending:SetText( SERVER_SPLIT_PENDING );
		else
			CharacterSelectRealmSplitButton:Enable();
			CharacterSelectRealmSplitButtonGlow:Show();
			local datetext = SERVER_SPLIT_CHOOSE_BY.."\n"..SERVER_SPLIT_DATE;
			RealmSplitPending:SetText( datetext );
		end

		if ( SERVER_SPLIT_SHOW_DIALOG and not GlueDialog:IsShown() ) then
			SERVER_SPLIT_SHOW_DIALOG = false;
			local dialogString = format(SERVER_SPLIT,SERVER_SPLIT_DATE);
			if ( SERVER_SPLIT_CLIENT_STATE > 0 ) then
				local serverChoice = RealmSplit_GetFormatedChoice(SERVER_SPLIT_REALM_CHOICE);
				local stringWithDate = format(SERVER_SPLIT,SERVER_SPLIT_DATE);
				dialogString = stringWithDate.."\n\n"..serverChoice;
				GlueDialog:ShowDialog("SERVER_SPLIT_WITH_CHOICE", dialogString);
			else
				GlueDialog:ShowDialog("SERVER_SPLIT", dialogString);
			end
		end
	else
		CharacterSelectRealmSplitButton:Hide();
	end

	-- Account Msg stuff
	if ( (ACCOUNT_MSG_NUM_AVAILABLE > 0) and not GlueDialog:IsShown() ) then
		if ( ACCOUNT_MSG_HEADERS_LOADED ) then
			if ( ACCOUNT_MSG_BODY_LOADED ) then
				local dialogString = AccountMsg_GetHeaderSubject( ACCOUNT_MSG_CURRENT_INDEX ).."\n\n"..AccountMsg_GetBody();
				GlueDialog:ShowDialog("ACCOUNT_MSG", dialogString);
			end
		end
	end

	if not GlueDialog:IsShown() and not GlueParent.dontShowInvalidVersionAddonDialog and not C_GlobalStorageSecure.GetGlobalVar("GLUE_CHAR_FACTION_CHANGE_EVENT") then
		if AddonList_HasNewVersion() then
			if not GetCVarBool("ignoreAddonVersion") then
				if IsGMAccount(true) then
					GlueDialog:ShowDialog("ADDON_INVALID_VERSION_DIALOG_NSA")
				else
					GlueDialog:ShowDialog("ADDON_INVALID_VERSION_DIALOG")
				end
			else
				GlueParent.dontShowInvalidVersionAddonDialog = true
			end
		else
			SetCVar("ignoreAddonVersion", nil)
			GlueParent.dontShowInvalidVersionAddonDialog = true
		end
	end

	GlueDialog:CheckQueuedDialogs()
end

function CharacterSelect_OnKeyDown(self,key)
	if GlueDialog:IsDialogShown("SERVER_WAITING")
	or CharacterServiceBoostFlowFrame:IsShown()
	or CharacterServiceGearBoostFlowFrame:IsShown()
	then
		return
	end

	if ( key == "ESCAPE" ) then
		if CharacterSelectCharacterFrame.DropDownMenu:IsShown() then
			CharacterSelectCharacterFrame.DropDownMenu:Hide()
		else
			CharacterSelect_Exit();
		end
	elseif ( key == "ENTER" ) then
		CharacterSelect_CloseDropdowns()
		CharacterSelect_EnterWorld();
	elseif ( key == "PRINTSCREEN" ) then
		CharacterSelect_CloseDropdowns()
		Screenshot();
	elseif ( key == "UP" or key == "LEFT" ) then
		if key == "LEFT" then
			local numPages = C_CharacterList.GetNumPages()
			if numPages > 1 and C_CharacterList.GetCurrentPageIndex() > 1 then
				C_CharacterList.ScrollListPage(-1)
				return
			end
		end

		local numChars = C_CharacterList.GetNumCharactersOnPage();
		if ( numChars > 1 ) then
			if ( CharacterSelect.selectedIndex > 1 ) then
				CharacterSelect_SelectCharacter(CharacterSelect.selectedIndex - 1);
			else
				CharacterSelect_SelectCharacter(numChars);
			end
		end
	elseif ( key == "DOWN" or key == "RIGHT" ) then
		if key == "RIGHT" then
			local numPages = C_CharacterList.GetNumPages()
			if numPages > 1 and C_CharacterList.GetCurrentPageIndex() < numPages then
				C_CharacterList.ScrollListPage(1)
				return
			end
		end

		local numChars = C_CharacterList.GetNumCharactersOnPage();
		if ( numChars > 1 ) then
			if ( CharacterSelect.selectedIndex < numChars ) then
				CharacterSelect_SelectCharacter(CharacterSelect.selectedIndex + 1);
			else
				CharacterSelect_SelectCharacter(1);
			end
		end
	end
end

function UpdateCharacterSelectListView()
	local connected = IsConnectedToServer() == 1
	local numCharacters = C_CharacterList.GetNumCharacters()
	local inPlayableMode = C_CharacterList.IsInPlayableMode()

	if not connected then
		C_CharacterList.ForceSetPlayableMode()
		inPlayableMode = true
	end

	CharacterSelectOptionsButton:SetShown(inPlayableMode)
	CharSelectRestoreButton:SetShown(not inPlayableMode)

	local showBoostServicePanel = connected and inPlayableMode and numCharacters > 0 --and C_CharacterServices.GetBoostStatus() ~= Enum.CharacterServices.BoostServiceStatus.Disabled
	CharacterBoostButton:SetShown(showBoostServicePanel)
	CharacterBoostRefundButton:SetShown(showBoostServicePanel and C_CharacterServices.IsBoostRefundAvailable())
	CharacterGearBoostButton:SetShown(showBoostServicePanel and C_CharacterServices.IsGearBoostServiceAvailable() and C_CharacterList.HasMaxLevelNonHardcore())
	CharacterSelectLeftPanel.CharacterBoostInfoFrame:SetShown(showBoostServicePanel)

	if not inPlayableMode then
		CharSelectCreateCharacterMiddleButton:Hide()
		CharSelectCreateCharacterButton:Hide()
		CharSelectChangeListStateButton:Hide()

		CharSelectCharacterName:Show()
		CharacterSelectAddonsButton:Hide()

		CharacterSelect_UpdateRealmButton()
	else
		CharSelectCreateCharacterMiddleButton:SetShown(connected and numCharacters == 0)
		CharSelectCreateCharacterButton:SetShown(connected and numCharacters > 0)
		CharSelectChangeListStateButton:SetShown(connected)
		CharSelectChangeListStateButton:SetText(CHARACTER_SELECT_UNDELETED_CHARACTER)

		CharSelectCharacterName:SetShown(connected and numCharacters > 0)
		CharacterSelectAddonsButton:SetShown(connected and GetNumAddOns() > 0)

		if not connected then
			CharacterServiceBoostFlowFrame:Hide()
			CharacterServiceGearBoostFlowFrame:Hide()
		end

		CharacterSelect_UIShowAnim(false, function()
			C_CharacterServices.CheckBoostServiceItemStage()
		end)
	end

	CharacterSelect_UpdateEnterWorldButton()

	if CharacterSelect.UndeleteCharacterAlert then
		if CharacterSelect.UndeleteCharacterAlert == 1 then
			GlueDialog:ShowDialog("OKAY_VOID", CHARACTER_UNDELETE_ALERT_1)
		else
			GlueDialog:ShowDialog("OKAY_VOID", CHARACTER_UNDELETE_ALERT_2)
		end
		CharacterSelect.UndeleteCharacterAlert = nil
	end
end

function CharacterSelect_OnEvent(self, event, ...)
	if ( event == "ADDON_LIST_UPDATE" ) then
		C_CharacterServices.RequestServiceInfo(true)
		UpdateAddonButton();
	elseif ( event == "CHARACTER_LIST_UPDATE" ) then
		do
			local listSize = C_CharacterList.GetNumCharacters(true)
			BuildCharIndexToIDMapping(listSize)
			CharacterSelect.orderChanged = nil
		end

		UpdateCharacterList();

		if CharacterSelect.AutoEnterWorldCharacterGUID then
			local characterID = C_CharacterList.GetCharacterIDByGUID(CharacterSelect.AutoEnterWorldCharacterGUID)
			if characterID then
				CharacterSelect.AutoEnterWorldCharacterGUID = nil
				C_CharacterList.SetPage(GetCharPageIndexFromCharID(characterID))
				C_CharacterList.SelectCharacter(characterID)
				C_CharacterList.EnterWorld(characterID)
			end
		end

		CharacterSelect_UpdateRealmButton()
		UpdateCharacterSelectListView()
		UpdateCharacterSelection()

		local factionChangeID = C_GlobalStorageSecure.GetGlobalVar("GLUE_CHAR_FACTION_CHANGE_EVENT")
		if factionChangeID then
			local factionText = FORCE_CHANGE_FACTION_TEXT[factionChangeID]

			if factionText then
				CharacterSelectUI:Hide()
				GlueDialog:ShowDialog("SERVER_WAITING", factionText)

				C_Timer:After(3, function()
					C_CharacterList.EnterWorld()
				end)
			end

			C_GlobalStorageSecure.SetGlobalVar("GLUE_CHAR_FACTION_CHANGE_EVENT", nil)
		else
			CharacterSelectUI:Show()
		end

		FireCustomClientEvent("CHARACTER_LIST_UPDATE_DONE")
	elseif ( event == "CUSTOM_UPDATE_SELECTED_CHARACTER" ) then
		local charID = ...;

		CheckBuildCharIndexToIDMapping();

		if ( charID == 0 ) then
			CharSelectCharacterName:SetText("");
		else
			CharacterSelect.selectedIndex = GetIndexFromCharID(charID);
			if CharacterSelect.selectedIndex == 0 and charID <= C_CharacterList.GetNumCharacters(true) then
				-- character translation table may not be populated after creation of new character until next list update
				CharacterSelect.selectedIndex = GetCharIndexFromGlobalIndex(charID)
			end
		end

		C_CharacterList.SetPage(GetCharPageIndexFromCharID(charID))
		UpdateCharacterSelection();
	elseif ( event == "SELECT_LAST_CHARACTER" ) then
		self.selectLast = 1;
	elseif ( event == "SELECT_FIRST_CHARACTER" ) then
		CharacterSelect_SelectCharacter(1, 1);
	elseif ( event == "SUGGEST_REALM" ) then
		local category, id = ...;
		local name = C_RealmList.GetRealmInfo(category, id);
		if ( name ) then
			SetGlueScreen("charselect");
			C_RealmList.ChangeRealm(category, id);
		else
			if ( RealmList:IsShown() ) then
				RealmListUpdate();
			else
				RealmList:Show();
			end
		end
	elseif ( event == "FORCE_RENAME_CHARACTER" ) then
		local message = ...;
		CharacterRenameDialog:SetTitleText(_G[message])
		CharacterRenameDialog:ShowDialog(GetCharIDFromIndex(CharacterSelect.selectedIndex))
	elseif event == "CONNECTION_REALM_CONNECT" or event == "CONNECTION_REALM_DISCONNECT" or event == "CONNECTION_REALM_CHANGED" then
		local serverName, isPVP, isRP = GetServerName()
		if serverName then
			local serverType
			if isPVP then
				serverType = isRP and RPPVP_PARENTHESES or PVP_PARENTHESES
			elseif isRP then
				serverType = RP_PARENTHESES
			else
				serverType = ""
			end

			if IsConnectedToServer() then
				CharSelectChangeRealmButton:SetFormattedText("%s %s", serverName, serverType)
			else
				CharSelectChangeRealmButton:SetFormattedText("%s %s\n(%s)", serverName, serverType, SERVER_DOWN)
				UpdateCharacterSelectListView()
				CharacterSelectCharacterFrame:PlayAnim(true)
				if not CharacterSelectLeftPanel.isRevers then
					CharacterSelectLeftPanel:PlayAnim(true)
				end
				CharacterSelectPlayerNameFrame:PlayAnim(true)
				CharacterSelectUI.PaidServiceSelection:PlayAnim(true, nil, nil, true)
			end

			CharSelectChangeRealmButton:SetWidth(math.max(160, math.floor(CharSelectChangeRealmButton:GetTextWidth() + 0.5) + 20))
		end
	elseif event == "SERVICE_DATA_UPDATE" then
		if not C_GlobalStorageSecure.GetGlobalVar("GLUE_CHAR_FACTION_CHANGE_EVENT") then
			GlueDialog:HideDialog("SERVER_WAITING")
		end
	elseif event == "CHARACTER_LIST_PAGE_CHANGED" then
		CharacterSelect_UpdatePageButton()
		CharacterSelect_UpdateCharecterCreateButton()
		UpdateCharacterList()
		UpdateCharacterSelection()
		UpdateCharacterSelectListView()
		CharSelectEnterWorldButton:SetEnabled(C_CharacterList.CanEnterWorld(C_CharacterList.GetSelectedCharacter()))
	elseif event == "CUSTOM_CHARACTER_LIST_UPDATE" then
		local listModeChanged, listChanged = ...

		if CharacterSelectCharacterFrame:IsShown() ~= 1 and C_CharacterList.GetNumCharactersOnPage() == 0 then
			CharacterSelectCharacterFrame:PlayAnim()
		end

		CharacterSelect_UpdatePageButton()
		CharacterSelect_UpdateCharecterCreateButton()

		if listChanged then
			UpdateCharacterList()
		end

		if listModeChanged or listChanged then
			UpdateCharacterSelection()
			UpdateCharacterSelectListView()
		end

		CharSelectEnterWorldButton:SetEnabled(C_CharacterList.CanEnterWorld(C_CharacterList.GetSelectedCharacter()))
	elseif event == "CUSTOM_CHARACTER_INFO_UPDATE" then
		local characterID = ...
		if CharacterSelectCharacterFrame.characterSelectButtons[characterID] then
			CharacterSelectCharacterFrame.characterSelectButtons[characterID]:UpdateCharData()
		end
		if characterID == C_CharacterList.GetSelectedCharacter() then
			CharacterSelect_UpdateEnterWorldButton()
		end
	elseif event == "CUSTOM_CHARACTER_FIXED" then
		local characterID = ...
		if C_CharacterList.GetSelectedCharacter() ~= characterID then
			C_CharacterList.SetPage(GetCharPageIndexFromCharID(characterID))
			C_CharacterList.SelectCharacter(characterID)
		end

		CharacterSelect_EnterWorld()
	elseif event == "CHARACTER_ORDER_SAVED" then
		local success = ...
		CharacterSelect.lockCharacterMove = nil
	end
end

local function playPanelAnim(f, revers, finishCallback, resetAnimation)
	if (revers and f:IsShown()) or (not revers and not f:IsShown()) then
		f:PlayAnim(revers, finishCallback, resetAnimation)
	end
end

function CharacterSelect_UIShowAnim(revers, finishCallback)
	CharacterSelectBottomLeftPanel.startPoint = CharacterSelectAddonsButton:IsShown() and -175 or -150
	CharacterSelectPlayerNameFrame.startPoint = CharacterSelectUI.PaidServiceSelection:IsShown() and -150 or -100

	if C_CharacterList.GetNumCharactersOnPage() > 0 then
		playPanelAnim(CharacterSelectCharacterFrame, revers)
		playPanelAnim(CharacterSelectLeftPanel, revers)
		playPanelAnim(CharacterSelectPlayerNameFrame, revers)
	end

	playPanelAnim(CharSelectChangeRealmButton, revers)
	playPanelAnim(CharacterSelectBottomLeftPanel, revers, finishCallback)
	CharacterSelectUI.PaidServiceSelection:PlayAnim(revers, nil, nil, true)
end

function CharacterSelect_UIResetAnim()
	CharacterSelectCharacterFrame:Reset()
	CharacterSelectLeftPanel:Reset()
	CharacterSelectPlayerNameFrame:Reset()
	CharSelectChangeRealmButton:Reset()
	CharacterSelectBottomLeftPanel:Reset()

	CharacterSelectCharacterFrame:SetPosition(CharacterSelectCharacterFrame.startPoint)
	CharacterSelectLeftPanel:SetPosition(CharacterSelectLeftPanel.startPoint)
	CharacterSelectPlayerNameFrame:SetPosition(CharacterSelectPlayerNameFrame.startPoint)
	CharSelectChangeRealmButton:SetPosition(CharSelectChangeRealmButton.startPoint)
	CharacterSelectBottomLeftPanel:SetPosition(CharacterSelectBottomLeftPanel.startPoint)
end

function CharacterSelect_UpdateRealmButton()
	if C_CharacterList.IsInPlayableMode() and GetServerName() then
		playPanelAnim(CharSelectChangeRealmButton)
	else
		playPanelAnim(CharSelectChangeRealmButton, true, function()
			CharSelectChangeRealmButton:Hide()
		end, true)
	end
end

function CharSelectChangeListState_OnClick(self, button)
	self:Disable()

	if C_CharacterList.IsInPlayableMode() then
		CharSelectCharPageButtonPrev:Disable()
		CharSelectCharPageButtonNext:Disable()

		C_CharacterList.EnterRestoreMode()
	else
		CharacterSelect_Exit()
	end
end

function CharacterSelect_UpdateModel(self)
	C_CharacterList.UpdateSelectionCustomizationScene()
	self:AdvanceTime();
end

function UpdateCharacterSelection()
	CharacterSelect_CloseDropdowns()

	local inPlayableMode = C_CharacterList.IsInPlayableMode()

	for i = 1, C_CharacterList.GetNumCharactersPerPage() do
		local button = _G["CharSelectCharacterButton"..i]
		button.selection:Hide()
		button.MoveUp:Hide()
		button.MoveDown:Hide()
		button.FactionEmblem:Show()

		if inPlayableMode
		and not CharacterServiceBoostFlowFrame:IsShown()
		and not CharacterServiceGearBoostFlowFrame:IsShown()
		then
			button:EnableDrag()
		else
			button:DisableDrag()
		end

		button:HideMoveButtons()
	end

	local index = CharacterSelect.selectedIndex;
	if ( (index > 0) and (index <= C_CharacterList.GetNumCharactersPerPage()) ) then
		local button = _G["CharSelectCharacterButton"..index]
		if ( button ) then
			button.selection:Show()
			button:UpdateMouseOver()
		end
	end
end

function CharacterSelect_UpdateCharecterCreateButton()
	CharacterSelect.createIndex = 0

	if C_CharacterList.CanCreateCharacter()
	and not CharacterServiceBoostFlowFrame:IsShown()
	and not CharacterServiceGearBoostFlowFrame:IsShown()
	then
		local numCharactersTotal = C_CharacterList.GetNumCharacters(true)

		CharacterSelect.createIndex = numCharactersTotal + 1;
		if ( IsConnectedToServer() ) then
			CharSelectCreateCharacterButton:SetID(numCharactersTotal + 1)
		end

		CharSelectCreateCharacterButton:Enable()
	else
		CharSelectCreateCharacterButton:Disable()
	end
end

function UpdateCharacterList(skipAutoCharacterSelection)
	local inPlayableMode = C_CharacterList.IsInPlayableMode()
	local numCharactersOnPage = C_CharacterList.GetNumCharacters()
	local numCharactersTotal = C_CharacterList.GetNumCharacters(true)

	for characterIndex = 1, numCharactersOnPage do
		local characterID = GetCharIDFromIndex(characterIndex)
		local name, race, class, level, zone, sex, ghost, PCC, PRC, PFC = C_CharacterList.GetCharacterInfo(characterID)

		local button = _G["CharSelectCharacterButton"..characterIndex];
		if name then
			if ( not zone ) then
				zone = "";
			end

			button.buttonText.name:SetText(inPlayableMode and name or (name .. DELETED))
			button.buttonText.Location:SetText(zone == "" and UNKNOWN_ZONE or zone);
			button.PortraitFrame.LevelFrame.Level:SetText(level)
		end

		button:SetID(characterID)
		button:SetIndex(characterIndex)
		button:SetCharacterInfo(name, race, class, level, zone, sex, ghost, PCC, PRC, PFC)
		button:UpdateCharData()
		button:UpdateFaction()
		button:Show()
	end

	for characterIndex = numCharactersOnPage + 1, C_CharacterList.GetNumCharactersPerPage() do
		local button = _G["CharSelectCharacterButton"..characterIndex];
		button:Hide();
	end

	CharacterSelect_UpdateCharecterCreateButton()

	if ( numCharactersTotal == 0 ) then
		CharacterSelect.selectedIndex = 0;
		CharacterSelect_SelectCharacter(CharacterSelect.selectedIndex, true);
		return;
	end

	if ( CharacterSelect.selectLast == 1 ) then
		CharacterSelect.selectLast = 0;
		CharacterSelect_SelectCharacterID(numCharactersTotal, true);
		return;
	end

	if ( (CharacterSelect.selectedIndex == 0) or (CharacterSelect.selectedIndex > numCharactersOnPage) ) then
		CharacterSelect.selectedIndex = 1;
	end

	if not skipAutoCharacterSelection then
		CharacterSelect_SelectCharacter(CharacterSelect.selectedIndex, true);
	end
end

function CharacterSelect_OpenCharacterCreate(paidServiceID, characterID, onShowAnim, skipAnimCheck, skipForcedActionCheck)
	if not skipAnimCheck and CharacterSelectBottomLeftPanel and CharacterSelectBottomLeftPanel:IsAnimPlaying() then
		return
	end

	if not skipForcedActionCheck and paidServiceID then
		if paidServiceID ~= E_PAID_SERVICE.CUSTOMIZATION then
			if C_CharacterList.HasCharacterForcedCustomization(characterID)
			or C_CharacterList.HasCharacterHardcoreProposal(characterID) then
				GlueDialog:ShowDialog("OKAY", CUSTOMIZATION_DISABLED_REASON_FORCED_CUSTOMIZATION)
				return
			end
		end

		if C_CharacterList.HasCharacterForcedRename(characterID) then
			GlueDialog:ShowDialog("OKAY", CUSTOMIZATION_DISABLED_REASON_FORCED_RENAME)
			return
		end
	end

	CharacterSelectUI.Background.hideAnim:Play()
	CharacterSelect_UIShowAnim(true, function(this)
		HelpTip:Hide(CharacterBoostButton, BOOST_SERVICE_UPDATE_TIP)

		if type(onShowAnim) == "function" then
			onShowAnim()
		end
		PlaySound("gsCharacterSelectionCreateNew");
		C_CharacterCreation.SetCreateScreen(paidServiceID, characterID)
	end)

	return true
end

function CharacterSelect_SelectCharacter(characterIndex, noCreate)
	CharacterSelect_CloseDropdowns()

	if ( characterIndex == CharacterSelect.createIndex ) then
		CharacterSelect_SelectCharacterID(characterIndex, noCreate)
	else
		local characterID = GetCharIDFromIndex(characterIndex)
		CharacterSelect_SelectCharacterID(characterID, noCreate)
	end
end

function CharacterSelect_SelectCharacterID(characterID, noCreate)
	CharacterSelect_CloseDropdowns()

	if ( characterID == CharacterSelect.createIndex ) then
		if ( not noCreate ) then
			CharacterSelect_OpenCharacterCreate()
		end
	else
		local name, race, class = C_CharacterList.GetCharacterInfo(characterID)
		local guid, raceID, classID, level, zoneID, sexID, customizationFlags, displayIDs = C_CharacterList.GetCharacterInfoEx(characterID)

		if name then
			local factionID, factionGroup, factionNameLocalized = C_CreatureInfo.GetFactionInfoByRace(raceID)
			local _classID, classFile, classFlag, classLocMale, classLocFemale = C_CreatureInfo.GetClassInfoEx(classID)

			local modelName = factionGroup

			if raceID == E_CHARACTER_RACES.RACE_ZANDALARITROLL then
				if classFile == "DEATHKNIGHT" then
					modelName = "Zandalar_DeathKnight"
				elseif C_CharacterList.GetCharacterFaction(characterID) == PLAYER_FACTION_GROUP.Alliance then
					modelName = "Zandalar_Alliance"
				else
					modelName = "Zandalar_Horde"
				end
			elseif classFile == "DEATHKNIGHT" then
				if C_CharacterCreation.IsPandarenRace(raceID) then
					modelName = "Pandaren_DeathKnight"
				else
					modelName = "DeathKnight"
				end
			elseif raceID == E_CHARACTER_RACES.RACE_DRACTHYR then
				modelName = "Dracthyr"
			elseif C_CharacterCreation.IsPandarenRace(raceID) then
				modelName = "Pandaren"
			elseif C_CharacterCreation.IsVulperaRace(raceID) then
				modelName = "Vulpera"
			else
				local factionOverrideID = C_CharacterList.GetCharacterFactionOverride(characterID)
				if factionOverrideID == PLAYER_FACTION_GROUP.Horde then
					modelName = "Horde"
				elseif factionOverrideID == PLAYER_FACTION_GROUP.Alliance then
					modelName = "Alliance"
				end
			end

			CharSelectCharacterName:SetText(GetClassColorObj(classFile):WrapTextInColorCode(name))
			CharacterModelManager.SetBackground(modelName)
			C_CharacterList.SetPage(GetCharPageIndexFromCharID(characterID))
			C_CharacterList.SelectCharacter(characterID)

			if C_GlobalStorageSecure.GetGlobalVar("GLUE_CHAR_FORCE_CUSTOMIZATION") then
				if C_CharacterCreation.PaidChange_GetCharacterID() then
					RunNextFrame(function()
						CharacterSelect_OpenCharacterCreate(E_PAID_SERVICE.CUSTOMIZATION, characterID, nil, true, true)
					end)
					C_GlobalStorageSecure.SetGlobalVar("GLUE_CHAR_FORCE_CUSTOMIZATION", nil)
					return
				end
			end

			CharacterSelect_UpdateEnterWorldButton()
		else
			CharacterModelManager.SetBackground("Alliance")
		end

		CharacterSelectUI.PaidServiceSelection:UpdateState()
	end
end

function CharacterSelect_UpdateEnterWorldButton()
	if C_CharacterList.IsInPlayableMode() and IsConnectedToServer() == 1 and C_CharacterList.GetNumCharactersOnPage() > 0 then
		CharSelectEnterWorldButton:Show()
	else
		CharSelectEnterWorldButton:Hide()
		return
	end

	local characterID = C_CharacterList.GetSelectedCharacter()
	if C_CharacterList.HasCharacterForcedCustomization(characterID)
	or C_CharacterList.HasCharacterHardcoreProposal(characterID)
	then
		CharSelectEnterWorldButton:SetText(COMPLETE_FORCED_CUSTOMIZATION)
	elseif C_CharacterList.HasCharacterForcedRename(characterID) then
		CharSelectEnterWorldButton:SetText(COMPLETE_FORCED_RENAME)
	else
		CharSelectEnterWorldButton:SetText(ENTER_WORLD)
	end
	CharSelectEnterWorldButton:SetEnabled(C_CharacterList.CanEnterWorld(characterID))
end

function CharacterSelect_EnterWorld()
	if not C_CharacterList.IsInPlayableMode() or GlueDialog:IsDialogShown("SERVER_WAITING") then return end

	local characterID = C_CharacterList.GetSelectedCharacter()

	if C_CharacterList.HasCharacterForcedCustomization(characterID) then
		CharacterSelect_OpenCharacterCreate(E_PAID_SERVICE.CUSTOMIZATION, characterID)
		C_GlobalStorageSecure.SetGlobalVar("GLUE_CHAR_FORCE_CUSTOMIZATION", nil)
		return
	elseif C_CharacterList.HasCharacterHardcoreProposal(characterID) then
		GlueDialog:ShowDialog("HARDCORE_PROPOSAL", nil, characterID)
		return
	end

	PlaySound("gsCharacterSelectionEnterWorld");
	StopGlueAmbience();

	if CharacterServiceBoostFlowFrame:IsShown() then
		CharacterServiceBoostFlowFrame:OnWorldEnterAttempt()
	elseif CharacterServiceGearBoostFlowFrame:IsShown() then
		CharacterServiceGearBoostFlowFrame:OnWorldEnterAttempt()
	elseif C_CharacterList.CanEnterWorld(characterID) then
		C_CharacterList.EnterWorld()
	end
end

function CharacterSelect_Exit()
	if GlueDialog:IsDialogShown("SERVER_WAITING") then return end

	if C_CharacterList.IsInPlayableMode() then
		CharacterSelect.lockCharacterMove = nil
		PlaySound("gsCharacterSelectionExit");
		DisconnectFromServer();
		SetGlueScreen("login");
	else
		CharSelectCharPageButtonPrev:Disable()
		CharSelectCharPageButtonNext:Disable()
		C_CharacterList.ExitRestoreMode()
	end
end

function CharacterSelect_ChangeRealm()
	PlaySound("gsCharacterSelectionDelCharacter");
	C_RealmList.RequestRealmList(1);
end

function CharacterSelectRotateRight_OnUpdate(self)
	if ( self:GetButtonState() == "PUSHED" ) then
		C_CharacterList.SetCharacterSelectFacing(C_CharacterList.GetCharacterSelectFacing() + CHARACTER_FACING_INCREMENT)
	end
end

function CharacterSelectRotateLeft_OnUpdate(self)
	if ( self:GetButtonState() == "PUSHED" ) then
		C_CharacterList.SetCharacterSelectFacing(C_CharacterList.GetCharacterSelectFacing() - CHARACTER_FACING_INCREMENT)
	end
end

function RealmSplit_GetFormatedChoice(formatText)
	local realmChoice
	if ( SERVER_SPLIT_CLIENT_STATE == 1 ) then
		realmChoice = SERVER_SPLIT_SERVER_ONE;
	else
		realmChoice = SERVER_SPLIT_SERVER_TWO;
	end
	return format(formatText, realmChoice);
end

function RealmSplit_SetChoiceText()
	RealmSplitCurrentChoice:SetText( RealmSplit_GetFormatedChoice(SERVER_SPLIT_CURRENT_CHOICE) );
	RealmSplitCurrentChoice:Show();
end

function CharacterSelect_PrevPage(self, button)
	local pageIndex = C_CharacterList.GetCurrentPageIndex()
	if pageIndex <= 1 then
		return
	end

	C_CharacterList.SetPage(pageIndex - 1)
end

function CharacterSelect_NextPage(self, button)
	local pageIndex = C_CharacterList.GetCurrentPageIndex()
	if pageIndex >= C_CharacterList.GetNumPages() then
		return
	end

	C_CharacterList.SetPage(pageIndex + 1)
end

function CharacterSelect_SaveCharacterOrder()
	if CharacterSelect.orderChanged
	and not CharacterSelect.lockCharacterMove
	then
		CharacterSelect.lockCharacterMove = true
		C_CharacterList.SaveCharacterOrder(translationTable)
		CharacterSelect.orderChanged = nil
	end
end

function MoveCharacterID(originCharacterID, targetCharacterID, saveOrder)
	if CharacterSelect.lockCharacterMove then
		return
	end

	local originIndex, originPageIndex = GetIndexFromCharID(originCharacterID)
	local targetIndex, targetPageIndex = GetIndexFromCharID(targetCharacterID)
	local differentPages = originPageIndex ~= targetPageIndex

	if differentPages then
		local charactersPerPage = C_CharacterList.GetNumCharactersPerPage()
		originIndex = originIndex + charactersPerPage * (originPageIndex - 1)
		targetIndex = targetIndex + charactersPerPage * (targetPageIndex - 1)
	end

	CharacterSelect.orderChanged = true
	if targetIndex < 1 then
		targetIndex = #translationTable
	elseif targetIndex > #translationTable then
		targetIndex = 1
	end
	translationTable[originIndex], translationTable[targetIndex] = translationTable[targetIndex], translationTable[originIndex]

	if saveOrder then
		CharacterSelect_SaveCharacterOrder()
	end

	if differentPages then
		C_CharacterList.SetPage(targetPageIndex)
		C_CharacterList.SelectCharacter(originCharacterID)
	else
		if originPageIndex == CharacterSelect.selectedIndex then
			CharacterSelect.selectedIndex = targetPageIndex
		elseif targetPageIndex == CharacterSelect.selectedIndex then
			CharacterSelect.selectedIndex = originPageIndex
		end

		UpdateCharacterSelection()
		UpdateCharacterList(true)
	end
end

function MoveCharacter(originIndex, targetIndex, fromDrag)
	if CharacterSelect.lockCharacterMove then
		return
	end

	CharacterSelect.orderChanged = true
	if targetIndex < 1 then
		targetIndex = #translationTable
	elseif targetIndex > #translationTable then
		targetIndex = 1
	end
	translationTable[originIndex], translationTable[targetIndex] = translationTable[targetIndex], translationTable[originIndex];

	local originOnPageIndex = GetIndexFromCharID(GetCharIDFromGlobalIndex(originIndex))
	local targetOnPageIndex = GetIndexFromCharID(GetCharIDFromGlobalIndex(targetIndex))

	-- update character list
	if ( fromDrag ) then
		DRAG_BUTTON_INDEX = targetOnPageIndex

		local originButton = _G["CharSelectCharacterButton"..originOnPageIndex]
		local targetButton = _G["CharSelectCharacterButton"..targetOnPageIndex]

		if originButton then
			originButton:SetAlpha(0.6)
			originButton:UnlockHighlight()
			if C_CharacterList.IsHardcoreCharacter(originButton.characterID) then
				originButton.buttonText.HardcoreIcon:SetPoint("TOPLEFT", DEFAULT_PRETEXT_ICON_OFFSET_X, DEFAULT_PRETEXT_ICON_OFFSET_Y)
			elseif C_CharacterList.GetCharacterCategorySpellID(originButton.characterID) then
				originButton.buttonText.CategoryIcon:SetPoint("TOPLEFT", DEFAULT_PRETEXT_ICON_OFFSET_X, DEFAULT_PRETEXT_ICON_OFFSET_Y)
			else
				originButton.buttonText.name:SetPoint("TOPLEFT", DEFAULT_TEXT_OFFSET_X, DEFAULT_TEXT_OFFSET_Y)
			end
		end

		if targetButton then
			targetButton:SetAlpha(1)
			targetButton:LockHighlight()
			if C_CharacterList.IsHardcoreCharacter(targetButton.characterID) then
				targetButton.buttonText.HardcoreIcon:SetPoint("TOPLEFT", MOVING_PRETEXT_ICON_OFFSET_X, MOVING_PRETEXT_ICON_OFFSET_Y)
			elseif C_CharacterList.GetCharacterCategorySpellID(targetButton.characterID) then
				targetButton.buttonText.CategoryIcon:SetPoint("TOPLEFT", MOVING_PRETEXT_ICON_OFFSET_X, MOVING_PRETEXT_ICON_OFFSET_Y)
			else
				targetButton.buttonText.name:SetPoint("TOPLEFT", MOVING_TEXT_OFFSET_X, MOVING_TEXT_OFFSET_Y)
			end
		end
	else
		CharacterSelect_SaveCharacterOrder()
	end

	if originOnPageIndex == CharacterSelect.selectedIndex then
		CharacterSelect.selectedIndex = targetOnPageIndex
	elseif targetOnPageIndex == CharacterSelect.selectedIndex then
		CharacterSelect.selectedIndex = originOnPageIndex
	end

	local originPageIndex = GetCharPageIndexFromGlobalIndex(originIndex)
	local targetPageIndex = GetCharPageIndexFromGlobalIndex(targetIndex)
	local differentPages = originPageIndex ~= targetPageIndex
	if differentPages then
		C_CharacterList.SetPage(targetPageIndex)
		C_CharacterList.SelectCharacter(GetCharIDFromGlobalIndex(targetIndex))
	else
		UpdateCharacterSelection()
		UpdateCharacterList(true)
	end
end

-- translation functions
function GetCharIDFromIndex(index)
	local pageIndex = C_CharacterList.GetCurrentPageIndex()
	if pageIndex > 1 then
		local charactersPerPage = C_CharacterList.GetNumCharactersPerPage()
		local offset = charactersPerPage * (pageIndex - 1)
		index = index + offset
	end
	return translationTable[index] or 0
end

function BuildCharIndexToIDMapping(listSize)
	if listSize and translationTable then
		CharacterSelect.orderChanged = (listSize > #translationTable);
	end

	listSize = listSize or C_CharacterList.GetNumCharacters(true)

	table.wipe(translationTable)

	if listSize > 0 then
		for i = 1, listSize do
			translationTable[i] = i
		end
	end
end

function CheckBuildCharIndexToIDMapping()
	if not translationTable or #translationTable == 0 then
		BuildCharIndexToIDMapping();
	end
end

function GetIndexFromCharID(characterID)
--[[
	if not CharacterSelect.orderChanged then
		local charactersPerPage = C_CharacterList.GetNumCharactersPerPage()
		if characterID > charactersPerPage then
			local pageIndex = math.ceil(characterID / charactersPerPage)
			return characterID - charactersPerPage * (pageIndex - 1), pageIndex
		end
		return characterID
	end
--]]
	for index = 1, #translationTable do
		if translationTable[index] == characterID then
			local charactersPerPage = C_CharacterList.GetNumCharactersPerPage()
			if index > charactersPerPage then
				local pageIndex = math.ceil(index / charactersPerPage)
				return index - charactersPerPage * (pageIndex - 1), pageIndex
			end
			return index, 1
		end
	end
	return 0, 1
end

function GetCharIndexFromGlobalIndex(index)
	local charactersPerPage = C_CharacterList.GetNumCharactersPerPage()
	local pageIndex = math.ceil(index / charactersPerPage)
	return index - charactersPerPage * (pageIndex - 1)
end

function GetCharGlobalIndexFromIndex(index)
--[[
	if not CharacterSelect.orderChanged then
		return characterID
	end
--]]
	local pageIndex = C_CharacterList.GetCurrentPageIndex()
	if pageIndex > 1 then
		local charactersPerPage = C_CharacterList.GetNumCharactersPerPage()
		return index + charactersPerPage * (pageIndex - 1)
	end
	return index
end

function GetCharIDFromGlobalIndex(index)
	return translationTable[index] or 0
end

function GetCharGlobalIndexFromCharID(characterID)
--[[
	if not CharacterSelect.orderChanged then
		return characterID
	end
--]]
	for index = 1, #translationTable do
		if translationTable[index] == characterID then
			return index
		end
	end
	return 0
end

function GetCharPageIndexFromGlobalIndex(index)
	local charactersPerPage = C_CharacterList.GetNumCharactersPerPage()
	if index > charactersPerPage then
		return math.ceil(index / charactersPerPage)
	end
	return 1
end

function GetCharPageIndexFromCharID(characterID)
	local characterIndex, pageIndex = GetIndexFromCharID(characterID)
	return pageIndex or 1
end

CharacterSelectPagePurchaseButtonMixin = CreateFromMixins(GlueDark_ButtonMixin)

function CharacterSelectPagePurchaseButtonMixin:OnLoad()
	GlueDark_ButtonMixin.OnLoadStyle(self, true)
end

function CharacterSelectPagePurchaseButtonMixin:OnEnter()
	GlueTooltip:SetOwner(self)
	GlueTooltip:AddLine(CHARACTER_SERVICES_LISTPAGE_TITLE)
	GlueTooltip:Show()
end

function CharacterSelectPagePurchaseButtonMixin:OnLeave()
	GlueTooltip:Hide()
end

function CharacterSelectPagePurchaseButtonMixin:OnClick(button)
	CharacterServicePagePurchaseFrame:SetPrice(C_CharacterServices.GetListPagePrice())
	CharacterServicePagePurchaseFrame:SetAltDescription(C_CharacterList.GetNumAvailablePages() > 1)
	CharacterServicePagePurchaseFrame:Show()
end

function CharacterSelect_UpdatePageButton()
	CharSelectChangeListStateButton:SetEnabled(not C_CharacterList.IsInPlayableMode() or C_CharacterList.IsRestoreModeAvailable())

	local numPages = C_CharacterList.GetNumPages()
	local currentPage = C_CharacterList.GetCurrentPageIndex()
	local numAvailablePages = C_CharacterList.GetNumAvailablePages()
	local isNewPageSuggested = C_CharacterServices.IsNewPageServiceAvailable()
	local bootCharacterID = CharacterServiceBoostFlowFrame:GetCharacterID() or CharacterServiceGearBoostFlowFrame:GetCharacterID()

	CharSelectCharPagePurchaseButton:SetShown(not bootCharacterID and isNewPageSuggested and currentPage == numAvailablePages)

	CharSelectCharPageButtonPrev:SetShown(numPages > 1)
	CharSelectCharPageButtonNext:SetShown(numPages > 1 and not CharSelectCharPagePurchaseButton:IsShown())

	if numPages > 1 then
		CharSelectCharPageButtonPrev:SetEnabled(not bootCharacterID and currentPage > 1)
		CharSelectCharPageButtonNext:SetEnabled(not bootCharacterID and currentPage < numPages)
	end
end

function CharacterSelect_RestoreButton_OnClick()
	CharacterServiceRestoreCharacterFrame:SetPurchaseArgs(GetCharIDFromIndex(CharacterSelect.selectedIndex))
	CharacterServiceRestoreCharacterFrame:SetPrice(C_CharacterServices.GetCharacterRestorePrice())
	CharacterServiceRestoreCharacterFrame:Show()
end

function CharacterSelect_OpenBoost(characterID, animated)
	CharacterSelect_CloseDropdowns()

	HelpTip:Acknowledge(CharacterBoostButton, BOOST_SERVICE_UPDATE_TIP)

	if not characterID then
		characterID = C_CharacterList.GetSelectedCharacter()
	end

	if characterID == 0 then
		error(string.format("Incorrect characterID [%s]", characterID), 2)
	end

	PlaySound(SOUNDKIT.GS_CHARACTER_SELECTION_ACCT_OPTIONS)
	C_CharacterServices.RequestServiceInfo()

	if not CharacterServiceBoostFlowFrame:IsShown() and C_CharacterServices.GetBoostStatus() == Enum.CharacterServices.BoostServiceStatus.Purchased then
		if animated then
			CharacterServiceBoostFlowFrame:PlayAnim()
		else
			CharacterServiceBoostFlowFrame:Show()
		end
	elseif not CharacterBoostBuyFrame:IsShown() and C_CharacterServices.GetBoostStatus() == Enum.CharacterServices.BoostServiceStatus.Available then
		CharacterBoostBuyFrame:Show()
	end
end

function CharacterSelect_OpenBoostRefund()
	PlaySound(SOUNDKIT.GS_CHARACTER_SELECTION_ACCT_OPTIONS)
	C_CharacterServices.RequestServiceInfo()

	if not CharacterBoostRefundDialog:IsShown() then
		CharacterBoostRefundDialog:Show()
	end
end

function CharacterSelect_OpenGearBoost(characterID, animated)
	CharacterSelect_CloseDropdowns()

	if not characterID then
		characterID = C_CharacterList.GetSelectedCharacter()
	end

	if characterID == 0 then
		error(string.format("Incorrect characterID [%s]", characterID), 2)
	end

	PlaySound(SOUNDKIT.GS_CHARACTER_SELECTION_ACCT_OPTIONS)

	if not CharacterServiceGearBoostFlowFrame:IsShown() and C_CharacterServices.IsGearBoostServiceAvailable() then
		if animated then
			CharacterServiceGearBoostFlowFrame:PlayAnim()
		else
			CharacterServiceGearBoostFlowFrame:Show()
		end
	end
end

function CharacterSelect_CloseDropdowns(button, event)
	if not button then
		CharacterSelectCharacterFrame.DropDownMenu:Hide()
	elseif event == "GLOBAL_MOUSE_DOWN" and (button == "LeftButton" or button == "RightButton") then
		if not WidgetContainsMouse(CharacterSelectCharacterFrame.DropDownMenu) then
			CharacterSelectCharacterFrame.DropDownMenu:Hide()
		end
	end
end

CharacterSelectPAIDButtonMixin = {}

function CharacterSelectPAIDButtonMixin:OnLoad()
	self.characterID = 0
	self.paidServiceID = E_PAID_SERVICE.NONE

	self.Borders = {self.Border, self.Border2, self.Border3}

	self.Border:SetAtlas("UI-Frame-jailerstower-Portrait-border")
	self.Border2:SetAtlas("UI-Frame-jailerstower-Portrait")
	self.Border3:SetAtlas("UI-Frame-jailerstower-Portrait")
end

function CharacterSelectPAIDButtonMixin:SetColor(r, g, b)
	self.Border:SetVertexColor(r, g, b)
	self.Border2:SetVertexColor(r, g, b)
	self.Border3:SetVertexColor(r, g, b)
end

function CharacterSelectPAIDButtonMixin:SetPaidServiceID(characterID, paidServiceID)
	self.characterID = characterID
	self.paidServiceID = paidServiceID or E_PAID_SERVICE.NONE

	if self.paidServiceID == E_PAID_SERVICE.NONE then
		self:Hide()
		return
	end

	local text, icon, hasTimer = C_CharacterList.GetPaidServiceInfo(self.paidServiceID)

	self.tooltipText = text
	self.UpdateTooltip = hasTimer and self.OnEnter or nil

	self:UpdateIcon()
	self:UpdateState()
	self:Show()
end

function CharacterSelectPAIDButtonMixin:GetPaidServiceID()
	return self.paidServiceID or E_PAID_SERVICE.NONE
end

function CharacterSelectPAIDButtonMixin:UpdateState()
	if C_CharacterList.IsCharacterInBoostMode(self.characterID) then
		self.disabledReason = CUSTOMIZATION_DISABLED_REASON_BOOST_SERVICE_MODE
	elseif C_CharacterList.HasCharacterForcedCustomization(self.characterID)
	or C_CharacterList.HasCharacterHardcoreProposal(self.characterID)
	then
		self.disabledReason = CUSTOMIZATION_DISABLED_REASON_FORCED_CUSTOMIZATION
	elseif C_CharacterList.HasCharacterForcedRename(self.characterID) then
		self.disabledReason = CUSTOMIZATION_DISABLED_REASON_FORCED_RENAME
	else
		self.disabledReason = nil
	end

	self:SetEnabled(not self.disabledReason)
end

function CharacterSelectPAIDButtonMixin:UpdateIcon()
	if self.paidServiceID == E_PAID_SERVICE.CHANGE_ZODIAC then
		local raceID = C_CharacterList.GetCharacterZodiacRaceID(self.characterID)
		local zodiacRaceID, name, description, icon, atlas, available = C_CharacterCreation.GetZodiacSignInfoByRaceID(raceID ~= 0 and raceID or 1)
		self.Icon:SetSize(24, 24)
		self.Icon:SetAtlas(atlas.."-Small")
	else
		local text, icon = C_CharacterList.GetPaidServiceInfo(self.paidServiceID)
		self.Icon:SetSize(30, 30)
		self.Icon:SetAtlas(icon)
	end
end

function CharacterSelectPAIDButtonMixin:OnEnable()
	if C_CharacterList.HasCharacterForcedCustomization(self.characterID)
	or C_CharacterList.HasCharacterHardcoreProposal(self.characterID)
	or C_CharacterList.HasCharacterForcedRename(self.characterID)
	then
		self:Disable()
		return
	end
	self.Icon:SetVertexColor(1, 1, 1)
end

function CharacterSelectPAIDButtonMixin:OnDisable()
	self.Icon:SetVertexColor(0.3, 0.3, 0.3)
end

function CharacterSelectPAIDButtonMixin:OnMouseDown(button)
	if button == "LeftButton" and self:IsEnabled() == 1 then
		local width, height = self.Icon:GetSize()
		self.Icon:SetSize(width - 2, height - 2)
	end
end

function CharacterSelectPAIDButtonMixin:OnMouseUp(button)
	if button == "LeftButton" and self:IsEnabled() == 1 then
		local width, height = self.Icon:GetSize()
		self.Icon:SetSize(width + 2, height + 2)
	end
end

function CharacterSelectPAIDButtonMixin:OnClick(button)
	if self.paidServiceID == E_PAID_SERVICE.RESTORE then
		CharacterServiceRestoreCharacterFrame:SetPurchaseArgs(self.characterID)
		CharacterServiceRestoreCharacterFrame:SetPrice(C_CharacterServices.GetCharacterRestorePrice())
		CharacterServiceRestoreCharacterFrame:Show()
		PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
		return
	elseif self.paidServiceID == E_PAID_SERVICE.BOOST_CANCEL then
		CharacterBoostCancelDialog:ShowDialog(self.characterID)
		PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
		return
	end

	CharacterSelect_OpenCharacterCreate(self.paidServiceID, self.characterID)
	PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
end

function CharacterSelectPAIDButtonMixin:OnEnter()
	if self:IsEnabled() ~= 1 then
		if self.disabledReason then
			GlueTooltip:SetOwner(self, self.tooltipAnchor or "ANCHOR_LEFT", self.tooltipOffsetX or 7, self.tooltipOffsetY or -7)
			GlueTooltip:SetText(self.disabledReason, 1, 0, 0, 1, true)
			GlueTooltip:Show()
		end
		return
	end

	for i = 2, 3 do
		local border = self.Borders[i]
		border.HideAnim:Stop()
		border:Show()

		if not border.Anim:IsPlaying() then
			border.Anim:Play()
			border.ShowAnim:Play()
		end
	end

	if self.tooltipText then
		GlueTooltip:SetOwner(self, self.tooltipAnchor or "ANCHOR_LEFT", self.tooltipOffsetX or 7, self.tooltipOffsetY or -7)
		GlueTooltip:SetText(self.tooltipText)
	--	GlueTooltip:AddLine(PAID_BOOST_CANCEL_TOOLTIP_DESCRIPTION, 1, 1, 1)

		if self.paidServiceID == E_PAID_SERVICE.BOOST_CANCEL then
			local totalTimeLeft, ingameTimeLeft = C_CharacterList.GetBoostCancelTimeLeft(self.characterID)
			local maxIngameTime = SECONDS_PER_HOUR * 6
			local ingameTime = maxIngameTime - ingameTimeLeft
			GlueTooltip:AddLine(string.format(PAID_BOOST_CANCEL_REMAINING_TIME, SecondsToTime(totalTimeLeft, false, false, 4, true), SecondsToTime(ingameTime, false, false, 4, true)), 1, 1, 1, 1, true)
		end

		GlueTooltip:Show()
	end
end

function CharacterSelectPAIDButtonMixin:OnLeave()
	if self:IsEnabled() ~= 1 then
		if self.disabledReason then
			GlueTooltip:Hide()
		end
		return
	end

	for i = 2, 3 do
		local border = self.Borders[i]
		border.HideAnim:Play()
		border.ShowAnim:Stop()
	end

	GlueTooltip:Hide()
end

CharacterSelectUIMixin = {}

function CharacterSelectUIMixin:OnLoad()
	CharSelectChangeListStateButton:Disable()
end

function CharacterSelectUIMixin:OnMouseDown(button)
	if button == "LeftButton" then
		CHARACTER_SELECT_ROTATION_START_X = GetScaledCursorPosition();
		CHARACTER_SELECT_INITIAL_FACING = C_CharacterList.GetCharacterSelectFacing()
	end

	CharacterSelect_CloseDropdowns()
end

function CharacterSelectUIMixin:OnMouseUp(button)
	if button == "LeftButton" then
		CHARACTER_SELECT_ROTATION_START_X = nil
	end
end

function CharacterSelectUIMixin:OnUpdate()
	if CHARACTER_SELECT_ROTATION_START_X then
		local cursorPos = GetScaledCursorPosition();
		local diff = (cursorPos - CHARACTER_SELECT_ROTATION_START_X) * CHARACTER_ROTATION_CONSTANT;
		CHARACTER_SELECT_ROTATION_START_X = cursorPos;
		C_CharacterList.SetCharacterSelectFacing(C_CharacterList.GetCharacterSelectFacing() + diff)
	end
end

CharacterSelectCharacterMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterSelectCharacterMixin:OnLoad()
	self.startPoint = self:GetWidth() + 10
	self.endPoint = 0
	self.duration = 0.500
end

function CharacterSelectCharacterMixin:SetPosition(easing, progress)
	local alpha = progress and (self.isRevers and (1 - progress) or progress) or (self.isRevers and 0 or 1)

	self:SetAlpha(alpha)
	CharSelectCharPageButtonPrev:SetAlpha(alpha)
	CharSelectCharPageButtonNext:SetAlpha(alpha)
	CharSelectCreateCharacterButton:SetAlpha(alpha)

	if easing then
		self:ClearAndSetPoint("RIGHT", easing, 10)
	else
		self:ClearAndSetPoint("RIGHT", self.isRevers and self.startPoint or self.endPoint, 10)
	end
end

function CharacterSelectCharacterMixin:OnMouseWheel(delta)
	C_CharacterList.ScrollListPage(-delta)
end

CharacterSelectLeftPanelMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterSelectLeftPanelMixin:OnLoad()
	self.startPoint = -300
	self.endPoint = 0
	self.duration = 0.500
end

function CharacterSelectLeftPanelMixin:SetPosition(easing, progress)
	if progress then
		self:SetAlpha(self.isRevers and (1 - progress) or progress)
	else
		self:SetAlpha(self.isRevers and 0 or 1)
	end
	if easing then
		self:ClearAndSetPoint("TOPLEFT", easing, -40)
	else
		self:ClearAndSetPoint("TOPLEFT", self.isRevers and self.startPoint or self.endPoint, -40)
	end
end

CharSelectChangeRealmButtonMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharSelectChangeRealmButtonMixin:OnLoad()
	self.startPoint = 40
	self.endPoint = -8
	self.duration = 0.500
end

function CharSelectChangeRealmButtonMixin:SetPosition(easing)
	if easing then
		self:ClearAndSetPoint("TOP", 0, easing)
	else
		self:ClearAndSetPoint("TOP", 0, self.isRevers and self.startPoint or self.endPoint)
	end
end

function CharSelectChangeRealmButtonMixin:OnClick(button)
	CharacterSelect_ChangeRealm()
end

CharacterSelectBottomLeftPanelMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterSelectBottomLeftPanelMixin:OnLoad()
	self.startPoint = -150
	self.endPoint = 23
	self.duration = 0.500
end

function CharacterSelectBottomLeftPanelMixin:SetPosition(easing, progress)
	if progress then
		CharSelectCreateCharacterMiddleButton:SetAlpha(self.isRevers and (1 - progress) or progress)
	else
		CharSelectCreateCharacterMiddleButton:SetAlpha(self.isRevers and 0 or 1)
	end
	if easing then
		self:ClearAndSetPoint("BOTTOMLEFT", 70, easing)
	else
		self:ClearAndSetPoint("BOTTOMLEFT", 70, self.isRevers and self.startPoint or self.endPoint)
	end
end

CharacterSelectPlayerNameFrameMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterSelectPlayerNameFrameMixin:OnLoad()
	self.startPoint = -100
	self.endPoint = 0
	self.duration = 0.500
end

function CharacterSelectPlayerNameFrameMixin:SetPosition(easing)
	if easing then
		self:ClearAndSetPoint("BOTTOM", 0, easing)
	else
		self:ClearAndSetPoint("BOTTOM", 0, self.isRevers and self.startPoint or self.endPoint)
	end
end

CharacterSelectButtonMixin = {}

function CharacterSelectButtonMixin:OnLoad()
	self:SetParentArray("characterSelectButtons")

	self:RegisterForClicks("LeftButtonUp", "RightButtonUp")
	self:RegisterForDrag("LeftButton")

	self.Background:SetAtlas("jailerstower-animapowerlist-dropdown-closedbg")
	self.selection:SetAtlas("jailerstower-animapowerlist-dropdown-closedbg2")

	self.HighlightTexture:SetAtlas("jailerstower-animapowerlist-dropdown-closedbg")

	self.PortraitFrame.Border:SetAtlas("UI-Frame-jailerstower-Portrait")
	self.PortraitFrame.FactionBorder:SetAtlas("UI-Frame-jailerstower-Portrait-border")

	self.PortraitFrame.LevelFrame.Border:SetAtlas("UI-Frame-jailerstower-Portrait")

	self.buttonText.HardcoreIcon.Icon:SetAtlas("Custom-Challenges-Icon-Hardcore")

	self.buttonText.GearBoost:SetSize(self.buttonText.GearBoost.Text:GetSize())

	self.PAIDButton:SetFrameLevel(self.PortraitFrame:GetFrameLevel() + 5)

	self.characterID = self:GetID()

	self:RegisterCustomEvent("CUSTOM_CHARACTER_FACTION_UPDATE")
	self:RegisterCustomEvent("CHARACTER_LIST_BOOST_MODE_CHANGED")
	self:RegisterCustomEvent("CHARACTER_SERVICES_BOOST_STATUS_UPDATE")
	self:RegisterCustomEvent("BOOST_SERVICE_ITEMS_LOADED")

	self:TogglePropagateClicks(true)
end

function CharacterSelectButtonMixin:OnEvent(event, ...)
	if event == "CHARACTER_FACTION_UPDATE" then
		local characterID = ...
		if self.characterID == characterID then
			self:UpdateFaction()
		end
	elseif event == "CHARACTER_LIST_BOOST_MODE_CHANGED" then
		local characterID = ...
		if self.characterID == characterID then
			self:UpdateBoostMode()
		end
	elseif event == "CHARACTER_SERVICES_BOOST_STATUS_UPDATE" then
		if self.classID then
			self:UpdateGearBoost()
		end
	elseif event == "BOOST_SERVICE_ITEMS_LOADED" then
		local classID = ...
		if self.classID == classID then
			self:UpdateGearBoost()
		end
	end
end

function CharacterSelectButtonMixin:GetID()
	return self.characterID or 0
end

function CharacterSelectButtonMixin:SetID(id)
	self.characterID = id
end

function CharacterSelectButtonMixin:GetIndex()
	return getmetatable(self).__index.GetID(self)
end

function CharacterSelectButtonMixin:SetIndex(index)
	return getmetatable(self).__index.SetID(self, index)
end

function CharacterSelectButtonMixin:TogglePropagateClicks(enable)
	if not self.clickPropagetingObjects then
		self.clickPropagetingObjects = {
			self.PortraitFrame,
			self.PortraitFrame.MailIcon,
			self.buttonText.HardcoreIcon,
			self.buttonText.CategoryIcon,
			self.buttonText.GearBoost,
		}

		self.clickPropagetingScripts = {
			OnMouseDown = function(this, button)
				self:OnMouseDown(button)
			end,
			OnMouseUp = function(this, button)
				self:OnMouseUp(button)
			end,
			OnClick = function(this, button)
				self:OnClick(button)
			end,
			OnDoubleClick = function(this, button)
				self:OnDoubleClick(button)
			end,
			OnDragStart = function(this, button)
				self:OnDragStart(button)
			end,
			OnDragStop = function(this)
				self:OnDragStop()
			end,
		}
	end

	for _, button in ipairs(self.clickPropagetingObjects) do
		for scripName, func in pairs(self.clickPropagetingScripts) do
			button:SetScript(scripName, enable and func or nil)
		end
	end
end

function CharacterSelectButtonMixin:UpdateCharacterInfo()
	self:SetCharacterInfo(C_CharacterList.GetCharacterInfo(self.characterID))
end

function CharacterSelectButtonMixin:SetCharacterInfo(name, race, class, level, zone, sex, ghost, PCC, PRC, PFC)
	if self.class ~= class then
		local classID, classFile, classFlag, classLocMale, classLocFemale = C_CreatureInfo.GetClassInfoEx(class)
		self.classID = classID
		self.classColor = GetClassColorObj(classFile)
		self:UpdateNameColor()
	end

	self.name = name
	self.race = race
	self.class = class
	self.level = level
	self.sex = sex
	self.PCC = PCC
	self.PRC = PRC
	self.PFC = PFC

	self:UpdateGearBoost()
end

function CharacterSelectButtonMixin:UpdateNameColor()
	self.buttonText.name:SetTextColor(self.classColor.r or 1, self.classColor.g or 1, self.classColor.b or 1)
	if self:IsEnabled() ~= 1 then
		self.buttonText.name:SetTextColor(0.3, 0.3, 0.3)
	end
end

function CharacterSelectButtonMixin:ClearCharacterInfo()
	self.characterID = self:GetID()
	self.name = nil
	self.race = nil
	self.class = nil
	self.level = nil
	self.sex = nil
	self.PCC = nil
	self.PRC = nil
	self.PFC = nil
end

function CharacterSelectButtonMixin:UpdateGearBoost(forceHide)
	if C_CharacterList.IsInPlayableMode()
	and self:IsMouseOverEx()
	and not self.PAIDButton:IsMouseOverEx()
	and self.characterID and C_CharacterServices.CanBoostCharacterGear(self.characterID)
	then
		if C_CharacterServices.IsBoostClassSpecItemsLoaded(self.classID) then
			local playerItemLevel = C_CharacterList.GetCharacterItemLevel(self.characterID)
			local pveGearAvgItemLevel, pvpGearAvgItemLevel = C_CharacterServices.GetBoostClassMaxAvgItemLevel(self.classID)
			self.buttonText.GearBoost:SetShown(playerItemLevel < math.floor(pveGearAvgItemLevel))
		else
			self.buttonText.GearBoost:Hide()
			C_CharacterServices.RequestSpecItems(self.classID)
		end
	else
		self.buttonText.GearBoost:Hide()
	end
end

function CharacterSelectButtonMixin:CanDragButton()
	if not C_CharacterList.IsInPlayableMode()
	or CharacterServiceBoostFlowFrame:IsShown()
	or CharacterServiceGearBoostFlowFrame:IsShown()
	or CharacterSelect.lockCharacterMove
	then
		return false
	end
	return true
end

function CharacterSelectButtonMixin:OnShow()
	SetParentFrameLevel(self.PortraitFrame.MailIcon, 1)
end

function CharacterSelectButtonMixin:OnHide()
	self:ClearCharacterInfo()
end

function CharacterSelectButtonMixin:OnEnable()
	self.PortraitFrame.Icon:SetVertexColor(1, 1, 1)
	self.PortraitFrame.LevelFrame.Level:SetTextColor(1, 1, 1)
	self.PortraitFrame.MailIcon:Enable()
	self.buttonText.HardcoreIcon:Enable()
	self.buttonText.CategoryIcon:Enable()
	self.buttonText.GearBoost:Enable()

	self:UpdateNameColor()
	self.buttonText.Location:SetTextColor(0.5, 0.5, 0.5)

	self.PAIDButton:Enable()
	self.PortraitFrame:Enable()
end

function CharacterSelectButtonMixin:OnDisable()
	self:HideMoveButtons()

	self.PortraitFrame.Icon:SetVertexColor(0.3, 0.3, 0.3)
	self.PortraitFrame.LevelFrame.Level:SetTextColor(0.3, 0.3, 0.3)
	self.PortraitFrame.MailIcon:Disable()
	self.buttonText.HardcoreIcon:Disable()
	self.buttonText.CategoryIcon:Disable()
	self.buttonText.GearBoost:Disable()

	self.buttonText.name:SetTextColor(0.3, 0.3, 0.3)
	self.buttonText.Location:SetTextColor(0.3, 0.3, 0.3)

	self.PAIDButton:Disable()
	self.PortraitFrame:Disable()
end

function CharacterSelectButtonMixin:OnMouseDown(button)
	if self:IsEnabled() ~= 1 or button == "RightButton" then
		return
	end

	if self:CanDragButton() then
		DRAG_HOLD_BUTTON = self
		DRAG_HOLD_BUTTON_TIME = 0
	end
end

function CharacterSelectButtonMixin:OnMouseUp(button)
	if self:IsEnabled() ~= 1 then
		return
	end
	if self:CanDragButton() then
		self:OnDragStop()
	end
end

function CharacterSelectButtonMixin:OnClick(button)
	if button == "RightButton" then
		if C_CharacterList.IsInPlayableMode() and not self:IsInBoostMode() then
			self:GetParent().DropDownMenu:Toggle(self, not self:GetParent().DropDownMenu:IsShown())
		end
	else
		self:GetParent().DropDownMenu:Hide()

		UpdateCharacterSelection()

		if CharacterServiceBoostFlowFrame:IsShown() then
			CharacterServiceBoostFlowFrame:SetCharacterID(self.characterID)
		end

		if CharacterServiceGearBoostFlowFrame:IsShown() then
			CharacterServiceGearBoostFlowFrame:SetCharacterID(self.characterID)
		end

		local characterIndex = self:GetIndex()
		if characterIndex ~= CharacterSelect.selectedIndex then
			CharacterSelect_SelectCharacter(characterIndex)
		end
	end
end

function CharacterSelectButtonMixin:OnDoubleClick(button)
	if button == "RightButton" then
		return
	end

	local characterIndex = self:GetIndex()
	if characterIndex ~= CharacterSelect.selectedIndex then
		CharacterSelect_SelectCharacter(characterIndex)
	end

	CharacterSelect_EnterWorld()
end

function CharacterSelectButtonMixin:OnEnter()
	if self.selection:IsShown() then
		self:ShowMoveButtons()
	end

	self:LockHighlight()

	if not DRAG_ACTIVE then
		self.buttonText.ItemLevel:Show()
		self.buttonText.Location:Hide()
		self:UpdateGearBoost()
	end
end

function CharacterSelectButtonMixin:OnLeave()
	for _, button in ipairs(self.serviceButtons) do
		if button:IsMouseOver() then
			return
		end
	end

	if self.MoveUp:IsShown() and not (self.MoveUp:IsMouseOverEx() or self.MoveDown:IsMouseOverEx()) then
		self:HideMoveButtons()
	end

	self:UnlockHighlight()
	self.buttonText.Location:Show()
	self.buttonText.ItemLevel:Hide()
	self:UpdateGearBoost()
end

function CharacterSelectButtonMixin:OnDragStart(button)
	if not self:CanDragButton() then
		return
	end

	if C_CharacterList.GetNumCharactersOnPage() > 1 then
		if not DRAG_ACTIVE then
			PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
			DRAG_ACTIVE = true
		end

		DRAG_HOLD_BUTTON = nil
		DRAG_BUTTON_INDEX = self:GetIndex()
		self:SetScript("OnUpdate", self.OnDragUpdate)
		for index = 1, C_CharacterList.GetNumCharactersPerPage() do
			local charButton = _G["CharSelectCharacterButton"..index]
			if charButton ~= self then
				charButton:SetAlpha(0.6)
			end
		end

		self.PortraitFrame:HideZodiacSign()
		self:HideMoveButtons()
		self:LockHighlight()
	end
end

function CharacterSelectButtonMixin:OnDragStop()
	if not self:CanDragButton() then
		return
	end

	if DRAG_ACTIVE then
		PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_OFF)
		DRAG_ACTIVE = false
	end

	DRAG_BUTTON_INDEX = nil
	DRAG_HOLD_BUTTON = nil

	self:OnLeave()
	self:SetScript("OnUpdate", nil)

	local stopIndex
	for index = 1, C_CharacterList.GetNumCharactersPerPage() do
		local button = _G["CharSelectCharacterButton"..index]
		button:SetAlpha(1)
		button:UnlockHighlight()
		button:UpdateMouseOver()

		if C_CharacterList.IsHardcoreCharacter(button.characterID) then
			button.buttonText.HardcoreIcon:SetPoint("TOPLEFT", DEFAULT_PRETEXT_ICON_OFFSET_X, DEFAULT_PRETEXT_ICON_OFFSET_Y)
		elseif C_CharacterList.GetCharacterCategorySpellID(button.characterID) then
			button.buttonText.CategoryIcon:SetPoint("TOPLEFT", DEFAULT_PRETEXT_ICON_OFFSET_X, DEFAULT_PRETEXT_ICON_OFFSET_Y)
		else
			button.buttonText.name:SetPoint("TOPLEFT", DEFAULT_TEXT_OFFSET_X, DEFAULT_TEXT_OFFSET_Y)
		end

		if button.selection:IsShown() or button:IsMouseOver() then
			stopIndex = button:GetIndex()
		end
	end

	if self:GetIndex() ~= stopIndex then
		CharacterSelect_SaveCharacterOrder()
	end
end

function CharacterSelectButtonMixin:OnDragUpdate(elapsed)
	if DRAG_ACTIVE then
		local draggedButton = _G["CharSelectCharacterButton"..DRAG_BUTTON_INDEX]
		local _, bottomOffset, _, buttonHeight = draggedButton:GetRect()

		local _, cursorY = GetScaledCursorPosition()
		if cursorY < bottomOffset then
			if DRAG_BUTTON_INDEX < C_CharacterList.GetNumCharactersOnPage() then
				local globalIndex = GetCharGlobalIndexFromIndex(DRAG_BUTTON_INDEX)
				MoveCharacter(globalIndex, globalIndex + 1, true)
			end
		elseif cursorY > bottomOffset + buttonHeight then
			if DRAG_BUTTON_INDEX > 1 then
				local globalIndex = GetCharGlobalIndexFromIndex(DRAG_BUTTON_INDEX)
				MoveCharacter(globalIndex, globalIndex - 1, true)
			end
		end
	else
		self:OnDragStop()
	end
end

function CharacterSelectButtonMixin:EnableDrag()
	self:SetScript("OnDragStart", self.OnDragStart)
	self:SetScript("OnDragStop", self.OnDragStop)
	self:SetScript("OnMouseUp", self.OnDragStop)
	self:SetScript("OnMouseDown", self.OnMouseDown)
end

function CharacterSelectButtonMixin:DisableDrag()
	self:SetScript("OnDragStart", nil)
	self:SetScript("OnDragStop", nil)
	self:SetScript("OnMouseUp", nil)
	self:SetScript("OnMouseDown", nil)
end

function CharacterSelectButtonMixin:ShowMoveButtons()
	if not C_CharacterList.IsInPlayableMode()
	or CharacterServiceBoostFlowFrame:IsShown()
	or CharacterServiceGearBoostFlowFrame:IsShown()
	then
		return
	end

	if not DRAG_ACTIVE and self.level then
		local characterIndex = self:GetIndex()
		local hasPendingBoost = C_CharacterList.HasPendingBoost(self.characterID)

		self.serviceButtons[1]:Show()
		self.serviceButtons[2]:SetShown(not hasPendingBoost)
		self.serviceButtons[3]:SetShown(C_CharacterServices.IsBoostAvailableForLevel(self.level) and not C_CharacterList.IsHardcoreCharacter(self.characterID))
		self.serviceButtons[3]:SetPoint("RIGHT", hasPendingBoost and self.serviceButtons[1] or self.serviceButtons[2], "LEFT", -4, 0)

		self.MoveUp:Show()
		self.MoveUp.NormalTexture:SetPoint("CENTER", 0, 0)
		self.MoveUp.HighlightTexture:SetPoint("CENTER", 0, 0)
		self.MoveDown:Show()
		self.MoveDown.NormalTexture:SetPoint("CENTER", 0, 0)
		self.MoveDown.HighlightTexture:SetPoint("CENTER", 0, 0)

		self.FactionEmblem:Hide()

		if characterIndex == 1
		and C_CharacterList.GetCurrentPageIndex() == 1
		then
			self.MoveUp:Disable()
			self.MoveUp:SetAlpha(0.35)
		else
			self.MoveUp:Enable()
			self.MoveUp:SetAlpha(1)
		end

		if characterIndex == C_CharacterList.GetNumCharactersOnPage()
		and (C_CharacterList.GetCurrentPageIndex() == C_CharacterList.GetNumAvailablePages() or C_CharacterList.GetCurrentPageIndex() == C_CharacterList.GetNumPages())
		then
			self.MoveDown:Disable()
			self.MoveDown:SetAlpha(0.35)
		else
			self.MoveDown:Enable()
			self.MoveDown:SetAlpha(1)
		end

		self.buttonText.ItemLevel:Show()
		self.buttonText.Location:Hide()
	end
end

function CharacterSelectButtonMixin:HideMoveButtons()
	self.MoveUp:Hide()
	self.MoveDown:Hide()
	self.FactionEmblem:Show()

	for _, serviceButton in ipairs(self.serviceButtons) do
		serviceButton:Hide()
	end

	self.buttonText.Location:Show()
	self.buttonText.ItemLevel:Hide()
end

function CharacterSelectButtonMixin:OnMoveUpClick(button)
	PlaySound("igMainMenuOptionCheckBoxOn")
	local index = GetCharGlobalIndexFromCharID(self.characterID)
	MoveCharacter(index, index - 1)
end

function CharacterSelectButtonMixin:OnMoveDownClick(button)
	PlaySound("igMainMenuOptionCheckBoxOn")
	local index = GetCharGlobalIndexFromCharID(self.characterID)
	MoveCharacter(index, index + 1)
end

function CharacterSelectButtonMixin:UpdateMouseOver()
	if self:IsEnabled() == 1 then
		self:UpdateGearBoost()

		if self.PortraitFrame:IsMouseOver() then
			self.PortraitFrame:OnEnter()
		else
			self.PortraitFrame:OnLeave()

			if self.buttonText.HardcoreIcon:IsShown() and self.buttonText.HardcoreIcon:IsMouseOver() then
				self:OnEnterHardcoreIcon(self.buttonText.HardcoreIcon)
			elseif self.buttonText.CategoryIcon:IsShown() and self.buttonText.CategoryIcon:IsMouseOver() then
				self:OnEnterCategoryIcon(self.buttonText.CategoryIcon)
			elseif self.buttonText.GearBoost:IsShown() and self.buttonText.GearBoost:IsMouseOver() then
				self:OnEnterGearBoost(self.buttonText.GearBoost)
			elseif self:IsMouseOver() then
				self:OnEnter()
			end
		end
	end
end

function CharacterSelectButtonMixin:OnEnterHardcoreIcon(this)
	self:OnEnter()
	GlueTooltip:SetOwner(this)
	GlueTooltip:AddLine(CHARACTER_INFO_HARDCORE_LABEL)
	GlueTooltip:Show()
end

function CharacterSelectButtonMixin:OnLeaveHardcoreIcon(this)
	self:OnLeave()
	GlueTooltip:Hide()
end

function CharacterSelectButtonMixin:OnEnterCategoryIcon(this)
	self:OnEnter()

	local categorySpellID = C_CharacterList.GetCharacterCategorySpellID(self.characterID)
	if categorySpellID then
		local categoryIndex, categoryLevel, name, icon = GetCharacterCategoryInfoBySpell(categorySpellID)
		if name then
			GlueTooltip:SetOwner(this)
			GlueTooltip:AddLine(name)
			GlueTooltip:Show()
		end
	end
end

function CharacterSelectButtonMixin:OnLeaveCategoryIcon(this)
	self:OnLeave()
	GlueTooltip:Hide()
end

function CharacterSelectButtonMixin:OnEnterGearBoost(this)
	if not DRAG_ACTIVE then
		self:OnEnter()

		local characterItemLevel = C_CharacterList.GetCharacterItemLevel(self.characterID)
		local pveGearAvgItemLevel, pvpGearAvgItemLevel = C_CharacterServices.GetBoostClassMaxAvgItemLevel(self.classID)

		GlueTooltip:SetOwner(self)
		GlueTooltip:ClearAllPoints()
		GlueTooltip:SetPoint("RIGHT", self, "LEFT", -5, 0)
		GlueTooltip:AddLine(RPE_TOOLTIP_LINE1)
		GlueTooltip:AddLine(string.format(RPE_TOOLTIP_LINE2, GetItemLevelColor(characterItemLevel):GenerateHexColor(), characterItemLevel), 1, 1, 1)
		GlueTooltip:AddLine(string.format(RPE_TOOLTIP_LINE3, GetItemLevelColor(pveGearAvgItemLevel):GenerateHexColor(), pveGearAvgItemLevel), 1, 1, 1)
		GlueTooltip:AddLine(string.format(RPE_TOOLTIP_LINE4, GetItemLevelColor(pvpGearAvgItemLevel):GenerateHexColor(), pvpGearAvgItemLevel), 1, 1, 1)
		GlueTooltip:Show()
	end
end

function CharacterSelectButtonMixin:OnLeaveGearBoost(this)
	self:OnLeave()
	GlueTooltip:Hide()
end

function CharacterSelectButtonMixin:SetBoostMode(inBoostMode, isSelectable)
	if self.characterID then
		C_CharacterList.SetCharacterInBoostMode(self.characterID, inBoostMode, isSelectable)
	end
end

function CharacterSelectButtonMixin:UpdateBoostMode()
	local inBoostMode, isSelecteble = C_CharacterList.IsCharacterInBoostMode(self.characterID)

	if inBoostMode then
		self.selection:Hide()
	end

	self.PAIDButton:UpdateState()
	self.PortraitFrame.MailIcon:SetEnabled(not inBoostMode)

	self.Arrow:SetShown(inBoostMode and isSelecteble)

	self.inBoostMode = inBoostMode
end

function CharacterSelectButtonMixin:IsInBoostMode()
	return self.inBoostMode
end

function CharacterSelectButtonMixin:UpdateCharData()
	self.PortraitFrame.MailIcon:SetShown(C_CharacterList.GetCharacterMailCount(self.characterID) > 0)

	local isHardcoreCharacter = C_CharacterList.IsHardcoreCharacter(self.characterID)
	local categorySpellID = C_CharacterList.GetCharacterCategorySpellID(self.characterID)

	self.buttonText.name:ClearAllPoints()

	if isHardcoreCharacter then
		self.buttonText.name:SetPoint("LEFT", self.buttonText.HardcoreIcon, "RIGHT", -2, -1)
	elseif categorySpellID then
		self.buttonText.name:SetPoint("LEFT", self.buttonText.CategoryIcon, "RIGHT", 2, -1)
	else
		self.buttonText.name:SetPoint("TOPLEFT", DEFAULT_TEXT_OFFSET_X, DEFAULT_TEXT_OFFSET_Y)
	end

	self.buttonText.HardcoreIcon:SetShown(isHardcoreCharacter)
	self.buttonText.CategoryIcon:SetShown(categorySpellID)

	if categorySpellID then
		local categoryIndex, categoryLevel, name, icon = GetCharacterCategoryInfoBySpell(categorySpellID)
		self.buttonText.CategoryIcon.Icon:SetTexture(icon)
	end

	local itemLevel = C_CharacterList.GetCharacterItemLevel(self.characterID)
	self.buttonText.ItemLevel:SetFormattedText("%s |c%s%i|r", CHARACTER_ITEM_LEVEL, GetItemLevelColor(itemLevel):GenerateHexColor(), itemLevel)

	self:UpdatePaidServiceID()

	local zodiacSignRaceID = C_CharacterList.GetCharacterZodiacRaceID(self.characterID)
	if zodiacSignRaceID and zodiacSignRaceID ~= 0 then
		local zodiacRaceID, name, description, icon, atlas = C_ZodiacSign.GetZodiacSignInfo(zodiacSignRaceID)
		self.PortraitFrame.ZodiacSign.name = name
		self.PortraitFrame.ZodiacSign:SetAtlas(atlas)
	else
		self.PortraitFrame.ZodiacSign.name = nil
		self.PortraitFrame:HideZodiacSign()
	end

	if not DRAG_ACTIVE then
		local isMouseOver = self:IsMouseOverEx()
		self.buttonText.Location:SetShown(not isMouseOver)
		self.buttonText.ItemLevel:SetShown(isMouseOver)
	end
end

function CharacterSelectButtonMixin:UpdateFaction()
	if not self.race then
		return
	end

	local factionID, factionGroup, originalFactionID, originalFactionGroup = C_CharacterList.GetCharacterFaction(self.characterID)
	if not factionID then
		return
	end

	local factionColor = PLAYER_FACTION_COLORS[factionID]
	local raceID, raceFile, raceLocMale, raceLocFemale = C_CreatureInfo.GetRaceInfoEx(self.race)

	self.PortraitFrame.Border:SetVertexColor(factionColor:GetRGB())
	self.PortraitFrame.FactionBorder:SetVertexColor(factionColor:GetRGB())
	self.PortraitFrame.LevelFrame.Border:SetVertexColor(factionColor:GetRGB())
	self.selection:SetVertexColor(factionColor:GetRGB())
	self.PAIDButton:SetColor(factionColor:GetRGB())

	local raceAtlas = string.format("RACE_ICON_ROUND_%s_%s_%s", string.upper(raceFile), E_SEX[self.sex or 0], string.upper(factionGroup))
	self.PortraitFrame.Icon:SetAtlas(C_Texture.HasAtlasInfo(raceAtlas) and raceAtlas or "RACE_ICON_ROUND_HUMAN_MALE_HORDE")

	if factionID == PLAYER_FACTION_GROUP.Horde then
		self.PortraitFrame.Icon:SetSubTexCoord(1.0, 0.0, 0.0, 1.0)
	end

	local atlasTag

	if factionGroup ~= "Neutral" then
		atlasTag = factionGroup
	elseif raceID == E_CHARACTER_RACES.RACE_VULPERA_NEUTRAL then
		atlasTag = "Vulpera"
	elseif raceID == E_CHARACTER_RACES.RACE_PANDAREN_NEUTRAL then
		atlasTag = "Pandaren"
	elseif raceID == E_CHARACTER_RACES.RACE_DRACTHYR then
		atlasTag = "Dracthyr"
	end

	if atlasTag then
		self.FactionEmblem:SetAtlas(string.format("CharacterSelect-FactionIcon-%s", atlasTag))
		self.FactionEmblem:Show()
	else
		self.FactionEmblem:Hide()
	end
end

function CharacterSelectButtonMixin:UpdatePaidServiceID()
	if C_CharacterList.IsInPlayableMode() then
		local customizations = C_CharacterList.GetCharacterCustomizationList(self.characterID)
		if #customizations > 0 then
			self.PAIDButton:SetPaidServiceID(self.characterID, customizations[#customizations])
			self.PAIDButton.Icon:SetSize(30, 30)
			self.PAIDButton.Icon:SetAtlas("Glue-VAS-Selector")
		else
			self.PAIDButton:Hide()
		end
	else
		self.PAIDButton:SetPaidServiceID(self.characterID, E_PAID_SERVICE.RESTORE)
	end
end

function CharacterSelectButtonMixin:OnPAIDButtonClick(button)
	if self.PAIDButton:GetPaidServiceID() == E_PAID_SERVICE.RESTORE then
		self.PAIDButton:OnClick(button)
	elseif self.characterID ~= C_CharacterList.GetSelectedCharacter() then
		self:OnClick(button)
		self:OnPAIDButtonEnter()
		CharacterSelectUI.PaidServiceSelection:PlayHighlightAnim()
	end
end

function CharacterSelectButtonMixin:OnPAIDButtonEnter()
	if self.PAIDButton:GetPaidServiceID() == E_PAID_SERVICE.RESTORE then
		CharacterSelectPAIDButtonMixin.OnEnter(self.PAIDButton)
		self:OnLeave()
	else
		local tooltipText, isEnabled
		if self.PAIDButton:IsEnabled() == 1 then
			tooltipText = CHARACTER_SERVICES_AVAILABLE
			isEnabled = true
		else
			tooltipText = self.PAIDButton.disabledReason
		end

		if tooltipText then
			self:OnLeave()

			GlueTooltip:SetOwner(self, self.tooltipAnchor or "ANCHOR_LEFT", self.tooltipOffsetX or 7, self.tooltipOffsetY or -7)
			if isEnabled then
				GlueTooltip:SetText(tooltipText)
			else
				GlueTooltip:SetText(tooltipText, 1, 0, 0, 1, true)
			end
			GlueTooltip:Show()
		end
	end
end

function CharacterSelectButtonMixin:OnPAIDButtonLeave()
	CharacterSelectPAIDButtonMixin.OnLeave(self.PAIDButton)
	if self:IsEnabled() == 1 then
		self:UpdateMouseOver()
	end
end

CharacterSelectButtonPortraitMixin = {}

function CharacterSelectButtonPortraitMixin:OnLoad()
	self:RegisterForClicks("LeftButtonUp", "RightButtonUp")
	self:RegisterForDrag("LeftButton")
end

function CharacterSelectButtonPortraitMixin:OnDisable()
	self:HideZodiacSign()
end

function CharacterSelectButtonPortraitMixin:OnEnter()
	if not DRAG_ACTIVE then
		self:GetParent():OnEnter()

		if self.ZodiacSign.name then
			self.Icon:Hide()
			self.ZodiacBackground:Show()
			self.ZodiacSign:Show()

			GlueTooltip:SetOwner(self, "ANCHOR_LEFT")
			GlueTooltip:AddLine(self.ZodiacSign.name)
			GlueTooltip:Show()
		end
	end
end

function CharacterSelectButtonPortraitMixin:OnLeave()
	self:GetParent():OnLeave()
	GlueTooltip:Hide()
	self.Icon:Show()
	self.ZodiacBackground:Hide()
	self.ZodiacSign:Hide()
end

function CharacterSelectButtonPortraitMixin:HideZodiacSign()
	if self:IsMouseOver() then
		GlueTooltip:Hide()
		self.Icon:Show()
		self.ZodiacBackground:Hide()
		self.ZodiacSign:Hide()
	end
end

CharacterSelectButtonMailMixin = {}

function CharacterSelectButtonMailMixin:OnLoad()
	self.Icon:SetAtlas("GlueDark-Icon-Mail")
	self.charButton = self:GetParent():GetParent()
end

function CharacterSelectButtonMailMixin:OnEnter()
	self.charButton:OnEnter()

	GlueTooltip:SetOwner(self)
	GlueTooltip:SetText(string.format(UNREAD_MAILS, C_CharacterList.GetCharacterMailCount(self.charButton.characterID)))
	GlueTooltip:Show()
end

function CharacterSelectButtonMailMixin:OnLeave()
	GlueTooltip:Hide()
	self.charButton:OnLeave()
end

function CharacterSelectButtonMailMixin:OnEnable()
	self.Icon:SetVertexColor(1, 1, 1)
end

function CharacterSelectButtonMailMixin:OnDisable()
	self.Icon:SetVertexColor(0.5, 0.5, 0.5)
end

CharacterSelectButtonDropDownMenuMixin = {}

function CharacterSelectButtonDropDownMenuMixin:OnLoad()
	self.buttonSettings = {
		{
			atlas = "GlueDark-Button-Service-Fix-Normal",
			text = CHARACTER_SELECT_FIX_CHARACTER_BUTTON,
			func = function(this, owner)
				CharacterFixDialog:ShowDialog(owner.characterID)
			end
		},
		{
			atlas = "GlueDark-Button-Service-Delete-Normal",
			text = DELETE_CHARACTER,
			func = function(this, owner)
				CharacterDeleteDialog:ShowDialog(owner.characterID)
			end
		},
		{
			atlas = "GlueDark-Button-Service-Boost-Normal",
			text = CHARACTER_SERVICES_BOOST,
			func = function(this, owner)
				CharacterSelect_OpenBoost(owner.characterID)
			end
		},
	}

	self.buttonsPool = CreateFramePool("Button", self, "CharacterSelectButtonDropDownMenuButtonTemplate")
end

function CharacterSelectButtonDropDownMenuMixin:Toggle( owner, show )
	if self.owner ~= owner then
		self.owner = owner
		show = true
	end

	if show then
		self:UpdateButtons()
		self:ClearAllPoints()

		if owner.index == C_CharacterList.GetNumCharactersPerPage() then
			self:SetPoint("BOTTOMRIGHT", owner, "BOTTOMLEFT", -10, 0)
		else
			self:SetPoint("RIGHT", owner, "LEFT", -10, 0)
		end
	end

	self:SetShown(show)
end

function CharacterSelectButtonDropDownMenuMixin:UpdateButtons()
	local BUTTON_HEIGHT = 30
	local BUTTON_OFFSET_Y = -6

	local previous

	self.buttonsPool:ReleaseAll()

	for index, settings in ipairs(self.buttonSettings) do
		local skipOption
		if (index == 1 and C_CharacterList.HasPendingBoost(self.owner.characterID))
		or (index == 3 and not (self.owner.level and C_CharacterServices.IsBoostAvailableForLevel(self.owner.level) and not C_CharacterList.IsHardcoreCharacter(self.owner.characterID)))
		then
			skipOption = true
		end

		if not skipOption then
			local button = self.buttonsPool:Acquire()

			if not previous then
				button:SetPoint("TOP", 0, 0)
			else
				button:SetPoint("TOP", previous, "BOTTOM", 0, BUTTON_OFFSET_Y)
			end

			button.Text:SetText(settings.text)
			button.Icon:SetAtlas(settings.atlas)
			button.clickFunc = settings.func
			button:Show()

			previous = button
		end
	end

	local numButtons = self.buttonsPool:GetNumActive()
	self:SetHeight(numButtons * BUTTON_HEIGHT + (numButtons - 1) * -BUTTON_OFFSET_Y)
end

CharacterSelectButtonDropDownMenuButtonMixin = {}

function CharacterSelectButtonDropDownMenuButtonMixin:OnLoad()
	self.NormalTexture:SetAtlas("UI-Frame-jailerstower-PendingButton")
	self.HighlightTexture:SetAtlas("UI-Frame-jailerstower-PendingButtonHighlight")
end

function CharacterSelectButtonDropDownMenuButtonMixin:OnClick()
	if self.clickFunc then
		self.clickFunc(self, self:GetParent().owner)
	end

	self:GetParent():Hide()
end

CharacterSelectServiceButtonMixin = {}

function CharacterSelectServiceButtonMixin:OnLoad()
	self.normalTextureAtlas = self:GetAttribute("normalTextureAtlas")
	self.pushedTextureAtlas = self:GetAttribute("pushedTextureAtlas")
	self.highlightTextureAtlas = self:GetAttribute("highlightTextureAtlas")

	self.NormalTexture:SetAtlas(self.normalTextureAtlas)
	self.PushedTexture:SetAtlas(self.pushedTextureAtlas)
	self.HighlightTexture:SetAtlas(self.highlightTextureAtlas)

	self:SetParentArray("serviceButtons")
end

function CharacterSelectServiceButtonMixin:OnClick()
	local parent = self:GetParent()
	local actionID = self:GetID()
	if actionID == 1 then
		CharacterFixDialog:ShowDialog(parent.characterID)
	elseif actionID == 2 then
		CharacterDeleteDialog:ShowDialog(parent.characterID)
	elseif actionID == 3 then
		CharacterSelect_OpenBoost(parent.characterID)
	end

	parent:HideMoveButtons()
	parent.buttonText.Location:Show()
	parent.buttonText.ItemLevel:Hide()
end

function CharacterSelectServiceButtonMixin:OnShow()
	CharacterSelect.serviceButtonDelay = SERVICE_BUTTON_ACTIVATION_DELAY
	self:EnableMouse(false)
end

function CharacterSelectServiceButtonMixin:OnHide()
	CharacterSelect.serviceButtonDelay = nil
end

CharSelectPageShadowButtonTemplateMixin = {}

function CharSelectPageShadowButtonTemplateMixin:OnLoad()
	self.normalTextureH = self:GetAttribute("normalTextureSizeH")
	self.normalTextureW = self:GetAttribute("normalTextureSizeW")
	self.pushedTextureAtlas = self:GetAttribute("pushedTextureAtlas")

	self.PushedTexture:SetAtlas(self.pushedTextureAtlas)
	self.PushedTexture:SetSize(self.normalTextureH, self.normalTextureW)
end

CharacterBoostInfoMixin = {}

function CharacterBoostInfoMixin:OnLoad()
	self.Background:SetVertexColor(0.5, 0.5, 0.5)
end

function CharacterBoostInfoMixin:OnShow()
	C_CharacterServices.CheckBoostServiceItemStage()
end

CharacterGearBoostButtonMixin = CreateFromMixins(PKBT_ButtonMixin)

function CharacterGearBoostButtonMixin:OnLoad()
	PKBT_ButtonMixin.OnLoad(self)

	local scale = 0.8

	self.Icon:SetAtlas("GlueDark-Icon-Armor-Gold", true)
	self.CircleBorder.Border:SetAtlas("GlueDark-Ring-Silver", true)
	self.CircleBorder.Glow:SetAtlas("GlueDark-Ring-Glow", true)

	self.Icon:SetSize(self.Icon:GetWidth() * scale, self.Icon:GetHeight() * scale)
	self.CircleBorder.Border:SetSize(self.CircleBorder.Border:GetWidth() * scale, self.CircleBorder.Border:GetHeight() * scale)
	self.CircleBorder.Glow:SetSize(self.CircleBorder.Glow:GetWidth() * scale, self.CircleBorder.Glow:GetHeight() * scale)

	self.Icon:SetPoint("CENTER", self.CircleBorder, "CENTER", 0, -4)
end

function CharacterGearBoostButtonMixin:OnShow()
	SetParentFrameLevel(self, 2)
	SetParentFrameLevel(self.Glow, -2)
	SetParentFrameLevel(self.CircleBorder, -1)

	if not self.Glow.AlphaAnim:IsPlaying() then
		self.Glow.AlphaAnim:Play()
	end
	if not self.CircleBorder.Glow.AlphaAnim:IsPlaying() then
		self.CircleBorder.Glow.AlphaAnim:Play()
	end
end

function CharacterGearBoostButtonMixin:OnHide()
	if self.Glow.AlphaAnim:IsPlaying() then
		self.Glow.AlphaAnim:Stop()
	end
	if self.CircleBorder.Glow.AlphaAnim:IsPlaying() then
		self.CircleBorder.Glow.AlphaAnim:Stop()
	end
end

function CharacterGearBoostButtonMixin:OnClick(button)
	CharacterSelect_OpenGearBoost()
end

CharacterPaidServiceSelectionMixin = CreateFromMixins(GlueEasingAnimMixin)

function CharacterPaidServiceSelectionMixin:OnLoad()
	self.buttonList = {}
	self.OFFSET_X = 20
	self.duration = 0.500

	self:RegisterCustomEvent("CUSTOM_CHARACTER_INFO_UPDATE")
	self:RegisterCustomEvent("CHARACTER_LIST_BOOST_MODE_CHANGED")
end

function CharacterPaidServiceSelectionMixin:OnEvent(event, ...)
	if event == "CUSTOM_CHARACTER_INFO_UPDATE"
	or event == "CHARACTER_LIST_BOOST_MODE_CHANGED"
	then
		if not self:IsShown() then
			return
		end

		local characterID = ...
		if characterID == C_CharacterList.GetSelectedCharacter() then
			if event == "CUSTOM_CHARACTER_INFO_UPDATE" then
				self:UpdateState()
			elseif event == "CHARACTER_LIST_BOOST_MODE_CHANGED" then
				for index, button in ipairs(self.buttonList) do
					if button:IsShown() and button:GetPaidServiceID() ~= E_PAID_SERVICE.NONE then
						button:UpdateState()
					end
				end
			end
		end
	end
end

function CharacterPaidServiceSelectionMixin:UpdateState()
	local characterID = C_CharacterList.GetSelectedCharacter()
	if not C_CharacterList.GetCharacterInfo(characterID) then
		self:Hide()
		return
	end

	local customizations = C_CharacterList.GetCharacterCustomizationList(characterID)

	local numCustomizations = #customizations
	if numCustomizations == 0 then
		self:Hide()
		return
	end

--[[
	local factionID, factionGroup, originalFactionID, originalFactionGroup = C_CharacterList.GetCharacterFaction(characterID)
	local factionColor = PLAYER_FACTION_COLORS[factionID]

	self.BackgroundHighlight:SetVertexColor(factionColor:GetRGB())
--]]

	for index, paidServiceID in ipairs(customizations) do
		local button = self.buttonList[index]
		if not button then
			button = CreateFrame("Button", string.format("$parentPaidButton%i", index), self, "CharacterPaidServiceButtonTemplate")

			if index == 1 then
				button:SetPoint("LEFT", self, "LEFT", 0, 0)
			else
				button:SetPoint("LEFT", self.buttonList[index - 1], "RIGHT", self.OFFSET_X, 0)
			end

			button.tooltipAnchor = "ANCHOR_TOP"
			button.tooltipOffsetX = 0
			button.tooltipOffsetY = 7

			self.buttonList[index] = button
		end

		if index > 1 and numCustomizations > 2 then
			if index == 2 or (index == 3 and numCustomizations == 5) then
				button:SetPoint("LEFT", self.buttonList[index - 1], "RIGHT", self.OFFSET_X, -3)
				button.tooltipOffsetY = 10
			elseif index == numCustomizations or (index == 4 and numCustomizations == 5) then
				button:SetPoint("LEFT", self.buttonList[index - 1], "RIGHT", self.OFFSET_X, 3)
				button.tooltipOffsetY = 7
			else
				button:SetPoint("LEFT", self.buttonList[index - 1], "RIGHT", self.OFFSET_X, 0)
				button.tooltipOffsetY = 10
			end
		end

		button:SetPaidServiceID(characterID, paidServiceID)
	--	button:SetColor(factionColor:GetRGB())
	end

	for i = numCustomizations + 1, #self.buttonList do
		self.buttonList[i]:Hide()
	end

	self:SetSize(numCustomizations * self.buttonList[1]:GetWidth() + (numCustomizations - 1) * self.OFFSET_X, self.buttonList[1]:GetHeight())
	self:Show()

	if not self:IsAnimPlaying() and self:GetAlpha() ~= 1 then
		self:SetAlpha(1)
	end

	local tooltipOwner = GlueTooltip:GetOwner()
	if tooltipOwner then
		for index, button in ipairs(self.buttonList) do
			if button:IsMouseOverEx() then
				button:OnEnter()
			end
		end
	end
end

function CharacterPaidServiceSelectionMixin:PlayHighlightAnim()
	self.BackgroundHighlight.AnimPulse:Restart()
end

function CharacterPaidServiceSelectionMixin:SetPosition(easing, progress)
	if progress then
		self:SetAlpha(self.isRevers and (1 - progress) or progress)
	else
		self:SetAlpha(self.isRevers and 0 or 1)
	end
end

CharacterActionDialogMixin = {}

function CharacterActionDialogMixin:OnLoad()
	self.TopShadow:SetVertexColor(0, 0, 0, 0.4)
	self.dirty = true
end

function CharacterActionDialogMixin:OnShow()
	GlueParent_AddModalFrame(self)
	self:CheckConfirmation()

	if type(self.OnShowCallback) == "function" then
		pcall(self.OnShowCallback, self)
	end
end

function CharacterActionDialogMixin:OnHide()
	GlueParent_RemoveModalFrame(self)
	self.characterID = nil
	self.EditBox:SetText("")
end

function CharacterActionDialogMixin:OnKeyDown(key)
	if key == "ESCAPE" then
		self:Hide()
	elseif key == "PRINTSCREEN" then
		Screenshot()
	elseif key == "ENTER" then
		if self.AcceptButton:IsEnabled() == 1 then
			self:Accept()
		end
	end
end

function CharacterActionDialogMixin:OnEditBoxTextChanged(this, userInput)
	self:CheckConfirmation()
end

function CharacterActionDialogMixin:OnEditBoxEnterPressed(this)
	if self.AcceptButton:IsEnabled() == 1 then
		self:Accept()
	end
end

function CharacterActionDialogMixin:OnEditBoxEscapePressed(this)
	self:Cancel()
end

function CharacterActionDialogMixin:CheckConfirmation()
	if self.confirmationText then
		self.AcceptButton:SetEnabled(string.upper(self.EditBox:GetText()) == self.confirmationText)
	else
		self.AcceptButton:Enable()
	end
end

function CharacterActionDialogMixin:GetAttributeGlobalString(attribute, fallback)
	local str = self:GetAttribute(attribute)
	if not str or str == "" then
		return fallback or ""
	end
	return _G[str] or fallback or ""
end

function CharacterActionDialogMixin:UpdateContainer()
	local title = self:GetAttributeGlobalString("Title")
	if title ~= "" then
		self.Title:SetText(title)
		self.Title:Show()
		self.Separator:Show()
	else
		self.Title:Hide()
		self.Separator:Hide()
	end

	local description = self:GetAttributeGlobalString("Description")
	if description ~= "" then
		self.Description:SetText(description)
		self.Description:Show()
	else
		self.Description:Hide()
	end

	local warning = self:GetAttributeGlobalString("Warning")
	if warning ~= "" then
		self.Warning:SetText(warning)
		self.Warning:Show()
	else
		self.Warning:Hide()
	end

	if self:GetAttribute("ShowEditBox") then
		local confirmationText = self:GetAttributeGlobalString("EditBoxConfirmation")
		if confirmationText ~= "" then
			self.confirmationText = string.upper(confirmationText)
		else
			self.confirmationText = nil
		end

		local instruction = self:GetAttributeGlobalString("EditBoxInstruction")
		if instruction ~= "" then
			self.EditBox.Instruction:SetText(instruction)
			self.EditBox.Instruction:Show()
		else
			self.EditBox.Instruction:Hide()
		end

		self.EditBox:SetWidth(self:GetAttribute("EditBoxWidth") or 180)
		self.EditBox:Show()
	else
		self.confirmationText = nil
		self.EditBox:Hide()
	end

	local infoHeader = self:GetAttributeGlobalString("InfoHeader")
	local infoText = self:GetAttributeGlobalString("InfoText")
	if infoHeader ~= "" and infoText ~= "" then
		self.InfoIcon.InfoHeader = infoHeader
		self.InfoIcon.InfoText = infoText
		self.InfoIcon:Show()
	else
		self.InfoIcon.InfoHeader = nil
		self.InfoIcon.InfoText = nil
		self.InfoIcon:Hide()
	end

	self.AlertIcon:SetShown(self:GetAttribute("AlertIcon"))
	self.AcceptButton:SetText(self:GetAttributeGlobalString("AcceptText", OKAY))
	self.CancelButton:SetText(self:GetAttributeGlobalString("CancelText", CANCEL))

	self.showCharInfo = self:GetAttribute("ShowCharInfo")
end

function CharacterActionDialogMixin:UpdateRect()
	do -- update dialog width
		local width = self:GetWidth()
		self.Title:SetWidth(width - 10)
		self.CharacterInfo:SetWidth(width - 10)
		self.Description:SetWidth(width - 40)
		self.Warning:SetWidth(width - 75)
	end

	local height = 50
	local offsetY = 16
	local lastObject = self
	local relativePoint = "TOP"

	if self.Title:IsShown() then
		height = height + self.Title:GetHeight() + 16

		if self.Separator:IsShown() then
			height = height + self.Separator:GetHeight() + 11
			offsetY = 10
			lastObject = self.Separator
		else
			offsetY = 3
			lastObject = self.Title
		end
		relativePoint = "BOTTOM"
	end

	if self.CharacterInfo:IsShown() then
		self.CharacterInfo:SetPoint("TOP", lastObject, relativePoint, 0, -offsetY)
		height = height + self.CharacterInfo:GetHeight() + offsetY
		offsetY = 7
		lastObject = self.CharacterInfo
		relativePoint = "BOTTOM"
	end

	if self.Description:IsShown() then
		self.Description:SetPoint("TOP", lastObject, relativePoint, 0, -offsetY)
		height = height + self.Description:GetHeight() + offsetY
		offsetY = 7
		lastObject = self.Description
		relativePoint = "BOTTOM"
	end

	if self.Warning:IsShown() then
		offsetY = offsetY + 5
		self.Warning:SetPoint("TOP", lastObject, relativePoint, 0, -offsetY)
		height = height + self.Warning:GetHeight() + offsetY
		offsetY = 10
		lastObject = self.Warning
		relativePoint = "BOTTOM"
	end

	if self.EditBox:IsShown() then
		if self.EditBox.Instruction:IsShown() then
			offsetY = offsetY + self.EditBox.Instruction:GetHeight() + 10
		end

		self.EditBox:SetPoint("TOP", lastObject, relativePoint, 0, -offsetY)
		height = height + self.EditBox:GetHeight() + offsetY
		offsetY = 10
		lastObject = self.EditBox
		relativePoint = "BOTTOM"
	end

	self:SetHeight(height + offsetY)
end

function CharacterActionDialogMixin:UpdateCharacterInfo()
	if self.showCharInfo then
		local name, _, class, level = C_CharacterList.GetCharacterInfo(self.characterID)
		local classID, classFile, classFlag, classLocMale, classLocFemale = C_CreatureInfo.GetClassInfoEx(class)
		class = GetClassColorObj(classFile):WrapTextInColorCode(class)
		self.CharacterInfo:SetFormattedText(CONFIRM_CHAR_DELETE2, name, level, class)
		self.CharacterInfo:Show()
	else
		self.CharacterInfo:Hide()
	end
end

function CharacterActionDialogMixin:ShowDialog(characterID, usePredefinedCharacterID)
	if not usePredefinedCharacterID then
		self:SetCharacterID(characterID)
	end

	if self:CanShow() then
		if self.dirty then
			self:UpdateContainer()
			self.dirty = nil
		end

		self:UpdateCharacterInfo()
		self:UpdateRect()
		self:Show()
	end
end

function CharacterActionDialogMixin:CanShow()
	return self.characterID ~= nil
end

function CharacterActionDialogMixin:SetCharacterID(characterID)
	if not characterID then
		characterID = C_CharacterList.GetSelectedCharacter()
	end

	if characterID == 0 then
		error(string.format("Incorrect characterID [%s]", characterID), 2)
	end
	self.characterID = characterID
end

function CharacterActionDialogMixin:Accept()
	local success = true

	if type(self.OnAccept) == "function" then
		success = self:OnAccept()
	end

	if success then
		self:Hide()
	end
end

function CharacterActionDialogMixin:Cancel()
	self:Hide()
	if type(self.OnCancel) == "function" then
		self:OnCancel()
	end
end

CharacterDeleteDialogMixin = CreateFromMixins(CharacterActionDialogMixin)

function CharacterDeleteDialogMixin:CanShow()
	if not self.characterID then
		return false
	end

	local guid, raceID, classID, level, zoneID, sexID, customizationFlags, displayIDs = C_CharacterList.GetCharacterInfoEx(self.characterID)
	if classID == CLASS_ID_DEATHKNIGHT then
		if C_CharacterList.GetPendingBoostDK() and not C_CharacterList.HasPendingBoost(self.characterID) then
			GlueDialog:ShowDialog("OKAY_VOID", CHARACTER_DELETE_BLOCKED_BOOST_DEATH_KNIGHT)
			return false
		end
	end

	return true
end

function CharacterDeleteDialogMixin:OnAccept()
	if self.characterID then
		C_CharacterList.DeleteCharacter(self.characterID)
		return true
	end
end

CharacterRenameDialogMixin = CreateFromMixins(CharacterActionDialogMixin)

function CharacterRenameDialogMixin:OnEditBoxTextChanged(this, userInput)
	local isValid = strlenutf8(this:GetText()) > 1
	self.AcceptButton:SetEnabled(isValid)
end

function CharacterRenameDialogMixin:SetTitleText(text)
	self.Title:SetText(text)
end

function CharacterRenameDialogMixin:OnAccept()
	if self.characterID then
		local result = C_CharacterList.RenameCharacter(self.characterID, string.trim(self.EditBox:GetText()))
		return result == 1
	end
end

CharacterFixDialogMixin = CreateFromMixins(CharacterActionDialogMixin)

function CharacterFixDialogMixin:CanShow()
	if not self.characterID then
		return false
	end

	if C_CharacterList.HasPendingBoost(self.characterID) then
		return false
	end

	return true
end

function CharacterFixDialogMixin:OnAccept()
	if self.characterID then
		C_CharacterList.FixCharacter(self.characterID)
		return true
	end
end

CharacterBoostCancelDialogMixin = CreateFromMixins(CharacterActionDialogMixin)

function CharacterBoostCancelDialogMixin:CanShow()
	if not self.characterID then
		return false
	end
	return C_CharacterList.HasBoostCancel(self.characterID)
end

function CharacterBoostCancelDialogMixin:OnAccept()
	if self.characterID then
		C_CharacterServices.CancelBoost(self.characterID)
		return true
	end
end

CharacterBoostRefundConfirmationDialogMixin = CreateFromMixins(CharacterActionDialogMixin)

function CharacterBoostRefundConfirmationDialogMixin:CanShow()
	return C_CharacterServices.IsBoostRefundAvailable()
end

function CharacterBoostRefundConfirmationDialogMixin:OnHide()
	CharacterActionDialogMixin.OnHide(self)
	self.parentDialog = nil
end

function CharacterBoostRefundConfirmationDialogMixin:SetCharacterID()
	self.characterID = nil
end

function CharacterBoostRefundConfirmationDialogMixin:SetParentDialog(parentDialog)
	self.parentDialog = parentDialog
end

function CharacterBoostRefundConfirmationDialogMixin:OnAccept()
	if self.parentDialog then
		self.parentDialog:Hide()
	end
	C_CharacterServices.RequestBoostRefund()
	return true
end