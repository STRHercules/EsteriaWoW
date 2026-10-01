-- ============================================================
-- Freeborn third player team: character-creation selection.
--
-- This block also paints the Freeborn emblem beside a Freeborn
-- character's name on the character-select screen.
--
-- The Freeborn choice is NOT carried by the create packet. The only
-- create field Lua can influence is the name, and a Freeborn name has
-- to follow exactly the same rules as an Alliance or Horde one, so the
-- name is sent untouched and the selection is recorded for the in-world
-- addon `Interface/AddOns/FreebornClaim`, which claims it once the
-- character exists. characters.teamId stays the only source of truth.
--
-- LOAD ORDER: the XML creates the CharacterCreate frame AFTER this
-- file has been executed, so nothing here may touch a frame at load
-- time. A top-level `CharacterCreate.selectedFreeborn = ...` is a nil
-- index, and because it aborts the whole chunk it also prevents every
-- function below from being defined -- leaving the button
-- unpositioned and untextured. Every frame access lives inside a
-- function; the selection state is created on first use.
--
-- GlueXML.toc loads CharacterSelect.xml before CharacterCreate.xml, so by
-- the time this block runs the select screen's globals already exist and
-- can be wrapped here without touching Interface/GlueXML/CharacterSelect.lua.
--
-- THREE RULES THIS SCREEN FORCES, all learned the hard way:
--
--   1. `GetCVar`/`SetCVar` raise "Couldn't find CVar named '<x>'" for any
--      name the client does not already know. Never call either outside
--      pcall -- an uncaught glue error here takes the create screen down
--      and can crash the client.
--   2. An argument is evaluated BEFORE pcall is entered, so
--      `pcall(f, builder())` does NOT protect the builder. Do the work
--      inside the pcall, or pcall the builder separately.
--   3. Only names the engine registers at the login screen are writable.
--      Being present in Config.wtf does not imply SetCVar accepts it, and
--      a cvar is free to store a value as 0/1 -- which is why the record
--      is judged live rather than assumed.
-- ============================================================
if not CharacterFreeborn_Init then
    CharacterFreeborn_Init = true;

    -- Cvar names this client accepts, used to carry the hash of the chosen name from here to the
    -- world. This only has to survive within one session -- the create screen and the login that
    -- claims it are the same client run -- so a cvar the client rewrites at startup is fine here.
    CharacterFreeborn_CarrierCVars = { "readTOS" };

    -- Where the emblem records live. This must survive a client restart, because the emblem is read
    -- on the character-select screen at the START of the next session, and every integer cvar tried
    -- was normalised when the client loaded it: readTOS and readEULA became "1", and gameTip had a
    -- record clipped to a valid tip index (the value was on disk, but not what the client loaded).
    -- So the store has to be a STRING cvar the client never parses. These two are voice-chat device
    -- names, and voice chat does not exist in 3.3.5, so arbitrary text there is inert. Because they
    -- are strings, one of them holds every Freeborn record at once.
    -- Dedicated restart-persistent badge slot. ECS deliberately does not use
    -- Sound_VoiceChatInputDriverName anymore; sharing it caused recursive
    -- fb:/ecsN: wrapping and eventual Config.wtf corruption.
    CharacterFreeborn_BadgeCVars = { "Sound_VoiceChatInputDriverName" };
    CharacterFreeborn_BadgeMarker = "fb:";

    -- The stock slot is 60x60. The Alliance/Horde crests sit inside their artwork, while the
    -- Freeborn plate fills its image edge to edge, so it reads larger at the same size. Draw it
    -- smaller inside the very same 60x60 box (centred on it) so the three match.
    CharacterFreeborn_BadgeSize = 44;

    -- A record is 1000000000 + (hash % 1000000000): always exactly ten digits, always below
    -- INT_MAX, and never confusable with a cvar's own resting value ("1", "76", "0"). This client
    -- rejects values of other shapes -- a "fb:"-prefixed string was silently refused -- so a plain
    -- number is the only shape proven to survive. Must match the addon's copy.
    CharacterFreeborn_RecordBase = 1000000000;
    CharacterFreeborn_RecordMod = 1000000000;

    CharacterFreeborn_BadgeTexture = "Interface\\Glues\\CharacterSelect\\FreebornLogo";

    function CharacterFreeborn_IsSelected()
        return CharacterCreate ~= nil and CharacterCreate.selectedFreeborn == true;
    end

    -- Every CVar access goes through these two. On this client an unknown name is a hard error.
    function CharacterFreeborn_SafeGet(name)
        local ok, value = pcall(GetCVar, name);
        if ( not ok ) then
            return nil;
        end
        return value;
    end

    function CharacterFreeborn_SafeSet(name, value)
        local ok = pcall(SetCVar, name, value);
        return ok and true or false;
    end

    -- Small non-cryptographic hash, so the choice can ride cvars the client parses as numbers.
    -- Must stay identical to the addon's copy.
    function CharacterFreeborn_NameHash(name)
        local hash = 0;
        local lowered = strlower(name or "");
        for i = 1, strlen(lowered) do
            hash = (hash * 31 + strbyte(lowered, i)) % 2147483647;
        end
        return hash;
    end

    function CharacterFreeborn_UpdateButton()
        local button = CharacterCreateFreebornButton;
        if ( not button ) then
            return;
        end

        if ( CharacterFreeborn_IsSelected() ) then
            button:SetChecked(1);
        else
            button:SetChecked(nil);
        end

        if ( button.checkedTexture ) then
            if ( CharacterFreeborn_IsSelected() ) then
                button.checkedTexture:Show();
            else
                button.checkedTexture:Hide();
            end
        end
    end

    function CharacterFreeborn_SetSelected(selected)
        if ( CharacterCreate == nil ) then
            return;
        end

        CharacterCreate.selectedFreeborn = selected and true or false;
        CharacterFreeborn_UpdateButton();
    end

    function CharacterFreeborn_OnClick(self)
        PlaySound("gsCharacterCreationClass");
        CharacterFreeborn_SetSelected(not CharacterFreeborn_IsSelected());
    end

    -- Hover tooltip for the Freeborn pick. It explains what the pick does, and it wears the same
    -- border as the race tooltips -- same background, same edge texture, same 16px tile and 4px
    -- insets -- so the two read as the same widget. The backdrop is spelled out here rather than
    -- borrowed from the stock `Backdrop2` local: this block is appended to the stock file, and an
    -- unresolved index on the create screen takes the whole screen down. The contract test pins
    -- these values against the stock race-tooltip backdrop so they cannot drift.
    function CharacterFreeborn_GetTooltip()
        local tooltip = CharacterFreebornTooltip;
        if ( tooltip ) then
            return tooltip;
        end

        tooltip = CreateFrame("Frame", "CharacterFreebornTooltip", CharacterCreateFrame);
        tooltip:SetFrameStrata("TOOLTIP");
        tooltip:SetBackdrop({
            bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
            edgeFile = "Interface\\Tooltips\\ui-tooltip-border-maw",
            tile = true, tileSize = 16, edgeSize = 16,
            insets = { left = 4, right = 4, top = 4, bottom = 4 } });
        tooltip:SetBackdropColor(0, 0, 0, 1);
        tooltip:SetWidth(300);

        tooltip.title = tooltip:CreateFontString(nil, "OVERLAY");
        tooltip.title:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE");
        tooltip.title:SetPoint("TOPLEFT", tooltip, "TOPLEFT", 10, -10);
        tooltip.title:SetTextColor(1, 0.82, 0);
        tooltip.title:SetJustifyH("LEFT");
        tooltip.title:SetText("|cFFFFFFFFFreeborn|r");

        tooltip.body = tooltip:CreateFontString(nil, "OVERLAY");
        tooltip.body:SetFont("Fonts\\FRIZQT__.TTF", 10, "OUTLINE");
        tooltip.body:SetPoint("TOPLEFT", tooltip.title, "BOTTOMLEFT", 0, -6);
        tooltip.body:SetWidth(260);
        tooltip.body:SetWordWrap(true);
        tooltip.body:SetJustifyH("LEFT");
        tooltip.body:SetText("|cffffd100Freeborn are free of both the Alliance and the Horde. They swear no "
            .. "allegiance to either, though both have granted them access to their cities.\n\n"
            .. "They may take quests from either faction, and they can group and guild freely with "
            .. "other Freeborn. They can never group or guild with Alliance or Horde characters.\n\n"
            .. "Freeborn and the two factions are completely hostile to one another.|r");

        CharacterFreebornTooltip = tooltip;
        return tooltip;
    end

    -- The stock race tooltip sizes itself from its wrapped text, so this does the same: the body
    -- has to be laid out before its height means anything.
    function CharacterFreeborn_UpdateTooltipSize(tooltip)
        tooltip:SetHeight(tooltip.title:GetHeight() + tooltip.body:GetHeight() + 26);
    end

    function CharacterFreeborn_HideTooltip()
        if ( CharacterFreebornTooltip ) then
            CharacterFreebornTooltip:Hide();
        end
    end

    -- Sit the tooltip above the plate, clear of the button's own "Freeborn" label.
    function CharacterFreeborn_OnEnter(self)
        local tooltip = CharacterFreeborn_GetTooltip();
        CharacterFreeborn_UpdateTooltipSize(tooltip);
        tooltip:ClearAllPoints();
        tooltip:SetPoint("BOTTOM", self, "TOP", 0, 24);
        tooltip:Show();
    end

    function CharacterFreeborn_OnLeave(self)
        CharacterFreeborn_HideTooltip();
    end

    -- The Freeborn pick is a plain plate: no round border ring, unlike the gender picks. Only the
    -- checked ring is kept, and only while Freeborn is actually selected, as click feedback.
    local freeborn_originalGenderTextures = CharacterCreate_CreateGenderButtonTextures;
    function CharacterCreate_CreateGenderButtonTextures(...)
        freeborn_originalGenderTextures(...);

        local button = CharacterCreateFreebornButton;
        if ( button and not button.highlightTexture ) then
            button.staticTexture = button:CreateTexture(button:GetName().."StaticTexture", "ARTWORK");
            button.staticTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
            button.staticTexture:SetAlpha(0);
            button.staticTexture:SetSize(86, 86);
            button.staticTexture:SetPoint("CENTER", 0, 0);

            button.highlightTexture = button:CreateTexture(button:GetName().."HighlightTexture", "HIGHLIGHT");
            button.highlightTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorder_F1");
            button.highlightTexture:SetAlpha(0);
            button.highlightTexture:SetBlendMode("ADD");
            button.highlightTexture:SetSize(86, 86);
            button.highlightTexture:SetPoint("CENTER", 0, 0);

            button.checkedTexture = button:CreateTexture(button:GetName().."CheckedTexture", "OVERLAY");
            button.checkedTexture:SetDrawLayer("OVERLAY", 7);
            button.checkedTexture:SetTexture("Interface\\Glues\\CharacterCreate\\IconBorderRace_H");
            button.checkedTexture:SetBlendMode("ADD");
            button.checkedTexture:SetSize(86, 86);
            button.checkedTexture:SetPoint("CENTER", 0, 0);
            button.checkedTexture:Hide();

            button:SetScript("OnMouseDown", nil);
            button:SetScript("OnMouseUp", nil);
        end

        CharacterFreeborn_UpdateButton();
    end

    -- Sit the Freeborn pick between the two gender picks. It chooses a team,
    -- never a gender, so it never calls SetSelectedSex. The XML anchors it in the
    -- same place, so a wrapper that never ran would still leave it visible.
    local freeborn_originalPositionGenderButtons = CharacterCreate_PositionGenderButtons;
    function CharacterCreate_PositionGenderButtons(...)
        freeborn_originalPositionGenderButtons(...);

        local button = CharacterCreateFreebornButton;
        if ( button ) then
            button:ClearAllPoints();
            button:SetPoint("CENTER", CharacterCreateFrame, "CENTER", 0, -250);
            if ( PAID_SERVICE_TYPE ) then
                CharacterFreeborn_HideTooltip();
                button:Hide();
            else
                button:Show();
            end
        end
    end

    -- Race/gender clicks re-run this, so an explicit Freeborn selection is kept
    -- across race and gender changes until the player deselects it.
    local freeborn_originalUpdateButtonCheckedStates = CharacterCreate_UpdateButtonCheckedStates;
    function CharacterCreate_UpdateButtonCheckedStates(...)
        freeborn_originalUpdateButtonCheckedStates(...);
        CharacterFreeborn_UpdateButton();
    end

    -- A fresh visit to the create screen starts on the race's native team.
    local freeborn_originalOnShow = CharacterCreate_OnShow;
    function CharacterCreate_OnShow(...)
        CharacterFreeborn_SetSelected(false);
        CharacterFreeborn_HideTooltip();
        freeborn_originalOnShow(...);
        CharacterFreeborn_UpdateButton();
    end

    -- Record the choice for the addon, then run the stock accept path so the name reaches the
    -- server exactly as typed. Nothing here may raise. The record is written ONLY when Freeborn
    -- was chosen: an intervening native creation must not wipe an unclaimed choice, and a stale
    -- record cannot claim a later character because the addon also matches the name's hash.
    local freeborn_originalOkay = CharacterCreate_Okay;
    function CharacterCreate_Okay(...)
        local pending = "";
        if ( CharacterFreeborn_IsSelected() and not PAID_SERVICE_TYPE ) then
            if ( CharacterCreate_GetFullName ) then
                pending = CharacterCreate_GetFullName();
            else
                pending = CharacterCreateNameEdit:GetText();
            end
        end

        if ( pending ~= "" ) then
            local record = CharacterFreeborn_RecordFor(pending);
            for _, name in ipairs(CharacterFreeborn_CarrierCVars) do
                CharacterFreeborn_SafeSet(name, tostring(record));
            end
            -- Record the emblem here as well as from the addon on claiming. This screen can write
            -- cvars the world state refuses (readEULA is refused there), so the badge does not
            -- depend on that, and a record always claims a name, never a character that is not it.
            CharacterFreeborn_StoreBadge(record);
        end

        return freeborn_originalOkay(...);
    end

    -- The value the addon parks for a character, and the value this screen looks for.
    function CharacterFreeborn_RecordFor(name)
        return CharacterFreeborn_RecordBase + CharacterFreeborn_NameHash(name) % CharacterFreeborn_RecordMod;
    end

    -- The record format is "fb:<record>,<record>,...|<whatever the cvar held before>", so the
    -- client's own value is preserved behind the bar and all Freeborn records share one cvar.

    -- The hashes of every character the addon has claimed as Freeborn.
    function CharacterFreeborn_BadgeHashes()
        local hashes = {};
        local mark = strlen(CharacterFreeborn_BadgeMarker);

        for _, cvar in ipairs(CharacterFreeborn_BadgeCVars) do
            local stored = CharacterFreeborn_SafeGet(cvar);
            if ( type(stored) == "string" and strsub(stored, 1, mark) == CharacterFreeborn_BadgeMarker ) then
                local body = strsub(stored, mark + 1);
                local bar = strfind(body, "|", 1, true);
                if ( bar ) then
                    body = strsub(body, 1, bar - 1);
                end
                for digits in string.gmatch(body, "%d+") do
                    hashes[digits] = true;
                end
            end
        end

        return hashes;
    end

    -- Add this character's record to the first cvar that will take it, keeping whatever that cvar
    -- already held. Returns the cvar, or nil when no cvar would accept the write.
    function CharacterFreeborn_StoreBadge(record)
        local wanted = tostring(record - CharacterFreeborn_RecordBase);
        local mark = strlen(CharacterFreeborn_BadgeMarker);

        for _, cvar in ipairs(CharacterFreeborn_BadgeCVars) do
            local stored = CharacterFreeborn_SafeGet(cvar);
            if ( type(stored) ~= "string" ) then
                stored = "";
            end

            local original = stored;
            local body = "";
            if ( strsub(stored, 1, mark) == CharacterFreeborn_BadgeMarker ) then
                body = strsub(stored, mark + 1);
                local bar = strfind(body, "|", 1, true);
                if ( bar ) then
                    original = strsub(body, bar + 1);
                    body = strsub(body, 1, bar - 1);
                else
                    original = "";
                end
            end

            local list = {};
            for digits in string.gmatch(body, "%d+") do
                if ( digits == wanted ) then
                    return cvar;
                end
                list[#list + 1] = digits;
            end
            list[#list + 1] = wanted;

            CharacterFreeborn_SafeSet(cvar,
                CharacterFreeborn_BadgeMarker .. table.concat(list, ",") .. "|" .. original);

            local check = CharacterFreeborn_SafeGet(cvar);
            if ( type(check) == "string" and strsub(check, 1, mark) == CharacterFreeborn_BadgeMarker
                and strfind(check, wanted, 1, true) ) then
                return cvar;
            end
        end

        return nil;
    end

    -- Paint the Freeborn emblem over the Alliance/Horde logo for those characters. The stock list
    -- creates one FactionIcon texture per visible button and tags its button with the character's
    -- index, so the match is name-hash against the badge record.
    function CharacterFreeborn_ApplyBadges()
        if ( CharacterSelect == nil ) then
            return;
        end

        local hashes = CharacterFreeborn_BadgeHashes();
        if ( not next(hashes) ) then
            return;
        end

        for index = 1, ( MAX_CHARACTERS_DISPLAYED or 8 ) do
            local button = _G["CharSelectCharacterButton"..index];
            local icon = _G["CharSelectCharacterButton"..index.."FactionIcon"];
            if ( button and icon ) then
                local id = button:GetID() or 0;
                local name = nil;
                if ( id > 0 ) then
                    local ok, value = pcall(GetCharacterInfo, id);
                    if ( ok and type(value) == "string" ) then
                        name = value;
                    end
                end

                if ( name and hashes[tostring(CharacterFreeborn_RecordFor(name) - CharacterFreeborn_RecordBase)] ) then
                    -- The stock slot is anchored TOPLEFT (170,-5) at 60x60; keep the same centre.
                    icon:ClearAllPoints();
                    icon:SetPoint("CENTER", button, "TOPLEFT", 200, -35);
                    icon:SetSize(CharacterFreeborn_BadgeSize, CharacterFreeborn_BadgeSize);
                    icon:SetTexture(CharacterFreeborn_BadgeTexture);
                    icon:Show();
                end
            end
        end
    end

    local freeborn_originalUpdateCharacterList = UpdateCharacterList;
    function UpdateCharacterList(...)
        freeborn_originalUpdateCharacterList(...);
        pcall(CharacterFreeborn_ApplyBadges);
    end

    local freeborn_originalSelectOnEvent = CharacterSelect_OnEvent;
    function CharacterSelect_OnEvent(self, event, ...)
        freeborn_originalSelectOnEvent(self, event, ...);
        pcall(CharacterFreeborn_ApplyBadges);
    end
end
