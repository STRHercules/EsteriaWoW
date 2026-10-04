--[[ ECS_Integrate.lua -----------------------------------------------------------
    Esteria Character Select - wiring ECS into the live glue screen.

    STRATEGY: WRAP, DO NOT REWRITE.

    The deployed CharacterSelect.lua is heavily customised (retail-interface fork
    plus the Esteria race work) and two live contracts depend on it:

      * tools/test_character_select_contract.py pins exact strings inside it;
      * CharacterCreate.lua's Freeborn wrapper re-wraps UpdateCharacterList and
        reaches into the row buttons by name.

    So ECS changes nothing in that file's binding logic. Instead it wraps
    UpdateCharacterList the same way the Freeborn code already does: the stock
    binding runs first (keeping every pinned string and the scroll maths intact),
    then ECS re-skins the rows and, when a custom order or a search filter is
    active, re-points them at the correct REAL character indices.

    With no order and no filter the two agree, so ECS is a pure visual layer.

    Loaded LAST in GlueXML.toc, after CharacterSelect.xml and CharacterCreate.xml,
    so every global it wraps already exists.

    Lua 5.1 only.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};

local I = ECS.Integrate or {};
ECS.Integrate = I;

local C = ECS.Const;
local O = ECS.Order;

I.poolBuilt = false;
I.installed = false;
I.loadedStore = false;
I.applying = false;      -- recursion guard: our writes must not re-enter
I.syncing = false;       -- recursion guard for selection
I.data = I.data or {};
I.slots = I.slots or nil;

-- ---------------------------------------------------------------- client access
-- Everything the client might not expose is probed rather than assumed.
local function SafeCall(fn, ...)
    if ( type(fn) ~= "function" ) then
        return nil;
    end
    local ok, value = pcall(fn, ...);
    if ( not ok ) then
        return nil;
    end
    return value;
end

function I.RealmName()
    local name = SafeCall(_G.GetRealmName);
    if ( type(name) == "string" and name ~= "" ) then
        return name;
    end
    return "";
end

function I.RealmLabel()
    local name, isPVP, isRP;
    if ( type(_G.GetServerName) == "function" ) then
        local ok, serverName, pvp, rp = pcall(_G.GetServerName);
        if ( ok ) then
            name, isPVP, isRP = serverName, pvp, rp;
        end
    end

    if ( type(name) ~= "string" or name == "" ) then
        return I.RealmName();
    end

    local serverType = nil;
    if ( isPVP ) then
        if ( isRP ) then
            serverType = _G.RPPVP_PARENTHESES;
        else
            serverType = _G.PVP_PARENTHESES;
        end
    elseif ( isRP ) then
        serverType = _G.RP_PARENTHESES;
    end

    local connected = SafeCall(_G.IsConnectedToServer);
    if ( connected == false ) then
        local down = _G.SERVER_DOWN;
        if ( type(down) == "string" and down ~= "" ) then
            name = name .. " (" .. down .. ")";
        end
    end

    if ( type(serverType) == "string" and serverType ~= "" ) then
        name = name .. " " .. serverType;
    end
    return name;
end

-- The custom login screen stores username, password, auto-login and scene in
-- GetSavedAccountName(), separated by #&|&#. ECS must scope only by the username:
-- treating the whole packed credential record as the account key duplicated the
-- password into unrelated persistence CVars and made the ECS identity change when
-- any login preference changed. With a stock client this still returns the whole
-- value because there is no delimiter.
function I.AccountName()
    local name = SafeCall(_G.GetSavedAccountName);
    if ( type(name) ~= "string" or name == "" ) then
        return nil;
    end

    local delimiter = "#&|&#";
    local split = string.find(name, delimiter, 1, true);
    if ( split ) then
        name = string.sub(name, 1, split - 1);
    end

    if ( name ~= "" ) then
        return name;
    end
    return nil;
end

-- The stock screen can repopulate its visible row pool before the character
-- count getter reflects the new list. Use shown stock row IDs as a guarded count
-- fallback so ECS does not leave its empty state over a populated War Band list.
function I.StockCharacterCount()
    local maximum = 0;
    local poolSize = C.STOCK_ROW_COUNT or C.POOL_SIZE or 10;
    for slot = 1, poolSize do
        local button = _G[ECS.Roster.RowName(slot)];
        if ( button and button.IsShown and button.GetID ) then
            local okShown, shown = pcall(button.IsShown, button);
            if ( okShown and shown ) then
                local okID, realIndex = pcall(button.GetID, button);
                if ( okID and type(realIndex) == "number" and realIndex > maximum ) then
                    maximum = realIndex;
                end
            end
        end
    end
    return maximum;
end

-- ---------------------------------------------------------------- data
function I.BuildData()
    local revision = (I.revision or 0) + 1;
    I.revision = revision;

    local list, skipped = ECS.Data.BuildList({
        numCharacters = function()
            local count = SafeCall(_G.GetNumCharacters);
            if ( type(count) == "number" and count > 0 ) then
                return count;
            end
            return I.StockCharacterCount();
        end,
        characterInfo = function(index)
            local fields = {_G.GetCharacterInfo(index)};
            if type(CycleCharCustomization) == "function" then
                local ok,race,gender = pcall(CycleCharCustomization,"EA_SELECT",index);
                if ok and (race == 45 or race == 46 or race == 47 or race == 48 or race == 49 or race == 50 or race == 51 or race == 52 or race == 53 or (race >= 54 and race <= 59)) then
                    fields[2] = race;
                    fields[6] = gender + 2;
                end
            end
            return unpack(fields,1,10);
        end,
        backgroundModel = function(index)
            -- the fork's own API; the authoritative per-character race signal
            return SafeCall(_G.GetSelectBackgroundModel, index);
        end,
        realmName = function() return I.RealmName(); end,
        freebornHashes = function() return ECS.Schema.FreebornHashes(); end,
        revision = revision,
    });

    ECS.Data.ApplyNotes(list, ECS.Notes.Export());
    I.data = list;
    I.skipped = skipped;
    I.dataCount = #list;
    return list, skipped;
end

-- ---------------------------------------------------------------- persistence
function I.EnsureSlots()
    if ( I.slots ) then
        return I.slots;
    end
    I.slots = ECS.Persistence.ProbeCandidates();

    -- Measure how much each cvar will actually hold, rather than assuming. The
    -- real per-cvar limit is not discoverable offline, and the conservative
    -- default is not big enough for a full 100-character order (8 shards against
    -- 6 slots), so on a client whose cvars hold more, this is what makes a large
    -- roster's order persist at all. pcall-guarded because a probe touches every
    -- slot and a failure there must not stop the screen from loading.
    pcall(ECS.Persistence.ProbeCapacity, I.slots);

    return I.slots;
end

function I.LoadStore()
    if ( I.loadedStore ) then
        return false;
    end
    I.loadedStore = true;

    local slots = I.EnsureSlots();
    if ( not slots or #slots == 0 ) then
        return false, "no writable storage";
    end

    local store, reason = ECS.Persistence.Load(I.AccountName(), I.RealmName(), slots);
    if ( not store ) then
        return false, reason;
    end

    O.SetCustomOrder(store.order);
    ECS.Notes.Replace(store.notes);
    return true;
end

function I.SaveStore()
    local slots = I.EnsureSlots();
    if ( not slots or #slots == 0 ) then
        I.saveError = "no writable storage";
        return false, I.saveError;
    end
    local store = ECS.Persistence.MakeStore(
        I.AccountName(), I.RealmName(), O.GetCustomOrder(), ECS.Notes.Export());

    -- Degradation is write-side, because capacity is the failure that actually
    -- happens: notes dominate the payload and there are only a handful of
    -- writable cvars. The order must survive even when the notes cannot, so this
    -- gives up the notes rather than the reorder the user just performed.
    local saved, reason, droppedNotes = ECS.Persistence.SaveDegraded(store, slots);

    -- Keep the in-memory state honest about what is actually on disk. Leaving
    -- notes in memory after they were sacrificed would show the user notes that
    -- are guaranteed to vanish, which is the same "silently saved nothing"
    -- defect the notes editor already had once.
    if ( saved and droppedNotes ) then
        ECS.Notes.Replace({});
        pcall(I.Refresh);
    end

    I.saveError = saved and nil or reason;
    I.notesDropped = saved and droppedNotes or nil;

    -- Every save path reports through here, so this is the one place that has to
    -- re-render the status line. Without it a failed save was recorded and never
    -- shown, which is exactly the silent-failure this notice exists to prevent.
    if ( ECS.UI ) then
        pcall(ECS.UI.RefreshStatus);
    end

    return saved, reason, droppedNotes;
end

-- ---------------------------------------------------------------- roster
function I.HookScrollFrame(frame)
    if ( not frame ) then return false end
    if ( frame.EnableMouseWheel ) then
        pcall(frame.EnableMouseWheel, frame, true);
    end
    if ( frame.SetScript ) then
        -- The XML scroll frame is one pixel wide. Own its wheel and scrollbar
        -- callbacks explicitly; do not depend on the stock server-index list path.
        frame:SetScript("OnMouseWheel", function(_, delta)
            I.ScrollBy(delta);
        end);
        frame:SetScript("OnVerticalScroll", function(_, position)
            ECS.Roster.OnVerticalScroll(position);
        end);
    end
    return true;
end

function I.EnsureRoster()
    local frame = _G.CharacterSelectCharacterScrollFrame;
    if ( not frame ) then
        return false;
    end

    if ( not I.poolBuilt ) then
        -- Build the added chrome once, then only ever update it. It is parented to
        -- the SCREEN (see ECS_UI.PreferredParent) so that SetGlueScreen hiding
        -- CharacterSelect takes the chrome with it - parented to UIParent it stayed
        -- drawn over character creation, the options panel and the intro movie.
        local chromeParent = nil;
        if ( ECS.UI ) then
            chromeParent = ECS.UI.PreferredParent and ECS.UI.PreferredParent() or nil;
            pcall(ECS.UI.Build, chromeParent);
        end

        -- The stock row buttons are children of CharacterSelectCharacterFrame,
        -- whose origin is at the top of the screen. Anchoring them there placed
        -- slot 1 over the search header; ROSTER_TOP existed but was never
        -- applied. Keep the stock parent for visibility and click behavior while
        -- using the screen frame as their explicit visual anchor.
        local layoutParent = (ECS.UI and ECS.UI.parent) or chromeParent
            or _G.CharacterSelectCharacterFrame;
        if ( ECS.Roster.SetLayoutParent ) then
            pcall(ECS.Roster.SetLayoutParent, layoutParent);
        end

        ECS.Roster.BuildPool(nil, C.POOL_SIZE);
        ECS.Roster.SetScrollFrame(frame);
        I.HookScrollFrame(frame);
        if ( #(ECS.Roster.pool or {}) == 0 ) then
            return false;   -- the XML rows are not up yet; try again next refresh
        end
        I.poolBuilt = true;
        I.HookRows();

        if ( ECS.UI ) then
            pcall(ECS.UI.SetRealmName, I.RealmLabel());
            local pool = ECS.Roster.pool or {};
            for index = 1, #pool do
                pcall(ECS.UI.WireRow, pool[index]);
            end
        end
    end
    return true;
end

-- Adopt the stock offset, refresh, then write our clamped value back so the
-- stock scroll maths (maxOffset, clamping, the scrollbar range) stay consistent
-- with what is actually on screen.
function I.Refresh()
    if ( I.applying ) then
        return false;
    end
    if ( not I.EnsureRoster() ) then
        return false;
    end
    pcall(I.SyncSelectionFromStock);

    I.applying = true;
    local ok, reason = pcall(function()
        local select = _G.CharacterSelect;
        if ( select and type(select.scrollOffset) == "number" ) then
            ECS.Roster.offset = ECS.Roster.ClampOffset(
                select.scrollOffset, O.VisibleCount());
        end

        ECS.Roster.Refresh();

        if ( select ) then
            select.scrollOffset = ECS.Roster.GetOffset();
        end
    end);
    I.applying = false;
    if ( not ok ) then
        I.refreshError = tostring(reason);
        return false;
    end
    I.refreshError = nil;
    return true;
end

-- ---------------------------------------------------------------- selection
-- The stock helper treats `selectedIndex` as a visual row number and adjusts
-- scrollOffset in server-index space. Under ECS order/filtering, that can move the
-- viewport to an unrelated part of the list after a character is selected. Keep
-- the current window when the selected character is already visible; only move it
-- when its ECS visual position is actually outside the current page.
function I.AdjustOffsetForSelection()
    local select = _G.CharacterSelect;
    local roster = ECS.Roster;
    if ( not I.poolBuilt or not select or not roster or not roster.ComputeLayout ) then
        return false;
    end

    local realIndex = select.selectedIndex;
    if ( type(realIndex) ~= "number" or realIndex <= 0 ) then
        return true;   -- ECS owns the path; nothing to scroll to
    end

    local visual = O.VisualPosOf(realIndex);
    if ( not visual ) then
        return true;   -- filtered out: preserve the user's current window
    end

    local layout = roster.ComputeLayout(roster.ViewportHeight(), roster.RowHeight());
    local visibleRows = math.max(1, math.ceil(layout.viewportHeight / layout.rowHeight));
    local previous = roster.GetOffset();
    local offset = previous;
    if ( visual <= offset ) then
        offset = visual - 1;
    elseif ( visual > offset + visibleRows ) then
        offset = visual - visibleRows;
    end

    local clamped = roster.ClampOffset(offset, O.VisibleCount(), layout);
    roster.offset = clamped;
    select.scrollOffset = clamped;
    return true, clamped ~= previous;
end

-- Some client paths may still apply the stock offset before the ECS wrapper runs.
-- After a selected-character event, restore the pre-event page when the selected
-- character belonged to it; this is a final guard against server-index scrolling.
function I.PreserveVisibleSelectionOffset(previousOffset)
    local select = _G.CharacterSelect;
    local roster = ECS.Roster;
    previousOffset = tonumber(previousOffset);
    if ( not I.poolBuilt or not select or not roster or previousOffset == nil ) then
        return false;
    end

    local visual = O.VisualPosOf(select.selectedIndex);
    if ( not visual ) then return false end
    local layout = roster.ComputeLayout(roster.ViewportHeight(), roster.RowHeight());
    local visibleRows = math.max(1, math.ceil(layout.viewportHeight / layout.rowHeight));
    if ( visual <= previousOffset or visual > previousOffset + visibleRows ) then
        return false;
    end

    local offset = roster.ClampOffset(previousOffset, O.VisibleCount(), layout);
    if ( roster.GetOffset() == offset ) then return false end
    roster.SetOffset(offset);
    select.scrollOffset = roster.GetOffset();
    return true;
end

-- Sync FROM the stock screen into ECS without echoing back, so the two can never
-- ping-pong. Assignment rather than Select() is deliberate: Select() fires the
-- callback, which would call straight back into CharacterSelect_SelectCharacter.
function I.SyncSelectionFromStock()
    local select = _G.CharacterSelect;
    if ( not select ) then
        return false;
    end
    local index = select.selectedIndex;
    if ( type(index) ~= "number" or index <= 0 ) then
        -- The stock screen has no valid selection (an empty account, or every
        -- character filtered away). Clear ours too: a stale selection would be
        -- styled as selected the moment a character reappears in that slot.
        ECS.Roster.ClearSelection();
        return false;
    end
    local changed = ECS.Roster.selected ~= index;
    ECS.Roster.selected = index;

    -- The stock screen still computes selection visibility for ten buttons. ECS
    -- only renders eight, so move the eight-row window when the selected character
    -- would otherwise be below it.
    local visual = O.VisualPosOf(index);
    local poolSize = ECS.Roster.PoolSize();
    if ( visual and poolSize > 0 ) then
        local offset = ECS.Roster.GetOffset();
        if ( visual <= offset ) then
            offset = visual - 1;
        elseif ( visual > offset + poolSize ) then
            offset = visual - poolSize;
        end
        local layout = ECS.Roster.ComputeLayout(ECS.Roster.ViewportHeight(), ECS.Roster.RowHeight());
        ECS.Roster.offset = ECS.Roster.ClampOffset(offset, O.VisibleCount(), layout);
        select.scrollOffset = ECS.Roster.offset;
    end
    return changed;
end

-- spec 24: the roster's click must drive the real selection.
function I.OnRowSelected(realIndex)
    if ( I.syncing ) then
        return;
    end
    if ( type(realIndex) ~= "number" ) then
        return;
    end
    local select = _G.CharacterSelect;
    if ( select and select.selectedIndex == realIndex ) then
        return;
    end
    I.syncing = true;
    if ( type(_G.CharacterSelect_SelectCharacter) == "function" ) then
        pcall(_G.CharacterSelect_SelectCharacter, realIndex);
    end
    I.syncing = false;
end

-- spec 30: arrow-key navigation walks the VISUAL order, so it stays correct
-- under a custom order or an active filter.
function I.StepSelection(direction)
    local visibleCount = O.VisibleCount();
    if ( visibleCount < 1 ) then
        return false;
    end
    local current = ECS.Roster.selected;
    local position = current and O.VisualPosOf(current) or nil;

    if ( not position ) then
        position = (direction > 0) and 0 or (visibleCount + 1);
    end

    local target = position + (direction > 0 and 1 or -1);
    if ( target > visibleCount ) then target = 1; end
    if ( target < 1 ) then target = visibleCount; end

    local realIndex = O.RealIndexAt(target);
    if ( not realIndex ) then
        return false;
    end

    ECS.Roster.selected = realIndex;
    -- re-run the row refresh so the new selection is styled
    ECS.Roster.SetOffset(ECS.Roster.GetOffset());
    I.OnRowSelected(realIndex);
    return true;
end

-- The stock scroll frame is one pixel wide and cannot receive practical wheel
-- input over the visible rows. Route the eight visible row buttons and native
-- scrollbar through the visual roster offset instead of the stock ten-row list.
function I.ScrollBy(delta)
    delta = tonumber(delta) or 0;
    if ( delta == 0 ) then
        return false;
    end

    local changed = ECS.Roster.SetOffset(ECS.Roster.GetOffset() - delta);
    local select = _G.CharacterSelect;
    if ( select ) then
        select.scrollOffset = ECS.Roster.GetOffset();
        local layout = ECS.Roster.ComputeLayout(ECS.Roster.ViewportHeight(), ECS.Roster.RowHeight());
        select.scrollMax = ECS.Roster.MaxOffset(O.VisibleCount(), layout);
    end
    return changed;
end

-- ---------------------------------------------------------------- drag hooking
-- The rows are XML-defined buttons. Hooking rather than replacing keeps the
-- stock OnClick/OnDoubleClick (select and enter-world) exactly as they are.
function I.HookRows()
    local pool = ECS.Roster.pool or {};
    for index = 1, #pool do
        local button = pool[index];
        if ( button and not button.__ecsHooked ) then
            button.__ecsHooked = true;

            if ( button.EnableMouseWheel ) then
                pcall(button.EnableMouseWheel, button, true);
            end
            if ( button.SetScript ) then
                button:SetScript("OnMouseWheel", function(_, delta)
                    I.ScrollBy(delta);
                end);
            end

            button:HookScript("OnMouseDown", function(self, mouseButton)
                if ( mouseButton ~= "LeftButton" ) then
                    return;
                end
                local x = 0;
                local ok, cursorX = pcall(GetCursorPosition);
                if ( ok ) then x = cursorX or 0 end
                -- pointerY is roster-relative; CursorOffsetY derives it from the
                -- row parent's own top edge, so it does not depend on where the
                -- roster happens to sit at this resolution.
                if ( ECS.Roster.BeginPress(self, x, ECS.Roster.CursorOffsetY() or 0) ) then
                    if ( ECS.UI ) then pcall(ECS.UI.StartDragDriver) end
                end
            end);

            button:HookScript("OnMouseUp", function(self, mouseButton)
                if ( mouseButton == "RightButton" ) then
                    -- spec 12/30: right-click opens the notes editor for the row
                    local character = ECS.Row.GetCharacter(self);
                    if ( character and ECS.UI ) then
                        pcall(ECS.UI.ShowNotesEditor, character);
                    end
                    return;
                end
                if ( mouseButton ~= "LeftButton" ) then
                    return;
                end
                if ( ECS.UI ) then pcall(ECS.UI.StopDragDriver) end
                if ( ECS.Roster.EndPress() ) then
                    pcall(I.SaveStore);   -- spec 11: persist the new order immediately
                end
            end);

            button:HookScript("OnEnter", function(self)
                local character = ECS.Row.GetCharacter(self);
                if ( character ) then
                    ECS.Tooltip.BeginHover(character);
                end
            end);

            button:HookScript("OnLeave", function()
                ECS.Tooltip.BeginHover(nil);
            end);
        end
    end
end

-- ---------------------------------------------------------------- scrolling
-- ECS DELIBERATELY DOES NOT TOUCH THE WHEEL.
--
-- CharacterSelect.xml already binds the scroll frame's OnMouseWheel to
-- `CharacterSelect_ScrollBy(delta)`, and that path is not a dead end: ScrollBy ->
-- CharacterSelect_SetScrollOffset -> CharacterSelect_RefreshVisibleList ->
-- UpdateCharacterList -> the wrapper installed above. So the stock handler already
-- keeps ECS in sync, and the rows bind the same handler, so a wheel over a row
-- works too.
--
-- Hooking it as well used to run BOTH handlers for one notch, which was worse than
-- merely scrolling twice. CharacterSelect_ClampScrollOffset rounds
-- (`math.floor(offset + 0.5)`), so every stock offset is an integer row. ECS's own
-- wheel moved by C.SCROLL_SPEED = 0.45 of a row and then assigned
-- `select.scrollOffset` DIRECTLY, bypassing that clamp - leaving a fractional
-- offset behind. Two things then break, because the offset doubles as a VISUAL
-- POSITION:
--
--   * O.RealIndexAt(5.55) is O.visible[5.55], which is nil, so every pooled row
--     saw no character and hid: one wheel notch blanked the whole roster;
--   * the stock UpdateCharacterSelection computes `selectedIndex - scrollOffset`,
--     so a fractional offset yields a name like "CharSelectCharacterButton1.55",
--     _G[...] is nil, and the LockHighlight() call errors inside the glue screen.
--
-- With the hook gone, ECS is driven entirely through UpdateCharacterList, and
-- R.ClampOffset now floors as well, so the "offset is a whole row" invariant that
-- RealIndexAt depends on holds no matter who sets it.

-- ---------------------------------------------------------------- notes
-- spec 12: called by the notes editor after Save so the row indicator and the
-- tooltip pick up the change immediately.
function I.ApplyNotesAndRefresh()
    ECS.Data.ApplyNotes(I.data or {}, ECS.Notes.Export());
    pcall(I.Refresh);
    if ( ECS.Tooltip and ECS.Tooltip.IsVisible() and ECS.Tooltip.IsVisible() ) then
        pcall(ECS.UI.RefreshTooltip);
    end
    pcall(I.SaveStore);
    return true;
end

-- ---------------------------------------------------------------- deletion (spec 20)
-- The STOCK confirmation is deliberately kept: it gates deletion behind typing
-- the confirm string and a hardcoded protected-name list, and replacing that
-- with anything of our own would weaken a safety feature for a cosmetic gain.
--
-- What ECS adds is the animation. After a successful delete the client pushes a
-- new character list; at that point the row that WAS showing the deleted
-- character is faded out and the refresh is deferred until the fade finishes, so
-- the gap closes after the row disappears rather than snapping shut under it.
--
-- A guard tween guarantees the deferred refresh always happens even if a row
-- callback is lost, so a failed animation can never leave a stale roster.
function I.SnapshotRows()
    local snapshot = {};
    local pool = ECS.Roster.pool or {};
    for slot = 1, #pool do
        snapshot[slot] = ECS.Row.GetCharacter(pool[slot]);
    end
    return snapshot;
end

function I.AnimateVanished(before, afterKeys)
    if ( not before or not ECS.Anim ) then
        return false;
    end
    local pool = ECS.Roster.pool or {};
    local pending = 0;

    for slot = 1, #pool do
        local previous = before[slot];
        local button = pool[slot];
        if ( previous and previous.stableKey and button
            and not afterKeys[previous.stableKey] ) then
            pending = pending + 1;
            pcall(ECS.Roster.AnimateDelete, button, function()
                pending = pending - 1;
                if ( pending <= 0 ) then
                    I.Refresh();
                end
            end);
        end
    end

    if ( pending > 0 ) then
        -- safety net: whatever happens to the row callbacks, refresh eventually
        pcall(ECS.Anim.Run, I, {
            key = "deleteGuard",
            setter = function() end,
            from = 0, to = 1,
            duration = C.DELETE_DURATION * 2.5,
            easing = "linear",
            onDone = function()
                if ( I.deleteGuardArmed ) then
                    I.deleteGuardArmed = false;
                    I.Refresh();
                end
            end,
        });
        I.deleteGuardArmed = true;
        return true;
    end
    return false;
end

-- ---------------------------------------------------------------- install
function I.PostUpdate()
    if ( I.applying ) then
        return;
    end

    if ( not I.loadedStore ) then
        pcall(I.LoadStore);
    end

    -- Snapshot BEFORE the rebuild: once the rows are rebound there is no way to
    -- tell which of them used to be showing the character that just disappeared.
    local before = nil;
    if ( I.poolBuilt and ECS.Roster.PoolSize() > 0 ) then
        before = I.SnapshotRows();
    end

    local buildOK, buildResult = pcall(I.BuildData);
    if ( not buildOK ) then
        I.buildError = tostring(buildResult);
        I.data = I.data or {};
    else
        I.buildError = nil;
    end
    I.stockCount = I.StockCharacterCount();
    I.dataCount = #(I.data or {});
    if ( I.dataCount == 0 and I.stockCount > 0 ) then
        I.buildError = "no ECS records for " .. tostring(I.stockCount) .. " visible stock rows";
    end
    if ( I.buildError ) then
        if ( ECS.UI ) then
            pcall(ECS.UI.SetRealmName, I.RealmLabel());
            pcall(ECS.UI.Layout);
            pcall(ECS.UI.RefreshStatus);
        end
        return false;
    end

    local afterKeys = {};
    for index = 1, #(I.data or {}) do
        local character = I.data[index];
        if ( character and character.stableKey ) then
            afterKeys[character.stableKey] = true;
        end
    end

    pcall(I.SyncSelectionFromStock);

    -- spec 20: a character left the list (most often a confirmed delete). Fade the
    -- row that was showing it and let the guard tween do the refresh, so the gap
    -- closes after the row has gone rather than snapping shut underneath it.
    if ( before and I.AnimateVanished(before, afterKeys) ) then
        if ( ECS.UI ) then
            pcall(ECS.UI.SetRealmName, I.RealmLabel());
            pcall(ECS.UI.Layout);
        end
        return;
    end

    pcall(I.Refresh);

    if ( ECS.UI ) then
        pcall(ECS.UI.SetRealmName, I.RealmLabel());
        pcall(ECS.UI.Layout);
        pcall(ECS.UI.RefreshStatus);
        -- spec 13: if the detail panel is open while the list changes underneath
        -- it, it must show the current data rather than a stale snapshot
        if ( ECS.Tooltip.IsVisible() ) then
            pcall(ECS.UI.RefreshTooltip);
        end
    end
end

local function ReconcileAfterStockChange()
    local ok = pcall(I.PostUpdate);
    if ( ok ) then
        I.postUpdateCount = (I.postUpdateCount or 0) + 1;
    end
    return ok;
end

function I.Install()
    if ( I.installed ) then
        return false;
    end
    I.installed = true;

    -- spec 24: the roster click resolves through ECS, which maps visual -> real.
    ECS.Roster.onSelected = I.OnRowSelected;
    ECS.Roster.onReordered = function()
        pcall(I.SaveStore);
    end;

    local original = _G.UpdateCharacterList;
    if ( type(original) ~= "function" ) then
        return false;
    end

    -- Replace only the stock real-index offset adjustment. The stock screen still
    -- owns selection and Enter World; ECS changes this calculation to use visual
    -- order so selecting a visible row never jumps the list.
    local originalAdjustOffset = _G.CharacterSelect_AdjustOffsetForSelection;
    if ( type(originalAdjustOffset) == "function" ) then
        _G.CharacterSelect_AdjustOffsetForSelection = function(...)
            local ok, handled = pcall(I.AdjustOffsetForSelection);
            if ( ok and handled ) then
                return;
            end
            return originalAdjustOffset(...);
        end;
    end

    -- Wrap, exactly as the Freeborn code does. The stock function keeps running
    -- in full, so every pinned string and every existing behaviour is preserved;
    -- ECS only re-skins afterwards.
    _G.UpdateCharacterList = function(...)
        original(...);
        ReconcileAfterStockChange();
    end;

    -- The custom War Band list has a visibility toggle that shows the stock
    -- CharacterSelectCharacterFrame directly, without calling UpdateCharacterList.
    -- Reconcile after that show so stock text/plates cannot reappear on top of ECS.
    local originalWarBandToggle = _G.CharacterSelect_OnEventO2;
    if ( type(originalWarBandToggle) == "function" ) then
        _G.CharacterSelect_OnEventO2 = function(...)
            originalWarBandToggle(...);
            ReconcileAfterStockChange();
        end;
    end

    local originalStyleToggle = _G.CharacterSelect_OnEventO;
    if ( type(originalStyleToggle) == "function" ) then
        _G.CharacterSelect_OnEventO = function(...)
            originalStyleToggle(...);
            ReconcileAfterStockChange();
        end;
    end

    -- Some character-list/selection notifications can arrive through the frame
    -- event handler without traversing the wrapped global. Reconcile only when the
    -- stock handler did not already run the wrapped UpdateCharacterList path.
    local originalEvent = _G.CharacterSelect_OnEvent;
    if ( type(originalEvent) == "function" ) then
        _G.CharacterSelect_OnEvent = function(self, event, ...)
            local previousCount = I.postUpdateCount or 0;
            local previousOffset = nil;
            if ( event == "UPDATE_SELECTED_CHARACTER" and I.poolBuilt ) then
                previousOffset = ECS.Roster.GetOffset();
            end
            originalEvent(self, event, ...);
            if ( (event == "CHARACTER_LIST_UPDATE" or event == "UPDATE_SELECTED_CHARACTER")
                and (I.postUpdateCount or 0) == previousCount ) then
                ReconcileAfterStockChange();
            end
            if ( previousOffset ~= nil ) then
                pcall(I.PreserveVisibleSelectionOffset, previousOffset);
            end
        end;
    end

    return true;
end

-- ---------------------------------------------------------------- activate
-- ACTIVATE AT LOAD. This call is the difference between ECS working and ECS
-- doing nothing at all: without it every module here would be loaded, fully
-- defined, and never invoked.
--
-- It is safe at file scope because Install only WRAPS UpdateCharacterList and
-- assigns callbacks - it touches no frame. The TOC loads this file last, after
-- CharacterSelect.xml (which defines UpdateCharacterList) and CharacterCreate.xml
-- (whose Freeborn code wraps it), so the function we wrap already exists.
--
-- Wrapped in pcall so that if anything here is missing, the stock character
-- select screen still works untouched rather than failing to load.
pcall(I.Install);
