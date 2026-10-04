--[[ ECS_Constants.lua ----------------------------------------------------------
    Esteria Character Select - every tunable in one place (spec 35).

    Nothing here touches a frame. Safe to load before any XML, and safe to load
    when the character-select frames do not exist yet.

    Lua 5.1 only: no integer division, no goto, no bitwise operators.
------------------------------------------------------------------------------ ]]

ECS = ECS or {};
ECS.Const = ECS.Const or {};

local C = ECS.Const;

-- ---------------------------------------------------------------- identity
C.ADDON_TAG      = "ECS";
-- 3: same compact order format as v2, but note-pair separators are printable
--    ASCII instead of raw control bytes. v2 could put 0x1E/0x1F directly into a
--    string CVar, which made Config.wtf serialization unsafe. Older records are
--    ignored rather than misread (spec 34); the next successful save writes v3.
C.SCHEMA_VERSION = 3;

-- ---------------------------------------------------------------- roster layout
-- The scroll frame viewport is 560px tall in CharacterSelect.xml. 70 divides it
-- exactly, so a whole number of rows fills the viewport with no dead band.
C.VIEWPORT_HEIGHT = 560;
C.ROW_HEIGHT      = 70;
C.ROW_SPACING     = 0;     -- extra gap between rows (0 = flush, modern list look)
C.ROSTER_WIDTH    = 258;
C.ROSTER_RIGHT    = 14;    -- gap from the right screen edge
C.ROSTER_TOP      = 58;    -- compact chrome: search then roster

-- Show exactly eight rows at once. The client defines ten stock buttons; ECS
-- virtualizes the first eight and permanently suppresses the two overflow slots.
C.POOL_SIZE = 8;
C.STOCK_ROW_COUNT = 10;

-- ---------------------------------------------------------------- tile visuals
C.PORTRAIT_SIZE   = 46;
C.PORTRAIT_INSET  = 9;     -- portrait offset from the tile's left edge
C.PORTRAIT_BORDER_SIZE = 60;
C.CLASS_ICON_SIZE = 18;
C.LEVEL_BADGE     = 18;    -- small overlapping level badge (spec 4)
C.LEVEL_BORDER_SIZE = 24;
C.NOTE_DOT_SIZE   = 6;
C.TILE_BORDER     = 1;     -- 1px rim, matching the ElvUI glue language
C.ROW_ART_SCALE   = 1.10;  -- modestly zoom row backdrops without changing row geometry

-- Faction emblem slot.
-- These MUST match CharacterFreeborn_ApplyBadges in CharacterCreate.lua, which
-- re-anchors its badge to `button TOPLEFT + (200, -35)` at 44x44. Keeping our own
-- emblem in the same slot means the existing Freeborn wrapper and ECS agree on
-- placement instead of fighting over it.
C.EMBLEM_X        = 200;
C.EMBLEM_Y        = -35;
C.EMBLEM_SIZE     = 44;

-- Text column: everything sits to the right of the portrait.
C.TEXT_LEFT       = 63;    -- PORTRAIT_INSET + PORTRAIT_SIZE + 8
C.TEXT_RIGHT      = 168;   -- stops before the emblem slot
C.NAME_TOP        = -12;
C.ZONE_TOP        = -28;
C.NOTE_TOP        = -44;
C.NAME_FONT_SIZE  = 13;
C.SUB_FONT_SIZE   = 11;
C.ZONE_FONT_SIZE  = 10;

-- ---------------------------------------------------------------- chrome layout
-- With the realm header removed, search starts at the top and the roster follows
-- with the same 18px gap it had beneath the search field before.
C.ACTION_BUTTON_MARGIN = 16;
C.ACTION_BUTTON_GAP = 10;
C.VANILLA_GLUE_BUTTON_WIDTH = 150;
C.VANILLA_GLUE_BUTTON_HEIGHT = 51;
C.VANILLA_ENTER_WORLD_WIDTH = 200;
C.VANILLA_ENTER_WORLD_HEIGHT = 60;
C.ENTER_WORLD_BOTTOM_OFFSET = 20;
C.CREATE_BUTTON_BOTTOM_MARGIN = 8;
C.VANILLA_DELETE_BUTTON_SIZE = 32;
C.SEARCH_TOP       = 18;
C.SEARCH_HEIGHT    = 22;
-- Names the fields the search actually uses (the blob carries name, race, class,
-- zone, faction and level - see ECS_Order.SearchBlob), because "Search characters"
-- left the user guessing what would match. test_search pins the promise: every word
-- here has to correspond to a field a query really matches.
C.SEARCH_PLACEHOLDER = "Search by name, class, race, level...";
-- Magnifier geometry. SEARCH_TEXT_INSET must clear the icon, or the placeholder and
-- the typed text run underneath it; the invariant is asserted in test_ui.
C.SEARCH_ICON_SIZE   = 12;
C.SEARCH_ICON_INSET  = 6;    -- icon offset from the box's left edge
C.SEARCH_TEXT_INSET  = 22;   -- where the placeholder and the text begin
C.STATUS_TOP       = 44;   -- filtered result summary, below the search box

C.EMPTY_TITLE      = "No characters yet";
C.EMPTY_BODY       = "Create your first character to enter Esteria.";

-- Persistence feedback (spec 11/33). A reorder that did not reach storage must
-- say so: silently keeping the new order on screen would show the user a state
-- that will be gone at the next login, which is the same "looked like it worked"
-- defect the notes editor already had once. The degraded case is separate because
-- the order DID survive - only the notes were given up to make room for it.
C.NOTICE_SAVE_FAILED   = "Order not saved - storage full";
C.NOTICE_NOTES_DROPPED = "Notes cleared - storage full";

-- Tooltip / modal presentation
C.TOOLTIP_ALPHA    = 0.96;
C.MODAL_WIDTH      = 300;
C.MODAL_MIN_HEIGHT = 120;
C.MODAL_BUTTON_W   = 90;
C.MODAL_BUTTON_H   = 22;

-- ---------------------------------------------------------------- animation
-- Durations in seconds. Kept short: glue is running on a 2008 client.
C.FADE_DURATION     = 0.16;
C.HOVER_DURATION    = 0.12;
C.SELECTION_DURATION= 0.18;
C.DELETE_DURATION   = 0.26;
C.SLIDE_DURATION    = 0.16;
C.MODAL_DURATION    = 0.14;
C.DRAG_THRESHOLD    = 6;   -- px of travel before a press becomes a drag (spec 10)
C.TOOLTIP_DELAY     = 0.35;
C.HOVER_SLIDE       = 3;   -- px the row nudges right on hover (spec 6)

-- Guard so a runaway tween can never spin the shared driver forever.
C.ANIM_MAX_DT  = 0.1;      -- clamp a single OnUpdate step
C.ANIM_EPSILON = 0.001;    -- treat as settled below this

-- ---------------------------------------------------------------- input
-- No scroll-speed constant: the wheel is owned by the stock glue handler, which
-- moves exactly one row per notch. An ECS-side fractional rate is what used to
-- leave a fractional offset behind and blank the roster (see ECS_Integrate.lua).

-- ---------------------------------------------------------------- colour
-- ElvUI 6.09 defaults, already established by the glue reskin pass, so the
-- character screen matches the rest of the client.
C.COLOUR = {
    backdrop     = { 0.06,  0.11,  0.12 },
    backdropFade = { 0.03,  0.08,  0.09, 0.58 },
    border       = { 0.02,  0.04,  0.04, 0.72 },
    text         = { 0.898, 0.890, 0.890 },
    textDim      = { 0.560, 0.560, 0.560 },
    textBright   = { 1.00,  1.00,  1.00 },
    accent       = { 0.99,  0.48,  0.17 },   -- valuecolor #FD7A2B
    realmBar     = { 0.42,  0.015, 0.02, 0.96 },
    realmBorder  = { 0.86,  0.64, 0.16, 1.00 },
    realmText    = { 1.00,  0.84, 0.18 },
    dragTarget   = { 0.99,  0.48,  0.17, 0.10 },
    danger       = { 0.78,  0.25,  0.25 },
};

-- ---------------------------------------------------------------- texture roots
-- One place to retarget art (spec 26). Never inline a texture path elsewhere.
C.TEX = {
    -- The single flat texel the whole ElvUI look is built from.
    blank        = "Interface\\Buttons\\WHITE8X8",

    root         = "Interface\\Glues\\CharacterSelect\\",
    common       = "Interface\\Glues\\Common\\",
    create       = "Interface\\Glues\\CharacterCreate\\",

    -- Existing Esteria assets, reused rather than reinvented.
    highlight    = "Interface\\Glues\\CharacterSelect\\Glue-CharacterSelect-Highlight",
    freebornBadge= "Interface\\Glues\\CharacterSelect\\FreebornLogo",
    allianceBadge= "Interface\\Glues\\CharacterSelect\\AllianceLogo",
    hordeBadge   = "Interface\\Glues\\CharacterSelect\\HordeLogo",

    -- Per-race 64x64 portraits generated by tools/derive_playable_race_portraits.py
    -- and shipped as UI-CharacterCreate-<Race><Male|Female>.blp
    --
    -- ECS ships its own circular-masked copies in a dedicated namespace rather
    -- than altering the shared CharacterCreate art (spec 26). If the ECS copy is
    -- missing the schema falls back to the stock square portrait, so a partial
    -- install still renders.
    portraitNs   = "Interface\\Glues\\CharacterSelect\\ECS-Portrait-",
    portraitBorder= "Interface\\Glues\\CharacterSelect\\ECS-Portrait-Border",
    idlePlate     = "Interface\\Glues\\CharacterSelect\\ECS-Row-Idle-Grey",
    allianceHoverPlate = "Interface\\Glues\\CharacterSelect\\ECS-Row-Hover-Alliance-Blue",
    hordeHoverPlate = "Interface\\Glues\\CharacterSelect\\ECS-Row-Hover-Horde-Red",
    freebornHoverPlate = "Interface\\Glues\\CharacterSelect\\ECS-Row-Hover-Freeborn-Purple",
    selectedPlate = "Interface\\Glues\\CharacterSelect\\ECS-Row-Selected-Gold",
    levelBorder   = "Interface\\Glues\\CharacterSelect\\ECS-Level-Border",
    deleteButtonBlueAtlas = "Interface\\Glues\\CharacterSelect\\ECS-Delete-Button-Blue",
    createTooltipBackground = "Interface\\Tooltips\\UI-Tooltip-Background",
    createTooltipBorder = "Interface\\Tooltips\\ui-tooltip-border-maw",
    glueButtonUpBlue = "Interface\\Glues\\Common\\Glue-Panel-Button-Up-Blue",
    glueButtonDownBlue = "Interface\\Glues\\Common\\Glue-Panel-Button-Down-Blue",
    glueButtonHighlightBlue = "Interface\\Glues\\Common\\Glue-Panel-Button-Highlight-Blue",
    glueButtonDisabled = "Interface\\Glues\\Common\\Glue-Panel-Button-Disabled",
    classIcon    = "Interface\\Glues\\CharacterCreate\\UI-CHARACTERCREATE-RACES-ClASS",
    noteDot      = "Interface\\Glues\\CharacterSelect\\ECS-Note-Dot",
    searchIcon   = "Interface\\Glues\\CharacterSelect\\ECS-Search-Icon",
};

-- ---------------------------------------------------------------- fallbacks
-- spec 33: one unusual character must never break the screen.
C.FALLBACK_RACE_NAME  = "Unknown Race";
C.FALLBACK_CLASS_NAME = "Hero";
C.FALLBACK_ZONE       = "Unknown Zone";
C.LEVEL_UNKNOWN       = "??";   -- shown instead of a blank level badge
C.NEUTRAL_FACTION     = "Neutral";

-- spec 8 / 24: when the selected character is filtered out we keep the real
-- selection and simply show no selected row. This is the choice that cannot
-- cause accidental entry.
C.KEEP_SELECTION_WHEN_FILTERED = true;

-- spec 11: where a newly seen character lands in a saved custom order.
C.NEW_CHARACTER_POSITION = "tail";   -- "tail" | "head"
