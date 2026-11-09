// Collections and display (Esteria_Housing_Main_Updated.md section 4). Included inside the anonymous namespace of
// mod_esteria_housing.cpp, after HousingAdventure.inc, whose text channel it shares: the addon sends "col\t..." commands
// through ActionCommerce and gets "trophy", "mountdisp", "mannequin", "mqpick", "library", "libdata"/"libmore", "book" and
// "habitat" records back through SMSG_COMMERCE (Collections.lua reads them).
//
// Every display is decor (catalog rows CollectionDecorBase + kind, sql/world/housing_collections_world.sql), so the editor
// places, moves and stores it. Trophy stands, stalls, pedestals, library pieces and pet furniture are objects; what they show
// is spawned with them (DisplayExtras): a replica, a relic or a floating name for a trophy, a mount, a habitat's pets. A
// mannequin is itself a creature. Nothing shown is ever taken from the collection: a display keeps an id, never an item.

    constexpr uint32 DisplayEntryFirst = 9507100, DisplayEntryLast = 9509999, DisplayDefaultModel = 3649;
    constexpr uint32 RelicGoBase = 9506080; // + style - 1 (make: housing_collections_world.sql)
    enum TrophySource : uint8 { TrophyNone = 0, TrophyAchievement = 1, TrophyItem = 2 };
    // a trophy's style: 0 a statue of the boss, 1-8 a relic object, 9 its name only
    constexpr uint8 StyleStatue = 0, StyleAureate = 1, StyleArgent = 2, StyleGleaming = 3, StyleAllianceBanner = 4,
        StyleHordeBanner = 5, StyleNameOnly = 9;
    constexpr uint32 TrophyEffects[] = { 0, 70788, 36945, 46679, 60044 };   // none, radiance, arcane glow, blue flame, victory
    constexpr uint32 AuraFreeze = 16245, AuraStone = 10255, AuraSpectral = 22650;
    // a mannequin's pose: a looping emote or a stand state (sit, kneel)
    constexpr uint32 PoseEmote[] = { 0, EMOTE_STATE_READY1H, EMOTE_STATE_READY2H, EMOTE_STATE_READY_BOW, EMOTE_STATE_READY_RIFLE,
        EMOTE_STATE_READY_SPELL_OMNI, 0, 0 };
    constexpr uint8 PoseKneel = 6, PoseSit = 7, PoseCount = 8, MannequinTypes = 4, MaxHabitatPets = 10;
    constexpr uint8 FlagHideRug = 2; // a habitat's flags: only its pets show
    // pets a habitat holds: the Grand Pet Rug ten, the others six
    uint8 HabitatPets(uint32 decorId) { return decorId == 40273 ? 10 : 6; }
    constexpr size_t MaxPicks = 400;

    // how a mount stands: still (a statue), idle in place, or wandering its radius
    enum MountMotion : uint8 { MotionStill = 0, MotionIdle = 1, MotionWander = 2, MotionDefault = 255 };

    struct Display
    {
        uint8 kind = 0;
        uint32 entry = 0;                    // the pooled creature that carries its name (replica, mount, mannequin, label)
        std::string label, sub;              // its name and title; empty: the trophy's or mount's own
        // a trophy
        uint8 source = TrophyNone, style = StyleStatue, effect = 0;
        uint32 id = 0, date = 0;             // achievement or item; when it was earned or put on show
        // a mount
        uint32 mount = 0;                    // its spell
        uint8 finish = 0;                    // a pedestal's statue: 0 natural, 1 stone, 2 spectral
        // where a replica or mount stands, from the object: yards up and ahead, degrees turned, and its size
        float height = 0, forward = 0, turn = 0, size = 1;
        // a mannequin
        uint8 race = 1, sex = 0, type = 0, pose = 0;
        std::string lookHex, bodyHex;
        std::map<uint8, uint32> gear;        // slot (GearSlotOf) -> item entry, a copy of its look
        // a habitat
        uint8 radius = 5;
        std::vector<uint32> pets;            // companion spells
        // a household service: who may use it (0 the owner only, else Access bits; a chest's withdrawals), a chest's
        // deposits, flags (HouseholdFlag) and an auctioneer's greeting
        uint8 access = AccessEveryone, access2 = 0, flags = 0;
        std::string greeting;
        float side = 0;                      // a replica's or mount's yards to the object's right
        uint8 motion = MotionDefault;        // a mount's MountMotion; MotionDefault: its piece's own
    };

    uint8 MotionOf(Display const& d)
    {
        if (d.motion != MotionDefault)
            return d.motion;
        return d.kind == ColMountPedestal ? MotionStill : d.kind == ColMountMat ? MotionIdle : MotionWander;
    }

    void HouseholdDefaults(Display& d);
    void NameFigure(Display& d, uint32 decorId);

    struct BookEntry { std::string name, group; };
    struct AreaEntry { uint32 id = 0, zone = 0, bit = 0; std::string name; };
    struct Storyline { uint32 first = 0; std::vector<uint32> quests; std::string name, group; };

    std::unordered_map<uint64, Display> s_displays;                       // placed id ->
    // a mat with a mount, or a trophy rug with a trophy: only what stands on it shows
    bool MatHidden(uint64 placed)
    {
        auto it = s_displays.find(placed);
        return it != s_displays.end() && ((it->second.kind == ColMountMat && it->second.mount)
            || (it->second.kind == ColTrophyRug && it->second.source != TrophyNone)
            || (it->second.kind == ColHabitat && (it->second.flags & FlagHideRug)));
    }

    // what each display spawned beside its object: placed id -> instance, its creatures and objects
    struct Extras { uint32 instance = 0; std::vector<ObjectGuid> units, objects; bool animated = false; };
    std::unordered_map<uint64, Extras> s_extras;
    std::unordered_map<ObjectGuid, uint64> s_extraPlaced;                 // a display's creature -> its placed id
    std::map<uint32, BookEntry> s_books;                                  // first page -> its book
    std::map<uint32, std::set<uint32>> s_booksRead;                       // account -> first pages read
    std::vector<AreaEntry> s_areas;
    std::vector<Storyline> s_storylines;
    std::map<std::pair<uint32, std::string>, std::string> s_outfits;     // (account, name) -> gear text
    uint32 s_nextDisplayEntry = DisplayEntryFirst;

    bool IsTrophyKind(uint8 k) { return (k >= ColTrophyMount && k <= ColTrophyCase) || k == ColTrophyRug; }

    // What each trophy piece can show (bit per style): the plaque is the wall's (mounted heads, the dragon skull), the
    // case holds cups and the Horseman's head, the rug banners and statues, the pedestal statues. Any can show a name.
    bool StyleAllowed(uint8 kind, uint8 style)
    {
        uint32 mask = 1u << StyleNameOnly;
        switch (kind)
        {
            case ColTrophyPedestal: mask |= 1u << StyleStatue; break;
            case ColTrophyPlaque: mask |= (1u << 6) | (1u << 8); break;                       // Broodmother's head, dragon skull
            case ColTrophyCase: mask |= (1u << StyleAureate) | (1u << StyleArgent) | (1u << StyleGleaming) | (1u << 7); break;
            case ColTrophyRug: mask |= (1u << StyleStatue) | (1u << StyleAllianceBanner) | (1u << StyleHordeBanner); break;
            default: mask = 0x3ff; break;
        }
        return style <= StyleNameOnly && (mask & (1u << style));
    }

    std::string AllowedStyles(uint8 kind)
    {
        std::string out;
        for (uint8 s = 0; s <= StyleNameOnly; ++s)
            if (StyleAllowed(kind, s))
                out += (out.empty() ? "" : ",") + std::to_string(s);
        return out;
    }
    bool IsMountKind(uint8 k) { return (k >= ColStall && k <= ColMountPedestal) || k == ColMountMat; }
    bool IsLibraryKind(uint8 k) { return k >= ColBookshelf && k <= ColReadingNook; }
    bool IsPetKind(uint8 k) { return k >= ColHabitat && k <= ColFeeder; }

    // ---------------------------------------------------------------- saving

    std::string GearText(std::map<uint8, uint32> const& gear)
    {
        std::string out;
        for (auto const& [slot, item] : gear)
            out += S(slot) + ":" + S(item) + ",";
        return out;
    }

    std::map<uint8, uint32> ParseGear(std::string const& text)
    {
        std::map<uint8, uint32> out;
        for (auto const& [slot, item] : ParseMaterials(text)) // the same "a:b," list the commission materials use
            if (slot < 19 && item)
                out[uint8(slot)] = item;
        return out;
    }

    std::string DisplayText(Display const& d)
    {
        std::string pets;
        for (uint32 p : d.pets)
            pets += S(p) + ",";
        char place[96];
        std::snprintf(place, sizeof(place), "%.2f\t%.2f\t%.1f\t%.2f", d.height, d.forward, d.turn, d.size);
        // the order LoadCollections reads; text fields last but the look, which has no tabs
        return Join({ S(d.entry), S(d.source), S(d.id), S(d.date), S(d.style), S(d.effect), S(d.mount), S(d.finish), place,
            S(d.race), S(d.sex), S(d.type), S(d.pose), GearText(d.gear), S(d.radius), pets, d.lookHex, d.bodyHex, d.label, d.sub,
            S(d.access), S(d.access2), S(d.flags), d.greeting, S(int(d.side * 100)), S(d.motion) });
    }

    void SaveDisplay(uint64 placed, Display const& d)
    {
        CharacterDatabase.Execute("REPLACE INTO housing_display (placed_id, config) VALUES ({}, '{}')", placed, Sql(DisplayText(d)));
    }

    Display ParseDisplay(uint8 kind, std::string const& text)
    {
        Fields f = Split(text);
        auto num = [&](size_t i) { return i < f.size() ? uint32(std::strtoul(f[i].c_str(), nullptr, 10)) : 0u; };
        auto real = [&](size_t i, float def) { return i < f.size() && !f[i].empty() ? std::strtof(f[i].c_str(), nullptr) : def; };
        Display d;
        d.kind = kind;
        d.entry = num(0); d.source = uint8(num(1)); d.id = num(2); d.date = num(3); d.style = uint8(num(4)); d.effect = uint8(num(5));
        d.mount = num(6); d.finish = uint8(num(7));
        d.height = real(8, 0); d.forward = real(9, 0); d.turn = real(10, 0); d.size = real(11, 1);
        d.race = uint8(std::max<uint32>(1, num(12))); d.sex = uint8(num(13)); d.type = uint8(num(14)); d.pose = uint8(num(15));
        d.gear = ParseGear(f.size() > 16 ? f[16] : "");
        d.radius = uint8(std::clamp<uint32>(num(17), 2, 10));
        if (f.size() > 18) // "a,b," -> spells
        {
            std::istringstream in(f[18]);
            for (std::string part; std::getline(in, part, ',');)
                if (uint32 const spell = uint32(std::strtoul(part.c_str(), nullptr, 10)); spell && d.pets.size() < MaxHabitatPets)
                    d.pets.push_back(spell);
        }
        d.lookHex = f.size() > 19 ? f[19] : "";
        d.bodyHex = f.size() > 20 ? f[20] : "";
        d.label = f.size() > 21 ? f[21] : "";
        d.sub = f.size() > 22 ? f[22] : "";
        if (f.size() > 25)
        {
            d.access = uint8(num(23)); d.access2 = uint8(num(24)); d.flags = uint8(num(25));
            d.greeting = f.size() > 26 ? f[26] : "";
        }
        if (f.size() > 28)
        {
            d.side = float(int32(std::strtol(f[27].c_str(), nullptr, 10))) / 100.0f;
            d.motion = uint8(num(28));
        }
        return d;
    }

    // Defaults for a new display: where on its object the replica or mount stands (the owner adjusts it).
    Display NewDisplay(uint8 kind)
    {
        Display d;
        d.kind = kind;
        switch (kind)
        {
            case ColTrophyMount: d.height = 1.0f; d.forward = 0.3f; d.size = 0.6f; break;
            case ColTrophyPedestal: d.height = 1.1f; d.size = 0.6f; break;
            case ColTrophyPlaque: d.height = 1.2f; d.forward = 0.2f; d.size = 0.4f; break;
            case ColTrophyCase: d.height = 1.15f; d.size = 0.2f; break;
            case ColTrophyRug: d.size = 0.6f; break;
            case ColStall: d.forward = 2.0f; d.turn = 90; d.radius = 3; break;
            case ColPaddock: d.radius = 4; break;
            case ColMountPedestal: d.height = 1.0f; d.size = 0.5f; break;
            case ColMannequin: d.label = "Mannequin"; break;
            default: HouseholdDefaults(d); break;
        }
        return d;
    }

    // ---------------------------------------------------------------- the pooled names

    // shortcut: like the merchants', a display renamed takes the next pooled entry (clients cache names by entry) and the
    // 2900-entry pool wraps; widen it if a realm ever renames that many displays between client cache clears.
    uint32 NextDisplayEntry()
    {
        for (uint32 tries = 0; tries <= DisplayEntryLast - DisplayEntryFirst; ++tries)
        {
            uint32 const entry = s_nextDisplayEntry;
            s_nextDisplayEntry = entry == DisplayEntryLast ? DisplayEntryFirst : entry + 1;
            CharacterDatabase.Execute("REPLACE INTO housing_counter (name, value) VALUES ('display_entry', {})", s_nextDisplayEntry);
            if (std::none_of(s_displays.begin(), s_displays.end(), [entry](auto const& d) { return d.second.entry == entry; }))
                return entry;
        }
        return 0;
    }

    // The pooled template, named and drawn as the display shows it: created at its size, never seen growing or shrinking.
    void DressTemplate(uint32 entry, std::string const& name, std::string const& sub, uint32 display, float scale)
    {
        auto* t = const_cast<CreatureTemplate*>(sObjectMgr->GetCreatureTemplate(entry));
        if (!t)
            return;
        t->Name = name.empty() ? "Display" : name;
        t->SubName = sub;
        if (!display || !sObjectMgr->GetCreatureModelInfo(display))
            display = DisplayDefaultModel;
        t->Models = { CreatureModel(display, scale, 1.0f) };
        t->InitializeQueryData();
    }

    // The first model a creature template draws, and its scale.
    std::pair<uint32, float> ModelOf(uint32 creatureEntry)
    {
        CreatureTemplate const* t = sObjectMgr->GetCreatureTemplate(creatureEntry);
        CreatureModel const* m = t ? t->GetFirstValidModel() : nullptr;
        return m ? std::make_pair(m->CreatureDisplayID, m->DisplayScale > 0 ? m->DisplayScale : 1.0f) : std::make_pair(0u, 1.0f);
    }

    // ---------------------------------------------------------------- what the collections hold

    // The creature a mount spell rides, or a companion spell summons; 0 when it is neither.
    uint32 MountCreature(uint32 spell)
    {
        if (SpellInfo const* info = sSpellMgr->GetSpellInfo(spell))
            for (SpellEffectInfo const& e : info->Effects)
                if (e.ApplyAuraName == SPELL_AURA_MOUNTED && e.MiscValue > 0)
                    return uint32(e.MiscValue);
        return 0;
    }

    uint32 CompanionCreature(uint32 spell)
    {
        if (SpellInfo const* info = sSpellMgr->GetSpellInfo(spell))
            for (SpellEffectInfo const& e : info->Effects)
                if (e.Effect == SPELL_EFFECT_SUMMON && e.MiscValue > 0)
                    if (SummonPropertiesEntry const* p = sSummonPropertiesStore.LookupEntry(e.MiscValueB); p && p->Type == SUMMON_TYPE_MINIPET)
                        return uint32(e.MiscValue);
        return 0;
    }

    // Every spell any character of the account knows (the one playing now from memory, the others as last saved).
    std::set<uint32> AccountSpells(uint32 account, Player* player)
    {
        std::set<uint32> out;
        if (QueryResult r = CharacterDatabase.Query("SELECT DISTINCT s.spell FROM character_spell s JOIN characters c ON c.guid = s.guid "
            "WHERE c.account = {}", account))
            do out.insert(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        if (player && player->GetSession()->GetAccountId() == account)
            for (auto const& [spell, ps] : player->GetSpellMap())
                if (ps->State != PLAYERSPELL_REMOVED)
                    out.insert(spell);
        return out;
    }

    // achievement -> the earliest date any character of the account earned it
    std::map<uint32, uint32> AccountAchievements(uint32 account, Player* player)
    {
        std::map<uint32, uint32> out;
        if (QueryResult r = CharacterDatabase.Query("SELECT a.achievement, MIN(a.date) FROM character_achievement a JOIN characters c "
            "ON c.guid = a.guid WHERE c.account = {} GROUP BY a.achievement", account))
            do out[r->Fetch()[0].Get<uint32>()] = r->Fetch()[1].Get<uint32>(); while (r->NextRow());
        if (player && player->GetSession()->GetAccountId() == account)
            for (uint32 i = 0; i < sAchievementStore.GetNumRows(); ++i)
                if (sAchievementStore.LookupEntry(i) && player->HasAchieved(i) && !out.count(i))
                    out[i] = uint32(GameTime::GetGameTime().count());
        return out;
    }

    std::set<uint32> AccountQuests(uint32 account, Player* player)
    {
        std::set<uint32> out;
        if (QueryResult r = CharacterDatabase.Query("SELECT DISTINCT q.quest FROM character_queststatus_rewarded q JOIN characters c "
            "ON c.guid = q.guid WHERE c.account = {}", account))
            do out.insert(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        if (player && player->GetSession()->GetAccountId() == account)
            for (uint32 q : player->getRewardedQuests())
                out.insert(q);
        return out;
    }

    std::array<uint32, PLAYER_EXPLORED_ZONES_SIZE> AccountExplored(uint32 account, Player* player)
    {
        std::array<uint32, PLAYER_EXPLORED_ZONES_SIZE> out{};
        if (QueryResult r = CharacterDatabase.Query("SELECT exploredZones FROM characters WHERE account = {}", account))
            do
            {
                std::istringstream in(r->Fetch()[0].Get<std::string>());
                uint32 v = 0;
                for (size_t i = 0; i < out.size() && (in >> v); ++i)
                    out[i] |= v;
            } while (r->NextRow());
        if (player && player->GetSession()->GetAccountId() == account)
            for (size_t i = 0; i < out.size(); ++i)
                out[i] |= player->GetUInt32Value(PLAYER_EXPLORED_ZONES_1 + i);
        return out;
    }

    // The top category an achievement sits under (Dungeons & Raids 168, Player vs. Player 95, World Events 155, ...).
    int32 RootCategory(AchievementEntry const* a)
    {
        int32 id = int32(a->categoryId);
        for (int depth = 0; depth < 8; ++depth)
        {
            AchievementCategoryEntry const* c = sAchievementCategoryStore.LookupEntry(id);
            if (!c || c->parentCategory < 0)
                break;
            id = c->parentCategory;
        }
        return id;
    }

    // The creature an achievement is for: its last kill criterion (a raid's achievement ends on its final boss).
    uint32 TrophyCreature(uint32 achievement)
    {
        uint32 creature = 0;
        if (AchievementCriteriaEntryList const* list = sAchievementMgr->GetAchievementCriteriaByAchievement(achievement))
            for (AchievementCriteriaEntry const* c : *list)
                if (c->requiredType == ACHIEVEMENT_CRITERIA_TYPE_KILL_CREATURE && ModelOf(c->kill_creature.creatureID).first)
                    creature = c->kill_creature.creatureID;
        return creature;
    }

    uint8 DefaultStyle(uint32 achievement, Player* player)
    {
        AchievementEntry const* a = sAchievementStore.LookupEntry(achievement);
        if (!a)
            return StyleNameOnly;
        if (TrophyCreature(achievement))
            return StyleStatue;
        int32 const root = RootCategory(a);
        if (root == 95)
            return player && player->GetTeamId() == TEAM_HORDE ? StyleHordeBanner : StyleAllianceBanner;
        MapEntry const* map = a->mapID >= 0 ? sMapStore.LookupEntry(uint32(a->mapID)) : nullptr;
        if (map && map->IsRaid())
            return StyleAureate;
        return root == 168 ? StyleArgent : StyleGleaming;
    }

    std::string AchievementName(uint32 id)
    {
        AchievementEntry const* a = sAchievementStore.LookupEntry(id);
        return a ? a->name[sWorld->GetDefaultDbcLocale()] : "";
    }

    // QuestSort.dbc's names (the server does not load them): a quest's ZoneOrSort below 0 is one of these.
    std::string QuestSortName(uint32 sort)
    {
        static std::map<uint32, char const*> const names = { { 1, "Epic" }, { 22, "Seasonal" }, { 24, "Herbalism" }, { 61, "Warlock" },
            { 81, "Warrior" }, { 82, "Shaman" }, { 101, "Fishing" }, { 121, "Blacksmithing" }, { 141, "Paladin" }, { 161, "Mage" },
            { 162, "Rogue" }, { 181, "Alchemy" }, { 182, "Leatherworking" }, { 201, "Engineering" }, { 221, "Treasure Map" },
            { 261, "Hunter" }, { 262, "Priest" }, { 263, "Druid" }, { 264, "Tailoring" }, { 284, "Special" }, { 304, "Cooking" },
            { 324, "First Aid" }, { 344, "Legendary" }, { 364, "Darkmoon Faire" }, { 365, "Ahn'Qiraj War" }, { 366, "Lunar Festival" },
            { 367, "Reputation" }, { 368, "Invasion" }, { 369, "Midsummer" }, { 370, "Brewfest" }, { 371, "Inscription" },
            { 372, "Death Knight" }, { 373, "Jewelcrafting" }, { 374, "Noblegarden" }, { 375, "Pilgrim's Bounty" },
            { 376, "Love is in the Air" } };
        auto it = names.find(sort);
        return it == names.end() ? "Other" : it->second;
    }

    std::string AreaName(uint32 area)
    {
        AreaTableEntry const* a = sAreaTableStore.LookupEntry(area);
        return a ? a->area_name[sWorld->GetDefaultDbcLocale()] : "";
    }

    std::string ContinentName(uint32 map)
    {
        switch (map)
        {
            case 0: return "Eastern Kingdoms";
            case 1: return "Kalimdor";
            case 530: return "Outland";
            case 571: return "Northrend";
            default:
                if (MapEntry const* m = sMapStore.LookupEntry(map))
                    return m->name[sWorld->GetDefaultDbcLocale()];
                return "Elsewhere";
        }
    }

    // ---------------------------------------------------------------- loading

    void DressDisplay(Display const& d);
    void LoadHousehold();

    void LoadCollections()
    {
        s_displays.clear(); s_books.clear(); s_booksRead.clear(); s_areas.clear(); s_storylines.clear(); s_outfits.clear();
        std::unordered_map<uint64, uint32> decorOf;
        for (auto const& [id, house] : s_houses)
        {
            for (auto const& [pid, p] : house.placed)
                decorOf[pid] = p.decorId;
            for (auto const& [hood, decor] : house.outdoor)
                for (auto const& [pid, p] : decor)
                    decorOf[pid] = p.decorId;
        }
        if (QueryResult r = CharacterDatabase.Query("SELECT placed_id, config FROM housing_display"))
            do
            {
                uint64 const placed = r->Fetch()[0].Get<uint64>();
                uint8 const kind = decorOf.count(placed) ? CollectionKindOf(decorOf[placed]) : 0;
                if (kind)
                    s_displays[placed] = ParseDisplay(kind, r->Fetch()[1].Get<std::string>());
            } while (r->NextRow());
        if (QueryResult r = CharacterDatabase.Query("SELECT value FROM housing_counter WHERE name = 'display_entry'"))
            s_nextDisplayEntry = std::clamp(r->Fetch()[0].Get<uint32>(), DisplayEntryFirst, DisplayEntryLast);
        if (QueryResult r = CharacterDatabase.Query("SELECT account_id, page_id FROM housing_library_book"))
            do s_booksRead[r->Fetch()[0].Get<uint32>()].insert(r->Fetch()[1].Get<uint32>()); while (r->NextRow());
        if (QueryResult r = CharacterDatabase.Query("SELECT account_id, name, gear FROM housing_outfit"))
            do s_outfits[{ r->Fetch()[0].Get<uint32>(), r->Fetch()[1].Get<std::string>() }] = r->Fetch()[2].Get<std::string>();
            while (r->NextRow());

        // books: the readable objects placed in the world, and readable items, each by its first page
        if (QueryResult r = WorldDatabase.Query("SELECT t.name, IF(t.type = 9, t.Data0, t.Data7), MIN(g.map), MAX(g.zoneId) FROM "
            "gameobject_template t JOIN gameobject g ON g.id = t.entry WHERE (t.type = 9 AND t.Data0 > 0) OR (t.type = 10 AND t.Data7 > 0) "
            "GROUP BY t.entry"))
            do
            {
                Field* f = r->Fetch();
                uint32 const page = f[1].Get<uint32>(), zone = f[3].Get<uint32>();
                std::string const group = zone ? AreaName(zone) : ContinentName(f[2].Get<uint32>());
                s_books.emplace(page, BookEntry{ f[0].Get<std::string>(), group.empty() ? "Elsewhere" : group });
            } while (r->NextRow());
        for (auto const& [entry, item] : *sObjectMgr->GetItemTemplateStore())
            if (item.PageText)
                s_books.emplace(item.PageText, BookEntry{ item.Name1, item.Class == ITEM_CLASS_QUEST ? "Letters and Notes" : "Readable Items" });

        // exploration: the continents' areas the explored-zones bits track
        for (uint32 i = 0; i < sAreaTableStore.GetNumRows(); ++i)
            if (AreaTableEntry const* a = sAreaTableStore.LookupEntry(i))
                if (a->exploreFlag && (a->mapid == 0 || a->mapid == 1 || a->mapid == 530 || a->mapid == 571)
                    && a->exploreFlag < PLAYER_EXPLORED_ZONES_SIZE * 32 && a->area_name[0] && *a->area_name[0])
                    s_areas.push_back({ a->ID, a->zone ? a->zone : a->ID, a->exploreFlag, a->area_name[sWorld->GetDefaultDbcLocale()] });

        // storylines: quest chains of three or more (each quest leading to the next), named for their last quest
        std::unordered_map<uint32, uint32> next;
        std::unordered_set<uint32> led;
        for (auto const& [id, q] : sObjectMgr->GetQuestTemplates())
        {
            uint32 const n = q->GetNextQuestInChain() ? q->GetNextQuestInChain() : q->GetNextQuestId();
            if (n && n != id && sObjectMgr->GetQuestTemplate(n))
            {
                next[id] = n;
                led.insert(n);
            }
        }
        for (auto const& [id, n] : next)
        {
            if (led.count(id))
                continue;
            Storyline s;
            s.first = id;
            std::unordered_set<uint32> seen;
            for (uint32 q = id; q && seen.insert(q).second && s.quests.size() < 60;)
            {
                s.quests.push_back(q);
                auto it = next.find(q);
                q = it == next.end() ? 0 : it->second;
            }
            if (s.quests.size() < 3)
                continue;
            Quest const* last = sObjectMgr->GetQuestTemplate(s.quests.back());
            Quest const* first = sObjectMgr->GetQuestTemplate(id);
            s.name = last ? last->GetTitle() : "";
            int32 const zone = first ? first->GetZoneOrSort() : 0;
            s.group = zone > 0 ? AreaName(uint32(zone)) : QuestSortName(uint32(-zone));
            if (s.group.empty())
                s.group = "Other";
            s_storylines.push_back(std::move(s));
        }
        for (auto& [placed, d] : s_displays)
            if (d.entry)
            {
                s_nextDisplayEntry = std::max(s_nextDisplayEntry, std::min(d.entry + 1, DisplayEntryLast));
                DressDisplay(d); // the pool's templates load unnamed
            }
        LOG_INFO("module", "housing: {} displays, {} books, {} explorable areas, {} storylines", s_displays.size(), s_books.size(),
            s_areas.size(), s_storylines.size());
        LoadHousehold();
    }

    // ---------------------------------------------------------------- the world

    Position ExtraSpot(Placed const& p, Display const& d)
    {
        float const yaw = p.yaw, s = p.scale * BaseScale(p.decorId);
        float const c = std::cos(yaw), n = std::sin(yaw);
        return Position(p.pos[0] + (d.forward * c + d.side * n) * s, p.pos[1] + (d.forward * n - d.side * c) * s,
            p.pos[2] + d.height * s, Position::NormalizeOrientation(yaw + d.turn * float(M_PI) / 180.0f));
    }

    GameObject* SpawnExtraGo(Map* map, uint32 entry, Position const& at, float scale)
    {
        float const o = at.GetOrientation();
        GameObject* go = new GameObject();
        if (!go->Create(map->GenerateLowGuid<HighGuid::GameObject>(), entry, map, PHASEMASK_NORMAL, at.GetPositionX(), at.GetPositionY(),
            at.GetPositionZ(), o, G3D::Quat(0, 0, std::sin(o / 2), std::cos(o / 2)), 100, GO_STATE_READY))
        {
            delete go;
            return nullptr;
        }
        go->SetObjectScale(scale);
        go->SetRespawnTime(0);
        go->SetSpawnedByDefault(false);
        map->AddToMap(go, false);
        return go;
    }

    // Wandering pets and paddock mounts, still statues and labels: the AI every display creature runs.
    struct DisplayAI : public ScriptedAI
    {
        explicit DisplayAI(Creature* c) : ScriptedAI(c)
        {
            me->SetReactState(REACT_PASSIVE);
            me->SetCombatMovement(false);
        }

        struct Spot { Position at; uint8 kind = 0; float ring = 0.6f; }; // ring: how far from it the visitor stands
        bool m_roam = false;
        Position m_center;
        float m_radius = 0;
        std::vector<Spot> m_spots;      // beds, toys and feeders a pet goes to
        uint32 m_wait = 0, m_rest = 0, m_emote = 0, m_emoteWait = 0;
        uint8 m_doing = 0;              // 0 idle, 1 walking, 2 resting at a spot

        void Roam(Position const& center, float radius, std::vector<Spot> spots)
        {
            m_roam = true;
            m_center = center;
            m_radius = radius;
            m_spots = std::move(spots);
            m_wait = urand(1000, 5000);
            me->SetWalk(true);
        }

        float FloorAt(float x, float y) const
        {
            float const z = me->GetMap()->GetHeight(me->GetPhaseMask(), x, y, m_center.GetPositionZ() + 2.0f, true, 5.0f);
            return std::abs(z - m_center.GetPositionZ()) < 3.0f ? z : m_center.GetPositionZ();
        }

        void Stand()
        {
            me->SetStandState(UNIT_STAND_STATE_STAND);
            me->SetEmoteState(EMOTE_ONESHOT_NONE);
            m_emote = 0;
        }

        void UpdateAI(uint32 diff) override
        {
            if (!m_roam)
                return;
            if (m_doing == 2)
            {
                if (m_emote && (m_emoteWait += diff) >= 3000)
                {
                    m_emoteWait = 0;
                    me->HandleEmoteCommand(m_emote);
                }
                if (m_rest > diff) { m_rest -= diff; return; }
                Stand();
                m_doing = 0;
                m_wait = urand(3000, 9000);
                return;
            }
            if (m_doing == 1)
                return; // MovementInform
            if (m_wait > diff) { m_wait -= diff; return; }
            m_doing = 1;
            if (!m_spots.empty() && urand(0, 99) < 40)
            {
                Spot const& s = m_spots[urand(0, uint32(m_spots.size() - 1))];
                float const a = frand(0, 2 * float(M_PI));
                float const x = s.at.GetPositionX() + s.ring * std::cos(a), y = s.at.GetPositionY() + s.ring * std::sin(a);
                me->GetMotionMaster()->MovePoint(1 + s.kind, x, y, FloorAt(x, y), FORCED_MOVEMENT_NONE, 0.f, 0.f, false);
                return;
            }
            float const a = frand(0, 2 * float(M_PI)), r = frand(0.5f, std::max(0.6f, m_radius));
            float const x = m_center.GetPositionX() + r * std::cos(a), y = m_center.GetPositionY() + r * std::sin(a);
            me->GetMotionMaster()->MovePoint(1, x, y, FloorAt(x, y), FORCED_MOVEMENT_NONE, 0.f, 0.f, false);
        }

        void MovementInform(uint32 type, uint32 id) override
        {
            if (type != POINT_MOTION_TYPE || m_doing != 1)
                return;
            uint8 const kind = uint8(id - 1);
            if (kind == ColPetBed)
            {
                me->SetStandState(UNIT_STAND_STATE_SLEEP);
                m_rest = urand(15000, 40000);
            }
            else if (kind == ColFeeder || kind == ColPetToy)
            {
                m_emote = kind == ColFeeder ? EMOTE_ONESHOT_EAT : EMOTE_ONESHOT_ATTACK1H;
                me->HandleEmoteCommand(m_emote);
                m_rest = urand(6000, 14000);
            }
            else
            {
                m_doing = 0;
                m_wait = urand(4000, 12000);
                return;
            }
            m_emoteWait = 0;
            m_doing = 2;
        }

        void AttackStart(Unit*) override { }
        void MoveInLineOfSight(Unit*) override { }
        void EnterEvadeMode(EvadeReason) override { }
    };

    class npc_esteria_housing_display : public CreatureScript
    {
    public:
        npc_esteria_housing_display() : CreatureScript("npc_esteria_housing_display") { }
        CreatureAI* GetAI(Creature* creature) const override { return new DisplayAI(creature); }
        bool OnGossipHello(Player* player, Creature* creature) override;
        bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override;
        bool OnGossipSelectCode(Player* player, Creature* creature, uint32 sender, uint32 action, char const* code) override;
    };

    void Calm(Creature* c)
    {
        c->SetFlag(UNIT_FIELD_FLAGS, UNIT_FLAG_NON_ATTACKABLE | UNIT_FLAG_IMMUNE_TO_PC | UNIT_FLAG_IMMUNE_TO_NPC);
        c->SetReactState(REACT_PASSIVE);
        c->SetFaction(35);
    }

    bool AnimatedRoom(uint32 instance)
    {
        uint32 animated = 0;
        for (auto const& [placed, e] : s_extras)
            if (e.instance == instance && e.animated)
                animated += uint32(e.units.size());
        return animated < s_config.maxAnimated;
    }

    void DespawnDisplayExtras(Map* map, uint64 placed)
    {
        auto it = s_extras.find(placed);
        if (it == s_extras.end())
            return;
        if (it->second.instance == map->GetInstanceId())
        {
            for (ObjectGuid const& g : it->second.units)
                if (Creature* c = map->GetCreature(g))
                    c->DespawnOrUnsummon();
            for (ObjectGuid const& g : it->second.objects)
                if (GameObject* go = map->GetGameObject(g))
                {
                    go->SetRespawnTime(0);
                    go->Delete();
                }
        }
        for (ObjectGuid const& g : it->second.units)
            s_extraPlaced.erase(g);
        s_extras.erase(it);
    }

    void SendLookHex(Player* to, ObjectGuid guid, std::string const& lookHex, std::string const& bodyHex);

    void PushTemplateName(Map* map, uint32 entry)
    {
        if (CreatureTemplate const* t = sObjectMgr->GetCreatureTemplate(entry))
        {
            WorldPacket name = t->queryData;
            map->DoForAllPlayers([&](Player* p) { p->SendDirectMessage(&name); });
        }
    }

    void SpawnHouseholdExtras(Map* map, Placed const& p, Extras& e);
    void ApplyFigure(Creature* c, Display const& d, uint32 decorId);

    // What a display shows beside its object; called with the object's spawn (Spawn) and again after every change.
    void SpawnDisplayExtras(Map* map, Placed const& p)
    {
        DespawnDisplayExtras(map, p.id);
        if (IsHouseholdKind(CollectionKindOf(p.decorId))) // a hidden banker, mailbox or spell focus beside the piece
        {
            Extras e;
            e.instance = map->GetInstanceId();
            SpawnHouseholdExtras(map, p, e);
            if (!e.units.empty() || !e.objects.empty())
                s_extras[p.id] = std::move(e);
            return;
        }
        auto it = s_displays.find(p.id);
        if (it == s_displays.end())
            return;
        Display const& d = it->second;
        Extras e;
        e.instance = map->GetInstanceId();
        Position const at = ExtraSpot(p, d);
        auto summon = [&](uint32 entry, Position const& pos) -> Creature* {
            Creature* c = map->SummonCreature(entry, pos);
            if (c)
            {
                Calm(c);
                e.units.push_back(c->GetGUID());
                s_extraPlaced[c->GetGUID()] = p.id;
            }
            return c;
        };
        if (IsTrophyKind(d.kind) && d.source != TrophyNone && d.entry)
        {
            uint32 const creature = d.source == TrophyAchievement && d.style == StyleStatue ? TrophyCreature(d.id) : 0;
            if (creature)
            {
                if (Creature* c = summon(d.entry, at))
                {
                    c->SetDisableGravity(true);
                    c->SetControlled(true, UNIT_STATE_ROOT);
                    c->AddAura(AuraFreeze, c);
                    if (d.effect && d.effect < std::size(TrophyEffects))
                        c->AddAura(TrophyEffects[d.effect], c);
                }
            }
            else
            {
                if (d.style >= StyleAureate && d.style < StyleNameOnly)
                    if (GameObject* go = SpawnExtraGo(map, RelicGoBase + d.style - 1, at, d.size * p.scale * 2.0f))
                        e.objects.push_back(go->GetGUID());
                // the name floats over the relic (or alone), on a speck of a model (the template's scale)
                Position label = at;
                label.m_positionZ += 1.0f * p.scale;
                if (Creature* c = summon(d.entry, label))
                {
                    c->SetDisableGravity(true);
                    c->SetControlled(true, UNIT_STATE_ROOT);
                }
            }
        }
        else if (IsMountKind(d.kind) && d.mount && d.entry)
        {
            uint8 const motion = MotionOf(d);
            // wandering counts against the realm's moving displays; past the limit a mount idles in place
            bool const wander = motion == MotionWander && AnimatedRoom(e.instance);
            // a roaming mount starts on the ground, beside the paddock rather than up on it
            Position start = at;
            if (wander)
            {
                start.m_positionZ = p.pos[2];
                if (d.kind == ColPaddock)
                    start.m_positionX += 1.8f * p.scale * BaseScale(p.decorId);
            }
            if (Creature* c = summon(d.entry, start))
            {
                if (!wander)
                    c->SetControlled(true, UNIT_STATE_ROOT);
                if (motion == MotionStill)
                {
                    c->AddAura(AuraFreeze, c);
                    if (d.finish == 1)
                        c->AddAura(AuraStone, c);
                    else if (d.finish == 2)
                        c->AddAura(AuraSpectral, c);
                }
                if (motion == MotionStill || (!wander && d.height > 0.05f))
                    c->SetDisableGravity(true); // a statue, or a mount raised off the floor, stays where it is put
                if (wander)
                    if (auto* ai = dynamic_cast<DisplayAI*>(c->AI()))
                    {
                        // around a stall or paddock, on the ground, coming back to it to graze (at its edge, not on it)
                        std::vector<DisplayAI::Spot> spots;
                        float const s = p.scale * BaseScale(p.decorId);
                        Position const piece(p.pos[0], p.pos[1], p.pos[2]);
                        if (d.kind == ColPaddock)
                            spots.push_back({ piece, ColFeeder, 1.8f * s });
                        else if (d.kind == ColStall)
                            spots.push_back({ at, ColFeeder, 0.4f });
                        ai->Roam(d.kind == ColPaddock || d.kind == ColStall ? piece : at, float(d.radius), spots);
                    }
                e.animated = wander;
            }
        }
        else if (d.kind == ColHabitat && !d.pets.empty())
        {
            // the pet furniture near the habitat is where its pets go to sleep, play and eat
            std::vector<DisplayAI::Spot> spots;
            if (House* house = HouseOfPlaced(p.id))
            {
                auto look = [&](std::map<uint64, Placed> const& decor) {
                    if (!decor.count(p.id))
                        return;
                    for (auto const& [id, q] : decor)
                        if (uint8 const k = CollectionKindOf(q.decorId); k >= ColPetBed && k <= ColFeeder)
                            if (std::hypot(q.pos[0] - p.pos[0], q.pos[1] - p.pos[1]) <= d.radius * 2.0f + 2.0f)
                                spots.push_back({ Position(q.pos[0], q.pos[1], q.pos[2]), k });
                };
                look(house->placed);
                for (auto const& [hood, decor] : house->outdoor)
                    look(decor);
            }
            for (uint32 spell : d.pets)
            {
                uint32 const creature = CompanionCreature(spell);
                if (!creature)
                    continue;
                bool const animated = AnimatedRoom(e.instance);
                float const a = frand(0, 2 * float(M_PI));
                Position spot(p.pos[0] + std::cos(a), p.pos[1] + std::sin(a), p.pos[2], a);
                Creature* c = map->SummonCreature(creature, spot);
                if (!c)
                    continue;
                Calm(c);
                // talking to a pet opens its habitat (whose rug may be hidden); EsteriaHousingHousehold catches the gossip
                c->ReplaceAllNpcFlags(UNIT_NPC_FLAG_GOSSIP);
                s_extraPlaced[c->GetGUID()] = p.id;
                c->AIM_Initialize(new DisplayAI(c)); // the pet's own AI would follow an owner; this one keeps it home
                if (animated)
                    static_cast<DisplayAI*>(c->AI())->Roam(Position(p.pos[0], p.pos[1], p.pos[2]), float(d.radius), spots);
                else
                    c->SetStandState(UNIT_STAND_STATE_SLEEP); // past the realm's limit of moving displays, it naps
                e.units.push_back(c->GetGUID());
                e.animated = e.animated || animated;
            }
        }
        if (!e.units.empty() || !e.objects.empty())
            s_extras[p.id] = std::move(e);
    }

    // A mannequin: a character model, its gear drawn from item looks (the mirror image), its customization by guid.
    void SpawnMannequin(Map* map, Placed const& p)
    {
        auto it = s_displays.find(p.id);
        if (it == s_displays.end())
        {
            Display d = NewDisplay(CollectionKindOf(p.decorId));
            NameFigure(d, p.decorId);
            d.lookHex = DefaultLookHex(d.race, d.sex);
            if (!(d.entry = NextDisplayEntry()))
                return;
            it = s_displays.emplace(p.id, d).first;
            SaveDisplay(p.id, d);
        }
        if (it->second.lookHex.empty()) // placed before figures had a default look: the customizer needs one
        {
            it->second.lookHex = DefaultLookHex(it->second.race, it->second.sex);
            SaveDisplay(p.id, it->second);
        }
        Display const& d = it->second;
        ChrRacesEntry const* race = sChrRacesStore.LookupEntry(d.race);
        uint32 const display = race ? (d.sex ? race->model_f : race->model_m) : 0;
        // The template keeps the placeholder model, as a merchant's does. The unit is created with it and then switched to
        // the race's body below; that model change is what makes the client rebuild it as a retail character (race and
        // mirror flag set by then). Created with the race's body already, it stayed the stock model, and no customizer.
        DressTemplate(d.entry, d.label, d.sub, 0, 1.0f);
        Creature* c = map->SummonCreature(d.entry, Position(p.pos[0], p.pos[1], p.pos[2], p.yaw));
        if (!c)
            return;
        Calm(c);
        c->SetObjectScale(p.scale);
        if (display)
        {
            c->SetDisplayId(display);
            c->SetNativeDisplayId(display);
            c->SetByteValue(UNIT_FIELD_BYTES_0, 0, d.race);
            c->SetByteValue(UNIT_FIELD_BYTES_0, 1, CLASS_WARRIOR);
            c->SetByteValue(UNIT_FIELD_BYTES_0, 2, d.sex);
            c->SetFlag(UNIT_FIELD_FLAGS_2, UNIT_FLAG2_MIRROR_IMAGE);
        }
        for (uint8 i = 0; i < 3; ++i)
            if (auto g = d.gear.find(uint8(GearMainHand + i)); g != d.gear.end())
                c->SetUInt32Value(UNIT_VIRTUAL_ITEM_SLOT_ID + i, g->second);
        c->SetControlled(true, UNIT_STATE_ROOT);
        uint8 const pose = d.pose < PoseCount ? d.pose : 0;
        if (pose == PoseKneel)
            c->SetStandState(UNIT_STAND_STATE_KNEEL);
        else if (pose == PoseSit)
            c->SetStandState(UNIT_STAND_STATE_SIT);
        else if (PoseEmote[pose])
        {
            c->SetEmoteState(Emote(PoseEmote[pose]));
            c->SetSheath(pose == 3 || pose == 4 ? SHEATH_STATE_RANGED : SHEATH_STATE_MELEE);
        }
        if (d.type == 1 || d.type == 3)
            c->AddAura(AuraFreeze, c);
        if (d.type == 1)
            c->AddAura(AuraStone, c);
        else if (d.type == 2)
            c->AddAura(AuraSpectral, c);
        ApplyFigure(c, d, p.decorId);
        s_spawned[map->GetInstanceId()][p.id] = c->GetGUID();
        s_extraPlaced[c->GetGUID()] = p.id;
        ObjectGuid const guid = c->GetGUID();
        map->DoForAllPlayers([&](Player* player) { SendLookHex(player, guid, d.lookHex, d.bodyHex); });
    }

    void StorageRemoved(uint64 placed, CharacterDatabaseTransaction trans);

    void CollectionRemoved(uint64 placed, CharacterDatabaseTransaction trans)
    {
        StorageRemoved(placed, trans);
        if (s_displays.erase(placed))
            trans->Append("DELETE FROM housing_display WHERE placed_id = {}", placed);
    }

    // The names of a map's displays (cached by entry, the pool's are reused) and its mannequins' looks, for a player arriving.
    void PushDisplayNames(Player* player, Map* map)
    {
        std::set<uint32> sent;
        auto name = [&](uint32 entry) {
            if (!entry || !sent.insert(entry).second)
                return;
            if (CreatureTemplate const* t = sObjectMgr->GetCreatureTemplate(entry))
            {
                WorldPacket packet = t->queryData;
                player->SendDirectMessage(&packet);
            }
        };
        for (auto const& [placed, e] : s_extras)
            if (e.instance == map->GetInstanceId())
                if (auto d = s_displays.find(placed); d != s_displays.end())
                    name(d->second.entry);
        for (auto const& [placed, guid] : s_spawned[map->GetInstanceId()])
            if (auto d = s_displays.find(placed); d != s_displays.end() && IsFigureKind(d->second.kind))
            {
                name(d->second.entry);
                SendLookHex(player, guid, d->second.lookHex, d->second.bodyHex);
            }
    }

    bool DisplayMirrorImage(Player* player, Unit* unit)
    {
        Creature* c = unit->ToCreature();
        if (!c || c->GetEntry() < DisplayEntryFirst || c->GetEntry() > DisplayEntryLast)
            return false;
        auto placed = s_extraPlaced.find(c->GetGUID());
        auto d = placed == s_extraPlaced.end() ? s_displays.end() : s_displays.find(placed->second);
        if (d == s_displays.end() || !IsFigureKind(d->second.kind))
            return false;
        Display const& m = d->second;
        SendLookHex(player, c->GetGUID(), m.lookHex, m.bodyHex);
        WorldPacket data(SMSG_MIRRORIMAGE_DATA, 68);
        data << c->GetGUID() << uint32(c->GetDisplayId()) << uint8(m.race) << uint8(m.sex) << uint8(CLASS_WARRIOR);
        data << uint8(0) << uint8(0) << uint8(0) << uint8(0) << uint8(0) << uint32(0); // the look carries these
        for (uint8 slot : MirrorSlots)
        {
            auto g = m.gear.find(slot);
            ItemTemplate const* t = g == m.gear.end() ? nullptr : sObjectMgr->GetItemTemplate(g->second);
            data << uint32(t ? t->DisplayInfoID : 0);
        }
        player->SendDirectMessage(&data);
        return true;
    }

    // ---------------------------------------------------------------- reading books

    // A book was opened (a readable object used, or a readable item read): the account has it in its library from now on.
    void BookRead(Player* player, uint32 page)
    {
        if (!page || !s_books.count(page))
            return;
        uint32 const account = player->GetSession()->GetAccountId();
        if (!s_booksRead[account].insert(page).second)
            return;
        CharacterDatabase.Execute("INSERT IGNORE INTO housing_library_book (account_id, page_id, read_at) VALUES ({}, {}, {})", account,
            page, uint32(GameTime::GetGameTime().count()));
        ChatHandler(player->GetSession()).PSendSysMessage("|cffffd100{}|r is now in your library.", s_books[page].name);
    }

    // ---------------------------------------------------------------- the windows

    struct ViewCtx { Player* player; uint64 placed; House* house; Placed const* p; Display* d; bool owner; };
    void SendStorage(ViewCtx const& v, std::string const& message = "");
    bool HandleHousehold(ViewCtx& v, std::string const& verb, Fields const& f);
    void FigureChanged(ViewCtx const& v);
    bool OpenHousehold(ViewCtx& v, WorldObject* object);
    void HouseholdSelect(Player* player, WorldObject* object, uint32 sender, uint32 action, char const* code);

    std::string LabelOf(Display const& d, std::string const& fallback) { return d.label.empty() ? fallback : d.label; }

    std::string DateText(uint32 t)
    {
        if (!t)
            return "";
        std::time_t const tt = std::time_t(t);
        std::tm tm{};
        localtime_r(&tt, &tm);
        char out[32];
        std::strftime(out, sizeof(out), "%b %d, %Y", &tm);
        return out;
    }

    // The name a trophy shows: the owner's label, else the achievement's or item's.
    std::string TrophyName(Display const& d)
    {
        if (!d.label.empty())
            return d.label;
        if (d.source == TrophyAchievement)
            return AchievementName(d.id);
        if (ItemTemplate const* t = d.source == TrophyItem ? sObjectMgr->GetItemTemplate(d.id) : nullptr)
            return t->Name1;
        return "";
    }

    std::string Side(Display const& d)
    {
        char out[16];
        std::snprintf(out, sizeof(out), "%.2f", d.side);
        return out;
    }

    std::string PlaceText(Display const& d)
    {
        char out[96];
        std::snprintf(out, sizeof(out), "%.2f\t%.2f\t%.0f\t%.2f", d.height, d.forward, d.turn, d.size);
        return out;
    }

    void SendTrophy(ViewCtx const& v)
    {
        Display const& d = *v.d;
        std::string link;
        if (d.source == TrophyItem)
            link = ItemLink(nullptr, d.id);
        std::string text = "trophy\n" + Join({ "trophy", S(v.placed), S(int(v.owner)), S(d.kind), S(d.source), S(d.id), DateText(d.date),
            TrophyName(d), S(d.style), S(d.effect), PlaceText(d), d.label, d.sub, link, S(int(TrophyCreature(d.source == TrophyAchievement ? d.id : 0) != 0)),
            Side(d), AllowedStyles(d.kind) });
        if (v.owner)
        {
            for (auto const& [id, date] : AccountAchievements(v.house->account, v.player))
                if (AchievementEntry const* a = sAchievementStore.LookupEntry(id); a && !(a->flags & ACHIEVEMENT_FLAG_COUNTER))
                    text += "\n" + Join({ "ta", S(id), DateText(date), a->name[sWorld->GetDefaultDbcLocale()], S(RootCategory(a)),
                        S(int(TrophyCreature(id) != 0)) });
            std::set<uint32> seen;
            auto visit = [&](Item* it) {
                if (!it || seen.size() >= MaxPicks || !seen.insert(it->GetEntry()).second)
                    return;
                ItemTemplate const* t = it->GetTemplate();
                text += "\n" + Join({ "ti", S(it->GetEntry()), t->Name1, S(t->Quality), ItemLink(it, it->GetEntry()) });
            };
            for (uint8 i = EQUIPMENT_SLOT_START; i < INVENTORY_SLOT_ITEM_END; ++i)
                visit(v.player->GetItemByPos(INVENTORY_SLOT_BAG_0, i));
            for (uint8 i = BANK_SLOT_ITEM_START; i < BANK_SLOT_ITEM_END; ++i)
                visit(v.player->GetItemByPos(INVENTORY_SLOT_BAG_0, i));
            for (uint8 b = INVENTORY_SLOT_BAG_START; b < INVENTORY_SLOT_BAG_END; ++b)
                if (Bag* bag = v.player->GetBagByPos(b))
                    for (uint32 j = 0; j < bag->GetBagSize(); ++j)
                        visit(bag->GetItemByPos(uint8(j)));
            for (uint8 b = BANK_SLOT_BAG_START; b < BANK_SLOT_BAG_END; ++b)
                if (Bag* bag = v.player->GetBagByPos(b))
                    for (uint32 j = 0; j < bag->GetBagSize(); ++j)
                        visit(bag->GetItemByPos(uint8(j)));
        }
        SendCommerce(v.player, text);
    }

    std::string MountName(uint32 spell)
    {
        SpellInfo const* info = sSpellMgr->GetSpellInfo(spell);
        return info ? info->SpellName[sWorld->GetDefaultDbcLocale()] : "";
    }

    void SendMount(ViewCtx const& v)
    {
        Display const& d = *v.d;
        std::string text = "mountdisp\n" + Join({ "mount", S(v.placed), S(int(v.owner)), S(d.kind), S(d.mount), LabelOf(d, MountName(d.mount)),
            S(d.finish), PlaceText(d), d.label, d.sub, Side(d), S(MotionOf(d)), S(d.radius) });
        if (v.owner)
        {
            std::set<std::string> names; // one row per mount, though some have a spell per faction
            for (uint32 spell : AccountSpells(v.house->account, v.player))
                if (MountCreature(spell) && ModelOf(MountCreature(spell)).first && names.insert(MountName(spell)).second)
                    text += "\n" + Join({ "mo", S(spell), MountName(spell) });
        }
        SendCommerce(v.player, text);
    }

    std::string SlotItemText(uint8 slot, uint32 entry)
    {
        ItemTemplate const* t = sObjectMgr->GetItemTemplate(entry);
        return Join({ "slot", S(slot), S(entry), t ? t->Name1 : "", S(t ? t->Quality : 0), t ? ItemLink(nullptr, entry) : "" });
    }

    void SendMannequin(ViewCtx const& v)
    {
        Display const& d = *v.d;
        ObjectGuid guid;
        if (auto it = s_spawned[v.player->GetInstanceId()].find(v.placed); it != s_spawned[v.player->GetInstanceId()].end())
            guid = it->second;
        std::string text = "mannequin\n" + Join({ "mq", S(v.placed), S(int(v.owner)), S(d.race), S(d.sex), S(d.type), S(d.pose), d.label,
            d.sub, GuidHex(guid), S(d.kind) });
        for (auto const& [slot, entry] : d.gear)
            text += "\n" + SlotItemText(slot, entry);
        if (v.owner)
            for (auto const& [key, gear] : s_outfits)
                if (key.first == v.house->account)
                    text += "\noutfit\t" + key.second;
        SendCommerce(v.player, text);
    }

    // What may go in a mannequin's slot: the character's own gear (bags, bank, worn) and the account's collected looks.
    void SendMannequinPicks(ViewCtx const& v, uint8 slot)
    {
        std::string text = Join({ "mqpick", S(v.placed), S(slot) });
        std::set<uint32> seen;
        auto fits = [slot](ItemTemplate const* t) {
            uint8 const s = GearSlotOf(t);
            return s == slot || (slot == GearOffHand && t->InventoryType == INVTYPE_WEAPON);
        };
        auto add = [&](uint32 entry, char const* source) {
            ItemTemplate const* t = sObjectMgr->GetItemTemplate(entry);
            if (!t || !fits(t) || seen.size() >= MaxPicks || !seen.insert(entry).second)
                return;
            text += "\n" + Join({ "c", S(entry), t->Name1, S(t->Quality), source, ItemLink(nullptr, entry) });
        };
        auto visit = [&](Item* it) { if (it) add(it->GetEntry(), "Owned"); };
        Player* p = v.player;
        for (uint8 i = EQUIPMENT_SLOT_START; i < INVENTORY_SLOT_ITEM_END; ++i)
            visit(p->GetItemByPos(INVENTORY_SLOT_BAG_0, i));
        for (uint8 i = BANK_SLOT_ITEM_START; i < BANK_SLOT_ITEM_END; ++i)
            visit(p->GetItemByPos(INVENTORY_SLOT_BAG_0, i));
        for (uint8 b = INVENTORY_SLOT_BAG_START; b < INVENTORY_SLOT_BAG_END; ++b)
            if (Bag* bag = p->GetBagByPos(b))
                for (uint32 j = 0; j < bag->GetBagSize(); ++j)
                    visit(bag->GetItemByPos(uint8(j)));
        for (uint8 b = BANK_SLOT_BAG_START; b < BANK_SLOT_BAG_END; ++b)
            if (Bag* bag = p->GetBagByPos(b))
                for (uint32 j = 0; j < bag->GetBagSize(); ++j)
                    visit(bag->GetItemByPos(uint8(j)));
        // shortcut: at most MaxPicks per slot, owned gear first; a search on the server would lift the cap for huge collections.
        if (QueryResult r = CharacterDatabase.Query("SELECT item_template_id FROM custom_unlocked_appearances WHERE account_id = {}",
            v.house->account))
            do add(r->Fetch()[0].Get<uint32>(), "Collected"); while (r->NextRow());
        SendCommerce(v.player, text);
    }

    bool MayDress(Player* player, uint32 account, uint32 entry, uint8 source)
    {
        if (source == 0)
            return player->HasItemCount(entry, 1, true);
        QueryResult r = CharacterDatabase.Query("SELECT 1 FROM custom_unlocked_appearances WHERE account_id = {} AND item_template_id = {}",
            account, entry);
        return r != nullptr;
    }

    void SendHabitat(ViewCtx const& v)
    {
        Display const& d = *v.d;
        std::string text = "habitat\n" + Join({ "hab", S(v.placed), S(int(v.owner)), S(d.radius), S(HabitatPets(v.p->decorId)),
            S(int((d.flags & FlagHideRug) != 0)) });
        std::set<uint32> chosen(d.pets.begin(), d.pets.end());
        std::set<uint32> listed;
        auto row = [&](uint32 spell) {
            uint32 const creature = CompanionCreature(spell);
            CreatureTemplate const* t = creature ? sObjectMgr->GetCreatureTemplate(creature) : nullptr;
            if (t && listed.insert(spell).second)
                text += "\n" + Join({ "pet", S(spell), t->Name, S(int(chosen.count(spell) != 0)) });
        };
        for (uint32 spell : d.pets)
            row(spell);
        if (v.owner)
            for (uint32 spell : AccountSpells(v.house->account, v.player))
                row(spell);
        SendCommerce(v.player, text);
    }

    // A library tab, in chunks the client strings together ("libdata" then "libmore").
    void SendLibraryTab(ViewCtx const& v, uint8 tab)
    {
        uint32 const account = v.house->account;
        std::vector<std::string> lines;
        uint32 have = 0, total = 0;
        std::map<std::string, std::vector<std::string>> groups;
        if (tab == 1) // books
        {
            std::set<uint32> const& read = s_booksRead[account];
            for (auto const& [page, b] : s_books)
            {
                bool const got = read.count(page) != 0;
                have += got; ++total;
                groups[b.group].push_back(Join({ "e", S(page), b.name, S(int(got)), "" }));
            }
        }
        else if (tab == 2) // exploration
        {
            auto const explored = AccountExplored(account, v.player);
            for (AreaEntry const& a : s_areas)
            {
                bool const got = (explored[a.bit / 32] >> (a.bit % 32)) & 1;
                have += got; ++total;
                AreaTableEntry const* zone = sAreaTableStore.LookupEntry(a.zone);
                std::string const group = ContinentName(zone ? zone->mapid : 0) + ": " + AreaName(a.zone);
                groups[group].push_back(Join({ "e", S(a.id), a.name, S(int(got)), a.id == a.zone ? "Zone" : "" }));
            }
        }
        else if (tab == 3) // achievements: the client knows their names and categories; it needs what the account earned
        {
            for (auto const& [id, date] : AccountAchievements(account, v.player))
                lines.push_back(Join({ "a", S(id), DateText(date) }));
            have = uint32(lines.size());
        }
        else if (tab == 4) // storylines
        {
            std::set<uint32> const done = AccountQuests(account, v.player);
            for (Storyline const& s : s_storylines)
            {
                uint32 n = 0;
                for (uint32 q : s.quests)
                    n += done.count(q) ? 1 : 0;
                bool const got = n == s.quests.size();
                have += got; ++total;
                groups[s.group].push_back(Join({ "e", S(s.first), s.name, S(int(got)), S(n) + " / " + S(s.quests.size()) }));
            }
        }
        for (auto& [name, rows] : groups)
        {
            lines.push_back("g\t" + name);
            for (std::string& r : rows)
                lines.push_back(std::move(r));
        }
        std::string chunk = Join({ "libdata", S(v.placed), S(tab), S(have), S(total) });
        for (std::string const& line : lines)
        {
            if (chunk.size() + line.size() > 16000)
            {
                SendCommerce(v.player, chunk);
                chunk = "libmore";
            }
            chunk += "\n" + line;
        }
        chunk += "\nlibend";
        SendCommerce(v.player, chunk);
    }

    void SendLibrary(ViewCtx const& v)
    {
        uint8 const tab = v.d->kind == ColLectern ? 4 : v.d->kind == ColDisplayTable ? 2 : v.d->kind == ColReadingNook ? 3 : 1;
        SendCommerce(v.player, Join({ "library", S(v.placed), S(int(v.owner)), v.house->owner, S(tab) }));
        SendLibraryTab(v, tab);
    }

    void SendBook(ViewCtx const& v, uint32 page)
    {
        auto b = s_books.find(page);
        if (b == s_books.end() || !s_booksRead[v.house->account].count(page))
            return SendCommerce(v.player, "note\tThat book is not in this library.");
        std::string text = Join({ "book", S(page), b->second.name });
        std::unordered_set<uint32> seen;
        for (uint32 id = page; id && seen.insert(id).second && seen.size() <= 30;)
        {
            PageText const* pt = sObjectMgr->GetPageText(id);
            if (!pt)
                break;
            std::string body = pt->Text;
            for (char& c : body)
                if (c == '\n') c = '\r'; else if (c == '\t') c = ' ';
            text += "\np\t" + body;
            id = pt->NextPage;
        }
        SendCommerce(v.player, text);
    }

    void OpenDisplay(ViewCtx const& v)
    {
        uint8 const kind = v.d->kind;
        if (IsTrophyKind(kind)) SendTrophy(v);
        else if (IsMountKind(kind)) SendMount(v);
        else if (kind == ColMannequin) SendMannequin(v);
        else if (IsLibraryKind(kind)) SendLibrary(v);
        else if (kind == ColHabitat) SendHabitat(v);
        else if (IsPetKind(kind))
            SendCommerce(v.player, "note\tPets in a nearby Pet Habitat come here to sleep, play and eat.");
        else if (kind == ColStorage)
            SendStorage(v);
    }

    // The display a placed id is, made on first use; null when the player is not where it is.
    bool ViewOf(Player* player, uint64 placed, ViewCtx& v)
    {
        House* house = HouseOfPlaced(placed);
        Placed const* p = house ? FindPlaced(*house, placed) : nullptr;
        uint8 const kind = p ? CollectionKindOf(p->decorId) : 0;
        if (!kind || !s_spawned[player->GetInstanceId()].count(placed))
            return false;
        auto it = s_displays.find(placed);
        if (it == s_displays.end())
            it = s_displays.emplace(placed, NewDisplay(kind)).first;
        v = { player, placed, house, p, &it->second, house->account == player->GetSession()->GetAccountId() };
        return true;
    }

    // How tall a creature display stands at scale 1 (yd): its model's collision height and the display's own scale.
    // Bounding radius said little: Ragnaros' and Illidan's statues came out huge and others tiny.
    float ModelHeight(uint32 display, float templateScale)
    {
        CreatureDisplayInfoEntry const* info = sCreatureDisplayInfoStore.LookupEntry(display);
        CreatureModelDataEntry const* model = info ? sCreatureModelDataStore.LookupEntry(info->ModelId) : nullptr;
        float height = model ? model->CollisionHeight * (model->Scale > 0 ? model->Scale : 1.0f) * (info->scale > 0 ? info->scale : 1.0f) : 0;
        if (height < 0.1f) // no collision box: fall back to the bounding radius, roughly half a model's height
        {
            CreatureModelInfo const* mi = sObjectMgr->GetCreatureModelInfo(display);
            height = mi && mi->bounding_radius > 0.05f ? mi->bounding_radius * 2.0f : 2.0f;
        }
        return std::max(0.1f, height * templateScale);
    }

    // A display's pooled template, named and drawn as it shows (at load, and after every change).
    void DressDisplay(Display const& d)
    {
        if (!d.entry)
            return;
        if (IsTrophyKind(d.kind))
        {
            uint32 const creature = d.source == TrophyAchievement && d.style == StyleStatue ? TrophyCreature(d.id) : 0;
            auto [display, scale] = ModelOf(creature);
            float size = 0.01f; // a label's speck
            if (creature)
                size = std::clamp(d.size / ModelHeight(display, 1.0f), 0.002f, 5.0f); // the statue's own scale replaces its template's
            std::string const sub = !d.sub.empty() ? d.sub : d.date ? (d.source == TrophyItem ? "Displayed " : "Earned ") + DateText(d.date) : "";
            DressTemplate(d.entry, TrophyName(d), sub, creature ? display : 0, size);
        }
        else if (IsFigureKind(d.kind))
        {
            DressTemplate(d.entry, d.label, d.sub, 0, 1.0f); // the placeholder model, as SpawnMannequin's
        }
        else if (IsMountKind(d.kind))
        {
            auto [display, scale] = ModelOf(MountCreature(d.mount));
            DressTemplate(d.entry, LabelOf(d, MountName(d.mount)), d.sub, display, scale * std::clamp(d.size, 0.1f, 3.0f));
        }
    }

    // A changed display: a new pooled name (the client caches by entry) dressed as it now shows, then spawned again.
    void Redisplay(ViewCtx const& v, bool renamed = true)
    {
        Display& d = *v.d;
        Map* map = v.player->GetMap();
        if (renamed)
            if (uint32 const entry = NextDisplayEntry())
                d.entry = entry;
        DressDisplay(d);
        SaveDisplay(v.placed, d);
        if (renamed)
            PushTemplateName(map, d.entry);
        if (IsFigureKind(d.kind) || d.kind == ColMountMat || d.kind == ColTrophyRug || d.kind == ColHabitat) // a figure is its own creature; a rug shows or hides
        {
            Despawn(map, v.placed);
            Spawn(map, *v.p);
        }
        else
            SpawnDisplayExtras(map, *v.p);
    }

    std::string CheckLook(std::string const& lookHex, std::string const& bodyHex, uint8 race, uint8 sex)
    {
        std::array<uint8, CharacterRetailLook::PayloadSize> raw;
        CharacterRetailLook::Look look;
        if (!FromHex(lookHex, raw) || !CharacterRetailLook::ReadPayload(raw.data(), raw.size(), look) || look.race != race || look.sex != sex)
            return "That appearance could not be saved.";
        std::array<uint8, CharacterBodyShape::PayloadSize> rawBody;
        CharacterBodyShape::Values body{};
        if (!FromHex(bodyHex, rawBody) || !CharacterBodyShape::ReadPayload(rawBody.data(), rawBody.size(), body))
            return "Those body sliders could not be saved.";
        return "";
    }

    void SendMannequinCustomize(ViewCtx const& v)
    {
        ObjectGuid guid;
        if (auto it = s_spawned[v.player->GetInstanceId()].find(v.placed); it != s_spawned[v.player->GetInstanceId()].end())
            guid = it->second;
        std::ostringstream out;
        out << "customize\t" << GuidHex(guid) << '\t' << int(v.d->race) << '\t' << int(v.d->sex) << '\t' << v.d->bodyHex << '\t' << v.placed << '\t'
            << LabelOf(*v.d, "Mannequin") << '\n';
        for (uint32 i = 0; i < sChrRacesStore.GetNumRows(); ++i)
            if (ChrRacesEntry const* race = sChrRacesStore.LookupEntry(i); race && PlayableRace(uint8(i)))
                out << "R\t" << i << '\t' << race->name[0] << '\n';
        SendCommerce(v.player, out.str());
    }

    float Real(Fields const& f, size_t i, float lo, float hi, float def)
    {
        if (i >= f.size())
            return def;
        float const v = std::strtof(f[i].c_str(), nullptr);
        return std::isfinite(v) ? std::clamp(v, lo, hi) : def;
    }

    // The addon's commands: "col", verb, placed id, then the verb's fields.
    void HandleCollection(Player* player, Fields const& f)
    {
        std::string const& verb = f.size() > 1 ? f[1] : std::string();
        auto note = [&](std::string const& text) { if (!text.empty()) SendCommerce(player, "note\t" + text); };
        ViewCtx v;
        if (!ViewOf(player, std::strtoull(f.size() > 2 ? f[2].c_str() : "0", nullptr, 10), v))
            return note("You are no longer near that display.");
        Display& d = *v.d;
        uint32 const account = player->GetSession()->GetAccountId();
        if (verb == "open")
            return OpenDisplay(v);
        if (IsHouseholdKind(d.kind) && HandleHousehold(v, verb, f))
            return;
        if (verb == "libtab" && IsLibraryKind(d.kind))
            return SendLibraryTab(v, uint8(std::clamp<uint32>(Num(f, 3), 1, 4)));
        if (verb == "book" && IsLibraryKind(d.kind))
            return SendBook(v, Num(f, 3));
        if (!v.owner)
            return note("Only the owner can change this display.");
        if (verb == "trophyset" && IsTrophyKind(d.kind))
        {
            uint8 const source = uint8(Num(f, 3));
            uint32 const id = Num(f, 4);
            if (source == TrophyAchievement)
            {
                auto const earned = AccountAchievements(account, player);
                auto it = earned.find(id);
                if (it == earned.end())
                    return note("Your account has not earned that achievement.");
                d.date = it->second;
                d.style = DefaultStyle(id, player);
                AchievementEntry const* a = sAchievementStore.LookupEntry(id);
                MapEntry const* map = a && a->mapID >= 0 ? sMapStore.LookupEntry(uint32(a->mapID)) : nullptr;
                d.effect = map && map->IsRaid() ? 1 : 0; // a raid's trophy shines
            }
            else if (source == TrophyItem)
            {
                if (!sObjectMgr->GetItemTemplate(id) || !player->HasItemCount(id, 1, true))
                    return note("You need to own that item to show it.");
                d.date = uint32(GameTime::GetGameTime().count());
                d.style = StyleNameOnly; // shortcut: 3.3.5 draws an item's model only on a character; a mannequin shows gear
                d.effect = 0;
            }
            else if (source != TrophyNone)
                return;
            d.source = source;
            d.id = source == TrophyNone ? 0 : id;
            d.label.clear();
            d.sub.clear();
            if (!StyleAllowed(d.kind, d.style))
            {
                bool const statue = source == TrophyAchievement && TrophyCreature(id) && StyleAllowed(d.kind, StyleStatue);
                d.style = statue ? StyleStatue : StyleNameOnly;
                for (uint8 st = StyleAureate; !statue && st < StyleNameOnly; ++st)
                    if (StyleAllowed(d.kind, st) && source == TrophyAchievement)
                    {
                        d.style = st;
                        break;
                    }
            }
            Display const fresh = NewDisplay(d.kind); // the piece's own placement for its new trophy
            d.height = fresh.height; d.forward = fresh.forward; d.side = fresh.side; d.turn = fresh.turn; d.size = fresh.size;
            Redisplay(v);
            return SendTrophy(v);
        }
        if (verb == "trophystyle" && IsTrophyKind(d.kind))
        {
            if (!StyleAllowed(d.kind, uint8(Num(f, 3))))
                return note("That does not go on this piece.");
            d.style = uint8(std::min<uint32>(Num(f, 3), StyleNameOnly));
            d.effect = uint8(std::min<uint32>(Num(f, 4), std::size(TrophyEffects) - 1));
            d.size = Real(f, 5, 0.1f, 3.0f, d.size);
            d.height = Real(f, 6, -2.0f, 6.0f, d.height);
            d.forward = Real(f, 7, -3.0f, 3.0f, d.forward);
            d.turn = Real(f, 8, -360.0f, 360.0f, d.turn);
            d.side = Real(f, 9, -3.0f, 3.0f, d.side);
            Redisplay(v, false);
            return SendTrophy(v);
        }
        if (verb == "label")
        {
            d.label = Clean(f.size() > 3 ? f[3] : "", 40);
            d.sub = Clean(f.size() > 4 ? f[4] : "", 40);
            Redisplay(v);
            return IsFigureKind(d.kind) ? SendMannequin(v) : OpenDisplay(v);
        }
        if (verb == "mountset" && IsMountKind(d.kind))
        {
            uint32 const spell = Num(f, 3);
            if (spell && (!MountCreature(spell) || !AccountSpells(account, player).count(spell)))
                return note("Your account does not know that mount.");
            d.mount = spell;
            d.label.clear();
            Redisplay(v);
            return SendMount(v);
        }
        if (verb == "mountstyle" && IsMountKind(d.kind))
        {
            d.finish = uint8(std::min<uint32>(Num(f, 3), 2));
            d.size = Real(f, 4, 0.1f, 3.0f, d.size);
            d.height = Real(f, 5, -2.0f, 6.0f, d.height);
            d.forward = Real(f, 6, -6.0f, 6.0f, d.forward);
            d.turn = Real(f, 7, -360.0f, 360.0f, d.turn);
            d.side = Real(f, 8, -6.0f, 6.0f, d.side);
            if (f.size() > 9 && !f[9].empty())
                d.motion = uint8(std::min<uint32>(Num(f, 9), MotionWander));
            if (f.size() > 10 && !f[10].empty())
                d.radius = uint8(std::clamp<uint32>(Num(f, 10), 2, 10));
            Redisplay(v, false);
            return SendMount(v);
        }
        if (IsFigureKind(d.kind))
        {
            if (verb == "mqopen") // the outfit window, for a service NPC (the innkeeper, an auctioneer, a trainer...)
                return SendMannequin(v);
            if (verb == "mqpick")
                return SendMannequinPicks(v, uint8(Num(f, 3)));
            if (verb == "mqslot")
            {
                uint8 const slot = uint8(Num(f, 3));
                uint32 const entry = Num(f, 4);
                ItemTemplate const* t = sObjectMgr->GetItemTemplate(entry);
                bool const fits = t && (GearSlotOf(t) == slot || (slot == GearOffHand && t->InventoryType == INVTYPE_WEAPON));
                if (!fits)
                    return note("That does not go there.");
                if (!MayDress(player, account, entry, uint8(Num(f, 5))))
                    return note("You need to own that item, or have collected its look.");
                d.gear[slot] = entry;
                if (slot == GearMainHand && t->InventoryType == INVTYPE_2HWEAPON)
                    d.gear.erase(GearOffHand);
            }
            else if (verb == "mqclear")
                d.gear.erase(uint8(Num(f, 3)));
            else if (verb == "mqstrip")
                d.gear.clear();
            else if (verb == "mqstyle")
            {
                d.type = uint8(std::min<uint32>(Num(f, 3), MannequinTypes - 1));
                d.pose = uint8(std::min<uint32>(Num(f, 4), PoseCount - 1));
            }
            else if (verb == "mqsave")
            {
                std::string const name = Clean(f.size() > 3 ? f[3] : "", 32);
                if (name.empty())
                    return note("Give the outfit a name.");
                s_outfits[{ account, name }] = GearText(d.gear);
                CharacterDatabase.Execute("REPLACE INTO housing_outfit (account_id, name, gear) VALUES ({}, '{}', '{}')", account, Sql(name),
                    GearText(d.gear));
                note("Outfit saved: " + name);
                return SendMannequin(v);
            }
            else if (verb == "mqload" || verb == "mqdel")
            {
                std::string const name = f.size() > 3 ? f[3] : "";
                auto it = s_outfits.find({ account, name });
                if (it == s_outfits.end())
                    return note("That outfit is gone.");
                if (verb == "mqdel")
                {
                    s_outfits.erase(it);
                    CharacterDatabase.Execute("DELETE FROM housing_outfit WHERE account_id = {} AND name = '{}'", account, Sql(name));
                    return SendMannequin(v);
                }
                d.gear = ParseGear(it->second);
            }
            else if (verb == "mqappearance")
                return SendMannequinCustomize(v);
            else if (verb == "mqrace")
            {
                if (!PlayableRace(uint8(Num(f, 3))))
                    return note("That race is not available.");
                d.race = uint8(Num(f, 3));
                d.sex = Num(f, 4) ? 1 : 0;
                d.lookHex = DefaultLookHex(d.race, d.sex);
                d.bodyHex.clear();
                Redisplay(v);
                return SendMannequinCustomize(v);
            }
            else if (verb == "mqlook" && f.size() >= 5)
            {
                if (std::string const error = CheckLook(f[3], f[4], d.race, d.sex); !error.empty())
                    return note(error);
                d.lookHex = f[3];
                d.bodyHex = f[4];
                SaveDisplay(v.placed, d);
                if (auto it = s_spawned[player->GetInstanceId()].find(v.placed); it != s_spawned[player->GetInstanceId()].end())
                {
                    ObjectGuid const guid = it->second;
                    player->GetMap()->DoForAllPlayers([&](Player* other) { SendLookHex(other, guid, d.lookHex, d.bodyHex); });
                }
                return FigureChanged(v);
            }
            else if (verb == "mqlookreset")
            {
                Despawn(player->GetMap(), v.placed); // the saved look comes back with the new one
                Spawn(player->GetMap(), *v.p);
                return;
            }
            else
                return;
            Redisplay(v, false);
            return SendMannequin(v);
        }
        if (verb == "habset" && d.kind == ColHabitat)
        {
            d.radius = uint8(std::clamp<uint32>(Num(f, 3), 2, 10));
            std::set<uint32> const known = AccountSpells(account, player);
            d.pets.clear();
            std::istringstream in(f.size() > 4 ? f[4] : "");
            for (std::string part; std::getline(in, part, ',') && d.pets.size() < HabitatPets(v.p->decorId);)
                if (uint32 const spell = uint32(std::strtoul(part.c_str(), nullptr, 10)); CompanionCreature(spell) && known.count(spell)
                    && std::find(d.pets.begin(), d.pets.end(), spell) == d.pets.end())
                    d.pets.push_back(spell);
            if (f.size() > 5 && !f[5].empty())
                d.flags = uint8((d.flags & ~FlagHideRug) | (Num(f, 5) ? FlagHideRug : 0));
            Redisplay(v, false); // the rug shows or hides, the pets come back
            return SendHabitat(v);
        }
    }

    // A display's object or creature was clicked. Services answer with gossip, so they work without the addon.
    bool OpenCollection(Player* player, WorldObject* object)
    {
        if (!s_config.enabled || !s_loaded)
            return false;
        uint64 placed = 0;
        if (auto it = s_extraPlaced.find(object->GetGUID()); it != s_extraPlaced.end())
            placed = it->second;
        else
            placed = PlacedOf(object);
        ViewCtx v;
        if (!placed || !ViewOf(player, placed, v))
            return false;
        if (!v.owner && !MayEnter(player, *v.house))
            return false;
        if (IsHouseholdKind(v.d->kind))
            return OpenHousehold(v, object);
        if (!s_hasUi.count(player->GetSession()->GetAccountId()))
            return false;
        CloseGossipMenuFor(player);
        OpenDisplay(v);
        return true;
    }

    bool npc_esteria_housing_display::OnGossipHello(Player* player, Creature* creature)
    {
        std::lock_guard<std::recursive_mutex> guard(s_lock);
        ClearGossipMenuFor(player);
        if (OpenCollection(player, creature))
            return true; // the window, a service's own frame, or a gossip menu it sent
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This needs the Esteria housing client.", 0, 0);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
        return true;
    }

    class go_esteria_housing_collection : public GameObjectScript
    {
    public:
        go_esteria_housing_collection() : GameObjectScript("go_esteria_housing_collection") { }
        bool OnGossipHello(Player* player, GameObject* go) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            if (OpenCollection(player, go))
                return true;
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This needs the Esteria housing client.", 0, 0);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, go->GetGUID());
            return true;
        }
        bool OnGossipSelect(Player* player, GameObject* go, uint32 sender, uint32 action) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            HouseholdSelect(player, go, sender, action, nullptr);
            return true;
        }
        bool OnGossipSelectCode(Player* player, GameObject* go, uint32 sender, uint32 action, char const* code) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            HouseholdSelect(player, go, sender, action, code);
            return true;
        }
    };

    // Books read anywhere in the world: a readable object used (CMSG_GAMEOBJ_USE) or a readable item read (CMSG_READ_ITEM).
    class EsteriaHousingBooks : public ServerScript
    {
    public:
        EsteriaHousingBooks() : ServerScript("EsteriaHousingBooks", { SERVERHOOK_CAN_PACKET_RECEIVE }) { }

        bool CanPacketReceive(WorldSession* session, WorldPacket const& packet) override
        {
            uint16 const op = packet.GetOpcode();
            if (op != CMSG_GAMEOBJ_USE && op != CMSG_READ_ITEM)
                return true;
            Player* player = session ? session->GetPlayer() : nullptr;
            if (!player || !player->IsInWorld() || packet.size() < (op == CMSG_GAMEOBJ_USE ? 8u : 2u))
                return true;
            WorldPacket copy(packet);
            uint32 page = 0;
            if (op == CMSG_GAMEOBJ_USE)
            {
                ObjectGuid guid;
                copy >> guid;
                if (GameObject* go = player->GetMap()->GetGameObject(guid); go && go->IsWithinDistInMap(player, 15.0f))
                {
                    GameObjectTemplate const* t = go->GetGOInfo();
                    page = t->type == GAMEOBJECT_TYPE_TEXT ? t->text.pageID : t->type == GAMEOBJECT_TYPE_GOOBER ? t->goober.pageId : 0;
                }
            }
            else
            {
                uint8 bag = 0, slot = 0;
                copy >> bag >> slot;
                if (Item* item = player->GetItemByPos(bag, slot))
                    page = item->GetTemplate()->PageText;
            }
            if (page)
            {
                std::lock_guard<std::recursive_mutex> guard(s_lock);
                if (s_config.enabled && s_loaded)
                    BookRead(player, page);
            }
            return true;
        }
    };

    void ForgetDisplayUnit(ObjectGuid guid) { s_extraPlaced.erase(guid); }
