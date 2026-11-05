#include "BattlemonSpawns.h"
#include "BattlemonMgr.h"

#include "Common.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "Player.h"
#include "Random.h"
#include "StringFormat.h"
#include "WorldSession.h"

#include <algorithm>
#include <cstdlib>
#include <set>
#include <sstream>

namespace Rules = BattlemonSpawnRules;

namespace
{
std::set<std::string> const TYPE_NAMES = {
    "NORMAL", "FIRE", "WATER", "ELECTRIC", "GRASS", "ICE", "FIGHTING", "POISON", "GROUND",
    "FLYING", "PSYCHIC", "BUG", "ROCK", "GHOST", "DRAGON", "DARK", "STEEL", "FAIRY"};

bool ToUint(std::string const& text, uint32 lo, uint32 hi, uint32& out)
{
    char* stop = nullptr;
    unsigned long const v = std::strtoul(text.c_str(), &stop, 10);
    if (text.empty() || *stop != '\0' || v < lo || v > hi)
        return false;
    out = static_cast<uint32>(v);
    return true;
}

bool ToFloat(std::string const& text, float lo, float hi, float& out)
{
    char* stop = nullptr;
    float const v = std::strtof(text.c_str(), &stop);
    if (text.empty() || *stop != '\0' || !(v >= lo) || v > hi)
        return false;
    out = v;
    return true;
}

// Validates one knob and returns its canonical text; the canonical text, never the caller's, is what gets saved.
bool ParseSetting(BattlemonSpawns::Settings& s, std::string const& name, std::string const& value,
                  std::string& canonical, std::string& error)
{
    uint32 u = 0;
    float f = 0.0f;
    if (name == "enable" && ToUint(value, 0, 1, u))
        s.enable = u != 0;
    else if (name == "level_mode" && ToUint(value, 0, 2, u))
        s.levelMode = u;
    else if (name == "rarity_exponent" && ToFloat(value, 0.0f, 3.0f, f))
        s.rarityExponent = f;
    else if (name == "stage_step" && ToUint(value, 0, 50, u))
        s.stageStep = u;
    else if (name == "leak" && ToFloat(value, 0.0f, 1.0f, f))
        s.leak = f;
    else if (name == "weight_legendary" && ToUint(value, 0, 1000, u))
        s.weightLegendary = u;
    else if (name == "weight_starter" && ToUint(value, 0, 1000, u))
        s.weightStarter = u;
    else if (name == "weight_normal" && ToUint(value, 0, 1000, u))
        s.weightNormal = u;
    else
    {
        error = "Bad value for " + name + ".";
        return false;
    }
    canonical = u || value == "0" ? std::to_string(u) : Acore::StringFormat("{}", f);
    return true;
}

std::vector<std::string> SplitTabs(std::string const& text)
{
    std::vector<std::string> out;
    std::string cur;
    for (char c : text)
    {
        if (c == '\t')
        {
            out.push_back(cur);
            cur.clear();
        }
        else
            cur.push_back(c);
    }
    out.push_back(cur);
    return out;
}
} // namespace

BattlemonSpawns* BattlemonSpawns::instance()
{
    static BattlemonSpawns inst;
    return &inst;
}

void BattlemonSpawns::Load(uint32 confLegendary, uint32 confStarter, uint32 confNormal)
{
    Settings settings;
    settings.weightLegendary = confLegendary;
    settings.weightStarter = confStarter;
    settings.weightNormal = confNormal;
    std::unordered_map<uint32, Zone> zones;
    std::unordered_map<uint32, float> multipliers;
    std::vector<Entry> entries;
    std::unordered_map<uint32, Rules::EvoLink> links;

    if (QueryResult result = WorldDatabase.Query("SELECT name, value FROM battlemon_spawn_setting"))
    {
        do
        {
            Field* f = result->Fetch();
            std::string canonical, error;
            if (!ParseSetting(settings, f[0].Get<std::string>(), f[1].Get<std::string>(), canonical, error))
                LOG_WARN("module", "Battlemon spawns: ignoring setting '{}' = '{}'", f[0].Get<std::string>(),
                         f[1].Get<std::string>());
        } while (result->NextRow());
    }
    if (QueryResult result = WorldDatabase.Query(
            "SELECT zone_id, min_level, max_level, types FROM battlemon_spawn_zone"))
    {
        do
        {
            Field* f = result->Fetch();
            Zone zone;
            zone.minLevel = f[1].Get<uint32>();
            zone.maxLevel = f[2].Get<uint32>();
            zone.typesText = f[3].Get<std::string>();
            if (!Rules::ParseTypes(zone.typesText, zone.types) || zone.minLevel < 1 || zone.maxLevel < zone.minLevel)
            {
                LOG_WARN("module", "Battlemon spawns: ignoring zone {} (bad levels or types)", f[0].Get<uint32>());
                continue;
            }
            zones[f[0].Get<uint32>()] = std::move(zone);
        } while (result->NextRow());
    }
    if (QueryResult result = WorldDatabase.Query("SELECT species_id, multiplier FROM battlemon_spawn_species"))
    {
        do
        {
            Field* f = result->Fetch();
            multipliers[f[0].Get<uint32>()] = std::max(0.0f, f[1].Get<float>());
        } while (result->NextRow());
    }

    // Species first: group every spawnable form under its species.
    std::unordered_map<uint32, Entry> bySpecies;
    for (uint32 formId : sBattlemonMgr->FormIds())
    {
        BattlemonForm const* form = sBattlemonMgr->GetBattlemonForm(formId);
        BattlemonSpecies const* species = form ? sBattlemonMgr->GetSpecies(form->speciesId) : nullptr;
        if (!species || form->sprite.empty())
            continue;
        Entry& entry = bySpecies[species->id];
        entry.species = species;
        entry.spawnClass = sBattlemonMgr->SpawnClass(species->id);
        entry.formIds.push_back(formId);
    }
    for (auto& pair : bySpecies)
        entries.push_back(std::move(pair.second));

    // Evolutions are target,method,parameter triples naming the target by internal name. "Level" and its
    // variants (LevelDay, LevelFemale, ...) carry the level as the parameter.
    std::unordered_map<std::string, uint32> idByName;
    for (auto const& species : sBattlemonMgr->SpeciesMap())
        idByName[species.second.internalName] = species.first;
    for (auto const& species : sBattlemonMgr->SpeciesMap())
    {
        std::vector<std::string> parts;
        std::stringstream stream(species.second.evolutions);
        for (std::string part; std::getline(stream, part, ',');)
            parts.push_back(part);
        for (size_t i = 0; i + 2 < parts.size(); i += 3)
        {
            auto target = idByName.find(parts[i]);
            if (target == idByName.end())
                continue;
            bool const byLevel = parts[i + 1].compare(0, 5, "Level") == 0;
            links.emplace(target->second, Rules::EvoLink{ species.first,
                byLevel ? static_cast<uint32>(std::strtoul(parts[i + 2].c_str(), nullptr, 10)) : 0u });
        }
    }

    std::lock_guard<std::mutex> guard(_lock);
    _settings = settings;
    _zones = std::move(zones);
    _speciesMultiplier = std::move(multipliers);
    _links = std::move(links);
    _entries = std::move(entries);
    LOG_INFO("module", "Battlemon spawns: {} species, {} zone rules, zone-aware spawning {}", _entries.size(),
             _zones.size(), _settings.enable ? "on" : "off");
}

BattlemonSpawns::Settings BattlemonSpawns::GetSettings() const
{
    std::lock_guard<std::mutex> guard(_lock);
    return _settings;
}

bool BattlemonSpawns::GetZone(uint32 zoneId, Zone& out) const
{
    std::lock_guard<std::mutex> guard(_lock);
    auto it = _zones.find(zoneId);
    if (it == _zones.end())
        return false;
    out = it->second;
    return true;
}

uint32 BattlemonSpawns::EnemyLevel(uint32 zoneId, uint32 scaledLevel) const
{
    std::lock_guard<std::mutex> guard(_lock);
    auto it = _zones.find(zoneId);
    if (!_settings.enable || it == _zones.end())
        return scaledLevel;
    Zone const& zone = it->second;
    return Rules::EnemyLevel(_settings.levelMode, scaledLevel, zone.minLevel, zone.maxLevel,
                             urand(zone.minLevel, zone.maxLevel));
}

uint32 BattlemonSpawns::BaseSpecies(uint32 speciesId) const
{
    std::lock_guard<std::mutex> guard(_lock);
    uint32 current = speciesId;
    for (int depth = 0; depth < 8; ++depth)
    {
        auto it = _links.find(current);
        if (it == _links.end() || !it->second.prevo)
            break;
        current = it->second.prevo;
    }
    return current;
}

uint32 BattlemonSpawns::LevelHint(uint32 zoneId) const
{
    std::lock_guard<std::mutex> guard(_lock);
    auto it = _zones.find(zoneId);
    return _settings.enable && it != _zones.end() ? it->second.maxLevel : 100;
}

// Caller holds _lock. classShare[c] turns a candidate's weight into a probability: the class is picked by
// its weight (only among classes that have a candidate), then the species by its own weight inside it.
void BattlemonSpawns::Candidates(uint32 zoneId, uint32 level, std::vector<Candidate>& out, float classShare[3]) const
{
    auto zoneIt = _zones.find(zoneId);
    Zone const* zone = zoneIt == _zones.end() ? nullptr : &zoneIt->second;

    float sum[3] = {};
    for (Entry const& entry : _entries)
    {
        BattlemonSpecies const& sp = *entry.species;
        if (level < Rules::MinLevel(sp.id, _links, _settings.stageStep))
            continue;
        float weight = Rules::RarityWeight(sp.catchRate, _settings.rarityExponent);
        if (auto m = _speciesMultiplier.find(sp.id); m != _speciesMultiplier.end())
            weight *= m->second;
        if (zone)
            weight *= Rules::TypeWeight(zone->types, sp.type1, sp.type2, _settings.leak);
        if (weight <= 0.0f)
            continue;
        out.push_back({ &entry, weight });
        sum[entry.spawnClass] += weight;
    }

    float const classWeight[3] = { static_cast<float>(_settings.weightNormal), static_cast<float>(_settings.weightStarter),
                                   static_cast<float>(_settings.weightLegendary) };
    float total = 0.0f;
    for (int c = 0; c < 3; ++c)
        if (sum[c] > 0.0f)
            total += classWeight[c];
    for (int c = 0; c < 3; ++c)
    {
        if (sum[c] <= 0.0f)
            classShare[c] = 0.0f;
        else if (total > 0.0f)
            classShare[c] = classWeight[c] / total / sum[c];
        else
            classShare[c] = 1.0f / sum[c]; // every class weighted 0: treat them as equal rather than spawn nothing
    }
}

BattlemonForm const* BattlemonSpawns::PickForm(uint32 zoneId, uint32 level) const
{
    std::lock_guard<std::mutex> guard(_lock);
    if (!_settings.enable)
        return nullptr;
    std::vector<Candidate> candidates;
    float share[3];
    Candidates(zoneId, level, candidates, share);
    if (candidates.empty())
        return nullptr;

    float roll = frand(0.0f, 1.0f);
    Entry const* picked = candidates.back().entry;
    for (Candidate const& c : candidates)
    {
        roll -= c.weight * share[c.entry->spawnClass];
        if (roll <= 0.0f)
        {
            picked = c.entry;
            break;
        }
    }
    return sBattlemonMgr->GetBattlemonForm(picked->formIds[urand(0, static_cast<uint32>(picked->formIds.size() - 1))]);
}

std::vector<std::pair<BattlemonSpecies const*, float>> BattlemonSpawns::Odds(uint32 zoneId, uint32 level) const
{
    std::lock_guard<std::mutex> guard(_lock);
    std::vector<std::pair<BattlemonSpecies const*, float>> out;
    std::vector<Candidate> candidates;
    float share[3];
    Candidates(zoneId, level, candidates, share);
    for (Candidate const& c : candidates)
        out.emplace_back(c.entry->species, c.weight * share[c.entry->spawnClass]);
    std::sort(out.begin(), out.end(), [](auto const& a, auto const& b) { return a.second > b.second; });
    return out;
}

bool BattlemonSpawns::SetSetting(std::string const& name, std::string const& value, std::string& error)
{
    std::lock_guard<std::mutex> guard(_lock);
    Settings next = _settings;
    std::string canonical;
    if (!ParseSetting(next, name, value, canonical, error))
        return false;
    _settings = next;
    // name passed the whitelist above and canonical is built from the parsed number: both are safe to embed.
    WorldDatabase.Execute("REPLACE INTO battlemon_spawn_setting (name, value) VALUES ('{}', '{}')", name, canonical);
    return true;
}

bool BattlemonSpawns::SetZone(uint32 zoneId, uint32 minLevel, uint32 maxLevel, std::string const& types,
                              std::string& error)
{
    std::vector<std::pair<std::string, float>> parsed;
    if (!zoneId || minLevel < 1 || maxLevel > 100 || maxLevel < minLevel)
    {
        error = "Levels must be 1-100 with min <= max.";
        return false;
    }
    if (!Rules::ParseTypes(types, parsed))
    {
        error = "Types must look like GRASS:3,BUG:2.";
        return false;
    }
    std::string canonical;
    for (auto const& entry : parsed)
    {
        if (!TYPE_NAMES.count(entry.first))
        {
            error = "Unknown type " + entry.first + ".";
            return false;
        }
        canonical += (canonical.empty() ? "" : ",") + Acore::StringFormat("{}:{}", entry.first, entry.second);
    }
    if (canonical.size() > 255)
    {
        error = "Too many types.";
        return false;
    }

    Zone zone;
    zone.minLevel = minLevel;
    zone.maxLevel = maxLevel;
    zone.typesText = canonical;
    zone.types = std::move(parsed);
    std::lock_guard<std::mutex> guard(_lock);
    _zones[zoneId] = std::move(zone);
    // canonical is rebuilt from whitelisted type names and numbers, so it cannot carry quotes.
    WorldDatabase.Execute("INSERT INTO battlemon_spawn_zone (zone_id, min_level, max_level, types) "
                          "VALUES ({}, {}, {}, '{}') ON DUPLICATE KEY UPDATE min_level = VALUES(min_level), "
                          "max_level = VALUES(max_level), types = VALUES(types)",
                          zoneId, minLevel, maxLevel, canonical);
    return true;
}

std::vector<std::pair<std::string, std::string>> BattlemonSpawns::SettingsList() const
{
    std::lock_guard<std::mutex> guard(_lock);
    return {
        { "enable", _settings.enable ? "1" : "0" },
        { "level_mode", std::to_string(_settings.levelMode) },
        { "rarity_exponent", Acore::StringFormat("{}", _settings.rarityExponent) },
        { "stage_step", std::to_string(_settings.stageStep) },
        { "leak", Acore::StringFormat("{}", _settings.leak) },
        { "weight_legendary", std::to_string(_settings.weightLegendary) },
        { "weight_starter", std::to_string(_settings.weightStarter) },
        { "weight_normal", std::to_string(_settings.weightNormal) },
    };
}

// Addon admin panel, command ADMIN. Only administrators; every request is answered with the current state
// (settings, this zone's rule, optionally a preview) so the panel never shows stale numbers.
//   GET | SET <name> <value> | ZONE <min> <max> <types> | PREVIEW
void BattlemonMgr::HandleAdmin(Player* player, std::string const& arg)
{
    if (!player)
        return;
    if (player->GetSession()->GetSecurity() < SEC_ADMINISTRATOR)
    {
        SendAddon(player, "BM\tMSG\tAdministrators only.");
        return;
    }

    std::vector<std::string> const parts = SplitTabs(arg);
    std::string const verb = parts.empty() || parts[0].empty() ? "GET" : parts[0];
    uint32 const zoneId = player->GetZoneId();
    std::string error;
    bool preview = false;

    if (verb == "SET" && parts.size() >= 3)
        sBattlemonSpawns->SetSetting(parts[1], parts[2], error);
    else if (verb == "ZONE" && parts.size() >= 4)
        sBattlemonSpawns->SetZone(zoneId, static_cast<uint32>(std::strtoul(parts[1].c_str(), nullptr, 10)),
                                  static_cast<uint32>(std::strtoul(parts[2].c_str(), nullptr, 10)), parts[3], error);
    else if (verb == "PREVIEW")
        preview = true;
    else if (verb != "GET")
        error = "Unknown admin request.";

    if (!error.empty())
        SendAddon(player, "BM\tMSG\t" + error);

    for (auto const& setting : sBattlemonSpawns->SettingsList())
        SendAddon(player, "BM\tADMIN\tSET\t" + setting.first + "\t" + setting.second);

    BattlemonSpawns::Zone zone;
    bool const hasZone = sBattlemonSpawns->GetZone(zoneId, zone);
    SendAddon(player, Acore::StringFormat("BM\tADMIN\tZONE\t{}\t{}\t{}\t{}", zoneId, hasZone ? zone.minLevel : 0u,
                                           hasZone ? zone.maxLevel : 0u, hasZone ? zone.typesText : ""));

    if (preview)
    {
        BattlemonSpawns::Settings const settings = sBattlemonSpawns->GetSettings();
        BattlemonOwned const lead = LoadOwnedById(PartyOwnedId(player->GetGUID().GetCounter(), 1));
        uint32 const scaled = ScaledEnemyLevel(lead.id ? lead.level : 1);
        uint32 const level = hasZone && settings.enable
            ? Rules::EnemyLevel(settings.levelMode, scaled, zone.minLevel, zone.maxLevel,
                                (zone.minLevel + zone.maxLevel) / 2)
            : scaled;
        std::string line = Acore::StringFormat("BM\tADMIN\tODDS\t{}", level);
        auto const odds = sBattlemonSpawns->Odds(zoneId, level);
        for (size_t i = 0; i < odds.size() && i < 12; ++i)
            line += Acore::StringFormat("\t{}~{:.1f}", odds[i].first->name, odds[i].second * 100.0f);
        SendAddon(player, line);
    }
    SendAddon(player, "BM\tADMIN\tEND");
}
