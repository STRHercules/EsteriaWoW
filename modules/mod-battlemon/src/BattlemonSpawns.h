#ifndef BATTLEMON_SPAWNS_H
#define BATTLEMON_SPAWNS_H

#include "BattlemonSpawnRules.h"
#include "BattlemonTypes.h"
#include "Define.h"

#include <mutex>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// Which wild Pokemon appear where. A zone lists the Pokemon types that live there and a level range; on top of
// that every species is weighted by rarity (catch rate) and held back until the level allows its evolution
// stage. Species are picked first and a form second, so a species with 28 forms is not 28 times as common.
// The numbers are runtime knobs (battlemon_spawn_setting) an administrator edits from the addon's admin panel.
class BattlemonSpawns
{
public:
    static BattlemonSpawns* instance();

    struct Settings
    {
        bool enable = true;
        uint32 levelMode = 0;       // 0 player-scaled (unchanged), 1 roll in the zone's range, 2 clamp into it
        float rarityExponent = 1.0f;  // 0 ignores catch rate
        uint32 stageStep = 8;         // extra levels for an evolution that is not level-based; 0 disables the gate
        float leak = 0.15f;           // weight for a type the zone does not list
        uint32 weightLegendary = 1;
        uint32 weightStarter = 5;
        uint32 weightNormal = 94;
    };

    struct Zone
    {
        uint32 minLevel = 0; // 0 = this zone has no rule
        uint32 maxLevel = 0;
        std::string typesText;
        std::vector<std::pair<std::string, float>> types;
    };

    // Reads the three tables. Call after the catalog (species and forms) is loaded.
    void Load(uint32 confLegendary, uint32 confStarter, uint32 confNormal);

    Settings GetSettings() const;
    bool GetZone(uint32 zoneId, Zone& out) const;

    // The level a wild Pokemon gets in this zone, given the player-scaled level.
    uint32 EnemyLevel(uint32 zoneId, uint32 scaledLevel) const;
    // The level used to decide which evolution stages may appear when no fight level exists yet
    // (an overworld critter morphing): the top of the zone's range, or 100 with no rule.
    uint32 LevelHint(uint32 zoneId) const;
    // Nullptr when spawning is switched off or nothing qualifies; the caller falls back to its old pick.
    BattlemonForm const* PickForm(uint32 zoneId, uint32 level) const;
    // Species and their chance (0-1), most likely first; for the admin preview.
    std::vector<std::pair<BattlemonSpecies const*, float>> Odds(uint32 zoneId, uint32 level) const;

    // Administrator edits. They validate, persist and apply immediately; `error` says what was wrong.
    bool SetSetting(std::string const& name, std::string const& value, std::string& error);
    bool SetZone(uint32 zoneId, uint32 minLevel, uint32 maxLevel, std::string const& types, std::string& error);
    std::vector<std::pair<std::string, std::string>> SettingsList() const;

private:
    BattlemonSpawns() = default;

    struct Entry
    {
        BattlemonSpecies const* species = nullptr;
        uint32 spawnClass = 0; // 0 normal, 1 starter, 2 legendary
        std::vector<uint32> formIds;
    };
    struct Candidate
    {
        Entry const* entry = nullptr;
        float weight = 0.0f;
    };

    void Candidates(uint32 zoneId, uint32 level, std::vector<Candidate>& out, float classShare[3]) const;

    mutable std::mutex _lock;
    Settings _settings;
    std::unordered_map<uint32, Zone> _zones;
    std::unordered_map<uint32, float> _speciesMultiplier;
    std::unordered_map<uint32, BattlemonSpawnRules::EvoLink> _links;
    std::vector<Entry> _entries;
};

#define sBattlemonSpawns BattlemonSpawns::instance()

#endif
