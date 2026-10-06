if GetUIEventTheme() == Enum.UIEventTheme.Winterveil then
	CurrentGlueMusic = "LoginScreenNewYear";
else
	CurrentGlueMusic = "SirusLoginScreenBackground";
end

GlueScreenInfo = { };
GlueScreenInfo["login"]			= "AccountLogin";
GlueScreenInfo["charselect"]	= "CharacterSelect";
GlueScreenInfo["realmwizard"]	= "RealmWizard";
GlueScreenInfo["charcreate"]	= "CharacterCreate";
GlueScreenInfo["patchdownload"]	= "PatchDownload";
GlueScreenInfo["trialconvert"]	= "TrialConvert";
GlueScreenInfo["movie"]			= "MovieFrame";
GlueScreenInfo["credits"]		= "CreditsFrame";
GlueScreenInfo["options"]		= "OptionsFrame";

CharModelFogInfo = { };
CharModelFogInfo["HUMAN"] = { r=0.8, g=0.65, b=0.73, far=222 };
CharModelFogInfo["QUELDO"] = { r=1, g=0.65, b=0.73, far=255 };
CharModelFogInfo["ORC"] = { r=0.5, g=0.5, b=0.5, far=270 };
CharModelFogInfo["DWARF"] = { r=0.85, g=0.88, b=1.0, far=500 };
CharModelFogInfo["NIGHTELF"] = { r=0.25, g=0.22, b=0.55, far=611 };
CharModelFogInfo["TAUREN"] = { r=1.0, g=0.61, b=0.42, far=153 };
CharModelFogInfo["SCOURGE"] = { r=0, g=0.22, b=0.22, far=26 };
CharModelFogInfo["CHARACTERSELECT"] = { r=0.8, g=0.65, b=0.73, far=222 };

CharModelGlowInfo = { };
CharModelGlowInfo["WORGEN"] = 0.2;
CharModelGlowInfo["GOBLIN"] = 0.2;
CharModelGlowInfo["HUMAN"] = 0.15;
CharModelGlowInfo["DWARF"] = 0.15;
CharModelGlowInfo["CHARACTERSELECT"] = 0.3;

GlueAmbienceTracks = { };
GlueAmbienceTracks["HUMAN"] = "GlueScreenHuman";
GlueAmbienceTracks["ORC"] = "GlueScreenOrc";
GlueAmbienceTracks["DWARF"] = "GlueScreenDwarf";
GlueAmbienceTracks["TAUREN"] = "GlueScreenTauren";
GlueAmbienceTracks["SCOURGE"] = "GlueScreenUndead";
GlueAmbienceTracks["NIGHTELF"] = "GlueScreenNightElf";
GlueAmbienceTracks["DRAENEI"] = "GlueScreenDraenei";
GlueAmbienceTracks["BLOODELF"] = "GlueScreenBloodElf";
GlueAmbienceTracks["DARKPORTAL"] = "GlueScreenIntro";
GlueAmbienceTracks["DEATHKNIGHT"] = "GlueScreenIntro";
GlueAmbienceTracks["CHARACTERSELECT"] = "GlueScreenIntro";
GlueAmbienceTracks["GOBLIN"] = "GlueScreenGoblin";
GlueAmbienceTracks["WORGEN"] = "GlueScreenWorgen";
GlueAmbienceTracks["NAGA"] = "GlueScreenNightElf";
GlueAmbienceTracks["PANDAREN"] = "GlueScreenHuman";
GlueAmbienceTracks["QUELDO"] = "GlueScreenBloodElf";
GlueAmbienceTracks["VRYKUL"] = "GlueScreenVrykul";
GlueAmbienceTracks["DEMONHUNTER"] = "GlueScreenIntro";


-- RaceLights[] duplicates the 3.2.2 color values in the models. Henceforth, the models no longer contain directional lights
RaceLights = {
	HUMAN = {
        -- {1, 0, -1, -4, 6, 0, 1, 1, 1, 10, 1, 1, 1},
        {1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.80000,    0.80000,    0.80000,    0.0,    0,    0,    0},
    },
	ORC = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	DWARF = {
		{1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.80000,    0.80000,    0.80000,    0.0,    0,    0,    0},
        {1,     0,  -0.88314,       0.42916,        -0.18945,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.44706,    0.67451,    0.760785},
    },
	TAUREN = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	SCOURGE = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	NIGHTELF = {
		{1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.80000,    0.80000,    0.80000,    0.0,    0,    0,    0},
        {1,     0,  -0.88314,       0.42916,        -0.18945,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.44706,    0.67451,    0.760785},
    },
	DRAENEI = {
		{1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.80000,    0.80000,    0.80000,    0.0,    0,    0,    0},
        {1,     0,  -0.88314,       0.42916,        -0.18945,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.44706,    0.67451,    0.760785},
    },
	BLOODELF = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	CHARACTERSELECT = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0.3,          0.1,          0.8},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	GOBLIN = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	WORGEN = {
		{1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.80000,    0.80000,    0.80000,    0.0,    0,    0,    0},
        {1,     0,  -0.88314,       0.42916,        -0.18945,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.44706,    0.67451,    0.760785},
    },
	NAGA = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	PANDAREN = {
		{1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
		{1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
		{1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
    },
	QUELDO = {
		{1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.80000,    0.80000,    0.80000,    0.0,    0,    0,    0},
        {1,     0,  -0.88314,       0.42916,        -0.18945,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.44706,    0.67451,    0.760785},
    },

 --    HUMAN =  {
 --       	{1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.80000,    0.80000,    0.80000,    0.0,    0,    0,    0},
 --        {1,     0,  -0.88314,       0.42916,        -0.18945,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.44706,    0.67451,    0.760785},

 --    },
 --    ORC = {
 --        {1,     0,  0.00000,        0.00000,        -1.00000,   1.0,    0.15000,    0.15000,    0.15000,    1.0,    0.00000,    0.00000,    0.00000},
 --        {1,     0,  -0.74919,       0.35208,        -0.56103,   1.0,    0.00000,    0.00000,    0.00000,    1.0,    0.44706,    0.54510,    0.73725},
 --        {1,     0,  0.53162,        -0.84340,       0.07780,    1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.55,       0.338625,   0.148825},
 --    },
 --    DWARF = {
 --        {1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.30000,    0.30000,    0.30000,    0.0,    0.00000,    0.00000,    0.00000},
 --        {1,     0,  -0.88314,       0.42916,        -0.18945,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.44706,    0.67451,    0.760785},
 --    },
 --    TAUREN = {
 --        {1,     0,  -0.48073,       0.71827,        -0.50297,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.65,       0.397645,   0.2727},
 --        {1,     0,  -0.49767,       -0.78677,       0.36513,    1.0,    0.00000,    0.00000,    0.00000,    1.0,    0.60000,    0.47059,    0.32471},
 --    },
 --    SCOURGE = {
 --       {1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
 --        {1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
 --        {1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
 --    },
 --    NIGHTELF = {
 --        {1,     0,  -0.00000,       -0.00000,       -1.00000,   1.0,    0.09020,    0.09020,    0.17020,    1.0,    0.00000,    0.00000,    0.00000},
 --    },
 --    DRAENEI = {
 --        {1,     0,  0.61185,        0.62942,        -0.47903,   1.0,    0.00000,    0.00000,    0.00000,    1.0,    0.56941,    0.52000,    0.60000},
 --        {1,     0,  -0.64345,       -0.31052,       -0.69968,   1.0,    0.00000,    0.00000,    0.00000,    1.0,    0.60941,    0.60392,    0.70000},
 --        {1,     0,  -0.46481,       -0.14320,       0.87376,    1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.5835,     0.48941,    0.60000},
 --    },
 --    BLOODELF = {
 --        {1,     0,  -0.82249,       -0.54912,       -0.14822,   1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.581175,   0.50588,    0.42588},
 --        {1,     0,  0.00000,        -0.00000,       -1.00000,   1.0,    0.60392,    0.61490,    0.70000,    1.0,    0.00000,    0.00000,    0.00000},
 --        {1,     0,  0.02575,        0.86518,        -0.50081,   1.0,    0.00000,    0.00000,    0.00000,    1.0,    0.59137,    0.51745,    0.63471},
 --    },
 --    DEATHKNIGHT = {
 --        {1,     0,  0.00000,        0.00000,        -1.00000,   1.0,    0.38824,    0.66353,    0.76941,    1.0,    0.00000,    0.00000,    0.00000},
 --    },
	-- -- DEMONHUNTER = {
 -- --        {1,     0,  0.000000,       0.000000,       -1.000000,   1.0,   0.27,       0.27,       .27,        1.0,    0,          0,          0},
 -- --        {1,     0,  -0.45756075,    -0.58900136,    -0.66611975, 1.0,   0.000000,   0.000000,   0.000000,   1.0,    0.19882353, 0.34921569, 0.43588236 },
 -- --        {1,     0,  -0.64623469,    0.57582057,     -0.50081086, 1.0,   0.000000,   0.000000,   0.000000,   2.0,    0.52196085, 0.44,       0.29764709 },
 -- --    },
 --    CHARACTERSELECT =  {
 --        {1,     0,  0.00000,        0.00000,        -1.00000,   1.0,    0.15000,    0.15000,    0.15000,    1.0,    0.00000,    0.00000,    0.00000},
 --        {1,     0,  -0.74919,       0.35208,        -0.56103,   1.0,    0.00000,    0.00000,    0.00000,    1.0,    0.44706,    0.54510,    0.73725},
 --        {1,     0,  0.53162,        -0.84340,       0.07780,    1.0,    0.00000,    0.00000,    0.00000,    2.0,    0.55,       0.338625,   0.148825},
 --    },
}

-- indicies for adding lights ModelFFX:Add*Light
LIGHT_LIVE  = 0;
LIGHT_GHOST = 1;

-- Alpha animation stuff
FADEFRAMES = {};
CURRENT_GLUE_SCREEN = nil;
PENDING_GLUE_SCREEN = nil;
-- Time in seconds to fade
LOGIN_FADE_IN = 1.5;
LOGIN_FADE_OUT = 0.5;
CHARACTER_SELECT_FADE_IN = 0.75;
RACE_SELECT_INFO_FADE_IN = .5;
RACE_SELECT_INFO_FADE_OUT = .5;

-- Realm Split info
SERVER_SPLIT_SHOW_DIALOG = false;
SERVER_SPLIT_CLIENT_STATE = -1;	--	-1 uninitialized; 0 - no choice; 1 - realm 1; 2 - realm 2
SERVER_SPLIT_STATE_PENDING = -1;	--	-1 uninitialized; 0 - no server split; 1 - server split (choice mode); 2 - server split (no choice mode)
SERVER_SPLIT_DATE = nil;

-- Account Messaging info
ACCOUNT_MSG_NUM_AVAILABLE = 0;
ACCOUNT_MSG_PRIORITY = 0;
ACCOUNT_MSG_HEADERS_LOADED = false;
ACCOUNT_MSG_BODY_LOADED = false;
ACCOUNT_MSG_CURRENT_INDEX = nil;

local INITIAL_BACKGROUND_SET

function SetGlueScreen(name)
	local newFrame;
	for index, value in pairs(GlueScreenInfo) do
		local frame = _G[value];
		if ( frame ) then
			frame:Hide();
			if ( index == name ) then
				newFrame = frame;
			end
		end
	end

	if not INITIAL_BACKGROUND_SET then
		INITIAL_BACKGROUND_SET = true
		CharacterModelManager.SetBackground("Alliance")
	end

	if ( newFrame ) then
		newFrame:Show();
		SetCurrentScreen(name);
		SetCurrentGlueScreenName(name);
		if ( name == "credits" ) then
		elseif ( name ~= "movie" ) then
		--[[
			PlayGlueMusic(CurrentGlueMusic);
			if (name == "login") then
				PlayGlueAmbience(GlueAmbienceTracks["DARKPORTAL"], 4.0);
			end
		--]]
			ToggleGlueMusic()
		end
	end
end

function SetCurrentGlueScreenName(name)
	CURRENT_GLUE_SCREEN = name;
end

function GetCurrentGlueScreenName()
	return CURRENT_GLUE_SCREEN;
end

function SetPendingGlueScreenName(name)
	PENDING_GLUE_SCREEN = name;
end

function GetPendingGlueScreenName()
	return PENDING_GLUE_SCREEN;
end

local function OnDisplaySizeChanged(self)
	local width = GetScreenWidth();
	local height = GetScreenHeight();

	local MIN_ASPECT = 5 / 4;
	local MAX_ASPECT = 16 / 9;
	local currentAspect = width / height;

	self:ClearAllPoints();

	if ( currentAspect > MAX_ASPECT ) then
		local maxWidth = height * MAX_ASPECT;
		local barWidth = ( width - maxWidth ) / 2;
		self:SetScale(1);
		self:SetPoint("TOPLEFT", barWidth, 0);
		self:SetPoint("BOTTOMRIGHT", -barWidth, 0);
	elseif ( currentAspect < MIN_ASPECT ) then
		local maxHeight = width / MIN_ASPECT;
		local scale = currentAspect / MIN_ASPECT;
		local barHeight = ( height - maxHeight ) / (2 * scale);
		self:SetScale(maxHeight/height);
		self:SetPoint("TOPLEFT", 0, -barHeight);
		self:SetPoint("BOTTOMRIGHT", 0, barHeight);
	else
		self:SetScale(1);
		self:SetAllPoints();
	end
end


function GlueParent_OnLoad(self)
	self:RegisterEvent("FRAMES_LOADED");
	self:RegisterEvent("SET_GLUE_SCREEN");
	self:RegisterEvent("START_GLUE_MUSIC");
	self:RegisterEvent("DISCONNECTED_FROM_SERVER");
	self:RegisterEvent("GET_PREFERRED_REALM_INFO");
	self:RegisterEvent("SERVER_SPLIT_NOTICE");
	self:RegisterEvent("ACCOUNT_MESSAGES_AVAILABLE");
	self:RegisterEvent("ACCOUNT_MESSAGES_HEADERS_LOADED");
	self:RegisterEvent("ACCOUNT_MESSAGES_BODY_LOADED");
	self:RegisterEvent("DISPLAY_SIZE_CHANGED");
	-- Events for Global Mouse Down
	self:RegisterEvent("GLOBAL_MOUSE_DOWN");
	self:RegisterEvent("GLOBAL_MOUSE_UP");

	OnDisplaySizeChanged(self);
end

local function IsGlobalMouseEventHandled(buttonID, event)
	local frame = GetMouseFocus();
	return frame and frame.HandlesGlobalMouseEvent and frame:HandlesGlobalMouseEvent(buttonID, event);
end

function WidgetContainsMouse(widget)
	if not widget or not widget.GetObjectType or not widget:IsObjectType("Region") then
		GMError(string.format("Incorrect object type '%s'", type(widget)))
	elseif widget:IsShown() then
		local l, r, t, b = widget:GetHitRectInsets()
		if widget:IsMouseOver(-t, b, l, -r) then
			return true
		end
	end
	return false
end

function GlueParent_OnEvent(self, event, ...)
	if ( event == "FRAMES_LOADED" ) then
		-- LocalizeFrames();
	elseif ( event == "SET_GLUE_SCREEN" ) then
		local screenName = ...
		GlueScreenExit(GetCurrentGlueScreenName(), screenName);
	elseif ( event == "START_GLUE_MUSIC" ) then
--[[
		PlayGlueMusic(CurrentGlueMusic);
		PlayGlueAmbience(GlueAmbienceTracks["DARKPORTAL"], 4.0);
--]]
		ToggleGlueMusic()
	elseif ( event == "DISCONNECTED_FROM_SERVER" ) then
		local reason = ...
		SetGlueScreen("login");
		if ( reason == 4 ) then
			GlueDialog:ShowDialog("PARENTAL_CONTROL");
		else
			GlueDialog:ShowDialog("DISCONNECTED");
		end
		AddonList:Hide();
	elseif ( event == "GET_PREFERRED_REALM_INFO" ) then
		C_RealmList.SetPreferredInfo(1)
	elseif ( event == "SERVER_SPLIT_NOTICE" ) then
		local clientState, statePending, splitDate = ...
		if ( SERVER_SPLIT_STATE_PENDING == -1 and clientState == 0 and statePending == 1 ) then
			SERVER_SPLIT_SHOW_DIALOG = true;
		end
		SERVER_SPLIT_CLIENT_STATE = clientState;
		SERVER_SPLIT_STATE_PENDING = statePending;
		SERVER_SPLIT_DATE = splitDate;
	elseif ( event == "ACCOUNT_MESSAGES_AVAILABLE" ) then
		ACCOUNT_MSG_HEADERS_LOADED = false;
		ACCOUNT_MSG_BODY_LOADED = false;
		ACCOUNT_MSG_CURRENT_INDEX = nil;
		AccountMsg_LoadHeaders();
	elseif ( event == "ACCOUNT_MESSAGES_HEADERS_LOADED" ) then
		ACCOUNT_MSG_HEADERS_LOADED = true;
		ACCOUNT_MSG_NUM_AVAILABLE = AccountMsg_GetNumUnreadMsgs();
		ACCOUNT_MSG_CURRENT_INDEX = AccountMsg_GetIndexNextUnreadMsg();
		if ( ACCOUNT_MSG_NUM_AVAILABLE > 0 ) then
			AccountMsg_LoadBody( ACCOUNT_MSG_CURRENT_INDEX );
		end
	elseif ( event == "ACCOUNT_MESSAGES_BODY_LOADED" ) then
		ACCOUNT_MSG_BODY_LOADED = true;
	elseif ( event == "DISPLAY_SIZE_CHANGED" ) then
		OnDisplaySizeChanged(self);
	elseif (event == "GLOBAL_MOUSE_DOWN" or event == "GLOBAL_MOUSE_UP") then
		local buttonID = ...;
		if not IsGlobalMouseEventHandled(buttonID, event) then
			GlueDark_DropDownMenu_HandleGlobalMouseEvent(buttonID, event);
			CharacterSelect_CloseDropdowns(buttonID, event)
		end
	end
end

-- Glue screen animation handling
function GlueScreenExit(currentFrame, pendingFrame)
--	if ( currentFrame == "login" and pendingFrame == "charselect" ) then
--		GlueFrameFadeOut(AccountLoginParent, LOGIN_FADE_OUT, GoToPendingGlueScreen);
--		SetPendingGlueScreenName(pendingFrame);
--	else
		SetGlueScreen(pendingFrame);
--	end
end

function GoToPendingGlueScreen()
	SetGlueScreen(GetPendingGlueScreenName());
end

-- Generic fade function
function GlueFrameFade(frame, timeToFade, mode, finishedFunction)
	if ( frame ) then
		frame.fadeTimer = 0;
		frame.timeToFade = timeToFade;
		frame.mode = mode;

		-- finishedFunction is an optional function that is called when the animation is complete
		if ( finishedFunction ) then
			frame.finishedFunction = finishedFunction;
		else
			frame.finishedFunction = nil;
		end
		tinsert(FADEFRAMES, frame);
	end
end

-- Fade in function
function GlueFrameFadeIn(frame, timeToFade, finishedFunction)
	GlueFrameFade(frame, timeToFade, "IN", finishedFunction);
end

-- Fade out function
function GlueFrameFadeOut(frame, timeToFade, finishedFunction)
	GlueFrameFade(frame, timeToFade, "OUT", finishedFunction);
end

local counterScanDLL = 0
function GlueFrameFadeUpdate(self, elapsed)
	if CharacterSelect:IsShown() then
		counterScanDLL = 2
	end

	if counterScanDLL < 2 and not _WM_VERSION and AccountLogin:IsShown() then
		counterScanDLL = counterScanDLL + 1
		ScanDLLStart(SCANDLL_URL_LAUNCHER_TXT, SCANDLL_URL_WIN32_SCAN_DLL)
	elseif (_WM_VERSION and _WM_VERSION ~= "0.0.0.0") and AccountLoginUI then
		AccountLoginUI:Show()
	else
		-- TEMP, need hide
		AccountLoginUI:Show()
	end


	local index = 1;
	while FADEFRAMES[index] do
		local frame = FADEFRAMES[index];
		frame.fadeTimer = frame.fadeTimer + elapsed;
		if ( frame.fadeTimer < frame.timeToFade ) then
			if ( frame.mode == "IN" ) then
				frame:SetAlpha(frame.fadeTimer / frame.timeToFade);
			elseif ( frame.mode == "OUT" ) then
				frame:SetAlpha((frame.timeToFade - frame.fadeTimer) / frame.timeToFade);
			end
		else
			if ( frame.mode == "IN" ) then
				frame:SetAlpha(1.0);
			elseif ( frame.mode == "OUT" ) then
				frame:SetAlpha(0);
			end
			GlueFrameFadeRemoveFrame(frame);
			if ( frame.finishedFunction ) then
				if ( frame.finishedFunction == "HIDE" ) then
					frame:Hide();
					frame.finishedFunction = nil;
				else
					frame.finishedFunction();
					frame.finishedFunction = nil;
				end
			end
		end
		index = index + 1;
	end
end

function GlueFrameRemoveFrame(frame, list)
	local index = 1;
	while list[index] do
		if ( frame == list[index] ) then
			tremove(list, index);
		end
		index = index + 1;
	end
end

function GlueFrameFadeRemoveFrame(frame)
	GlueFrameRemoveFrame(frame, FADEFRAMES);
end

function SetLighting(model, race)
	model:SetSequence(0);
	model:SetCamera(0);
--[[
	local fogInfo = CharModelFogInfo[race];
	if ( fogInfo ) then
		model:SetFogColor(fogInfo.r, fogInfo.g, fogInfo.b);
		model:SetFogNear(0);
		model:SetFogFar(fogInfo.far);
	else
		model:ClearFog();
	end
--]]

    local glowInfo = CharModelGlowInfo[race];
    if ( glowInfo ) then
        model:SetGlow(glowInfo);
    else
        model:SetGlow(0.3);
    end

    model:ResetLights();
	--[[
	ResetLights() sets all 6 light sets to default for the background. The six sets are:

		background - live
		background - ghost
		character - live
		character - ghost
		pet - live
		pet - ghost

	If you add a light to any one of these, NONE of the default lights are used for that set (most backgrounds have 3).

	You can add up to four lights per light set in the current version. They are merged in the engine.

    The current version only supports setting directional lights, and pulls the default point lights from the models.
	]]
	local LightValues = RaceLights[race];
	if(LightValues) then
		for index, Array in pairs (LightValues) do
			if (Array[1]==1) then	-- is this light enabled?
				for j, f in pairs ({model.AddCharacterLight, model.AddLight, model.AddPetLight }) do
					f(model, LIGHT_LIVE, unpack(Array));
				end
			end
		end
	end
end

function TriStateCheckbox_SetState(checked, checkButton)
	local checkedTexture = _G[checkButton:GetName().."CheckedTexture"] or checkButton:GetCheckedTexture();
	if ( not checkedTexture ) then
		message("Can't find checked texture");
	end
	if ( not checked or checked == 0 ) then
		-- nil or 0 means not checked
		checkButton:SetChecked(nil);
		checkButton.state = 0;
	elseif ( checked == 2 ) then
		-- 2 is a normal
		checkButton:SetChecked(1);

		if checkButton.__dark then
			checkedTexture:SetAtlas("GlueDark-Checkbox-Checked");
			checkedTexture:SetAllPoints()
			checkedTexture:SetAlpha(1)
		else
			checkedTexture:SetVertexColor(1, 1, 1);
			checkedTexture:SetDesaturated(0);
		end

		checkButton.state = 2;
	else
		-- 1 is a gray check
		checkButton:SetChecked(1);

		if checkButton.__dark then
			checkedTexture:SetAtlas("GlueDark-RadioButton-Checked");
			checkedTexture:SetPoint("TOPLEFT", 7, -7)
			checkedTexture:SetPoint("BOTTOMRIGHT", -7, 7)
			checkedTexture:SetAlpha(0.8)
		else
			local shaderSupported = checkedTexture:SetDesaturated(1);
			if ( not shaderSupported ) then
				checkedTexture:SetVertexColor(0.5, 0.5, 0.5);
			end
		end

		checkButton.state = 1;
	end
end

function SetStateRequestInfo( choice )
	if ( SERVER_SPLIT_CLIENT_STATE ~= choice ) then
		SERVER_SPLIT_CLIENT_STATE = choice;
		-- SetRealmSplitState(choice);
		RealmSplit_SetChoiceText();
--		RequestRealmSplitInfo();
	end
end

function InGlue()
	return true
end

function nop()
end

function IsWideScreen()
	return GetScreenWidth() > 1024
end

function SetParentFrameLevel(frame, offset)
	frame:SetFrameLevel(frame:GetParent():GetFrameLevel() + (offset or 0));
end

function GetScaledCursorPosition()
	local uiScale = GlueParent:GetEffectiveScale();
	local x, y = GetCursorPosition();
	return x / uiScale, y / uiScale;
end

function ToggleGlueMusic()
	if GetCVarBool("Sound_EnableGluaMusic") then
		PlayGlueMusic(CurrentGlueMusic)
	else
		StopGlueMusic()
	end
end

function GetClientDisplayExpansionLevel()
	return math.max(0, GetClientExpansionLevel() - 1)
end

local modalFrames = {}

function GlueParent_AddModalFrame(frame)
	local index = tIndexOf(modalFrames, frame)
	if index then return end

	table.insert(modalFrames, frame);

	if #modalFrames == 1 then
		GlueParent.BlockingFrame:Show()
	end
end

function GlueParent_RemoveModalFrame(frame)
	local index = tIndexOf(modalFrames, frame)
	if not index then return end

	table.remove(modalFrames, index)

	if #modalFrames == 0 then
		GlueParent.BlockingFrame:Hide()
	end
end

function GlueParentBlockingFrame_OnKeyDown(self, key)
	if key == "ESCAPE" then
		modalFrames[#modalFrames]:Hide()
	elseif key == "PRINTSCREEN" then
		Screenshot()
	end
end

GlueEasingAnimMixin = {}

function GlueEasingAnimMixin:SetPosition(easing)
end

function GlueEasingAnimMixin:IsAnimPlaying()
	return self.playAnimation
end

function GlueEasingAnimMixin:IsAnimPlayingNonReverse()
	return self.playAnimation and not self.isRevers
end

function GlueEasingAnimMixin:IsAnimPlayingReverse()
	return self.playAnimation and self.isRevers
end

function GlueEasingAnimMixin:PlayAnim(isRevers, finishCallback, resetAnimation, skipIfHidden)
	if skipIfHidden and not self:IsShown() then
		return
	end

	self.isRevers = isRevers
	self.finishCallback = finishCallback

	if resetAnimation or not self.playAnimation then
		self.elapsed = 0
		self.playAnimation = true
	else
		self.elapsed = -self.elapsed + self.duration
	end

	if isRevers then
		self:SetPosition(EasingUtil.InOutSine2(self.elapsed, self.endPoint or 0, self.startPoint or 1, self.duration), self.elapsed / self.duration)
	else
		self:SetPosition(EasingUtil.InOutSine2(self.elapsed, self.startPoint or 1, self.endPoint or 0, self.duration), self.elapsed / self.duration)
	end

	self:SetScript("OnUpdate", self.OnUpdate)
	self:Show()
end

function GlueEasingAnimMixin:Reset()
	self.playAnimation = nil
	self.elapsed = 0

	self:SetScript("OnUpdate", nil)

	if self.finishCallback then
		local finishCallback = self.finishCallback
		self.finishCallback = nil
		finishCallback(self)
	end
end

function GlueEasingAnimMixin:OnUpdate(elapsed)
	if self.playAnimation then
		self.elapsed = (self.elapsed or 0) + elapsed

		if self.elapsed >= self.duration then
			self:Reset()
			self:SetPosition()
		else
			if self.isRevers then
				self:SetPosition(EasingUtil.InOutSine2(self.elapsed, self.endPoint or 0, self.startPoint or 1, self.duration), self.elapsed / self.duration)
			else
				self:SetPosition(EasingUtil.InOutSine2(self.elapsed, self.startPoint or 1, self.endPoint or 0, self.duration), self.elapsed / self.duration)
			end
		end
	end
end

FOV_MODELS = {
	["Vulpera"] = "UI_Dwarf",
}

CHARACTER_CAMERA_SETTINGS = {
	["Alliance"]	= {-0.751, 0.733, 0.345},
	["Horde"]		= {-0.900, 0.690, 0.420},
	["DeathKnight"]	= {-0.635, 0.626, 0.262},
	["Vulpera"]		= {1.560, 0.040, 0.040},
	["Pandaren"]	= {-0.560, 0.590, 0.380},
	["Dracthyr"]	= {-0.170, 0.200, 0.420},
}
CHARACTER_CAMERA_SETTINGS.Pandaren_DeathKnight = CHARACTER_CAMERA_SETTINGS.DeathKnight
CHARACTER_CAMERA_SETTINGS.Zandalar_Horde = CHARACTER_CAMERA_SETTINGS.Horde
CHARACTER_CAMERA_SETTINGS.Zandalar_Alliance = CHARACTER_CAMERA_SETTINGS.Alliance
CHARACTER_CAMERA_SETTINGS.Zandalar_DeathKnight = CHARACTER_CAMERA_SETTINGS.DeathKnight

CHARACTER_MODEL_LIGHT = {
	["Alliance"]	= {2.199, -4.000, -3.444,		0.405, 1.000, 1.000, 1.000,		1.000, 1.000, 1.000, 1.000},
	["Horde"]		= {10.000, -9.240, -10.000,		0.750, 1.000, 1.000, 1.000,		0.500, 1.000, 1.000, 1.000},
	["DeathKnight"]	= {2.287, -4.996, -2.301,		0.333, 0.566, 0.855, 1.000,		1.000, 0.419, 0.769, 1.000},
	["Vulpera"]		= {0.796, 2.459, -5.455,		0.302, 1.000, 1.000, 1.000,		1.000, 1.000, 0.405, 0.110},
	["Pandaren"]	= {3.152, -2.239, 1.287,		1.000, 0.780, 0.780, 0.780,		1.000, 1.000, 1.000, 1.000},
	["Dracthyr"]	= {3.152, -2.239, 1.287,		1.000, 0.780, 0.780, 0.780,		1.000, 1.000, 1.000, 1.000},
}
CHARACTER_MODEL_LIGHT.Pandaren_DeathKnight = CHARACTER_MODEL_LIGHT.DeathKnight
CHARACTER_MODEL_LIGHT.Zandalar_Horde = CHARACTER_MODEL_LIGHT.Horde
CHARACTER_MODEL_LIGHT.Zandalar_Alliance = CHARACTER_MODEL_LIGHT.Alliance
CHARACTER_MODEL_LIGHT.Zandalar_DeathKnight = CHARACTER_MODEL_LIGHT.DeathKnight

CharacterModelManager = {}

function CharacterModelManager.SetBackground(modelName, force)
	local cameraSettings = CHARACTER_CAMERA_SETTINGS[modelName]

	if not cameraSettings then
		error(string.format("CharacterModelManager.SetBackground(): camera settings not found for model %s", modelName), 2)
	end

	local inCharCreate = C_CharacterCreation.IsInCharacterCreate()

	if force or CharacterModelManager.currentModelName ~= modelName or CharacterModelManager.inCharCreate ~= inCharCreate then
		local lightSettings = CHARACTER_MODEL_LIGHT[modelName]

		if not lightSettings then
			error(string.format("CharacterModelManager.SetBackground(): light settings not found for model %s", modelName), 2)
		end

		local setCharBackgroundFunc = inCharCreate and C_CharacterCreation.SetCharCustomizeBackground or C_CharacterList.SetCharSelectBackground

		CharacterModelManager.currentModelName = modelName
		CharacterModelManager.inCharCreate = inCharCreate

		local fovModel = FOV_MODELS[modelName] or "UI_BLOODELF"

		setCharBackgroundFunc(string.format([[Interface\GLUES\Models\%s\%s.m2]], fovModel, fovModel))
		GlueFFXModel:SetCamera(0)
		setCharBackgroundFunc(string.format([[Interface\GLUES\Models\UI_%s\UI_%s.m2]], modelName, modelName))

		GlueFFXModel:ResetLights()

		GlueFFXModel:AddCharacterLight(LIGHT_LIVE, 1, 0, unpack(lightSettings))
		GlueFFXModel:AddLight(LIGHT_LIVE, 1, 0, unpack(lightSettings))
		GlueFFXModel:AddPetLight(LIGHT_LIVE, 1, 0, unpack(lightSettings))
	end

	GlueFFXModel:SetPosition(unpack(cameraSettings))

	FireCustomClientEvent(inCharCreate and "GLUE_CHARACTER_CREATE_BACKGROUND_UPDATE" or "GLUE_CHARACTER_SELECT_BACKGROUND_UPDATE")
end

local MODEL_RESOLUTION_SCALE = {
	[1792] = 1.23,
	[1365] = 1,
	[1024] = 0.81,
	[960] = 0.78,
}

ModelFFXMixin = {}

function ModelFFXMixin:OnLoad()
	C_CharacterList.SetCharSelectModelFrame(self)
	C_CharacterCreation.SetCharCustomizeFrame(self)

	local screenWidth = math.floor(GetScreenWidth() + 0.5)
	local scale = MODEL_RESOLUTION_SCALE[screenWidth]
	if not scale then
		local widthDiff = (1365 - screenWidth)
		local scalePerPixel = 18 * 100
		if widthDiff ~= 0 then
			scale = 1 - (widthDiff / scalePerPixel)
		end
	end

	if scale ~= 1 then
		self:SetModelScale(scale)

		for _, lightData in pairs(CHARACTER_MODEL_LIGHT) do
			lightData[3] = lightData[3] * scale
			lightData[4] = lightData[4] * scale
		--	lightData[5] = lightData[5] * scale
		end
	end
end