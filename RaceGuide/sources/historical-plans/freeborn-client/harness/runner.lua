-- Drives the deployed block through the real call order and reports what it did.

print("== MODE=" .. MODE .. " INFO_COUNT=" .. tostring(INFO_COUNT) .. " ==");

-- the stock positioning pass runs before anything is clicked
CharacterCreate_PositionGenderButtons();
CharacterCreate_CreateGenderButtonTextures();
print("stock: positionGender=" .. tostring(STOCK.positionGender) ..
    " genderTextures=" .. tostring(STOCK.genderTextures));

CharacterCreate_OnShow();
print("stock: onShow=" .. tostring(STOCK.onShow) .. " (wrapper must delegate)");

if ( SKIP_CLICK ) then
    print("--- Freeborn NOT clicked: nothing may be recorded ---");
else
    CharacterFreeborn_OnClick();
end
print("selected=" .. tostring(CharacterCreate.selectedFreeborn));

-- The hover tooltip: built lazily, wearing the race tooltips' border, sized from its text, and
-- gone again on mouse-out, on a fresh visit to the screen, and behind the paid-service screen.
CharacterFreeborn_OnEnter(CharacterCreateFreebornButton);
local tip = CharacterFreebornTooltip;
print("tooltip: shown=" .. tostring(tip and tip.shown) ..
    " strata=" .. tostring(tip and tip.strata) ..
    " parent=" .. tostring(tip and tip.parent and tip.parent.name) ..
    " size=" .. tostring(tip and tip.width) .. "x" .. tostring(tip and tip.height) ..
    " edge=" .. tostring(tip and tip.backdrop and tip.backdrop.edgeFile) ..
    " tile=" .. tostring(tip and tip.backdrop and tip.backdrop.edgeSize) ..
    " color=" .. tostring(tip and tip.backdropColor and table.concat(tip.backdropColor, ",")));
print("tooltip title: " .. tostring(tip and tip.title and tip.title.text));
print("tooltip body : " .. tostring(tip and tip.body and tip.body.text));
CharacterFreeborn_OnLeave(CharacterCreateFreebornButton);
print("tooltip after leave: shown=" .. tostring(tip and tip.shown));
CharacterFreeborn_OnEnter(CharacterCreateFreebornButton);
print("second hover rebuilt a new frame? " .. tostring(CharacterFreeborn_GetTooltip() ~= tip));
print("tooltip after second hover: shown=" .. tostring(tip and tip.shown));
CharacterCreate_OnShow();
print("tooltip after a fresh visit: shown=" .. tostring(tip and tip.shown));
CharacterCreate_PositionGenderButtons();
print("tooltip after positioning pass: shown=" .. tostring(tip and tip.shown));

TYPED_NAME = "Dobb";
CharacterCreate_Okay();
print("stock: okay=" .. tostring(STOCK.okay));

-- What the create screen itself left behind, before the badge test below overwrites anything.
local afterOkay = {};
for _, cvar in ipairs(CharacterFreeborn_BadgeCVars) do
    afterOkay[#afterOkay + 1] = cvar .. "=" .. tostring(CVARS[cvar]);
end
print("badge slots straight after Okay: " .. table.concat(afterOkay, ", ") ..
    "   (record of Dobb = " .. tostring(CharacterFreeborn_RecordFor("Dobb")) .. ")");

local keys = {};
for name in pairs(CVARS) do
    keys[#keys + 1] = name;
end
table.sort(keys);
print("cvar store now holds: " .. table.concat(keys, ", "));

local armed = {};
for _, carrier in ipairs(CharacterFreeborn_CarrierCVars) do
    armed[#armed + 1] = carrier .. "=" .. tostring(CVARS[carrier]);
end
print("carriers now: " .. table.concat(armed, ", ") ..
    "   hash('Dobb')=" .. tostring(CharacterFreeborn_NameHash("Dobb")));

UpdateCharacterList();
print("stock: updateList=" .. tostring(STOCK.updateList));

-- The badge: store Dobb's record the way the addon does, and only Dobb's icon may change.
local record = CharacterFreeborn_RecordFor("Dobb");
local slot = CharacterFreeborn_StoreBadge(record);
print("StoreBadge(" .. tostring(record) .. ") -> " .. tostring(slot) ..
    "   value='" .. tostring(slot and CVARS[slot]) .. "'");
UpdateCharacterList();
for index = 1, #CHARACTERS do
    local icon = _G["CharSelectCharacterButton" .. index .. "FactionIcon"];
    print("  icon " .. index .. " (" .. CHARACTERS[index] .. ") -> " .. tostring(icon and icon.texture));
end
local diag = _G["CharacterFreebornDiag"];
print("diag line: " .. tostring(diag and diag.text and diag.text.text));

-- The shape that silently failed in the field must be refused by this model.
local ok, err = pcall(SetCVar, slot, "fb:" .. record);
print("wrong-shaped record accepted? " .. tostring(ok) .. "  (" .. tostring(err) .. ")");
print("== done ==");
