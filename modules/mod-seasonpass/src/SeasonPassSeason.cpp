/*
 * mod-seasonpass v4 — Saison-Erweiterung (zweisprachig DE/EN):
 *   Wochenziele (40, mit Traumtausch-Reroll), Runen (12 Buffs + 12 Fähigkeiten),
 *   Saison-Erfolge (20), Entdeckungen (18), Zonen-Events, Kopfgeld des Tages,
 *   Dungeon der Woche, Weltboss-Rotation mit Weltbuff, Teleporter-NPC.
 */

#include "SeasonPass.h"

#include "ScriptMgr.h"
#include "Player.h"
#include "Creature.h"
#include "Chat.h"
#include "Config.h"
#include "DatabaseEnv.h"
#include "ScriptedGossip.h"
#include "GameTime.h"
#include "MapMgr.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "ObjectAccessor.h"
#include "Random.h"
#include "SpellAuras.h"
#include "World.h"
#include "WorldSession.h"
#include "WorldSessionMgr.h"
#include "TemporarySummon.h"

#include <algorithm>
#include <array>
#include <functional>
#include <limits>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <sstream>

using SeasonPass::T;

namespace
{
    struct WeeklyDef
    {
        uint32 id = 0;
        uint8 type = 0;
        uint32 goal = 1;
        uint32 points = 100;
        std::string name;
        std::string nameEn;
        uint8 eventType = 255;
        uint32 mapId = 0;
        uint32 mapDifficultyMin = 0;
        uint32 mapDifficultyMax = 0;
        uint32 difficultyMin = 0;
        uint32 difficultyMax = 0;
        uint32 tierMin = 0;
        uint32 tierMax = 0;
        uint32 floorMin = 0;
        uint32 themeId = 0;
        uint32 bossEntry = 0;
        uint8 chestTier = 0;
        bool enabled = true;
    };
    struct WeeklySlot { uint32 defId = 0; uint32 progress = 0; bool done = false; };
    struct RuneDef    { uint32 id = 0; uint32 classmask = 0; uint8 kind = 0; uint32 spell = 0; uint32 cost = 0; std::string name; std::string nameEn; };
    struct BossDef    { uint32 entry = 0; uint32 map = 0; float x = 0, y = 0, z = 0, o = 0; std::string name; std::string zone; std::string zoneEn; };
    struct ZoneDef    { uint32 zone = 0; std::string name; std::string nameEn; };
    struct BountyDef  { uint32 entry = 0; uint32 points = 150; std::string name; std::string nameEn; std::string zone; std::string zoneEn; };
    struct DungeonDef { uint32 map = 0; uint32 points = 300; std::string name; std::string nameEn; };
    struct DiscDef    { uint32 id = 0; uint32 zone = 0; uint32 points = 25; std::string name; std::string nameEn; };
    struct AchDef     { uint32 id = 0; uint8 kind = 0; uint32 goal = 1; uint32 points = 100; std::string name; std::string nameEn; };
    struct AchState   { uint32 progress = 0; bool done = false; };
    struct TeleDef    { uint32 id = 0; std::string name; std::string nameEn; uint32 map = 0; float x = 0, y = 0, z = 0, o = 0; };

    struct EventCreditKey
    {
        ObjectGuid::LowType guid = 0;
        uint32 season = 0;
        uint8 eventType = 255;
        uint64 sourceId = 0;
        uint64 sourceStartedAt = 0;
        uint64 detailId = 0;

        bool operator==(EventCreditKey const& other) const
        {
            return guid == other.guid && season == other.season && eventType == other.eventType
                && sourceId == other.sourceId && sourceStartedAt == other.sourceStartedAt
                && detailId == other.detailId;
        }
    };

    struct EventCreditKeyHash
    {
        size_t operator()(EventCreditKey const& key) const noexcept
        {
            size_t hash = std::hash<uint32>{}(key.guid);
            hash ^= std::hash<uint32>{}(key.season) + 0x9e3779b9u + (hash << 6) + (hash >> 2);
            hash ^= std::hash<uint8>{}(key.eventType) + 0x9e3779b9u + (hash << 6) + (hash >> 2);
            hash ^= std::hash<uint64>{}(key.sourceId) + 0x9e3779b9u + (hash << 6) + (hash >> 2);
            hash ^= std::hash<uint64>{}(key.sourceStartedAt) + 0x9e3779b9u + (hash << 6) + (hash >> 2);
            hash ^= std::hash<uint64>{}(key.detailId) + 0x9e3779b9u + (hash << 6) + (hash >> 2);
            return hash;
        }
    };

    constexpr uint32 WEEKLY_SLOTS = 3;
    constexpr uint32 REROLL_SLOT  = 8; // Traumtausch-Marker
    constexpr uint32 DUNGEON_SLOT = 9;

    struct SeasonPlayerData
    {
        std::array<WeeklySlot, WEEKLY_SLOTS> weekly;
        bool   weeklyLoaded = false;
        bool   dungeonDone  = false;
        bool   rerollUsed   = false;
        std::vector<uint32> runes;
        bool   runesLoaded = false;
        std::unordered_map<uint32, AchState> ach;
        bool   achLoaded = false;
        std::set<uint32> discovered;
        bool   discLoaded = false;
    };

    bool   g_weeklyEnable    = true;
    bool   g_dungeonObjectivesEnable = true;
    bool   g_rerollEnable    = true;
    bool   g_runesEnable     = true;
    uint32 g_runeBaseSlots   = 3;
    bool   g_bossEnable      = true;
    uint32 g_bossIntervalH   = 6;
    uint32 g_bossDespawnMin  = 120;
    uint32 g_bossBonusPoints = 250;
    uint32 g_bossWorldBuff   = 22888;
    bool   g_zonesEnable     = true;
    uint32 g_zoneHours       = 3;
    bool   g_bountyEnable    = true;
    bool   g_dungeonEnable   = true;
    bool   g_discEnable      = true;
    bool   g_achEnable       = true;

    std::vector<WeeklyDef> g_weeklyDefs;
    std::unordered_map<uint32, WeeklyDef const*> g_weeklyById;
    std::vector<RuneDef>    g_runeDefs;
    std::vector<BossDef>    g_bossDefs;
    std::vector<ZoneDef>    g_zoneDefs;
    std::vector<BountyDef>  g_bountyDefs;
    std::vector<DungeonDef> g_dungeonDefs;
    std::vector<DiscDef>    g_discDefs;
    std::vector<AchDef>     g_achDefs;
    std::vector<TeleDef>    g_teleDefs;

    std::unordered_map<ObjectGuid::LowType, SeasonPlayerData> g_season;
    std::unordered_set<EventCreditKey, EventCreditKeyHash> g_eventCredits;
    std::array<uint32, WEEKLY_SLOTS> g_weeklyRotation{};
    uint32 g_rotationSeason = 0;
    uint32 g_rotationWeek = std::numeric_limits<uint32>::max();

    uint64 g_bossTimerMs  = 0;
    uint32 g_bossRotation = 0;
    uint32 g_activeBoss   = 0;
    std::string g_activeBossName;

    uint32 NowSecs()    { return static_cast<uint32>(GameTime::GetGameTime().count()); }
    uint32 CurrentDay() { return NowSecs() / 86400; }
    uint32 CurrentWeek(){ return NowSecs() / (86400 * 7); }

    void LoadWeeklyRotation(uint32 season, uint32 week)
    {
        g_weeklyRotation.fill(0);
        std::array<bool, WEEKLY_SLOTS> assigned{};
        std::unordered_set<uint32> objectives;

        if (QueryResult result = WorldDatabase.Query(
                "SELECT `week`, `slot`, `objective` FROM `seasonpass_weekly_rotation` "
                "WHERE `season` = {} AND (`week` = 0 OR `week` = {}) ORDER BY `week`, `slot`", season, week))
        {
            do
            {
                Field* fields = result->Fetch();
                uint32 rowWeek = fields[0].Get<uint32>();
                uint32 slot = fields[1].Get<uint8>();
                uint32 objectiveId = fields[2].Get<uint32>();
                if (slot >= WEEKLY_SLOTS || assigned[slot] || (rowWeek != week && rowWeek != 0))
                    continue;
                auto it = g_weeklyById.find(objectiveId);
                if (it == g_weeklyById.end() || !it->second->enabled || it->second->goal == 0
                    || objectives.contains(objectiveId))
                {
                    LOG_WARN("module", "[SeasonPass] Ignoring invalid weekly rotation season {} week {} slot {} objective {}",
                        season, rowWeek, slot, objectiveId);
                    continue;
                }
                g_weeklyRotation[slot] = objectiveId;
                assigned[slot] = true;
                objectives.insert(objectiveId);
            } while (result->NextRow());
        }

        g_rotationSeason = season;
        g_rotationWeek = week;
    }

    void EnsureWeeklyRotation()
    {
        uint32 season = SeasonPass::GetSeason();
        uint32 week = CurrentWeek();
        if (g_rotationSeason != season || g_rotationWeek != week)
            LoadWeeklyRotation(season, week);
    }

    char const* NM(Player* p, std::string const& de, std::string const& en)
    {
        return (SeasonPass::GetLang(p) == 1 && !en.empty()) ? en.c_str() : de.c_str();
    }

    ZoneDef const* ActiveZone()
    {
        if (!g_zonesEnable || g_zoneDefs.empty())
            return nullptr;
        return &g_zoneDefs[(NowSecs() / (3600 * std::max<uint32>(1, g_zoneHours))) % g_zoneDefs.size()];
    }

    BountyDef const* ActiveBounty()
    {
        if (!g_bountyEnable || g_bountyDefs.empty())
            return nullptr;
        return &g_bountyDefs[CurrentDay() % g_bountyDefs.size()];
    }

    DungeonDef const* ActiveDungeon()
    {
        if (!g_dungeonEnable || g_dungeonDefs.empty())
            return nullptr;
        return &g_dungeonDefs[CurrentWeek() % g_dungeonDefs.size()];
    }

    void LoadSeasonTables()
    {
        auto loadAll = [](char const* sql, auto fill)
        {
            if (QueryResult result = WorldDatabase.Query(sql))
                do
                    fill(result->Fetch());
                while (result->NextRow());
        };

        g_weeklyDefs.clear(); g_weeklyById.clear();
        loadAll("SELECT id, type, goal, points, name, name_en, event_type, map_id, "
                "map_difficulty_min, map_difficulty_max, difficulty_min, difficulty_max, "
                "tier_min, tier_max, floor_min, theme_id, boss_entry, chest_tier, enabled "
                "FROM seasonpass_weekly ORDER BY id", [](Field* f)
        {
            WeeklyDef d;
            d.id = f[0].Get<uint32>(); d.type = f[1].Get<uint8>(); d.goal = f[2].Get<uint32>();
            d.points = f[3].Get<uint32>(); d.name = f[4].Get<std::string>(); d.nameEn = f[5].Get<std::string>();
            d.eventType = f[6].Get<uint8>(); d.mapId = f[7].Get<uint32>();
            d.mapDifficultyMin = f[8].Get<uint32>(); d.mapDifficultyMax = f[9].Get<uint32>();
            d.difficultyMin = f[10].Get<uint32>(); d.difficultyMax = f[11].Get<uint32>();
            d.tierMin = f[12].Get<uint32>(); d.tierMax = f[13].Get<uint32>();
            d.floorMin = f[14].Get<uint32>(); d.themeId = f[15].Get<uint32>();
            d.bossEntry = f[16].Get<uint32>(); d.chestTier = f[17].Get<uint8>(); d.enabled = f[18].Get<uint8>() != 0;
            if (!d.goal || (d.eventType != 255 && d.eventType > 13) || d.chestTier > 3
                || (d.mapDifficultyMin && d.mapDifficultyMax && d.mapDifficultyMin > d.mapDifficultyMax)
                || (d.difficultyMin && d.difficultyMax && d.difficultyMin > d.difficultyMax)
                || (d.tierMin && d.tierMax && d.tierMin > d.tierMax))
            {
                LOG_WARN("module", "[SeasonPass] Ignoring invalid weekly objective {}", d.id);
                d.enabled = false;
            }
            g_weeklyDefs.push_back(std::move(d));
        });
        for (WeeklyDef const& d : g_weeklyDefs)
            if (d.enabled)
                g_weeklyById[d.id] = &d;
        LoadWeeklyRotation(SeasonPass::GetSeason(), CurrentWeek());

        g_runeDefs.clear();
        loadAll("SELECT id, classmask, kind, spell, cost, name, name_en FROM seasonpass_runes ORDER BY id", [](Field* f)
        {
            RuneDef d;
            d.id = f[0].Get<uint32>(); d.classmask = f[1].Get<uint32>(); d.kind = f[2].Get<uint8>();
            d.spell = f[3].Get<uint32>(); d.cost = f[4].Get<uint32>();
            d.name = f[5].Get<std::string>(); d.nameEn = f[6].Get<std::string>();
            g_runeDefs.push_back(std::move(d));
        });

        g_bossDefs.clear();
        loadAll("SELECT entry, map, x, y, z, o, name, zone, zone_en FROM seasonpass_worldboss ORDER BY id", [](Field* f)
        {
            BossDef d;
            d.entry = f[0].Get<uint32>(); d.map = f[1].Get<uint32>();
            d.x = f[2].Get<float>(); d.y = f[3].Get<float>(); d.z = f[4].Get<float>(); d.o = f[5].Get<float>();
            d.name = f[6].Get<std::string>(); d.zone = f[7].Get<std::string>(); d.zoneEn = f[8].Get<std::string>();
            g_bossDefs.push_back(std::move(d));
        });

        g_zoneDefs.clear();
        loadAll("SELECT zone, name, name_en FROM seasonpass_zones ORDER BY id", [](Field* f)
        {
            g_zoneDefs.push_back({ f[0].Get<uint32>(), f[1].Get<std::string>(), f[2].Get<std::string>() });
        });

        g_bountyDefs.clear();
        loadAll("SELECT entry, points, name, name_en, zone, zone_en FROM seasonpass_bounty ORDER BY id", [](Field* f)
        {
            g_bountyDefs.push_back({ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<std::string>(),
                                     f[3].Get<std::string>(), f[4].Get<std::string>(), f[5].Get<std::string>() });
        });

        g_dungeonDefs.clear();
        loadAll("SELECT map, points, name, name_en FROM seasonpass_dungeons ORDER BY id", [](Field* f)
        {
            g_dungeonDefs.push_back({ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<std::string>(), f[3].Get<std::string>() });
        });

        g_discDefs.clear();
        loadAll("SELECT id, zone, points, name, name_en FROM seasonpass_discoveries ORDER BY id", [](Field* f)
        {
            g_discDefs.push_back({ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<uint32>(),
                                   f[3].Get<std::string>(), f[4].Get<std::string>() });
        });

        g_achDefs.clear();
        loadAll("SELECT id, kind, goal, points, name, name_en FROM seasonpass_achievements ORDER BY id", [](Field* f)
        {
            AchDef d;
            d.id = f[0].Get<uint32>(); d.kind = f[1].Get<uint8>(); d.goal = f[2].Get<uint32>();
            d.points = f[3].Get<uint32>(); d.name = f[4].Get<std::string>(); d.nameEn = f[5].Get<std::string>();
            g_achDefs.push_back(std::move(d));
        });

        g_teleDefs.clear();
        loadAll("SELECT id, name, name_en, map, x, y, z, o FROM seasonpass_teleports ORDER BY id", [](Field* f)
        {
            TeleDef d;
            d.id = f[0].Get<uint32>(); d.name = f[1].Get<std::string>(); d.nameEn = f[2].Get<std::string>();
            d.map = f[3].Get<uint32>(); d.x = f[4].Get<float>(); d.y = f[5].Get<float>();
            d.z = f[6].Get<float>(); d.o = f[7].Get<float>();
            g_teleDefs.push_back(std::move(d));
        });

        LOG_INFO("module", "[SeasonPass] Saison-Content: {} Wochenziele, {} Runen, {} Weltbosse, {} Zonen, {} Kopfgelder, {} Dungeons, {} Orte, {} Erfolge.",
            g_weeklyDefs.size(), g_runeDefs.size(), g_bossDefs.size(), g_zoneDefs.size(),
            g_bountyDefs.size(), g_dungeonDefs.size(), g_discDefs.size(), g_achDefs.size());
    }

    // --------------------------- Wochenziele ---------------------------
    uint32 PickWeeklyDef(uint32 seed, std::array<WeeklySlot, WEEKLY_SLOTS> const& taken, uint32 skipId = 0)
    {
        if (g_weeklyDefs.empty())
            return 0;
        uint32 idx = seed % g_weeklyDefs.size();
        for (uint32 tries = 0; tries < g_weeklyDefs.size(); ++tries)
        {
            WeeklyDef const& candidateDef = g_weeklyDefs[(idx + tries) % g_weeklyDefs.size()];
            if (!candidateDef.enabled)
                continue;
            uint32 candidate = candidateDef.id;
            bool used = (candidate == skipId);
            for (uint32 s = 0; s < WEEKLY_SLOTS; ++s)
                if (taken[s].defId == candidate)
                    used = true;
            if (!used)
                return candidate;
        }
        return 0;
    }

    void SaveWeeklySlot(Player* player, uint32 week, uint32 slot, WeeklySlot const& w)
    {
        CharacterDatabase.Execute(
            "REPLACE INTO character_seasonpass_weekly (guid, week, slot, challenge, progress, done) "
            "VALUES ({}, {}, {}, {}, {}, {})",
            player->GetGUID().GetCounter(), week, slot, w.defId, w.progress, w.done ? 1 : 0);
    }

    void EnsureWeekly(Player* player)
    {
        EnsureWeeklyRotation();
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        if (sd.weeklyLoaded || !g_weeklyEnable)
            return;

        uint32 week = CurrentWeek();
        CharacterDatabase.Execute(
            "DELETE FROM character_seasonpass_weekly WHERE guid = {} AND week < {}",
            player->GetGUID().GetCounter(), week);

        if (QueryResult result = CharacterDatabase.Query(
                "SELECT slot, challenge, progress, done FROM character_seasonpass_weekly WHERE guid = {} AND week = {}",
                player->GetGUID().GetCounter(), week))
        {
            do
            {
                Field* f = result->Fetch();
                uint32 slot = f[0].Get<uint8>();
                if (slot == DUNGEON_SLOT)
                {
                    sd.dungeonDone = f[3].Get<uint8>() != 0;
                    continue;
                }
                if (slot == REROLL_SLOT)
                {
                    sd.rerollUsed = true;
                    continue;
                }
                if (slot >= WEEKLY_SLOTS)
                    continue;
                sd.weekly[slot].defId    = f[1].Get<uint32>();
                sd.weekly[slot].progress = f[2].Get<uint32>();
                sd.weekly[slot].done     = f[3].Get<uint8>() != 0;
            } while (result->NextRow());
        }

        for (uint32 slot = 0; slot < WEEKLY_SLOTS; ++slot)
        {
            WeeklySlot& weeklySlot = sd.weekly[slot];
            if (g_weeklyById.find(weeklySlot.defId) == g_weeklyById.end())
            {
                weeklySlot = {};
                uint32 rotationId = g_weeklyRotation[slot];
                bool rotationAvailable = rotationId && std::none_of(
                    sd.weekly.begin(), sd.weekly.end(), [rotationId](WeeklySlot const& existing)
                    {
                        return existing.defId == rotationId;
                    });
                weeklySlot.defId = rotationAvailable ? rotationId : PickWeeklyDef(
                    week * 7 + slot * 13, sd.weekly);
                if (weeklySlot.defId)
                    SaveWeeklySlot(player, week, slot, weeklySlot);
            }
        }
        sd.weeklyLoaded = true;
    }

    // Synchronous claim lookup/insert keeps restart deduplication exact; move to an async claim
    // queue only if event volume proves this boundary too expensive.
    EventCreditKey MakeEventCreditKey(Player* player, Progression::DungeonEvent const& event)
    {
        return { player->GetGUID().GetCounter(), SeasonPass::GetSeason(),
            static_cast<uint8>(event.type), event.sourceId, event.sourceStartedAt, event.detailId };
    }

    bool ClaimEvent(Player* player, Progression::DungeonEvent const& event)
    {
        EventCreditKey key = MakeEventCreditKey(player, event);
        if (g_eventCredits.contains(key))
            return false;

        if (CharacterDatabase.Query(
                "SELECT 1 FROM `character_seasonpass_event_credit` "
                "WHERE `guid` = {} AND `season` = {} AND `event_type` = {} AND `source_id` = {} "
                "AND `source_started_at` = {} AND `detail_id` = {}",
                key.guid, key.season, key.eventType, key.sourceId, key.sourceStartedAt, key.detailId))
        {
            g_eventCredits.insert(key);
            return false;
        }

        CharacterDatabase.Execute(
            "INSERT IGNORE INTO `character_seasonpass_event_credit` "
            "(`guid`, `season`, `event_type`, `source_id`, `source_started_at`, `detail_id`, `claimed_at`) "
            "VALUES ({}, {}, {}, {}, {}, {}, {})",
            key.guid, key.season, key.eventType, key.sourceId, key.sourceStartedAt, key.detailId, NowSecs());

        if (!CharacterDatabase.Query(
                "SELECT 1 FROM `character_seasonpass_event_credit` "
                "WHERE `guid` = {} AND `season` = {} AND `event_type` = {} AND `source_id` = {} "
                "AND `source_started_at` = {} AND `detail_id` = {}",
                key.guid, key.season, key.eventType, key.sourceId, key.sourceStartedAt, key.detailId))
        {
            LOG_WARN("module", "[SeasonPass] Event claim failed closed for player {}", key.guid);
            return false;
        }

        g_eventCredits.insert(key);
        return true;
    }

    void PruneEventCredits(Player* player)
    {
        CharacterDatabase.Execute(
            "DELETE FROM `character_seasonpass_event_credit` WHERE `guid` = {} AND `season` < {}",
            player->GetGUID().GetCounter(), SeasonPass::GetSeason());
    }

    bool Matches(WeeklyDef const& def, Progression::DungeonEvent const& event)
    {
        if (!def.enabled || def.eventType == 255
            || def.eventType != static_cast<uint8>(event.type))
            return false;
        if (def.mapId && def.mapId != event.mapId)
            return false;
        if (def.mapDifficultyMin && event.mapDifficulty < def.mapDifficultyMin)
            return false;
        if (def.mapDifficultyMax && event.mapDifficulty > def.mapDifficultyMax)
            return false;
        if (def.difficultyMin && event.difficultyId < def.difficultyMin)
            return false;
        if (def.difficultyMax && event.difficultyId > def.difficultyMax)
            return false;
        if (def.tierMin && event.tier < def.tierMin)
            return false;
        if (def.tierMax && event.tier > def.tierMax)
            return false;
        if (def.floorMin && event.floor < def.floorMin)
            return false;
        if (def.themeId && def.themeId != event.themeId)
            return false;
        if (def.bossEntry && def.bossEntry != event.bossEntry)
            return false;
        return true;
    }

    // --------------------------- Erfolge ---------------------------
    void EnsureAch(Player* player)
    {
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        if (sd.achLoaded || !g_achEnable)
            return;
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT ach, progress, done FROM character_seasonpass_ach WHERE guid = {}",
                player->GetGUID().GetCounter()))
        {
            do
            {
                Field* f = result->Fetch();
                sd.ach[f[0].Get<uint32>()] = { f[1].Get<uint32>(), f[2].Get<uint8>() != 0 };
            } while (result->NextRow());
        }
        sd.achLoaded = true;
    }

    void SaveAch(Player* player, uint32 achId, AchState const& s)
    {
        CharacterDatabase.Execute(
            "REPLACE INTO character_seasonpass_ach (guid, ach, progress, done) VALUES ({}, {}, {}, {})",
            player->GetGUID().GetCounter(), achId, s.progress, s.done ? 1 : 0);
    }

    void EnsureDiscoveries(Player* player)
    {
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        if (sd.discLoaded || !g_discEnable)
            return;
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT zone FROM character_seasonpass_discoveries WHERE guid = {}",
                player->GetGUID().GetCounter()))
        {
            do
                sd.discovered.insert((*result)[0].Get<uint32>());
            while (result->NextRow());
        }
        sd.discLoaded = true;
    }

    // --------------------------- Runen ---------------------------
    uint32 MaxRuneSlots(Player* player)
    {
        uint32 slots = g_runeBaseSlots;
        uint32 tier = SeasonPass::GetTier(player);
        if (tier >= 25) ++slots;
        if (tier >= 50) ++slots;
        if (tier >= 75) ++slots;
        return slots;
    }

    RuneDef const* FindRune(uint32 id)
    {
        for (RuneDef const& r : g_runeDefs)
            if (r.id == id)
                return &r;
        return nullptr;
    }

    void ApplyRunes(Player* player)
    {
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        for (uint32 runeId : sd.runes)
            if (RuneDef const* r = FindRune(runeId))
            {
                if (r->kind == 0)
                {
                    if (!player->HasAura(r->spell))
                        if (Aura* a = player->AddAura(r->spell, player))
                        {
                            a->SetMaxDuration(-1); // Dauerbuff: läuft nie ab
                            a->SetDuration(-1);
                        }
                }
                else if (!player->HasSpell(r->spell))
                    player->learnSpell(r->spell);
            }
    }

    void LoadRunes(Player* player)
    {
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        if (sd.runesLoaded || !g_runesEnable)
            return;
        sd.runes.clear();
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT rune FROM character_seasonpass_runes WHERE guid = {}",
                player->GetGUID().GetCounter()))
        {
            do
                sd.runes.push_back((*result)[0].Get<uint32>());
            while (result->NextRow());
        }
        sd.runesLoaded = true;
        ApplyRunes(player);
    }

    bool HasRune(Player* player, uint32 runeId)
    {
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        return std::find(sd.runes.begin(), sd.runes.end(), runeId) != sd.runes.end();
    }
}

// ---------------------------------------------------------------------------
//  Oeffentliche Schnittstelle (SeasonPass.h)
// ---------------------------------------------------------------------------
namespace SeasonPass
{
    void AdvanceWeeklySlot(Player* player, uint32 slotIndex, uint32 value, char const* reason);

    uint32 ActiveEventZone()
    {
        ZoneDef const* z = ActiveZone();
        return z ? z->zone : 0;
    }

    std::string ActiveEventZoneName(Player* player)
    {
        ZoneDef const* z = ActiveZone();
        if (!z)
            return "";
        return (player && GetLang(player) == 1) ? z->nameEn : z->name;
    }

    void AchProgress(Player* player, AchKind kind, uint32 value)
    {
        if (!g_achEnable || !IsTracked(player))
            return;

        EnsureAch(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        bool highWater = (kind == ACH_TIER || kind == ACH_PRESTIGE || kind == ACH_STREAK);

        for (AchDef const& def : g_achDefs)
        {
            if (def.kind != kind)
                continue;
            AchState& s = sd.ach[def.id];
            if (s.done)
                continue;

            uint32 old = s.progress;
            s.progress = highWater ? std::max(s.progress, value)
                                   : std::min(s.progress + value, def.goal);
            if (s.progress >= def.goal)
            {
                s.done = true;
                SaveAch(player, def.id, s);
                std::ostringstream msg;
                msg << "|cffFFD700[Dream Path]|r |cff00CCFF" << player->GetName()
                    << "|r earned the season achievement |cffFF8800"
                    << (def.nameEn.empty() ? def.name : def.nameEn) << "|r (+"
                    << def.points << " points)";
                ChatHandler(nullptr).SendGlobalSysMessage(msg.str().c_str());
                AddPoints(player, def.points, T(player, "Saison-Erfolg", "Season achievement"));
            }
            else if (s.progress != old)
                SaveAch(player, def.id, s);
        }
    }

    void WeeklyProgress(Player* player, WeeklyType type, uint32 value)
    {
        if (!g_weeklyEnable || !value || !IsTracked(player))
            return;

        EnsureWeekly(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        for (uint32 slot = 0; slot < WEEKLY_SLOTS; ++slot)
        {
            WeeklySlot& w = sd.weekly[slot];
            if (!w.defId || w.done)
                continue;
            auto it = g_weeklyById.find(w.defId);
            if (it == g_weeklyById.end() || it->second->eventType != 255 || it->second->type != type)
                continue;
            AdvanceWeeklySlot(player, slot, value, T(player, "Wochenziel", "Weekly goal"));
        }
    }

    bool TeleportTo(Player* player, uint32 destId)
    {
        if (!player || !player->GetSession())
            return false;
        if (player->IsInCombat())
        {
            ChatHandler(player->GetSession()).SendSysMessage(
                T(player, "|cffFF0000[Traumpfad]|r Nicht während des Kampfes!",
                          "|cffFF0000[Dream Path]|r Not while in combat!"));
            return false;
        }

        if (destId == 999)
        {
            if (!g_activeBoss)
            {
                ChatHandler(player->GetSession()).SendSysMessage(
                    T(player, "|cffFFD700[Traumpfad]|r Derzeit ist kein Saison-Weltboss aktiv.",
                              "|cffFFD700[Dream Path]|r No season world boss is active right now."));
                return false;
            }
            for (BossDef const& b : g_bossDefs)
                if (b.entry == g_activeBoss)
                {
                    player->TeleportTo(b.map, b.x + 30.0f, b.y + 30.0f, b.z + 5.0f, b.o);
                    return true;
                }
            return false;
        }

        for (TeleDef const& t : g_teleDefs)
            if (t.id == destId)
            {
                player->TeleportTo(t.map, t.x, t.y, t.z, t.o);
                return true;
            }
        return false;
    }

    bool ToggleRune(Player* player, uint32 runeId)
    {
        if (!g_runesEnable || !IsTracked(player))
            return false;

        LoadRunes(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        ChatHandler ch(player->GetSession());
        RuneDef const* r = FindRune(runeId);
        if (!r)
            return false;
        if (r->classmask && !(r->classmask & player->getClassMask()))
            return false;

        if (HasRune(player, runeId))
        {
            CharacterDatabase.Execute("DELETE FROM character_seasonpass_runes WHERE guid = {} AND rune = {}",
                player->GetGUID().GetCounter(), runeId);
            sd.runes.erase(std::remove(sd.runes.begin(), sd.runes.end(), runeId), sd.runes.end());
            if (r->kind == 0)
                player->RemoveAura(r->spell);
            else
                player->removeSpell(r->spell, SPEC_MASK_ALL, false);
            ch.PSendSysMessage(T(player, "|cffFFD700[Traumpfad]|r Rune entfernt: {}",
                                         "|cffFFD700[Dream Path]|r Rune removed: {}"),
                NM(player, r->name, r->nameEn));
            SendRuneSync(player);
            return true;
        }

        if (sd.runes.size() >= MaxRuneSlots(player))
        {
            ch.SendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r Alle Runenslots belegt — erst eine Rune entfernen (Extra-Slots ab Stufe 25/50/75).",
                "|cffFFD700[Dream Path]|r All rune slots used — remove a rune first (extra slots at tier 25/50/75)."));
            return false;
        }
        if (player->GetMoney() < r->cost)
        {
            ch.PSendSysMessage(T(player, "|cffFF0000[Traumpfad]|r Nicht genug Gold ({} Gold nötig).",
                                         "|cffFF0000[Dream Path]|r Not enough gold ({} gold needed)."),
                r->cost / 10000);
            return false;
        }

        player->ModifyMoney(-static_cast<int32>(r->cost));
        CharacterDatabase.Execute("REPLACE INTO character_seasonpass_runes (guid, rune) VALUES ({}, {})",
            player->GetGUID().GetCounter(), runeId);
        sd.runes.push_back(runeId);
        ApplyRunes(player);
        if (r->kind == 1)
            ch.PSendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r |cffA335EENeue Fähigkeit erlernt:|r {} — schau ins Zauberbuch!",
                "|cffFFD700[Dream Path]|r |cffA335EENew ability learned:|r {} — check your spellbook!"),
                NM(player, r->name, r->nameEn));
        else
            ch.PSendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r Rune graviert: |cff00FF00{}|r — wirkt dauerhaft, auch nach dem Tod.",
                "|cffFFD700[Dream Path]|r Rune engraved: |cff00FF00{}|r — permanent, survives death."),
                NM(player, r->name, r->nameEn));
        AchProgress(player, ACH_RUNE, 1);
        SendRuneSync(player);
        return true;
    }

    bool RerollWeekly(Player* player, uint32 slot)
    {
        if (!g_weeklyEnable || !g_rerollEnable || slot >= WEEKLY_SLOTS || !IsTracked(player))
            return false;

        EnsureWeekly(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        ChatHandler ch(player->GetSession());

        if (sd.rerollUsed)
        {
            ch.SendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r Traumtausch schon verbraucht — nächste Woche wieder!",
                "|cffFFD700[Dream Path]|r Dream swap already used — try again next week!"));
            return false;
        }
        WeeklySlot& w = sd.weekly[slot];
        if (!w.defId || w.done)
        {
            ch.SendSysMessage(T(player, "|cffFFD700[Traumpfad]|r Dieses Ziel ist schon erledigt.",
                                        "|cffFFD700[Dream Path]|r That goal is already done."));
            return false;
        }

        uint32 week = CurrentWeek();
        uint32 oldId = w.defId;
        w.defId = PickWeeklyDef(week * 31 + slot * 17 + oldId + NowSecs() % 97, sd.weekly, oldId);
        w.progress = 0;
        w.done = false;
        SaveWeeklySlot(player, week, slot, w);

        sd.rerollUsed = true;
        CharacterDatabase.Execute(
            "REPLACE INTO character_seasonpass_weekly (guid, week, slot, challenge, progress, done) VALUES ({}, {}, {}, 0, 1, 1)",
            player->GetGUID().GetCounter(), week, REROLL_SLOT);

        auto it = g_weeklyById.find(w.defId);
        ch.PSendSysMessage(T(player,
            "|cffFFD700[Traumpfad]|r |cff00CCFFTraumtausch!|r Neues Wochenziel: |cff00FF00{}|r",
            "|cffFFD700[Dream Path]|r |cff00CCFFDream swap!|r New weekly goal: |cff00FF00{}|r"),
            it != g_weeklyById.end() ? NM(player, it->second->name, it->second->nameEn) : "?");
        SendWeeklySync(player);
        return true;
    }

    void SendWeeklySync(Player* player)
    {
        if (!g_weeklyEnable)
            return;
        EnsureWeekly(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        ChatHandler ch(player->GetSession());
        for (uint32 slot = 0; slot < WEEKLY_SLOTS; ++slot)
        {
            WeeklySlot const& w = sd.weekly[slot];
            uint32 goal = 1;
            if (auto it = g_weeklyById.find(w.defId); it != g_weeklyById.end())
                goal = it->second->goal;
            // BPWK:slot:defId:progress:goal:done:rerollFrei
            ch.PSendSysMessage("BPWK:{}:{}:{}:{}:{}:{}", slot, w.defId, w.progress, goal,
                w.done ? 1 : 0, (!sd.rerollUsed && g_rerollEnable) ? 1 : 0);
        }
    }

    void SendWeeklyStatus(Player* player)
    {
        if (!g_weeklyEnable)
            return;
        EnsureWeekly(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        ChatHandler ch(player->GetSession());
        ch.SendSysMessage(T(player, "|cffFFD700=== Wochenziele ===|r", "|cffFFD700=== Weekly Goals ===|r"));
        for (uint32 slot = 0; slot < WEEKLY_SLOTS; ++slot)
        {
            WeeklySlot const& w = sd.weekly[slot];
            auto it = g_weeklyById.find(w.defId);
            if (it == g_weeklyById.end())
                continue;
            WeeklyDef const& def = *it->second;
            if (w.done)
                ch.PSendSysMessage(T(player, "|cff00FF00[erledigt]|r {} (+{} Punkte)",
                                             "|cff00FF00[done]|r {} (+{} points)"),
                    NM(player, def.name, def.nameEn), def.points);
            else
                ch.PSendSysMessage(T(player, "|cffFFA500[{}/{}]|r {} (+{} Punkte)",
                                             "|cffFFA500[{}/{}]|r {} (+{} points)"),
                    w.progress, def.goal, NM(player, def.name, def.nameEn), def.points);
        }
        if (!sd.rerollUsed && g_rerollEnable)
            ch.SendSysMessage(T(player, "Traumtausch verfügbar: .bp reroll <1-3> oder Würfel-Knopf im Fenster",
                                        "Dream swap available: .bp reroll <1-3> or dice button in the window"));
        if (DungeonDef const* dd = ActiveDungeon())
            ch.PSendSysMessage(T(player, "Dungeon der Woche: |cff00CCFF{}|r {}", "Dungeon of the week: |cff00CCFF{}|r {}"),
                NM(player, dd->name, dd->nameEn),
                sd.dungeonDone ? T(player, "|cff00FF00[erledigt]|r", "|cff00FF00[done]|r")
                               : T(player, "|cffFFA500(Bosskill = Bonuspunkte)|r", "|cffFFA500(boss kill = bonus points)|r"));
        if (BountyDef const* b = ActiveBounty())
            ch.PSendSysMessage(T(player, "Kopfgeld des Tages: |cffFF8800{}|r ({}, +{} Punkte)",
                                         "Bounty of the day: |cffFF8800{}|r ({}, +{} points)"),
                NM(player, b->name, b->nameEn), NM(player, b->zone, b->zoneEn), b->points);
        if (ZoneDef const* z = ActiveZone())
            ch.PSendSysMessage(T(player, "Aktive Eventzone: |cff00CCFF{}|r (doppelte Punkte!)",
                                         "Active event zone: |cff00CCFF{}|r (double points!)"),
                NM(player, z->name, z->nameEn));
    }

    uint32 AbilityRuneSpell(uint32 runeId)
    {
        RuneDef const* r = FindRune(runeId);
        return (r && r->kind == 1) ? r->spell : 0;
    }

    uint32 RandomUnknownRuneSpell(Player* player)
    {
        std::vector<uint32> pool;
        for (RuneDef const& r : g_runeDefs)
            if (r.kind == 1 && r.spell && !player->HasSpell(r.spell))
                pool.push_back(r.spell);
        return pool.empty() ? 0 : pool[urand(0, pool.size() - 1)];
    }

    uint32 EngravedBuffRunes(Player* player)
    {
        if (!g_runesEnable)
            return 0;
        LoadRunes(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        uint32 n = 0;
        for (uint32 id : sd.runes)
            if (RuneDef const* r = FindRune(id))
                if (r->kind == 0)
                    ++n;
        return n;
    }

    void SendRuneSync(Player* player)
    {
        if (!g_runesEnable)
            return;
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        std::ostringstream list;
        for (size_t i = 0; i < sd.runes.size(); ++i)
        {
            if (i)
                list << ",";
            list << sd.runes[i];
        }
        // BPRN:aktiveRunen:maxSlots:startFaehigkeit
        ChatHandler(player->GetSession()).PSendSysMessage("BPRN:{}:{}:{}",
            list.str().c_str(), MaxRuneSlots(player), GetStartRune(player));
    }

    void SendEventSync(Player* player)
    {
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        ZoneDef const* z = ActiveZone();
        BountyDef const* b = ActiveBounty();
        DungeonDef const* dd = ActiveDungeon();
        // BPEV mit ~ als Trenner (Namen können Doppelpunkte enthalten!)
        ChatHandler(player->GetSession()).PSendSysMessage("BPEV~{}~{}~{}~{}~{}~{}~{}",
            z ? NM(player, z->name, z->nameEn) : "-",
            b ? NM(player, b->name, b->nameEn) : "-",
            dd ? NM(player, dd->name, dd->nameEn) : "-",
            sd.dungeonDone ? 1 : 0,
            g_activeBoss ? g_activeBossName.c_str() : "-",
            ActiveMutatorName(player).c_str(),
            StormActive() ? 1 : 0);
    }

    void SendAchSync(Player* player)
    {
        if (!g_achEnable)
            return;
        EnsureAch(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        std::ostringstream list;
        bool first = true;
        for (AchDef const& def : g_achDefs)
        {
            if (!first)
                list << ",";
            first = false;
            list << def.id << "." << sd.ach[def.id].progress;
        }
        ChatHandler(player->GetSession()).PSendSysMessage("BPACH:{}", list.str().c_str());
    }

    bool OnWorldBossKilled(Player* player, uint32 entry)
    {
        if (!g_bossEnable || !g_activeBoss || entry != g_activeBoss)
            return false;

        std::string bossName = g_activeBossName;
        g_activeBoss = 0;

        AddPoints(player, g_bossBonusPoints, T(player, "Saison-Weltboss", "Season world boss"));
        WeeklyProgress(player, WK_WORLDBOSS, 1);
        AchProgress(player, ACH_BOSS, 1);

        std::ostringstream msg;
        msg << "|cffFFD700[Dream Path]|r Season world boss |cffFF4444" << bossName
            << "|r was defeated by |cff00CCFF" << player->GetName() << "|r and allies!"
            << " All of Azeroth receives the |cffFF8800Rallying Cry of the Dragonslayer|r!";
        ChatHandler(nullptr).SendGlobalSysMessage(msg.str().c_str());

        if (g_bossWorldBuff)
        {
            auto const& sessions = sWorldSessionMgr->GetAllSessions();
            for (auto const& itr : sessions)
                if (Player* p = itr.second ? itr.second->GetPlayer() : nullptr)
                    if (p->IsInWorld() && IsTracked(p))
                        p->AddAura(g_bossWorldBuff, p);
        }
        return true;
    }

    void HandleDungeonEvent(Progression::DungeonEvent const& event)
    {
        if (!g_dungeonObjectivesEnable || !g_weeklyEnable)
            return;

        EnsureWeeklyRotation();
        for (ObjectGuid guid : event.players)
        {
            Player* player = ObjectAccessor::FindPlayer(guid);
            if (!player || !player->IsInWorld() || !player->GetSession() || !IsTracked(player))
                continue;

            EnsureWeekly(player);
            SeasonPlayerData& data = g_season[player->GetGUID().GetCounter()];
            bool matchesAny = false;
            for (WeeklySlot const& slot : data.weekly)
            {
                auto it = g_weeklyById.find(slot.defId);
                if (!slot.done && it != g_weeklyById.end() && Matches(*it->second, event))
                {
                    matchesAny = true;
                    break;
                }
            }
            if (!matchesAny || !ClaimEvent(player, event))
                continue;

            bool changed = false;
            for (uint32 slotIndex = 0; slotIndex < WEEKLY_SLOTS; ++slotIndex)
            {
                WeeklySlot& slot = data.weekly[slotIndex];
                auto it = g_weeklyById.find(slot.defId);
                if (slot.done || it == g_weeklyById.end() || !Matches(*it->second, event))
                    continue;
                AdvanceWeeklySlot(player, slotIndex, 1, T(player, "Dungeon objective", "Dungeon objective"));
                changed = true;
            }
            if (changed)
                SendWeeklySync(player);
        }
    }

    void AdvanceWeeklySlot(Player* player, uint32 slotIndex, uint32 value, char const* reason)
    {
        SeasonPlayerData& data = g_season[player->GetGUID().GetCounter()];
        WeeklySlot& slot = data.weekly[slotIndex];
        auto it = g_weeklyById.find(slot.defId);
        if (!value || slot.done || it == g_weeklyById.end())
            return;

        WeeklyDef const& def = *it->second;
        slot.progress = std::min(slot.progress + value, def.goal);
        if (slot.progress < def.goal)
        {
            SaveWeeklySlot(player, CurrentWeek(), slotIndex, slot);
            return;
        }

        slot.done = true; // vor AddPoints setzen (Punkte-Ziele -> keine Endlosschleife)
        SaveWeeklySlot(player, CurrentWeek(), slotIndex, slot);
        uint32 points = def.points;
        if (ActiveMutatorKind() == 6) // Woche der Pflicht
            points = points * ActiveMutatorValue() / 100;
        ChatHandler(player->GetSession()).PSendSysMessage(
            T(player, "|cffFFD700[Traumpfad]|r Wochenziel geschafft: |cff00FF00{}|r (+{} Punkte)",
                      "|cffFFD700[Dream Path]|r Weekly goal complete: |cff00FF00{}|r (+{} points)"),
            NM(player, def.name, def.nameEn), points);
        AddPoints(player, points, reason);
        if (def.chestTier > 0)
            OpenChest(player, def.chestTier);
        AchProgress(player, ACH_WEEKLY, 1);
        SendWeeklySync(player);
    }
}

// ---------------------------------------------------------------------------
//  Welt: Config, Tabellen, Weltboss-Rotation
// ---------------------------------------------------------------------------
class SeasonPassSeasonWorld : public WorldScript
{
public:
    SeasonPassSeasonWorld() : WorldScript("SeasonPassSeasonWorld") { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        g_weeklyEnable    = sConfigMgr->GetOption<bool>("SeasonPass.Weekly.Enable", true);
        g_dungeonObjectivesEnable = sConfigMgr->GetOption<bool>("SeasonPass.DungeonObjectives.Enable", true);
        g_rerollEnable    = sConfigMgr->GetOption<bool>("SeasonPass.Weekly.RerollEnable", true);
        g_runesEnable     = sConfigMgr->GetOption<bool>("SeasonPass.Runes.Enable", true);
        g_runeBaseSlots   = sConfigMgr->GetOption<uint32>("SeasonPass.Runes.BaseSlots", 3);
        g_bossEnable      = sConfigMgr->GetOption<bool>("SeasonPass.WorldBoss.Enable", true);
        g_bossIntervalH   = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("SeasonPass.WorldBoss.IntervalHours", 6));
        g_bossDespawnMin  = std::max<uint32>(10, sConfigMgr->GetOption<uint32>("SeasonPass.WorldBoss.DespawnMinutes", 120));
        g_bossBonusPoints = sConfigMgr->GetOption<uint32>("SeasonPass.WorldBoss.BonusPoints", 250);
        g_bossWorldBuff   = sConfigMgr->GetOption<uint32>("SeasonPass.WorldBoss.WorldBuffSpell", 22888);
        g_zonesEnable     = sConfigMgr->GetOption<bool>("SeasonPass.ZoneEvent.Enable", true);
        g_zoneHours       = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("SeasonPass.ZoneEvent.RotationHours", 3));
        g_bountyEnable    = sConfigMgr->GetOption<bool>("SeasonPass.Bounty.Enable", true);
        g_dungeonEnable   = sConfigMgr->GetOption<bool>("SeasonPass.DungeonWeek.Enable", true);
        g_discEnable      = sConfigMgr->GetOption<bool>("SeasonPass.Discoveries.Enable", true);
        g_achEnable       = sConfigMgr->GetOption<bool>("SeasonPass.Achievements.Enable", true);

        LoadSeasonTables();
    }

    void OnUpdate(uint32 diff) override
    {
        if (!g_bossEnable || g_bossDefs.empty())
            return;

        g_bossTimerMs += diff;
        uint64 intervalMs = static_cast<uint64>(g_bossIntervalH) * 3600 * 1000;
        if (g_bossTimerMs < intervalMs)
            return;
        g_bossTimerMs = 0;

        BossDef const& b = g_bossDefs[g_bossRotation % g_bossDefs.size()];
        ++g_bossRotation;

        Map* map = sMapMgr->FindMap(b.map, 0);
        if (!map)
        {
            LOG_INFO("module", "[SeasonPass] Weltboss {}: Karte {} nicht geladen, Spawn übersprungen.", b.name, b.map);
            return;
        }

        Position pos(b.x, b.y, b.z, b.o);
        if (!map->SummonCreature(b.entry, pos, nullptr, g_bossDespawnMin * 60 * 1000))
        {
            LOG_ERROR("module", "[SeasonPass] Weltboss {} (Entry {}) konnte nicht gespawnt werden.", b.name, b.entry);
            return;
        }

        g_activeBoss = b.entry;
        g_activeBossName = b.name;

        std::ostringstream msg;
        msg << "|cffFFD700[Dream Path]|r |cffFF4444Season world boss spawned:|r |cffFF8800"
            << b.name
            << "|r in |cff00CCFF" << (b.zoneEn.empty() ? b.zone : b.zoneEn)
            << "|r! The killing blow grants " << g_bossBonusPoints << " bonus points.";
        ChatHandler(nullptr).SendGlobalSysMessage(msg.str().c_str());
    }
};

// ---------------------------------------------------------------------------
//  Spieler-Hooks
// ---------------------------------------------------------------------------
class SeasonPassSeasonPlayer : public PlayerScript
{
public:
    SeasonPassSeasonPlayer() : PlayerScript("SeasonPassSeasonPlayer") { }

    void OnPlayerLogin(Player* player) override
    {
        if (!SeasonPass::IsTracked(player))
            return;
        EnsureWeekly(player);
        PruneEventCredits(player);
        for (auto it = g_eventCredits.begin(); it != g_eventCredits.end();)
            if (it->guid == player->GetGUID().GetCounter() && it->season < SeasonPass::GetSeason())
                it = g_eventCredits.erase(it);
            else
                ++it;
        EnsureAch(player);
        EnsureDiscoveries(player);
        LoadRunes(player);

        if (ZoneDef const* z = ActiveZone())
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Aktive Eventzone: |cff00CCFF{}|r — doppelte Punkte!",
                          "|cffFFD700[Dream Path]|r Active event zone: |cff00CCFF{}|r — double points!"),
                NM(player, z->name, z->nameEn));
        if (BountyDef const* b = ActiveBounty())
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Kopfgeld des Tages: |cffFF8800{}|r ({})",
                          "|cffFFD700[Dream Path]|r Bounty of the day: |cffFF8800{}|r ({})"),
                NM(player, b->name, b->nameEn), NM(player, b->zone, b->zoneEn));
    }

    void OnPlayerLogout(Player* player) override
    {
        if (player)
            g_season.erase(player->GetGUID().GetCounter());
    }

    void OnPlayerResurrect(Player* player, float /*restore_percent*/, bool& /*applySickness*/) override
    {
        if (g_runesEnable && SeasonPass::IsTracked(player))
            ApplyRunes(player);
    }

    void OnPlayerUpdateZone(Player* player, uint32 newZone, uint32 /*newArea*/) override
    {
        if (!SeasonPass::IsTracked(player))
            return;

        if (ZoneDef const* z = ActiveZone())
            if (z->zone == newZone)
                ChatHandler(player->GetSession()).PSendSysMessage(
                    T(player, "|cffFFD700[Traumpfad]|r Du betrittst die Eventzone |cff00CCFF{}|r — doppelte Punkte!",
                              "|cffFFD700[Dream Path]|r You enter the event zone |cff00CCFF{}|r — double points!"),
                    NM(player, z->name, z->nameEn));

        if (!g_discEnable)
            return;
        EnsureDiscoveries(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        for (DiscDef const& d : g_discDefs)
        {
            if (d.zone != newZone || sd.discovered.count(newZone))
                continue;
            sd.discovered.insert(newZone);
            CharacterDatabase.Execute(
                "REPLACE INTO character_seasonpass_discoveries (guid, zone) VALUES ({}, {})",
                player->GetGUID().GetCounter(), newZone);
            uint32 pts = d.points;
            if (SeasonPass::ActiveMutatorKind() == 7) // Woche der Wanderer
                pts = pts * SeasonPass::ActiveMutatorValue() / 100;
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r |cff00FF00Verlorener Ort entdeckt:|r {} (+{} Punkte) — {}/{} gefunden",
                          "|cffFFD700[Dream Path]|r |cff00FF00Lost place discovered:|r {} (+{} points) — {}/{} found"),
                NM(player, d.name, d.nameEn), pts, static_cast<uint32>(sd.discovered.size()),
                static_cast<uint32>(g_discDefs.size()));
            SeasonPass::AddPoints(player, pts, T(player, "Entdeckung", "Discovery"));
            SeasonPass::WeeklyProgress(player, SeasonPass::WK_DISCOVER, 1);
            SeasonPass::AchProgress(player, SeasonPass::ACH_DISCOVER, 1);
            break;
        }
    }

    void OnPlayerCreatureKill(Player* player, Creature* killed) override
    {
        if (!player || !killed || !SeasonPass::IsTracked(player))
            return;

        if (BountyDef const* b = ActiveBounty())
        {
            if (killed->GetEntry() == b->entry)
            {
                SeasonPass::AddPoints(player, b->points, T(player, "Kopfgeld", "Bounty"));
                SeasonPass::WeeklyProgress(player, SeasonPass::WK_BOUNTY, 1);
                SeasonPass::AchProgress(player, SeasonPass::ACH_BOUNTY, 1);
                std::ostringstream msg;
                msg << "|cffFFD700[Dream Path]|r |cff00CCFF" << player->GetName()
                    << "|r claimed the bounty: |cffFF8800"
                    << (b->nameEn.empty() ? b->name : b->nameEn) << "|r is defeated!";
                ChatHandler(nullptr).SendGlobalSysMessage(msg.str().c_str());
            }
        }

        if (g_dungeonEnable && killed->IsDungeonBoss())
        {
            if (DungeonDef const* dd = ActiveDungeon())
            {
                SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
                EnsureWeekly(player);
                if (!sd.dungeonDone && player->GetMapId() == dd->map)
                {
                    sd.dungeonDone = true;
                    CharacterDatabase.Execute(
                        "REPLACE INTO character_seasonpass_weekly (guid, week, slot, challenge, progress, done) "
                        "VALUES ({}, {}, {}, 0, 1, 1)",
                        player->GetGUID().GetCounter(), CurrentWeek(), DUNGEON_SLOT);
                    SeasonPass::AddPoints(player, dd->points, T(player, "Dungeon der Woche", "Dungeon of the week"));
                    SeasonPass::AchProgress(player, SeasonPass::ACH_DUNGEON, 1);
                    ChatHandler(player->GetSession()).PSendSysMessage(
                        T(player, "|cffFFD700[Traumpfad]|r |cff00FF00Dungeon der Woche geschafft:|r {} (+{} Punkte)",
                                  "|cffFFD700[Dream Path]|r |cff00FF00Dungeon of the week complete:|r {} (+{} points)"),
                        NM(player, dd->name, dd->nameEn), dd->points);
                }
            }
        }
    }
};

// ---------------------------------------------------------------------------
//  Gossip-NPC: Runenmeisterin Sela
// ---------------------------------------------------------------------------
class npc_seasonpass_runes : public CreatureScript
{
public:
    npc_seasonpass_runes() : CreatureScript("npc_seasonpass_runes") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!g_runesEnable)
            return false;

        LoadRunes(player);
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];
        uint32 maxSlots = MaxRuneSlots(player);
        bool en = SeasonPass::GetLang(player) == 1;

        std::ostringstream head;
        head << (en ? "|cffFFD700Seasonal Runes|r — " : "|cffFFD700Saisonale Runen|r — ")
             << sd.runes.size() << " / " << maxSlots << (en ? " slots used" : " Slots belegt");
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, head.str(), GOSSIP_SENDER_MAIN, 1);

        for (RuneDef const& r : g_runeDefs)
        {
            if (r.classmask && !(r.classmask & player->getClassMask()))
                continue;

            if (HasRune(player, r.id))
            {
                std::ostringstream line;
                line << (en ? "|cff00FF00[active]|r " : "|cff00FF00[aktiv]|r ")
                     << NM(player, r.name, r.nameEn) << (en ? " — remove" : " entfernen");
                AddGossipItemFor(player, GOSSIP_ICON_BATTLE, line.str(), GOSSIP_SENDER_MAIN, 2000 + r.id);
            }
            else if (sd.runes.size() < maxSlots)
            {
                std::ostringstream line;
                if (r.kind == 1)
                    line << (en ? "|cffA335EE[Ability]|r " : "|cffA335EE[Fähigkeit]|r ");
                line << NM(player, r.name, r.nameEn) << (en ? " — engrave (" : " gravieren (")
                     << (r.cost / 10000) << (en ? " gold)" : " Gold)");
                AddGossipItemFor(player, GOSSIP_ICON_VENDOR, line.str(), GOSSIP_SENDER_MAIN, 1000 + r.id);
            }
        }

        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        ClearGossipMenuFor(player);
        ChatHandler ch(player->GetSession());
        SeasonPlayerData& sd = g_season[player->GetGUID().GetCounter()];

        if (action >= 2000)
        {
            uint32 runeId = action - 2000;
            if (RuneDef const* r = FindRune(runeId))
            {
                CharacterDatabase.Execute("DELETE FROM character_seasonpass_runes WHERE guid = {} AND rune = {}",
                    player->GetGUID().GetCounter(), runeId);
                sd.runes.erase(std::remove(sd.runes.begin(), sd.runes.end(), runeId), sd.runes.end());
                if (r->kind == 0)
                    player->RemoveAura(r->spell);
                else
                    player->removeSpell(r->spell, SPEC_MASK_ALL, false);
                ch.PSendSysMessage(T(player, "|cffFFD700[Traumpfad]|r Rune entfernt: {}",
                                             "|cffFFD700[Dream Path]|r Rune removed: {}"),
                    NM(player, r->name, r->nameEn));
                SeasonPass::SendRuneSync(player);
            }
        }
        else if (action >= 1000)
        {
            uint32 runeId = action - 1000;
            RuneDef const* r = FindRune(runeId);
            if (r && !HasRune(player, runeId) && sd.runes.size() < MaxRuneSlots(player))
            {
                if (player->GetMoney() < r->cost)
                    ch.PSendSysMessage(T(player, "|cffFF0000[Traumpfad]|r Nicht genug Gold ({} Gold nötig).",
                                                 "|cffFF0000[Dream Path]|r Not enough gold ({} gold needed)."),
                        r->cost / 10000);
                else
                {
                    player->ModifyMoney(-static_cast<int32>(r->cost));
                    CharacterDatabase.Execute("REPLACE INTO character_seasonpass_runes (guid, rune) VALUES ({}, {})",
                        player->GetGUID().GetCounter(), runeId);
                    sd.runes.push_back(runeId);
                    ApplyRunes(player);
                    if (r->kind == 1)
                        ch.PSendSysMessage(T(player,
                            "|cffFFD700[Traumpfad]|r |cffA335EENeue Fähigkeit erlernt:|r {} — schau ins Zauberbuch!",
                            "|cffFFD700[Dream Path]|r |cffA335EENew ability learned:|r {} — check your spellbook!"),
                            NM(player, r->name, r->nameEn));
                    else
                        ch.PSendSysMessage(T(player,
                            "|cffFFD700[Traumpfad]|r Rune graviert: |cff00FF00{}|r — wirkt dauerhaft, auch nach dem Tod.",
                            "|cffFFD700[Dream Path]|r Rune engraved: |cff00FF00{}|r — permanent, survives death."),
                            NM(player, r->name, r->nameEn));
                    SeasonPass::AchProgress(player, SeasonPass::ACH_RUNE, 1);
                    SeasonPass::SendRuneSync(player);
                }
            }
        }

        OnGossipHello(player, creature);
        return true;
    }
};

// ---------------------------------------------------------------------------
//  Gossip-NPC: Traumpfadhüterin (Teleporter)
// ---------------------------------------------------------------------------
class npc_seasonpass_teleport : public CreatureScript
{
public:
    npc_seasonpass_teleport() : CreatureScript("npc_seasonpass_teleport") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        bool en = SeasonPass::GetLang(player) == 1;
        AddGossipItemFor(player, GOSSIP_ICON_CHAT,
            en ? "|cffFFD700Where shall the journey go?|r" : "|cffFFD700Wohin soll die Reise gehen?|r",
            GOSSIP_SENDER_MAIN, 1);
        for (TeleDef const& t : g_teleDefs)
            AddGossipItemFor(player, GOSSIP_ICON_TAXI, NM(player, t.name, t.nameEn), GOSSIP_SENDER_MAIN, 100 + t.id);

        if (g_activeBoss)
            for (BossDef const& b : g_bossDefs)
                if (b.entry == g_activeBoss)
                    AddGossipItemFor(player, GOSSIP_ICON_BATTLE,
                        std::string(en ? "|cffFF4444To the season world boss: " : "|cffFF4444Zum Saison-Weltboss: ")
                        + b.name + "|r", GOSSIP_SENDER_MAIN, 999);

        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* /*creature*/, uint32 /*sender*/, uint32 action) override
    {
        ClearGossipMenuFor(player);
        CloseGossipMenuFor(player);
        if (action == 999)
            SeasonPass::TeleportTo(player, 999);
        else if (action >= 100)
            SeasonPass::TeleportTo(player, action - 100);
        return true;
    }
};

void AddSC_SeasonPassSeason()
{
    new SeasonPassSeasonWorld();
    new SeasonPassSeasonPlayer();
    new npc_seasonpass_runes();
    new npc_seasonpass_teleport();
}
