-- SeasonPassHUD v4 — Saisonleiste + Minimap-Knopf + Lokalisierung (DE/EN).
-- Sprache: folgt der Client-Sprache, per DE/EN-Knopf im Fenster umschaltbar,
-- Wahl wird dauerhaft gespeichert (SeasonPassDB.lang) und an den Server gemeldet.

-- ===========================================================================
--  Lokalisierung (von SeasonPass.lua mitbenutzt)
-- ===========================================================================
BP_LOCALE = {
    de = {
        tab1 = "Belohnungen", tab2 = "Wochenziele", tab3 = "Runen",
        tab4 = "Klassenset", tab5 = "Events", tab6 = "Erfolge",
        title = "Traumpfad — Saison %d",
        claim = "Belohnungen abholen", claimN = "Belohnungen abholen (%d)",
        claimed_all = "Alles abgeholt", page = "Seite %d / %d",
        weekly_head = "Wochenziele",
        weekly_sub = "Drei rotierende Aufgaben — neue Ziele jeden Donnerstag. Fortschritt zählt automatisch.",
        weekly_nodata = "(Noch keine Daten — gleich kommt der Sync)",
        done_excl = "Erledigt!",
        reroll_tip = "Traumtausch: Ziel neu würfeln (1x pro Woche)",
        runes_head = "Saisonale Runen",
        runes_sub = "Belegte Slots: %d / %d  (Extra-Slots ab Stufe 25, 50, 75)",
        runes_foot = "Klick auf eine Rune: gravieren oder entfernen (Gold wird abgebucht). [F] = neue Fähigkeit fürs Zauberbuch!",
        active_tag = "[aktiv]",
        set_head = "Klassenset: %s",
        set_sub = "Erbstück-Technik: ab Level 1 tragbar, die Werte wachsen bis Stufe 80 mit!",
        st_claimed = "Abgeholt", st_claimable = "Jetzt abholbar!", st_hero = "Stufe %d — Heldenpfad",
        ev_head = "Laufende Events",
        ev_zone = "Eventzone (doppelte Punkte)", ev_bounty = "Kopfgeld des Tages",
        ev_dungeon = "Dungeon der Woche", ev_boss = "Saison-Weltboss",
        ev_mutator = "Wochen-Mutator", ev_storm = "Traumsturm",
        dungeon_done = "[erledigt]", dungeon_hint = "(Bosskill = Bonuspunkte)",
        boss_none = "Derzeit schlummert alles ...", boss_active = "JETZT AKTIV: %s!",
        storm_on = "TOBT GERADE — dreifache Punkte!", storm_off = "zieht irgendwann auf — Augen offen halten ...",
        ev_chests = "Zufallskisten (Endgame)",
        chest_on = "AKTIV: Gegner droppen Kisten! Kistenfieber: +%d%% Epic-Chance",
        chest_off = "ab Maximalstufe droppen Gegner Kisten — Kistenfieber: +%d%%",
        info_welcome = "Willkommenspaket (automatisch bei der ersten Anmeldung):",
        tab7 = "Charakter",
        tab8 = "Sammlung",
        tab9 = "Shop",
        fish_head = "Angelauftrag (täglich):",
        fish_text = "Fang %dx %s",
        char_played = "Spielzeit",
        char_gold = "Gold",
        char_stats = "Attribute",
        char_season = "Saison-Statistiken",
        stat1 = "Stärke", stat2 = "Beweglichkeit", stat3 = "Ausdauer", stat4 = "Intelligenz", stat5 = "Willenskraft",
        char_ap = "Angriffskraft", char_crit = "Kritische Trefferchance", char_scrit = "Zauberkritchance",
        cs_points = "Punkte gesamt", cs_tier = "Traumpfad-Stufe", cs_prestige = "Prestige",
        cs_streak = "Login-Serie (Tage)", cs_pity = "Kistenfieber",
        cs_boss = "Saison-Weltbosse", cs_bounty = "Kopfgelder", cs_rare = "Seltene Gegner",
        cs_duel = "Duellsiege", cs_weekly = "Wochenziele", cs_dungeon = "Dungeons der Woche",
        cs_disc = "Verlorene Orte", cs_supply = "Lieferungen", cs_rune = "Runen graviert",
        coll_sub = "Deine Saison-Schätze — grau = noch nicht ergattert",
        coll_cat1 = "Haustiere", coll_cat2 = "Cosmetics & Spielzeug",
        tab10 = "Kisten",
        kt_head = "Traumkiste — was kann drin sein?",
        kt_odds = "Qualität wird beim Öffnen ausgewürfelt: |cff3399ffBlau %d%%|r · |cffa335eeMythisch %d%%|r · |cffff8000Golden %d%%|r  —  Ziehungen: 2/3/4",
        kt_fever = "Kistenfieber: +%d%% (verbessert Aufwertung UND Episch-Chance — steigt mit jeder Kiste ohne Episches)",
        chest_roll = "Traumkiste öffnet sich ...",
        fish_bonus = "+ Traumkiste!",
        kt_rar1 = "Häufig", kt_rar2 = "Selten", kt_rar3 = "Episch", kt_rar4 = "Legendär",
        kt_rune_desc = "Lehrt sofort eine zufällige Runen-Fähigkeit, die dieser Charakter noch nicht kennt!",
        kt_chance = "Chance: ca. %.2f%%",
        kt_see = "Alle möglichen Inhalte: siehe Kisten-Tab!",
        tab11 = "Prestige",
        pg_head = "Traumschmiede — dein Prestige-Pfad",
        pg_sub = "Prestige %d / %d   —   Freie Punkte: |cff00FF00%d|r",
        pg_disabled_head = "Traumschmiede deaktiviert",
        pg_disabled_sub = "Der Paragon-Fortschritt ist in dieser Saison deaktiviert.",
        pg_info = "Jedes Prestige = 2 Punkte, Gold und +3%% Erfahrung. ABER: Gegner erhalten je Prestige +%d%% Schaden und Leben — schmiede dich stärker!",
        pg_reset = "Punkte zurücksetzen",
        pg_reset_confirm = "Alle Traumschmiede-Punkte zurücksetzen und neu verteilen?",
        pg_pts = "%d / %d Punkte",
        pg_eff = "aktuell: |cff00FF00+%d%%|r",
        pg_stat1 = "Macht", pg_desc1 = "+%d%% Nahkampfschaden je Punkt",
        pg_stat2 = "Zauberkunst", pg_desc2 = "+%d%% Zauberschaden je Punkt",
        pg_stat3 = "Flächenwirkung", pg_desc3 = "+%d%% Flächenschaden (AoE) je Punkt",
        pg_stat4 = "Toxine", pg_desc4 = "+%d%% Gift- & DoT-Schaden je Punkt",
        pg_stat5 = "Vitalität", pg_desc5 = "+%d%% maximales Leben je Punkt",
        pg_stat6 = "Seelenkraft", pg_desc6 = "+%d%% maximales Mana je Punkt",
        pg_stat7 = "Heilkunst", pg_desc7 = "+%d%% Heilung je Punkt",
        pg_stat8 = "Weisheit", pg_desc8 = "+%d%% Erfahrung je Punkt",
        coll_owned = "Im Besitz!", coll_missing = "Noch nicht ergattert",
        box_desc = "Traumkiste: würfelt beim Öffnen ihre Qualität aus — Blau, Mythisch oder Golden! Jede geöffnete Kiste gibt +10 Traumpfad-Punkte.",
        start_head = "Wähle deine Startfähigkeit — einmalig, gratis, belegt keinen Runenslot:",
        start_done = "Deine Startfähigkeit: %s",
        start_confirm = "%s als Startfähigkeit lernen? Diese Wahl ist einmalig!",
        oracle_head = "Traumorakel (KI):",
        oracle1 = "Weissage mir etwas!",
        oracle2 = "Erzähle von der Saison",
        oracle3 = "Gib mir einen Schlachtruf!",
        oracle4 = "Witz über meine Klasse",
        prestige_btn = "Prestige starten",
        prestige_confirm = "Prestige setzt Punkte und Abholstand auf 0 — alle Belohnungen behältst du. Dafür gibt's Gold, +3% Erfahrung und 1 Traumschmiede-Punkt (Paragon-Tab) — aber die Gegner werden stärker! Wirklich neu starten?",
        shop_head = "Saisonhändlerin — Klick kauft das Item:",
        shop_count = "Menge: %d",
        shop_price = "Preis: %s",
        supply_head = "Versorgungsauftrag (täglich):",
        supply_text = "Liefere %dx %s",
        supply_reward = "Belohnung: +%d Punkte & %d Gold",
        supply_deliver = "Abgeben",
        hc_start = "Hardcore starten (bis Level 10)",
        hc_active = "HARDCORE AKTIV — stirb nicht!",
        hc_failed = "Hardcore gescheitert",
        hc_done = "HARDCORE GESCHAFFT!",
        hc_confirm = "Hardcore-Herausforderung: Erreiche Level 80 ohne einen einzigen Tod. Stirbst du, endet nur die Herausforderung — dein Charakter lebt normal weiter. Annehmen?",
        welcome_slot = "Stufe 0 — Willkommenspaket",
        welcome_claimed = "Abgeholt!",
        welcome_click = "Klicken zum Abholen!",
        info_points = "Punkte gesamt: %d",
        info_renown = "Renown %d — %d / %d",
        wait_sync = "(warte auf Sync)",
        info_rotation = "Weltboss-Rotation:",
        info_worldbuff = "Weltbuff: Fällt ein Saison-Weltboss, erhält GANZ Azeroth den Schlachtruf der Drachentöter!",
        info_weekend = "Bonus-Wochenende: Sa+So doppelte Punkte und mehr Erfahrung.",
        info_chests = "Zufallskisten: Ab Maximalstufe droppen Kisten von Gegnern — Kistenfieber steigert die Epic-Chance!",
        ach_head = "Saison-Erfolge",
        ach_sub = "Errungen: %d / %d — Erfolge geben Punkte und werden serverweit verkündet!",
        ach_done = "Errungen! (+%d Punkte)",
        pts_suffix = "(+%d P.)",
        info_prestige = "Prestige %d", info_streak = "Login-Serie: %d Tage", info_weekend2 = "Bonus-Wochenende!",
        fanfare = "Traumpfad-Stufe %d!",
        fanfare_prestige = "Prestige %d!",
        bar_max = "Maximalstufe %d erreicht — Prestige wartet!",
        bar_max_no_prestige = "Maximalstufe %d erreicht — Traumruhm aktiv!",
        bar_prog = "Stufe %d  —  %d / %d",
        bar_prestige = "Prestige %d / %d  —  %d / %d Punkte",
        hud_prestige = "Prestige %d  —  %d / %d",
        hud_renown = "Renown %d — %d / %d",
        char_prestige = "Prestige %d",
        need_points = "Noch %d Punkte", already = "Bereits abgeholt", claim_now = "Jetzt abholbar — klicken!",
        tier_label = "Traumpfad-Stufe %d", hero_tag = " (Heldenpfad)",
        hud_name = "Traumpfad",
        hud_max = "Max!", hud_max_no_prestige = "Max! Traumruhm aktiv!",
        hud_level = "Charakter-Level %d  —  %d%%",
        tt_tier = "Stufe %d / %d  (%d Punkte)", tt_claim = "Belohnungen abholbar — Fenster öffnen und abholen!",
        tt_click = "Klick: Traumpfad-Fenster", tt_claimbtn = "Belohnungen abholen!",
        hud_locked = "Saisonleiste gesperrt.", hud_unlocked = "Saisonleiste entsperrt — ziehen, dann /bp hud lock.",
        loaded = "geladen — Drachen-Knopf an der Minimap oder Saisonleiste anklicken!",
        lang_note = "Sprache umgestellt — Oberfläche wird neu geladen ...",
    },
    en = {
        tab1 = "Rewards", tab2 = "Weekly Goals", tab3 = "Runes",
        tab4 = "Class Set", tab5 = "Events", tab6 = "Achievements",
        title = "Dream Path — Season %d",
        claim = "Claim rewards", claimN = "Claim rewards (%d)",
        claimed_all = "All claimed", page = "Page %d / %d",
        weekly_head = "Weekly Goals",
        weekly_sub = "Three rotating goals — new ones every Thursday. Progress counts automatically.",
        weekly_nodata = "(No data yet — sync incoming)",
        done_excl = "Done!",
        reroll_tip = "Dream swap: reroll this goal (once per week)",
        runes_head = "Seasonal Runes",
        runes_sub = "Slots used: %d / %d  (extra slots at tier 25, 50, 75)",
        runes_foot = "Click a rune to engrave or remove it (gold is charged). [F] = new ability for your spellbook!",
        active_tag = "[active]",
        set_head = "Class set: %s",
        set_sub = "Heirloom tech: wearable from level 1, stats scale up to level 80!",
        st_claimed = "Claimed", st_claimable = "Claim now!", st_hero = "Tier %d — Hero path",
        ev_head = "Live Events",
        ev_zone = "Event zone (double points)", ev_bounty = "Bounty of the day",
        ev_dungeon = "Dungeon of the week", ev_boss = "Season world boss",
        ev_mutator = "Weekly mutator", ev_storm = "Dream storm",
        dungeon_done = "[done]", dungeon_hint = "(boss kill = bonus points)",
        boss_none = "All is quiet for now ...", boss_active = "ACTIVE NOW: %s!",
        storm_on = "RAGING NOW — triple points!", storm_off = "will gather eventually — keep watch ...",
        ev_chests = "Random chests (endgame)",
        chest_on = "ACTIVE: enemies drop chests! Chest Fever: +%d%% epic chance",
        chest_off = "at max tier enemies drop chests — Chest Fever: +%d%%",
        info_welcome = "Welcome package (automatic on first login):",
        tab7 = "Character",
        tab8 = "Collection",
        tab9 = "Shop",
        fish_head = "Fishing contract (daily):",
        fish_text = "Catch %dx %s",
        char_played = "Time played",
        char_gold = "Gold",
        char_stats = "Attributes",
        char_season = "Season statistics",
        stat1 = "Strength", stat2 = "Agility", stat3 = "Stamina", stat4 = "Intellect", stat5 = "Spirit",
        char_ap = "Attack power", char_crit = "Critical strike chance", char_scrit = "Spell crit chance",
        cs_points = "Total points", cs_tier = "Dream Path tier", cs_prestige = "Prestige",
        cs_streak = "Login streak (days)", cs_pity = "Chest Fever",
        cs_boss = "Season world bosses", cs_bounty = "Bounties", cs_rare = "Rare enemies",
        cs_duel = "Duel wins", cs_weekly = "Weekly goals", cs_dungeon = "Dungeons of the week",
        cs_disc = "Lost places", cs_supply = "Deliveries", cs_rune = "Runes engraved",
        coll_sub = "Your season treasures — gray = not collected yet",
        coll_cat1 = "Pets", coll_cat2 = "Cosmetics & toys",
        tab10 = "Chests",
        kt_head = "Dream Chest — what's inside?",
        kt_odds = "Quality is rolled on opening: |cff3399ffBlue %d%%|r · |cffa335eeMythic %d%%|r · |cffff8000Golden %d%%|r  —  pulls: 2/3/4",
        kt_fever = "Chest Fever: +%d%% (boosts upgrade AND epic chance — rises with every chest without an epic)",
        chest_roll = "Dream chest opening ...",
        fish_bonus = "+ dream chest!",
        kt_rar1 = "Common", kt_rar2 = "Rare", kt_rar3 = "Epic", kt_rar4 = "Legendary",
        kt_rune_desc = "Instantly teaches a random rune ability this character doesn't know yet!",
        kt_chance = "Chance: about %.2f%%",
        kt_see = "See the Chests tab for every possible drop!",
        tab11 = "Prestige",
        pg_head = "Dream Forge — your prestige path",
        pg_sub = "Prestige %d / %d   —   Free points: |cff00FF00%d|r",
        pg_disabled_head = "Dream Forge disabled",
        pg_disabled_sub = "Paragon progress is disabled for this season.",
        pg_info = "Every prestige = 2 points, gold and +3%% experience. BUT: enemies gain +%d%% damage and health per prestige — forge yourself stronger!",
        pg_reset = "Reset points",
        pg_reset_confirm = "Reset all Dream Forge points and redistribute?",
        pg_pts = "%d / %d points",
        pg_eff = "current: |cff00FF00+%d%%|r",
        pg_stat1 = "Might", pg_desc1 = "+%d%% melee damage per point",
        pg_stat2 = "Sorcery", pg_desc2 = "+%d%% spell damage per point",
        pg_stat3 = "Devastation", pg_desc3 = "+%d%% area (AoE) damage per point",
        pg_stat4 = "Toxins", pg_desc4 = "+%d%% poison & DoT damage per point",
        pg_stat5 = "Vitality", pg_desc5 = "+%d%% maximum health per point",
        pg_stat6 = "Soul Power", pg_desc6 = "+%d%% maximum mana per point",
        pg_stat7 = "Healing Arts", pg_desc7 = "+%d%% healing done per point",
        pg_stat8 = "Wisdom", pg_desc8 = "+%d%% experience per point",
        coll_owned = "Owned!", coll_missing = "Not collected yet",
        box_desc = "Dream chest: rolls its quality on opening — blue, mythic or golden! Every opened chest grants +10 Dream Path points.",
        start_head = "Choose your starting ability — one-time, free, uses no rune slot:",
        start_done = "Your starting ability: %s",
        start_confirm = "Learn %s as your starting ability? This choice is one-time!",
        oracle_head = "Dream Oracle (AI):",
        oracle1 = "Give me a prophecy!",
        oracle2 = "Tell me about the season",
        oracle3 = "Give me a battle cry!",
        oracle4 = "Joke about my class",
        prestige_btn = "Start prestige",
        prestige_confirm = "Prestige resets points and claims to 0 — you keep all rewards. In return: gold, +3% experience and 1 Dream Forge point (Paragon tab) — but enemies grow stronger! Really restart?",
        shop_head = "Season vendor — click to buy:",
        shop_count = "Amount: %d",
        shop_price = "Price: %s",
        supply_head = "Supply run (daily):",
        supply_text = "Deliver %dx %s",
        supply_reward = "Reward: +%d points & %d gold",
        supply_deliver = "Deliver",
        hc_start = "Start hardcore (up to level 10)",
        hc_active = "HARDCORE ACTIVE — don't die!",
        hc_failed = "Hardcore failed",
        hc_done = "HARDCORE COMPLETE!",
        hc_confirm = "Hardcore challenge: reach level 80 without dying once. If you die, only the challenge ends — your character lives on normally. Accept?",
        welcome_slot = "Tier 0 — Welcome package",
        welcome_claimed = "Claimed!",
        welcome_click = "Click to claim!",
        info_points = "Total points: %d",
        info_renown = "Renown %d — %d / %d",
        wait_sync = "(waiting for sync)",
        info_rotation = "World boss rotation:",
        info_worldbuff = "World buff: when a season world boss falls, ALL of Azeroth gets Rallying Cry of the Dragonslayer!",
        info_weekend = "Bonus weekend: Sat+Sun double points and extra experience.",
        info_chests = "Random chests: at max tier, chests drop from enemies — Chest Fever raises your epic chance!",
        ach_head = "Season Achievements",
        ach_sub = "Earned: %d / %d — achievements grant points and are announced server-wide!",
        ach_done = "Earned! (+%d points)",
        pts_suffix = "(+%d pts)",
        info_prestige = "Prestige %d", info_streak = "Streak: %d days", info_weekend2 = "Bonus weekend!",
        fanfare = "Dream Path tier %d!",
        fanfare_prestige = "Prestige %d!",
        bar_max = "Max tier %d reached — prestige awaits!",
        bar_max_no_prestige = "Max tier %d reached — Dream Renown active!",
        bar_prog = "Tier %d  —  %d / %d",
        bar_prestige = "Prestige %d / %d  —  %d / %d points",
        hud_prestige = "Prestige %d  —  %d / %d",
        hud_renown = "Renown %d — %d / %d",
        char_prestige = "Prestige %d",
        need_points = "%d more points", already = "Already claimed", claim_now = "Claim now — click!",
        tier_label = "Dream Path tier %d", hero_tag = " (Hero path)",
        hud_name = "Dream Path",
        hud_max = "Max!", hud_max_no_prestige = "Max! Dream Renown active!",
        hud_level = "Character level %d  —  %d%%",
        tt_tier = "Tier %d / %d  (%d points)", tt_claim = "Rewards ready — open the window to claim!",
        tt_click = "Click: Dream Path window", tt_claimbtn = "Claim rewards!",
        hud_locked = "Season bar locked.", hud_unlocked = "Season bar unlocked — drag it, then /bp hud lock.",
        loaded = "loaded — click the dragon button at the minimap or the season bar!",
        lang_note = "Language changed — reloading interface ...",
    },
}

function BP_Lang()
    if SeasonPassDB and SeasonPassDB.languageVersion ~= 1 then
        SeasonPassDB.lang = "en"
        SeasonPassDB.languageVersion = 1
    end
    if SeasonPassDB and SeasonPassDB.lang then
        return SeasonPassDB.lang
    end
    return "en"
end

function BPL(key)
    local l = BP_LOCALE[BP_Lang()] or BP_LOCALE.de
    return l[key] or key
end

function BPName(t)
    if not t then return "?" end
    if BP_Lang() == "en" and t.en then return t.en end
    return t.name
end

function BPSeasonName()
    return BP_Lang() == "en" and (BP_SEASON_NAME_EN or BP_SEASON_NAME) or BP_SEASON_NAME
end

-- ===========================================================================
--  Saisonleiste
-- ===========================================================================
local DEFAULTS = {
    -- Standard: unten mittig über der Aktionsleiste (wie die klassische XP-Leiste)
    point = "BOTTOM", x = 0, y = 46,
    locked = true, hidden = false, scale = 1.0,
    minimapAngle = 3.8,
    version = 2,
}

local state = nil
local claimable = false

local function DB()
    if not SeasonPassDB then
        SeasonPassDB = {}
    end
    -- Positions-Migration: neue Standardposition (unten mittig) einmalig übernehmen
    if SeasonPassDB.version ~= DEFAULTS.version then
        SeasonPassDB.version = DEFAULTS.version
        SeasonPassDB.point, SeasonPassDB.x, SeasonPassDB.y = DEFAULTS.point, DEFAULTS.x, DEFAULTS.y
    end
    for k, v in pairs(DEFAULTS) do
        if SeasonPassDB[k] == nil then
            SeasonPassDB[k] = v
        end
    end
    return SeasonPassDB
end

-- Schlichte Doppel-Leiste: oben Traumpfad, darunter das echte Level. Keine Icons.
local hud = CreateFrame("Frame", "SeasonPassHUDFrame", UIParent)
hud:SetWidth(280)
hud:SetHeight(40)
hud:SetMovable(true)
hud:EnableMouse(true)
hud:SetClampedToScreen(true)
hud:RegisterForDrag("LeftButton")
hud:SetFrameStrata("MEDIUM")

local function MakeBar(parent, w, h, r, g, b)
    local holder = CreateFrame("Frame", nil, parent)
    holder:SetWidth(w)
    holder:SetHeight(h)
    holder:SetBackdrop({
        bgFile = "Interface\\ChatFrame\\ChatFrameBackground",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true, tileSize = 8, edgeSize = 10,
        insets = { left = 2, right = 2, top = 2, bottom = 2 },
    })
    holder:SetBackdropColor(0, 0, 0, 0.7)
    local sb = CreateFrame("StatusBar", nil, holder)
    sb:SetPoint("TOPLEFT", 3, -3)
    sb:SetPoint("BOTTOMRIGHT", -3, 3)
    sb:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
    sb:SetStatusBarColor(r, g, b)
    sb:SetMinMaxValues(0, 100)
    sb:SetValue(0)
    local txt = sb:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    txt:SetPoint("CENTER", 0, 0)
    return holder, sb, txt
end

local bpHolder, bpBar, bpText = MakeBar(hud, 280, 21, 1, 0.82, 0)
bpHolder:SetPoint("TOPLEFT", 0, 0)
local spark = bpBar:CreateTexture(nil, "OVERLAY")
spark:SetTexture("Interface\\CastingBar\\UI-CastingBar-Spark")
spark:SetBlendMode("ADD")
spark:SetWidth(14)
spark:SetHeight(28)
spark:Hide()

local xpHolder, xpBar, xpText = MakeBar(hud, 280, 17, 0.58, 0.0, 0.75)
xpHolder:SetPoint("TOPLEFT", 0, -22)

local function ApplySettings()
    local db = DB()
    hud:ClearAllPoints()
    hud:SetPoint(db.point, UIParent, db.point, db.x, db.y)
    hud:SetScale(db.scale)
    if db.hidden then hud:Hide() else hud:Show() end
end

function SeasonPassHUD_SetLocked(locked)
    DB().locked = locked
    DEFAULT_CHAT_FRAME:AddMessage("|cffFFD700[Season Pass]|r " .. (locked and BPL("hud_locked") or BPL("hud_unlocked")))
end

function SeasonPassHUD_SetSide(side)
    local db = DB()
    if side == "right" then
        db.point, db.x, db.y = "TOPRIGHT", -30, -140
    else
        db.point, db.x, db.y = "TOPLEFT", 30, -140
    end
    ApplySettings()
end

function SeasonPassHUD_SetHidden(hidden)
    DB().hidden = hidden
    ApplySettings()
end

function SeasonPassHUD_SetScale(scale)
    scale = tonumber(scale)
    if scale and scale >= 0.5 and scale <= 2 then
        DB().scale = scale
        ApplySettings()
    end
end

local function UpdateXP()
    -- Mit Prestige verschwindet die Charakter-Level-Zeile: nur noch der Traumpfad zählt
    if state and (state.prestige or 0) > 0 then
        xpHolder:Hide()
        hud:SetHeight(21)
        return
    end
    xpHolder:Show()
    hud:SetHeight(40)
    local level = UnitLevel("player") or 1
    local xp, xpMax = UnitXP("player") or 0, UnitXPMax("player") or 1
    if xpMax < 1 then xpMax = 1 end
    xpBar:SetMinMaxValues(0, xpMax)
    xpBar:SetValue(xp)
    xpText:SetText(string.format(BPL("hud_level"), level, math.floor(xp / xpMax * 100)))
end

-- Prestige ersetzt die Levelzahl am Spielerporträt (Paragon-Farbe)
local function UpdatePlayerLevelText()
    if not PlayerLevelText then
        return
    end
    if state and (state.prestige or 0) > 0 then
        PlayerLevelText:SetText(state.prestige)
        PlayerLevelText:SetTextColor(1, 0.53, 0)
    else
        PlayerLevelText:SetTextColor(1, 0.82, 0)
        PlayerLevelText:SetText(UnitLevel("player"))
    end
end
if hooksecurefunc then
    hooksecurefunc("PlayerFrame_Update", UpdatePlayerLevelText)
end

-- Prestige ersetzt auch die "Stufe 80"-Zeile im Charakterfenster
local function UpdateCharSheetLevel()
    if not CharacterLevelText then
        return
    end
    if state and (state.prestige or 0) > 0 then
        local race = UnitRace("player") or ""
        local class = UnitClass("player") or ""
        CharacterLevelText:SetText("|cffFF8800" .. string.format(BPL("char_prestige"), state.prestige)
            .. "|r - " .. race .. ", " .. class)
    end
end
if hooksecurefunc then
    hooksecurefunc("PaperDollFrame_SetLevel", UpdateCharSheetLevel)
end

function SeasonPassHUD_Update(BP)
    state = BP

    local cost = BP.perTier
    local into
    if (BP.prestige or 0) > 0 then
        -- Prestige-Modus: Leiste zeigt nur noch den Prestige-Fortschritt (Orange)
        into = math.min(BP.points, cost)
        bpBar:SetStatusBarColor(1, 0.53, 0)
        bpText:SetText(string.format(BPL("hud_prestige"), BP.prestige, into, cost))
    elseif BP.tier >= BP.maxTier then
        into = cost
        bpBar:SetStatusBarColor(1, 0.82, 0)
        local capKey = BP.prestigeEnabled == 1 and "hud_max" or "hud_max_no_prestige"
        local text = BPL("hud_name") .. " " .. BP.tier .. "  —  " .. BPL(capKey)
        if BP.renown > 0 or BP.renownPoints > 0 then
            text = text .. "  —  " .. string.format(BPL("hud_renown"),
                BP.renown, BP.renownPoints, BP.renownPer)
        end
        bpText:SetText(text)
    else
        into = BP.points - BP.tier * BP.perTier
        bpBar:SetStatusBarColor(1, 0.82, 0)
        bpText:SetText(BPL("hud_name") .. " " .. BP.tier .. "  —  " .. into .. " / " .. cost)
    end
    bpBar:SetMinMaxValues(0, cost)
    bpBar:SetValue(into)
    local frac = into / cost
    if frac > 0 and frac < 1 then
        spark:SetPoint("CENTER", bpBar, "LEFT", frac * bpBar:GetWidth(), 0)
        spark:Show()
    else
        spark:Hide()
    end

    claimable = (BP.tier > BP.claimed) or (BP.tier > BP.claimedEpic)
    if not claimable then
        bpHolder:SetBackdropBorderColor(1, 1, 1, 1)
    end

    UpdateXP()
    UpdatePlayerLevelText()
    UpdateCharSheetLevel()
end

hud:SetScript("OnDragStart", function(self)
    if not DB().locked then
        self.isMoving = true
        self:StartMoving()
    end
end)
hud:SetScript("OnDragStop", function(self)
    if self.isMoving then
        self.isMoving = false
        self:StopMovingOrSizing()
        local point, _, _, x, y = self:GetPoint()
        local db = DB()
        db.point, db.x, db.y = point, x, y
    end
end)
hud:SetScript("OnMouseUp", function(self, button)
    if not self.isMoving and button == "LeftButton" and SeasonPass_Toggle then
        SeasonPass_Toggle()
    end
end)

local function ShowMainTooltip(self)
    GameTooltip:SetOwner(self, "ANCHOR_BOTTOMRIGHT")
    GameTooltip:AddLine(string.format(BPL("title"), BP_SEASON or 1), 1, 0.82, 0)
    GameTooltip:AddLine(BPSeasonName(), 0.8, 0.6, 1)
    if state then
        GameTooltip:AddLine(" ")
        GameTooltip:AddLine(string.format(BPL("tt_tier"), state.tier, state.maxTier, state.points), 1, 1, 1)
        if state.prestige and state.prestige > 0 then
            GameTooltip:AddLine(string.format(BPL("info_prestige"), state.prestige), 1, 0.53, 0)
        end
        if state.streak and state.streak > 1 then
            GameTooltip:AddLine(string.format(BPL("info_streak"), state.streak), 0.7, 1, 0.7)
        end
        if state.weekend == 1 then
            GameTooltip:AddLine(BPL("info_weekend2"), 0, 1, 0)
        end
        if state.events then
            GameTooltip:AddLine(" ")
            GameTooltip:AddLine(BPL("ev_zone") .. ": " .. state.events.zone, 0, 0.8, 1)
            GameTooltip:AddLine(BPL("ev_bounty") .. ": " .. state.events.bounty, 1, 0.53, 0)
            GameTooltip:AddLine(BPL("ev_dungeon") .. ": " .. state.events.dungeon
                .. (state.events.dungeonDone == 1 and " " .. BPL("dungeon_done") or ""), 0.7, 0.7, 1)
            GameTooltip:AddLine(BPL("ev_mutator") .. ": " .. (state.events.mutator or "-"), 1, 0.82, 0)
            if state.events.storm == 1 then
                GameTooltip:AddLine(BPL("ev_storm") .. ": " .. BPL("storm_on"), 0, 0.8, 1)
            end
            if state.events.boss ~= "-" then
                GameTooltip:AddLine(string.format(BPL("boss_active"), state.events.boss), 1, 0.27, 0.27)
            end
        end
        if claimable then
            GameTooltip:AddLine(" ")
            GameTooltip:AddLine(BPL("tt_claim"), 1, 0.82, 0)
        end
    end
    GameTooltip:AddLine(" ")
    GameTooltip:AddLine(BPL("tt_click"), 0.5, 0.5, 0.5)
    GameTooltip:Show()
end
hud:SetScript("OnEnter", ShowMainTooltip)
hud:SetScript("OnLeave", function() GameTooltip:Hide() end)

local pulse = 0
local syncTimer = 0
local loginTimer = nil
hud:SetScript("OnUpdate", function(self, elapsed)
    if claimable then
        -- Goldener Puls-Rahmen um den BP-Balken, solange etwas abholbar ist
        pulse = pulse + elapsed
        local a = 0.55 + 0.45 * math.sin(pulse * 4)
        bpHolder:SetBackdropBorderColor(1, 0.82, 0, a)
    end
    if loginTimer then
        loginTimer = loginTimer - elapsed
        if loginTimer <= 0 then
            loginTimer = nil
            SendChatMessage(".bp sync", "SAY")
        end
    end
    syncTimer = syncTimer + elapsed
    if syncTimer >= 30 then
        syncTimer = 0
        SendChatMessage(".bp sync", "SAY")
    end
end)

-- ===========================================================================
--  Minimap-Knopf
-- ===========================================================================
local mmBtn = CreateFrame("Button", "SeasonPassMinimapButton", Minimap)
mmBtn:SetWidth(33)
mmBtn:SetHeight(33)
mmBtn:SetFrameStrata("MEDIUM")
mmBtn:SetFrameLevel(8)
mmBtn:RegisterForClicks("LeftButtonUp")
mmBtn:RegisterForDrag("LeftButton")

local mmIcon = mmBtn:CreateTexture(nil, "BACKGROUND")
mmIcon:SetTexture("Interface\\Icons\\INV_Misc_Head_Dragon_01")
mmIcon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
mmIcon:SetWidth(20)
mmIcon:SetHeight(20)
mmIcon:SetPoint("CENTER", 0, 1)

local mmBorder = mmBtn:CreateTexture(nil, "OVERLAY")
mmBorder:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
mmBorder:SetWidth(54)
mmBorder:SetHeight(54)
mmBorder:SetPoint("TOPLEFT", 0, 0)
mmBtn:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")

local function MinimapSetPosition()
    local angle = DB().minimapAngle or 3.8
    mmBtn:ClearAllPoints()
    mmBtn:SetPoint("CENTER", Minimap, "CENTER", math.cos(angle) * 80, math.sin(angle) * 80)
end

mmBtn:SetScript("OnClick", function()
    if SeasonPass_Toggle then SeasonPass_Toggle() end
end)
mmBtn:SetScript("OnDragStart", function(self)
    self:SetScript("OnUpdate", function()
        local mx, my = Minimap:GetCenter()
        local cx, cy = GetCursorPosition()
        local scale = Minimap:GetEffectiveScale()
        DB().minimapAngle = math.atan2(cy / scale - my, cx / scale - mx)
        MinimapSetPosition()
    end)
end)
mmBtn:SetScript("OnDragStop", function(self)
    self:SetScript("OnUpdate", nil)
end)
mmBtn:SetScript("OnEnter", ShowMainTooltip)
mmBtn:SetScript("OnLeave", function() GameTooltip:Hide() end)

local events = CreateFrame("Frame")
events:RegisterEvent("VARIABLES_LOADED")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("PLAYER_XP_UPDATE")
events:RegisterEvent("PLAYER_LEVEL_UP")
events:SetScript("OnEvent", function(_, event)
    if event == "VARIABLES_LOADED" then
        ApplySettings()
        MinimapSetPosition()
        if SeasonPass_ApplyTexts then SeasonPass_ApplyTexts() end
    elseif event == "PLAYER_ENTERING_WORLD" then
        loginTimer = 8
        UpdateXP()
    else
        UpdateXP()
    end
end)
