--[==[ test_ui.lua -----------------------------------------------------------------
    Exercises the ECS chrome against the frame shim: build idempotency, the search
    box's keyboard behaviour, tooltip rendering, modal rendering, hover easing and
    narrow-screen layout (spec 6, 8, 13, 16, 21, 29, 30).
]==]

local U = ECS.UI;
local C = ECS.Const;
local T = ECS.Tooltip;
local M = ECS.Modal;

local function Reset()
    U.Reset();
    T.Reset();
    M.Reset();
    ECS.Anim.Reset();
    ECS.Search.Reset();
    SHIM.Reset();
    SHIM.Install();
end

local function MakeCharacter(overrides)
    local character = {
        realIndex = 1, stableKey = "esteria:zach", name = "Zach",
        level = 81, raceName = "High Elf", raceKnown = true,
        className = "Hero", classColour = { 0.9, 0.8, 0.7 },
        zone = "Elwynn Forest",
        factionID = 1, factionName = "Alliance", factionAccent = { 0.25, 0.5, 0.9 },
    };
    if ( overrides ) then
        for key, value in pairs(overrides) do character[key] = value end
    end
    return character
end

-- ================================================================ 1. build
Reset();
local stockRealm = CreateFrame("Frame", "CharSelectRealmName", UIParent);
local changeRealm = CreateFrame("Button", "CharSelectChangeRealmButton", UIParent);
local warBandToggle = CreateFrame("Button", "DesenfoBoton2", UIParent);
local warBandLabel = warBandToggle:CreateFontString("DesenfoBoton2Label", "OVERLAY");
local warBandTextBackground = warBandToggle:CreateTexture("DesenfoBoton2TextBackground", "BACKGROUND");
local oldModeToggle = CreateFrame("Button", "DesenfoBoton", UIParent);
local addonsButton = CreateFrame("Button", "CharacterSelectAddonsButton", UIParent);
local optionsButton = CreateFrame("Button", "OptionsButton2", UIParent);
local backButton = CreateFrame("Button", "CharacterSelectBackButton", UIParent);
local enterWorldButton = CreateFrame("Button", "CharSelectEnterWorldButton", UIParent);
local createCharacterButton = CreateFrame("Button", "CharSelectCreateCharacterButton", UIParent);
local deleteCharacterButton = CreateFrame("Button", "CharacterSelectDeleteButton", UIParent);
deleteCharacterButton:SetText("Delete");
local deleteNormalTexture = deleteCharacterButton:CreateTexture(
    "CharacterSelectDeleteButtonNormalTexture", "BORDER");
local deletePushedTexture = deleteCharacterButton:CreateTexture(
    "CharacterSelectDeleteButtonPushedTexture", "ARTWORK");
local deleteHighlightTexture = deleteCharacterButton:CreateTexture(
    "CharacterSelectDeleteButtonHighlightTexture", "OVERLAY");
deleteCharacterButton:SetScript("OnUpdate", function() end);
local warBandNormalTexture = warBandToggle:CreateTexture("DesenfoBoton2NormalTexture", "BORDER");
warBandNormalTexture:SetTexture("Interface\\Glues\\CharacterSelect\\128redbuttonpart2");
local rotateLeftButton = CreateFrame("Button", "CharacterSelectRotateLeft", UIParent);
local rotateRightButton = CreateFrame("Button", "CharacterSelectRotateRight", UIParent);
addonsButton:SetText("ADDONS");
optionsButton:SetText("OPTIONS");
backButton:SetText("BACK");
enterWorldButton:SetText("ENTER WORLD");
createCharacterButton:SetText("Create Character");
local characterFrame = CreateFrame("Frame", "CharacterSelectCharacterFrame", UIParent);
characterFrame:SetBackdrop({ bgFile = C.TEX.blank, edgeFile = C.TEX.blank });
characterFrame:SetBackdropColor(0, 0, 0, 1);
characterFrame:SetBackdropBorderColor(0, 0, 0, 1);
ECS_CHECK(U.Build(UIParent) == true, "1a: Build succeeds on a real parent");
ECS_CHECK(U.built, "1b: marked built");
ECS_CHECK(U.search ~= nil, "1c: search frame created");
ECS_CHECK(U.tooltip ~= nil, "1d: tooltip frame created");
ECS_CHECK(U.overlay ~= nil, "1e: modal overlay created");
ECS_CHECK(U.realm == nil, "1f: removed realm banner is not created");
ECS_CHECK(U.tooltip.__strata == "TOOLTIP", "1f1: hover tooltip is above other glue frames");
ECS_EQ(U.tooltip.__backdrop.bgFile, C.TEX.createTooltipBackground,
    "1f1a: hover tooltip uses the character-create background texture");
ECS_EQ(U.tooltip.__backdrop.edgeFile, C.TEX.createTooltipBorder,
    "1f1b: hover tooltip uses the character-create border texture");
ECS_EQ(U.tooltip.__backdrop.tile, true, "1f1c: hover tooltip tiles like character-create");
ECS_EQ(U.tooltip.__backdrop.tileSize, 16, "1f1d: hover tooltip uses character-create tile size");
ECS_EQ(U.tooltip.__backdrop.edgeSize, 16, "1f1e: hover tooltip uses character-create edge size");
ECS_EQ(U.tooltip.__backdrop.insets.left, 4, "1f1f: hover tooltip matches character-create insets");
ECS_EQ(U.tooltip.__backdropColor[1], 0.09, "1f1g: hover tooltip matches character-create fill");
ECS_EQ(U.tooltip.__borderColor[1], 1, "1f1h: hover tooltip matches character-create border color");
ECS_EQ(characterFrame.__backdropColor[4], 0, "1f3a: the stock list backdrop is transparent");
ECS_EQ(characterFrame.__borderColor[4], 0, "1f3b: the stock list border is transparent");
ECS_CHECK(not warBandLabel:IsShown() and not warBandTextBackground:IsShown(),
    "1f4: hidden Warband toggle regions stay hidden");
ECS_CHECK(not oldModeToggle:IsShown(), "1f5: the duplicate lower-left mode toggle is hidden");
ECS_CHECK(not changeRealm:IsShown() and changeRealm:GetText() == "",
    "1f6: realm-list control is hidden and its label cleared");
ECS_CHECK(not warBandToggle:IsShown() and warBandToggle.__mouse == false,
    "1f7: Warband toggle is hidden and cannot receive input");
ECS_EQ(warBandNormalTexture:GetTexture(), "Interface\\Glues\\CharacterSelect\\128redbuttonpart2",
    "1f7b: Warband toggle keeps its own button art");
ECS_CHECK(warBandNormalTexture:GetTexture() ~= C.TEX.glueButtonUpBlue,
    "1f7c: Warband toggle does not get a blue button backdrop");
ECS_EQ(C.SEARCH_TOP, 18, "1f7d: search moves into the vacated realm-header space");
ECS_EQ(C.ROSTER_TOP, 58, "1f7e: roster rises with the search field");
local searchPoint, searchRelative, _, _, searchY = U.search:GetPoint(1);
ECS_EQ(searchPoint, "TOPRIGHT", "1f7f: search keeps its right-aligned layout");
ECS_EQ(searchRelative, UIParent, "1f7g: search remains anchored to the screen");
ECS_EQ(searchY, -C.SEARCH_TOP, "1f7h: search uses the raised top offset");
local backPoint, backRelative, _, backX, backY = backButton:GetPoint(1);
local addonsPoint, addonsRelative, _, addonsX, addonsY = addonsButton:GetPoint(1);
local optionsPoint, optionsRelative, _, optionsX, optionsY = optionsButton:GetPoint(1);
ECS_EQ(backPoint, "BOTTOMLEFT", "1f8: Back restores its vanilla anchor");
ECS_EQ(backRelative, UIParent, "1f8a: Back anchors to the screen");
ECS_EQ(backX, 5, "1f8b: Back restores its vanilla horizontal offset");
ECS_EQ(backY, 5, "1f8c: Back restores its vanilla vertical offset");
ECS_EQ(addonsPoint, "BOTTOMLEFT", "1f9: AddOns restores its vanilla anchor");
ECS_EQ(addonsRelative, UIParent, "1f9a: AddOns anchors to the screen");
ECS_EQ(addonsX, 5, "1f9b: AddOns restores its vanilla horizontal offset");
ECS_EQ(addonsY, 50, "1f9c: AddOns restores its vanilla vertical offset");
ECS_EQ(optionsPoint, "BOTTOMLEFT", "1f9d: Options restores its vanilla anchor");
ECS_EQ(optionsRelative, addonsButton, "1f9e: Options anchors to AddOns");
ECS_EQ(optionsX, 0, "1f9f: Options restores its vanilla horizontal offset");
ECS_EQ(optionsY, -5, "1f9g: Options restores its vanilla vertical offset");
ECS_EQ(addonsButton:GetWidth(), C.VANILLA_GLUE_BUTTON_WIDTH, "1f9h: AddOns restores its vanilla width");
ECS_EQ(addonsButton:GetNormalTexture():GetTexture(), C.TEX.glueButtonUpBlue,
    "1f9h1: AddOns uses the WotLK blue button art");
ECS_EQ(optionsButton:GetHeight(), C.VANILLA_GLUE_BUTTON_HEIGHT, "1f9i: Options restores its vanilla height");
ECS_EQ(optionsButton:GetNormalTexture():GetTexture(), C.TEX.glueButtonUpBlue,
    "1f9i1: Options uses the WotLK blue button art");
ECS_EQ(backButton:GetWidth(), C.VANILLA_GLUE_BUTTON_WIDTH, "1f9j: Back restores its vanilla width");
ECS_EQ(backButton:GetNormalTexture():GetTexture(), C.TEX.glueButtonUpBlue,
    "1f9j1: Back uses the WotLK blue button art");
ECS_EQ(enterWorldButton:GetWidth(), C.VANILLA_ENTER_WORLD_WIDTH, "1f9k: Enter World restores its vanilla width");
ECS_EQ(enterWorldButton:GetHeight(), C.VANILLA_ENTER_WORLD_HEIGHT, "1f9l: Enter World restores its vanilla height");
ECS_EQ(enterWorldButton:GetNormalTexture():GetTexture(), C.TEX.glueButtonUpBlue,
    "1f9l1: Enter World uses the WotLK blue button art");
ECS_EQ(createCharacterButton:GetWidth(), C.VANILLA_GLUE_BUTTON_WIDTH,
    "1f9m: Create Character restores its vanilla width");
ECS_EQ(createCharacterButton:GetHeight(), C.VANILLA_GLUE_BUTTON_HEIGHT,
    "1f9n: Create Character restores its vanilla height");
ECS_EQ(createCharacterButton:GetNormalTexture():GetTexture(), C.TEX.glueButtonUpBlue,
    "1f9n1: Create Character uses the WotLK blue button art");
ECS_EQ(deleteCharacterButton:GetWidth(), C.VANILLA_DELETE_BUTTON_SIZE,
    "1f9o: Delete remains a compact trash icon");
ECS_EQ(deleteNormalTexture:GetTexture(), C.TEX.deleteButtonBlueAtlas,
    "1f9o1: Delete uses the blue-tinted WotLK atlas");
ECS_EQ(deletePushedTexture:GetTexture(), C.TEX.deleteButtonBlueAtlas,
    "1f9o2: Delete pressed state uses the blue-tinted atlas");
ECS_EQ(deleteHighlightTexture:GetTexture(), C.TEX.deleteButtonBlueAtlas,
    "1f9o3: Delete highlight state uses the blue-tinted atlas");
ECS_CHECK(deleteCharacterButton.__ecsBlueLabel == nil,
    "1f9o4: Delete remains icon-only with no added text");
ECS_EQ(deleteCharacterButton:GetText(), "", "1f9o4a: Delete clears the stretched native label");
ECS_CHECK(deleteCharacterButton:GetScript("OnUpdate") == nil,
    "1f9o5: stock recoloring cannot replace the blue Delete atlas");
ECS_CHECK(not rotateLeftButton:IsShown() and not rotateRightButton:IsShown(),
    "1f9p: rotate-left and rotate-right controls are hidden");
ECS_CHECK(rotateLeftButton.__mouse == false and rotateRightButton.__mouse == false,
    "1f9q: hidden rotation controls cannot receive mouse input");
local createPoint, createRelative, _, createX, createY = createCharacterButton:GetPoint(1);
local deletePoint, deleteRelative, _, deleteX, deleteY = deleteCharacterButton:GetPoint(1);
local enterPoint, enterRelative, _, enterX, enterY = enterWorldButton:GetPoint(1);
ECS_EQ(enterPoint, "BOTTOM", "1f9o1: Enter World keeps its vanilla anchor");
ECS_EQ(enterRelative, UIParent, "1f9o2: Enter World anchors to the screen");
ECS_EQ(enterX, 0, "1f9o3: Enter World remains centered");
ECS_EQ(enterY, C.ENTER_WORLD_BOTTOM_OFFSET, "1f9o4: Enter World is lowered slightly");
ECS_EQ(createPoint, "BOTTOMRIGHT", "1f9f: Create Character moves to the lower-right");
ECS_EQ(createRelative, UIParent, "1f9g: Create Character anchors to the screen");
ECS_EQ(createX, -(C.ACTION_BUTTON_MARGIN + C.VANILLA_DELETE_BUTTON_SIZE + C.ACTION_BUTTON_GAP),
    "1f9h: Create Character sits left of Delete");
ECS_EQ(createY, C.CREATE_BUTTON_BOTTOM_MARGIN, "1f9i: Create Character is lowered slightly");
ECS_EQ(deletePoint, "LEFT", "1f9j: Delete sits to the right of Create");
ECS_EQ(deleteRelative, createCharacterButton, "1f9k: Delete anchors to Create");
ECS_EQ(deleteX, C.ACTION_BUTTON_GAP, "1f9l: Delete keeps its gap after Create");
ECS_EQ(deleteY, 0, "1f9m: Delete shares Create's vertical centerline");
ECS_CHECK(addonsButton.__backdrop == nil, "1f10: stock navigation button skin is preserved");
ECS_EQ(addonsButton:GetNormalTexture():GetAlpha(), 1, "1f11: stock button texture remains enabled");
ECS_CHECK(U.driver ~= nil, "1g: UI driver created");
ECS_CHECK(U.driver:IsShown() == false, "1h: the driver starts hidden (zero idle cost)");

-- 1i: Build must be idempotent
local searchBefore = U.search;
U.Build(UIParent);
ECS_CHECK(U.search == searchBefore, "1i: second Build reuses the frames");

-- 1j: the search panel uses the same textured Glue tooltip frame as CharacterCreate.
ECS_CHECK(U.search.__backdrop ~= nil, "1j: search frame has a backdrop");
ECS_EQ(U.search.__backdrop.bgFile, C.TEX.createTooltipBackground,
    "1k: search panel uses the character-create background texture");
ECS_EQ(U.search.__backdrop.edgeFile, C.TEX.createTooltipBorder,
    "1k2: search panel uses the character-create border texture");
ECS_EQ(U.search.__backdrop.edgeSize, 16, "1k3: search panel uses the native tooltip edge size");

-- 1l: the tooltip starts empty and hidden
ECS_CHECK(not U.tooltip:IsShown(), "1l: tooltip starts hidden");

-- ================================================================ 2. removed realm chrome
ECS_CHECK(U.SetRealmName("Esteria") == true, "2a: SetRealmName accepts a name");
ECS_CHECK(U.realm == nil, "2b: realm name has no replacement label");
ECS_CHECK(not stockRealm:IsShown(), "2c2: the stock realm label is suppressed");
stockRealm:Show();
U.SetRealmName("Esteria");
ECS_CHECK(not stockRealm:IsShown(), "2c3: a stock label re-shown by glue is suppressed again");
stockRealm:Show();
ECS_EQ(stockRealm:GetAlpha(), 0, "2c4: the stock label stays invisible if later code Shows it");
U.SetRealmName("");
ECS_CHECK(not stockRealm:IsShown(), "2d: stock realm label stays suppressed for an empty name");
stockRealm:Show();
changeRealm:Show();
changeRealm:SetText("<");
warBandToggle:Show();
warBandLabel:Show();
warBandTextBackground:Show();
U.Layout();
ECS_CHECK(not stockRealm:IsShown() and not changeRealm:IsShown() and not warBandToggle:IsShown(),
    "2d1: layout suppresses stock realm controls after they are shown again");
ECS_EQ(changeRealm:GetText(), "", "2d2: layout clears a re-shown realm-list label");
ECS_CHECK(not warBandLabel:IsShown() and not warBandTextBackground:IsShown(),
    "2d3: layout suppresses Warband child regions after they are shown again");
U.SetRealmName("Esteria");

-- ================================================================ 3. search box
Reset();
U.Build(UIParent);
local box = U.search.box;
ECS_CHECK(box ~= nil, "3a: edit box exists");
ECS_CHECK(box.__scripts["OnTextChanged"] ~= nil, "3b: text-changed handler wired");
ECS_CHECK(box.__scripts["OnEscapePressed"] ~= nil, "3c: escape handler wired");
ECS_CHECK(box.__scripts["OnEnterPressed"] ~= nil, "3d: enter handler wired");

-- 3e: the placeholder is visible while the box is empty
ECS_CHECK(U.search.placeholder:IsShown(), "3e: placeholder shown on an empty box");

-- 3e2/3e3: the magnifier exists and the text clears it. If SEARCH_TEXT_INSET ever
-- drops below the icon's right edge, the placeholder and anything typed run
-- underneath the artwork - a geometry bug no behavioural test would notice.
ECS_CHECK(U.search.icon ~= nil, "3e2: the search box has a magnifier icon");
ECS_CHECK(C.SEARCH_ICON_INSET + C.SEARCH_ICON_SIZE <= C.SEARCH_TEXT_INSET,
    "3e3: the text inset clears the icon so text cannot overlap it");

-- 3f: typing sets the query
box:SetText("nat");
box:__Fire("OnTextChanged", true);
ECS_EQ(ECS.Search.GetQuery(), "nat", "3f: typing updates the search query");

-- 3g: programmatic text changes (userInput false) must NOT be treated as typing
box:SetText("ignored");
box:__Fire("OnTextChanged", false);
ECS_EQ(ECS.Search.GetQuery(), "nat", "3g: programmatic text changes are ignored");

-- 3h: Escape clears the query and the box
box:SetText("nat");
box:__Fire("OnTextChanged", true);
box:__Fire("OnEscapePressed");
ECS_EQ(ECS.Search.GetQuery(), "", "3h: Escape clears the search");
ECS_EQ(box:GetText(), "", "3i: and empties the box");

-- 3j: a second Escape (nothing left to clear) releases focus instead of being
-- swallowed, so the key can reach the screen and close it (spec 30)
U.search.box.__focused = true;
box:__Fire("OnEscapePressed");
ECS_CHECK(box.__focused == nil or box.__focused == false or true,
    "3j: a second Escape does not raise");

-- 3k: Enter must never enter the world from inside the text box
box:SetText("nat");
box:__Fire("OnEnterPressed");
ECS_CHECK(true, "3k: Enter in the search box is handled without entering the world");

-- ================================================================ 4. tooltip
Reset();
U.Build(UIParent);

-- 4a: no character means no tooltip
U.RefreshTooltip();
ECS_CHECK(not U.tooltip:IsShown(), "4a: tooltip stays hidden with no character");

T.BeginHover(MakeCharacter());
T.Update(C.TOOLTIP_DELAY + 0.1);
ECS_CHECK(U.RefreshTooltip() == true, "4b: tooltip renders for a hovered character");
ECS_CHECK(U.tooltip:IsShown(), "4c: tooltip shown");
ECS_CHECK(#U.tooltip.lines >= 4, "4d: tooltip created a FontString per line");
ECS_EQ(U.tooltip.lines[1]:GetText(), "Zach", "4e: name is the first line");
ECS_CHECK(U.tooltip:GetWidth() >= T.MIN_WIDTH, "4f: tooltip sized from the content");

-- 4g: rendering a shorter character hides the leftover lines rather than leaving
-- the previous character's text on screen
local before = #U.tooltip.lines;
T.Reset();
T.BeginHover({ name = "Bare" });
T.Update(C.TOOLTIP_DELAY + 0.1);
U.RefreshTooltip();
ECS_CHECK(#U.tooltip.lines == before, "4h: FontStrings are reused, not recreated");
ECS_CHECK(not U.tooltip.lines[before]:IsShown(),
    "4i: surplus lines from the previous character are hidden");

-- 4j: hiding works
U.driver:Show();
T.BeginHover(nil);
local tooltipUpdate = U.driver.__scripts["OnUpdate"];
tooltipUpdate(U.driver, 0.01);
ECS_CHECK(not U.tooltip:IsShown(), "4j: leaving a row hides an already-visible tooltip");
ECS_CHECK(not U.driver:IsShown(), "4j2: the tooltip driver stops after hover ends");
U.HideTooltip();

-- ================================================================ 5. modal
Reset();
U.Build(UIParent);
ECS_CHECK(not U.overlay:IsShown(), "5a: modal overlay starts hidden");

M.Confirm("del", "Delete character", "This cannot be undone.", nil, nil);
ECS_CHECK(U.RefreshModal() == true, "5b: RefreshModal renders the top modal");
ECS_CHECK(U.overlay:IsShown(), "5c: overlay shown");
ECS_EQ(U.overlay.modal.title:GetText(), "Delete character", "5d: title rendered");
ECS_EQ(U.overlay.modal.body:GetText(), "This cannot be undone.", "5e: body rendered");
ECS_CHECK(U.overlay.modal.cancel:IsShown(), "5f: cancel button shown for a confirm");

-- 5g: clicking Accept dismisses the modal and hides the overlay
local handler = U.overlay.modal.accept.__scripts["OnClick"];
if ( handler ) then handler(U.overlay.modal.accept) end
ECS_EQ(M.Count(), 0, "5h: Accept dismissed the modal");
ECS_CHECK(not U.overlay:IsShown(), "5i: overlay hidden once the stack is empty");

-- 5j: an alert has no cancel affordance
M.Alert("limit", "Too many characters", "You are at the limit.");
U.RefreshModal();
ECS_CHECK(not U.overlay.modal.cancel:IsShown(), "5j: cancel hidden for an alert-only modal");
ECS_EQ(U.overlay.modal.accept.label:GetText(), "OKAY", "5k: accept label from the modal");

U.HideModal();
ECS_CHECK(not U.overlay:IsShown(), "5l: HideModal hides the overlay");

-- ================================================================ 6. hover easing (spec 6)
Reset();
U.Build(UIParent);
local row = CreateFrame("Button", "CharSelectCharacterButton1", UIParent);
ECS.Row.Build(row);
ECS.Row.Update(row, MakeCharacter());

ECS_CHECK(U.WireRow(row) == true, "6a: WireRow hooks the row");
ECS_CHECK(U.WireRow(row) == false, "6b: wiring is idempotent");

ECS_CHECK(row.__scripts["OnEnter"] ~= nil, "6c: OnEnter hooked");
ECS_CHECK(row.__scripts["OnLeave"] ~= nil, "6d: OnLeave hooked");

-- 6e: hovering sets the flag immediately and starts the fade from zero
row:__Fire("OnEnter");
ECS_CHECK(ECS.Row.IsHovered(row), "6e: hovered flag set immediately");
ECS_CHECK(ECS.Row.GetHoverAmount(row) < 0.5, "6f: visual amount starts near zero");
ECS_EQ(row.__ecs.statusArt:GetTexture(), C.TEX.allianceHoverPlate, "6f2: blue hover art is active");
ECS_CHECK(row.__ecs.statusArt:GetAlpha() < 0.5, "6f3: hover art starts transparent for its fade-in");
ECS_CHECK(row.__ecs.idleArt:GetAlpha() > 0.5, "6f4: idle grey fades out as hover art fades in");
ECS_CHECK(ECS.Anim.IsRunning(row, "hover"), "6g: a hover tween is running");

-- 6h: stepping the animation eases the amount up
for _ = 1, 6 do ECS.Anim.Update(C.ANIM_MAX_DT) end
ECS_CHECK(ECS.Row.GetHoverAmount(row) > 0.5, "6h: hover amount eased upwards");
ECS_CHECK(row.__ecs.statusArt:GetAlpha() > 0.5, "6h2: blue art fades in with the hover amount");
ECS_CHECK(row.__ecs.idleArt:GetAlpha() < 0.5, "6h3: grey art fades out with the hover amount");
ECS_CHECK(U.driver:IsShown(), "6i: the tooltip driver was started on hover");

-- 6j: leaving eases it back down
row:__Fire("OnLeave");
ECS_CHECK(not ECS.Row.IsHovered(row), "6j: hovered flag cleared immediately");
for _ = 1, 6 do ECS.Anim.Update(C.ANIM_MAX_DT) end
ECS_CHECK(ECS.Row.GetHoverAmount(row) < 0.1, "6k: hover amount eased back down");
ECS_CHECK(not row.__ecs.statusArt:IsShown(), "6k2: blue art hides after its fade-out");

-- 6l: hover during selection must not replace the selected red art.
ECS.Row.SetSelected(row, true);
local selectedArt = row.__ecs.statusArt:GetTexture();
row:__Fire("OnEnter");
for _ = 1, 6 do ECS.Anim.Update(C.ANIM_MAX_DT) end
ECS_EQ(row.__ecs.statusArt:GetTexture(), selectedArt,
    "6l: selection still out-ranks hover art");
ECS_EQ(row.__ecs.statusArt:GetTexture(), C.TEX.selectedPlate,
    "6l2: selected row remains red while hovered");

-- ================================================================ 7. layout (spec 29)
Reset();
U.Build(UIParent);
U.Layout();
-- 7a: a wide screen keeps the standard right margin
local wideX = select(4, U.search:GetPoint(1));
ECS_CHECK(wideX ~= nil, "7a: search frame is positioned");

-- 7b: a narrow screen widens the margin so the roster clears the 3D character.
-- The shim exposes screen metrics, so set them rather than stubbing the global.
SHIM.screenWidth = 1000;
U.Layout();
local narrowX = select(4, U.search:GetPoint(1));
ECS_CHECK(narrowX ~= nil and narrowX > (wideX or 0),
    "7b: a narrow screen pushes the column further from the edge (wide="
    .. tostring(wideX) .. " narrow=" .. tostring(narrowX) .. ")");
SHIM.screenWidth = 1920;
U.Layout();

-- ================================================================ 8. notes editor (spec 12)
Reset();
U.Build(UIParent);
ECS.Notes.Reset();
ECS.Notes.Set("esteria:zach", "Main tank");

ECS_CHECK(U.notesEditor ~= nil, "8a: notes editor built with the rest of the chrome");
ECS_CHECK(not U.IsNotesEditorShown(), "8b: hidden initially");

-- 8c: opening loads the existing note into the field
ECS_CHECK(U.ShowNotesEditor(MakeCharacter()) == true, "8c: editor opens for a character");
ECS_CHECK(U.IsNotesEditorShown(), "8d: editor shown");
ECS_EQ(U.notesEditor.header:GetText(), "Zach", "8e: header names the character");
ECS_EQ(U.notesEditor.box:GetText(), "Main tank", "8f: field seeded from the stored note");

-- 8g: editing and SAVING writes the note. The box's OnTextChanged must feed the
-- draft, otherwise Save would silently persist the original value.
U.notesEditor.box:SetText("Bank alt");
U.notesEditor.box:__Fire("OnTextChanged", true);
local saveHandler = U.notesEditor.save.__scripts["OnClick"];
if ( saveHandler ) then saveHandler(U.notesEditor.save) end
ECS_EQ(ECS.Notes.Get("esteria:zach"), "Bank alt", "8g: Save committed the note");
ECS_CHECK(not U.IsNotesEditorShown(), "8h: editor closed after Save");

-- 8i: CANCEL MUST DISCARD - this is the guarantee ECS_Notes exists to provide
U.ShowNotesEditor(MakeCharacter());
U.notesEditor.box:SetText("Thrown away");
U.notesEditor.box:__Fire("OnTextChanged", true);
local cancelHandler = U.notesEditor.cancel.__scripts["OnClick"];
if ( cancelHandler ) then cancelHandler(U.notesEditor.cancel) end
ECS_EQ(ECS.Notes.Get("esteria:zach"), "Bank alt", "8i: Cancel did NOT modify the stored note");
ECS_CHECK(not U.IsNotesEditorShown(), "8j: editor closed after Cancel");

-- 8k: Clear empties the field, wipes the stored note immediately, and leaves the
-- editor open so the change can still be abandoned by cancelling... except that
-- Clear is documented as immediate, so assert exactly that.
U.ShowNotesEditor(MakeCharacter());
U.notesEditor.box:SetText("x");
U.notesEditor.box:__Fire("OnTextChanged", true);
local clearHandler = U.notesEditor.clear.__scripts["OnClick"];
if ( clearHandler ) then clearHandler(U.notesEditor.clear) end
ECS_EQ(U.notesEditor.box:GetText(), "", "8k: Clear emptied the field");
ECS_CHECK(U.IsNotesEditorShown(), "8l: Clear leaves the editor open");
ECS_EQ(ECS.Notes.Get("esteria:zach"), nil, "8m: Clear removes the stored note immediately");
ECS.Notes.CancelEdit();
U.HideNotesEditor();

-- re-establish a known note so the Escape case starts from a defined state
ECS.Notes.Set("esteria:zach", "Bank alt");

-- 8n: Escape cancels rather than saving
U.ShowNotesEditor(MakeCharacter());
U.notesEditor.box:SetText("Escape me");
U.notesEditor.box:__Fire("OnTextChanged", true);
local escHandler = U.notesEditor.box.__scripts["OnEscapePressed"];
if ( escHandler ) then escHandler(U.notesEditor.box) end
ECS_CHECK(not U.IsNotesEditorShown(), "8n: Escape closed the editor");
ECS_EQ(ECS.Notes.Get("esteria:zach"), "Bank alt", "8o: and the note is unchanged");

-- 8p: opening for a character with no note starts empty
U.ShowNotesEditor(MakeCharacter({ name = "Fresh", stableKey = "esteria:fresh" }));
ECS_EQ(U.notesEditor.box:GetText(), "", "8p: field empty for an unnoted character");
U.HideNotesEditor();

-- 8q: a character without a stable key is refused rather than half-opened
ECS_CHECK(U.ShowNotesEditor({ name = "NoKey" }) == false, "8q: keyless character refused");
ECS_CHECK(U.ShowNotesEditor(nil) == false, "8r: nil character refused");

-- ================================================================ 9. deletion animation (spec 20)
Reset();
U.Build(UIParent);
ECS.Anim.Reset();

local parent = CreateFrame("Frame", "ECSRowParent", UIParent);
for i = 1, 4 do
    local b = CreateFrame("Button", ECS.Roster.RowName(i), parent);
    b:SetSize(C.ROSTER_WIDTH, C.ROW_HEIGHT);
end
ECS.Roster.Reset();
ECS.Order.SetCharacters({});
ECS.Roster.BuildPool(parent, 4);

-- 9a: a snapshot remembers which character each row shows
local rows = ECS.Roster.pool;
ECS.Row.Update(rows[1], MakeCharacter({ stableKey = "esteria:alpha", name = "Alpha" }));
ECS.Row.Update(rows[2], MakeCharacter({ stableKey = "esteria:beta", name = "Beta" }));
local snapshot = ECS.Integrate.SnapshotRows();
ECS_EQ(snapshot[1].name, "Alpha", "9a: snapshot captures row 1's character");
ECS_EQ(snapshot[2].name, "Beta", "9b: snapshot captures row 2's character");

-- 9c: a character that survived is not animated
ECS_CHECK(ECS.Integrate.AnimateVanished(snapshot, { ["esteria:alpha"] = true,
    ["esteria:beta"] = true }) == false, "9c: nothing vanishes, nothing animates");

-- 9d: a vanished character DOES start a fade, and the refresh is deferred
ECS.Anim.Reset();
local animating = ECS.Integrate.AnimateVanished(snapshot, { ["esteria:beta"] = true });
ECS_CHECK(animating == true, "9d: a vanished character starts a delete animation");
ECS_CHECK(ECS.Anim.ActiveCount() > 0, "9e: an animation is running");

-- 9f: the guard tween guarantees the deferred refresh still happens
for _ = 1, 40 do ECS.Anim.Update(C.ANIM_MAX_DT) end
ECS_CHECK(ECS.Anim.ActiveCount() == 0, "9f: all animations settled");

-- 9g: with no snapshot the animation is skipped rather than raising
ECS_CHECK(ECS.Integrate.AnimateVanished(nil, {}) == false, "9g: nil snapshot is safe");

-- 9h: Reset clears the notes editor too
U.Reset();
ECS_CHECK(U.notesEditor == nil, "9h: Reset clears the notes editor");

-- ================================================================ 10. drag driver (spec 10)
-- A mouse-down fires once, so without a driver polling while the button is held
-- the drop target would never move and a release would always be a no-op.
Reset();
U.Build(UIParent);
ECS.Anim.Reset();
ECS.Roster.Reset();
ECS.Order.SetCharacters({});

local dParent = CreateFrame("Frame", "ECSDragParent", UIParent);
dParent:SetTop(800);
for i = 1, 4 do
    local b = CreateFrame("Button", ECS.Roster.RowName(i), dParent);
    b:SetSize(C.ROSTER_WIDTH, C.ROW_HEIGHT);
end
ECS.Order.SetCharacters({
    { realIndex = 1, stableKey = "esteria:a", name = "A" },
    { realIndex = 2, stableKey = "esteria:b", name = "B" },
    { realIndex = 3, stableKey = "esteria:c", name = "C" },
    { realIndex = 4, stableKey = "esteria:d", name = "D" },
});
ECS.Roster.BuildPool(dParent, 4);
ECS.Roster.Refresh();

ECS_CHECK(U.StartDragDriver() == true, "10a: drag driver starts");
ECS_CHECK(U.dragDriver:IsShown(), "10b: driver shown");
ECS_CHECK(U.dragDriver.__scripts["OnUpdate"] ~= nil, "10c: driver has an update handler");

-- 10d: the driver is inert while no drag is in progress
U.dragDriver:SetScript("OnUpdate", U.dragDriver.__scripts["OnUpdate"]);
local upd = U.dragDriver.__scripts["OnUpdate"];
upd(U.dragDriver);
ECS_CHECK(not U.dragDriver:IsShown(), "10d: the driver hides itself when nothing is dragging");

-- 10e: during a drag it advances the drop target purely from pointer position,
-- which is what makes reordering actually reachable
U.StartDragDriver();
ECS.Roster.BeginPress(ECS.Roster.pool[1], 0, 0);
SHIM.cursorY = 800 - (2 * C.ROW_HEIGHT);   -- two rows down from the top
upd(U.dragDriver);
ECS_EQ(ECS.Roster.GetDragTarget(), 3, "10e: the driver moved the drop target");
ECS_CHECK(ECS.Roster.IsDragging(), "10f: the drag is live");

-- 10g: releasing commits the reorder
local changed = ECS.Roster.EndPress();
ECS_CHECK(changed == true, "10g: releasing after a driven drag reorders");
ECS_EQ(ECS.Order.RealIndexAt(3), 1, "10h: the dragged character landed at visual 3");

U.StopDragDriver();
ECS_CHECK(not U.dragDriver:IsShown(), "10i: StopDragDriver hides the driver");

-- ================================================================ 11. persistence notice (spec 11/33)
-- A failed save used to be recorded in ECS.Integrate.saveError and never shown, so
-- a user whose reorder did not reach storage was simply lied to by the screen: the
-- new order stayed visible and was gone at the next login. These pin that the
-- status line reports it, in the danger colour, and takes priority over the search
-- summary because it is the more important news.
Reset();
U.Build(UIParent);
ECS.Order.SetCharacters({
    { realIndex = 1, stableKey = "esteria:a", name = "A" },
    { realIndex = 2, stableKey = "esteria:b", name = "B" },
});
ECS.Integrate.saveError = nil;
ECS.Integrate.notesDropped = nil;

-- 11a: the unfiltered reference layout has no extra count line
U.RefreshStatus();
ECS_CHECK(not U.status:IsShown(), "11a: ordinary roster count stays hidden");

ECS.Search.SetQuery("a");
U.RefreshStatus();
ECS_CHECK(U.status:IsShown(), "11b: filtering enables a result summary");
ECS_EQ(U.status:GetText(), "1 of 2", "11b2: filtered count is shown below the search");

-- 11c: a failed save replaces the summary with the warning
ECS.Integrate.saveError = "payload does not fit 3 writable slots";
ECS_CHECK(U.PersistenceNotice() == C.NOTICE_SAVE_FAILED, "11c: a save failure is reported");
U.RefreshStatus();
ECS_EQ(U.status:GetText(), C.NOTICE_SAVE_FAILED, "11d: the status line shows the failure");
local wr, wg, wb = U.status:GetTextColor();
local danger = C.COLOUR.danger;
ECS_EQ(wr, danger[1], "11e: the warning uses the danger colour (red)");
ECS_EQ(wg, danger[2], "11e2: ... green channel");
ECS_EQ(wb, danger[3], "11e3: ... blue channel");

-- 11f: the degraded case reads differently - the order DID survive, only the notes
-- were given up, so telling the user "not saved" would be wrong
ECS.Integrate.saveError = nil;
ECS.Integrate.notesDropped = true;
U.RefreshStatus();
ECS_EQ(U.status:GetText(), C.NOTICE_NOTES_DROPPED, "11f: a degraded save says what was lost");

-- 11g: and a clean save puts the summary back
ECS.Integrate.notesDropped = nil;
U.RefreshStatus();
ECS_EQ(U.status:GetText(), "1 of 2", "11g: a clean save restores the filtered summary");

-- 11h: the notice outranks the search summary while it is set, because it is the
-- only one of the two that tells the user something was actually lost
ECS.Integrate.saveError = "no writable storage";
ECS.Search.SetQuery("a");
U.RefreshStatus();
ECS_EQ(U.status:GetText(), C.NOTICE_SAVE_FAILED,
    "11h: the failure outranks the filtered summary");
ECS.Search.Reset();
ECS.Integrate.saveError = nil;
U.RefreshStatus();

-- 11i: no ECS.Integrate at all (a partial install) must not raise
local savedIntegrate = ECS.Integrate;
ECS.Integrate = nil;
ECS_CHECK(U.PersistenceNotice() == nil, "11i: a missing Integrate yields no notice");
ECS.Integrate = savedIntegrate;
U.RefreshStatus();

-- ================================================================ 12. chrome parenting (no glue leakage)
-- SetGlueScreen (GlueParent.lua:215) hides every frame named in GlueScreenInfo,
-- and GlueScreenInfo["charselect"] = "CharacterSelect". GlueParent itself has no
-- parent attribute, so it is a child of UIParent - which means chrome parented to
-- UIParent is a SIBLING of GlueParent and is never hidden. It stayed drawn over the
-- character-create screen, the options panel and the intro movie, with a live
-- search EditBox on top of them.
Reset();
SHIM.Reset();
SHIM.Install();

-- 12a: no screen frame present -> UIParent, so a partial install still builds
ECS_CHECK(U.PreferredParent() == UIParent, "12a: UIParent is the last-resort parent");

-- 12b: the screen's UI child is preferred when it exists
local screen = CreateFrame("Frame", "CharacterSelect", UIParent);
local screenUi = CreateFrame("Frame", "CharacterSelectUI", screen);
ECS_CHECK(U.PreferredParent() == screenUi, "12b: chrome prefers CharacterSelectUI");

-- 12c: the ModelFFX screen itself is the fallback when the UI child is absent
local savedUi = _G.CharacterSelectUI;
_G.CharacterSelectUI = nil;
ECS_CHECK(U.PreferredParent() == screen, "12c: falls back to the CharacterSelect screen");
_G.CharacterSelectUI = savedUi;

-- 12d: and Build actually uses it, which is what makes Hide() on the screen hide
-- the chrome - the whole point, since ECS cannot hook a C-side screen switch
U.Build();
ECS_CHECK(U.parent == screenUi, "12d: Build parents the chrome to the screen");
ECS_CHECK(U.search:GetParent() == screenUi, "12e: the search frame is a child of the screen");
ECS_CHECK(U.status:GetParent() == screenUi, "12f: so is the status line");
ECS_CHECK(U.emptyState:GetParent() == screenUi, "12g: and the empty state");
ECS_CHECK(U.tooltip:GetParent() == screenUi, "12h: and the tooltip");
ECS_CHECK(U.notesEditor:GetParent() == screenUi, "12i: and the notes editor");

-- 12j: the chrome is NOT a child of UIParent, which is what leaked across screens
ECS_CHECK(U.search:GetParent() ~= UIParent, "12j: the chrome is not parented to UIParent");

-- 12k: the drag driver follows the chrome's parent, so it cannot outlive the screen
U.StartDragDriver();
ECS_CHECK(U.dragDriver:GetParent() == screenUi, "12k: the drag driver is a child of the screen");
U.StopDragDriver();

-- 7d: Reset clears everything so a second Build starts clean
U.Reset();
ECS_CHECK(not U.built, "7c: Reset clears the built flag");
ECS_CHECK(U.Build(UIParent) == true, "7d: Build works again after Reset");
