#include "BattlemonMgr.h"
#include "BattlemonBattle.h"
#include "BattlemonSidecarServer.h"

#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "Map.h"
#include "GameTime.h"
#include "Log.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "Random.h"
#include "SharedDefines.h"
#include "Timer.h"
#include "WorldPacket.h"
#include "WorldSession.h"

#include <algorithm>
#include <array>
#include <ctime>
#include <cstdlib>
#include <iterator>
#include <sstream>
#include <unordered_set>

namespace
{
    // National Dex ids: legendaries + mythicals. Ultra Beasts stay in the normal pool.
    constexpr uint32 kLegendarySpecies[] = {
        144, 145, 146, 150, 151,
        243, 244, 245, 249, 250, 251,
        377, 378, 379, 380, 381, 382, 383, 384, 385, 386,
        480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493,
        494, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649,
        716, 717, 718, 719, 720, 721,
        785, 786, 787, 788, 789, 790, 791, 792, 800, 801, 802, 807, 808, 809,
        888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898
    };

    // Grass/fire/water starter lines (all three stages), gens 1-8.
    constexpr uint32 kStarterSpecies[] = {
        1, 2, 3, 4, 5, 6, 7, 8, 9,
        152, 153, 154, 155, 156, 157, 158, 159, 160,
        252, 253, 254, 255, 256, 257, 258, 259, 260,
        387, 388, 389, 390, 391, 392, 393, 394, 395,
        495, 496, 497, 498, 499, 500, 501, 502, 503,
        650, 651, 652, 653, 654, 655, 656, 657, 658,
        722, 723, 724, 725, 726, 727, 728, 729, 730,
        810, 811, 812, 813, 814, 815, 816, 817, 818
    };

    std::unordered_set<uint32> const kLegendarySet(std::begin(kLegendarySpecies), std::end(kLegendarySpecies));
    std::unordered_set<uint32> const kStarterSet(std::begin(kStarterSpecies), std::end(kStarterSpecies));

    bool IsLegendarySpecies(uint32 id)
    {
        return kLegendarySet.count(id) != 0;
    }

    bool IsStarterSpecies(uint32 id)
    {
        return kStarterSet.count(id) != 0;
    }

    // AzerothCore fmt SQL does not quote strings, so a bare {} turns 0025_Pikachu or
    // POKEBALL into a column name (MySQL 1054). Returns the surrounding quotes as well
    // as the escaping: pass this straight into a bare {}, never into '{}'.
    std::string SqlQuote(std::string s)
    {
        CharacterDatabase.EscapeString(s);
        return "'" + s + "'";
    }

    BattlemonForm const* PickForm(std::vector<uint32> const& ids,
                                  std::unordered_map<uint32, BattlemonForm> const& forms)
    {
        if (ids.empty())
            return nullptr;
        uint32 id = ids[urand(0, static_cast<uint32>(ids.size() - 1))];
        auto it = forms.find(id);
        return it == forms.end() ? nullptr : &it->second;
    }

    std::vector<std::string> Split(std::string const& s, char delim)
    {
        std::vector<std::string> out;
        std::string cur;
        for (char c : s)
        {
            if (c == delim)
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

    std::string MoveName(BattlemonBattler const& b, int i)
    {
        if (i < static_cast<int>(b.moves.size()) && b.moves[i].def)
            return b.moves[i].def->internalName;
        return "";
    }

    // The item catalog carries a heal amount but nothing that says which
    // condition a spray lifts, so the mapping lives here. Cure-only items have
    // a null heal_amount, which is why they used to be refused outright.
    BmStatus CureFor(std::string const& item)
    {
        if (item == "AWAKENING" || item == "CHESTOBERRY" || item == "BLUEFLUTE")
            return BmStatus::SLP;
        if (item == "ANTIDOTE" || item == "PECHABERRY")
            return BmStatus::PSN;
        if (item == "BURNHEAL" || item == "RAWSTBERRY")
            return BmStatus::BRN;
        if (item == "PARALYZEHEAL" || item == "PARLYZHEAL" || item == "CHERIBERRY")
            return BmStatus::PAR;
        if (item == "ICEHEAL" || item == "ASPEARBERRY")
            return BmStatus::FRZ;
        return BmStatus::None;
    }

    bool CuresEverything(std::string const& item)
    {
        return item == "FULLHEAL" || item == "FULLRESTORE" || item == "LUMBERRY"
            || item == "HEALPOWDER" || item == "LAVACOOKIE" || item == "OLDGATEAU"
            || item == "CASTELIACONE" || item == "LUMIOSEGALETTE" || item == "SHALOURSABLE"
            || item == "BIGMALASADA" || item == "PEWTERCRUNCHIES" || item == "RAGECANDYBAR";
    }

    bool IsReviveItem(std::string const& item)
    {
        return item == "REVIVE" || item == "MAXREVIVE" || item == "REVIVALHERB";
    }
}

BattlemonMgr* BattlemonMgr::instance()
{
    static BattlemonMgr inst;
    return &inst;
}

uint32 BattlemonMgr::NowSeconds() const
{
    return static_cast<uint32>(GameTime::GetGameTime().count());
}

void BattlemonMgr::LoadConfig()
{
    _enabled = sConfigMgr->GetOption<bool>("Battlemon.Enable", true);
    _announce = sConfigMgr->GetOption<bool>("Battlemon.Announce", true);
    _grantToBots = sConfigMgr->GetOption<bool>("Battlemon.GrantToBots", false);
    _starterSpecies = sConfigMgr->GetOption<uint32>("Battlemon.StarterSpecies", 25);
    _starterLevel = sConfigMgr->GetOption<uint32>("Battlemon.StarterLevel", 1);
    _encounterCooldown = sConfigMgr->GetOption<uint32>("Battlemon.EncounterCooldown", 300);
    _catchChance = sConfigMgr->GetOption<float>("Battlemon.CatchChance", 0.5f);
    _dailyBalls = sConfigMgr->GetOption<uint32>("Battlemon.DailyBalls", 5);
    _winBalls = sConfigMgr->GetOption<uint32>("Battlemon.WinBalls", 1);
    _bagMaxStack = sConfigMgr->GetOption<uint32>("Battlemon.BagMaxStack", 99);
    _catchThrows = static_cast<uint8>(sConfigMgr->GetOption<uint32>("Battlemon.CatchThrows", 3));
    _weightLegendary = sConfigMgr->GetOption<uint32>("Battlemon.EncounterLegendary", 1);
    _weightStarter = sConfigMgr->GetOption<uint32>("Battlemon.EncounterStarter", 5);
    _weightNormal = sConfigMgr->GetOption<uint32>("Battlemon.EncounterNormal", 94);
    _winPoints = sConfigMgr->GetOption<uint32>("Battlemon.WinPoints", 10);
    _shinyEvery = sConfigMgr->GetOption<uint32>("Battlemon.ShinyEvery", 10);
    _tutorMoveCost = sConfigMgr->GetOption<uint32>("Battlemon.TutorMoveCost", 25);
    _faintReviveHours = sConfigMgr->GetOption<uint32>("Battlemon.FaintReviveHours", 1);
    _greatBallMult = sConfigMgr->GetOption<float>("Battlemon.GreatBallMult", 1.5f);
    _ultraBallMult = sConfigMgr->GetOption<float>("Battlemon.UltraBallMult", 2.0f);
    if (_starterLevel < 1)
        _starterLevel = 1;
    if (_starterLevel > 100)
        _starterLevel = 100;
    if (_catchChance < 0.f)
        _catchChance = 0.f;
    if (_catchChance > 1.f)
        _catchChance = 1.f;
    if (_bagMaxStack < 1)
        _bagMaxStack = 1;
    if (_bagMaxStack > 999)
        _bagMaxStack = 999;
    if (_catchThrows < 1)
        _catchThrows = 1;
    if (_catchThrows > 10)
        _catchThrows = 10;
}

void BattlemonMgr::LoadCatalog()
{
    _species.clear();
    _forms.clear();
    _moves.clear();
    _learnsets.clear();
    _tutorMoves.clear();
    _formMoves.clear();
    _items.clear();
    _shop.clear();
    _typeChart.clear();
    _formIds.clear();
    _legendaryFormIds.clear();
    _starterFormIds.clear();
    _normalFormIds.clear();
    _starterFormId = 0;

    if (QueryResult result = WorldDatabase.Query(
            "SELECT id, internal_name, name, type1, type2, hp, atk, def, spa, spd, spe, "
            "gender_ratio, growth_rate, base_exp, sprite, ability1, ability2, hidden_ability FROM battlemon_species"))
    {
        do
        {
            Field* f = result->Fetch();
            BattlemonSpecies s;
            s.id = f[0].Get<uint32>();
            s.internalName = f[1].Get<std::string>();
            s.name = f[2].Get<std::string>();
            s.type1 = f[3].Get<std::string>();
            s.type2 = f[4].IsNull() ? "" : f[4].Get<std::string>();
            s.hp = f[5].Get<uint32>();
            s.atk = f[6].Get<uint32>();
            s.def = f[7].Get<uint32>();
            s.spa = f[8].Get<uint32>();
            s.spd = f[9].Get<uint32>();
            s.spe = f[10].Get<uint32>();
            s.genderRatio = f[11].IsNull() ? "Female50Percent" : f[11].Get<std::string>();
            s.growthRate = f[12].IsNull() ? "Medium" : f[12].Get<std::string>();
            s.baseExp = f[13].Get<uint32>();
            s.sprite = f[14].IsNull() ? "" : f[14].Get<std::string>();
            s.ability1 = f[15].IsNull() ? "" : f[15].Get<std::string>();
            s.ability2 = f[16].IsNull() ? "" : f[16].Get<std::string>();
            s.hiddenAbility = f[17].IsNull() ? "" : f[17].Get<std::string>();
            _species[s.id] = s;
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT id, species_id, sprite, variant, name, back_sprite FROM battlemon_forms"))
    {
        do
        {
            Field* f = result->Fetch();
            BattlemonForm form;
            form.id = f[0].Get<uint32>();
            form.speciesId = f[1].Get<uint32>();
            form.sprite = f[2].Get<std::string>();
            form.variant = f[3].IsNull() ? "" : f[3].Get<std::string>();
            form.name = f[4].Get<std::string>();
            form.backSprite = f[5].IsNull() ? form.sprite : f[5].Get<std::string>();
            _forms[form.id] = form;
            _formIds.push_back(form.id);
            if (IsLegendarySpecies(form.speciesId))
                _legendaryFormIds.push_back(form.id);
            else if (IsStarterSpecies(form.speciesId))
                _starterFormIds.push_back(form.id);
            else
                _normalFormIds.push_back(form.id);
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT id, internal_name, name, type, move_category, power, accuracy, pp, priority, "
            "function_code, flags, effect_chance FROM battlemon_moves"))
    {
        do
        {
            Field* f = result->Fetch();
            BattlemonMoveDef m;
            m.id = f[0].Get<uint32>();
            m.internalName = f[1].Get<std::string>();
            m.name = f[2].Get<std::string>();
            m.type = f[3].Get<std::string>();
            m.category = f[4].Get<std::string>();
            m.power = f[5].IsNull() ? 0 : f[5].Get<int32>();
            m.accuracy = f[6].IsNull() ? 100 : f[6].Get<int32>();
            m.pp = f[7].IsNull() ? 5 : f[7].Get<int32>();
            m.priority = f[8].Get<int32>();
            m.functionCode = f[9].IsNull() ? "None" : f[9].Get<std::string>();
            m.flags = f[10].IsNull() ? "" : f[10].Get<std::string>();
            m.effectChance = f[11].IsNull() ? 0 : f[11].Get<int32>();
            _moves[m.internalName] = m;
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT species_id, level, move_internal_name FROM battlemon_species_moves ORDER BY species_id, id"))
    {
        do
        {
            Field* f = result->Fetch();
            BattlemonLearn l;
            uint32 sid = f[0].Get<uint32>();
            l.level = f[1].Get<uint32>();
            l.moveInternal = f[2].Get<std::string>();
            _learnsets[sid].push_back(l);
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT species_id, move_internal_name FROM battlemon_species_tutor_moves ORDER BY species_id, id"))
    {
        do
        {
            Field* f = result->Fetch();
            _tutorMoves[f[0].Get<uint32>()].push_back(f[1].Get<std::string>());
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT form_id, method, level, move_internal_name FROM battlemon_form_moves ORDER BY form_id, id"))
    {
        do
        {
            Field* f = result->Fetch();
            BattlemonFormMoves& fm = _formMoves[f[0].Get<uint32>()];
            if (f[1].Get<std::string>() == "tutor")
                fm.tutor.push_back(f[3].Get<std::string>());
            else
            {
                BattlemonLearn l;
                l.level = f[2].Get<uint32>();
                l.moveInternal = f[3].Get<std::string>();
                fm.levelUp.push_back(l);
            }
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT internal_name, name, battle_use, heal_amount FROM battlemon_items"))
    {
        do
        {
            Field* f = result->Fetch();
            BattlemonItemDef item;
            item.internalName = f[0].Get<std::string>();
            item.name = f[1].Get<std::string>();
            item.battleUse = f[2].IsNull() ? "" : f[2].Get<std::string>();
            item.healAmount = f[3].IsNull() ? "" : f[3].Get<std::string>();
            _items[item.internalName] = item;
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT item_internal_name, cost, sort_order FROM battlemon_shop ORDER BY sort_order, item_internal_name"))
    {
        do
        {
            Field* f = result->Fetch();
            BattlemonShopEntry entry;
            entry.itemInternal = f[0].Get<std::string>();
            entry.cost = f[1].Get<uint32>();
            entry.sortOrder = f[2].Get<uint32>();
            if (_items.count(entry.itemInternal))
                _shop.push_back(entry);
        } while (result->NextRow());
    }

    if (QueryResult result = WorldDatabase.Query(
            "SELECT attacker, defender, multiplier FROM battlemon_type_chart"))
    {
        do
        {
            Field* f = result->Fetch();
            _typeChart[f[0].Get<std::string>()][f[1].Get<std::string>()] = f[2].Get<float>();
        } while (result->NextRow());
    }

    BattlemonForm const* starter = GetStarterForm();
    _starterFormId = starter ? starter->id : 0;

    LOG_INFO("module", "Battlemon: catalog {} species, {} forms ({} legendary, {} starter, {} normal), {} moves",
             _species.size(), _forms.size(), _legendaryFormIds.size(), _starterFormIds.size(),
             _normalFormIds.size(), _moves.size());
}

bool BattlemonMgr::ShouldHandle(Player* player) const
{
    if (!_enabled || !player || !player->GetSession())
        return false;
    if (player->GetSession()->IsBot() && !_grantToBots)
        return false;
    return true;
}

BattlemonSpecies const* BattlemonMgr::GetSpecies(uint32 id) const
{
    auto it = _species.find(id);
    return it == _species.end() ? nullptr : &it->second;
}

BattlemonForm const* BattlemonMgr::GetForm(uint32 id) const
{
    auto it = _forms.find(id);
    return it == _forms.end() ? nullptr : &it->second;
}

BattlemonForm const* BattlemonMgr::GetStarterForm() const
{
    BattlemonForm const* fallback = nullptr;
    for (auto const& pair : _forms)
    {
        if (pair.second.speciesId != _starterSpecies)
            continue;
        if (!fallback)
            fallback = &pair.second;
        if (pair.second.variant.empty())
            return &pair.second;
    }
    return fallback;
}

BattlemonMoveDef const* BattlemonMgr::GetMove(std::string const& internal) const
{
    auto it = _moves.find(internal);
    return it == _moves.end() ? nullptr : &it->second;
}

BattlemonForm const* BattlemonMgr::RandomForm() const
{
    if (_formIds.empty())
        return GetStarterForm();

    uint32 const legendaryW = _legendaryFormIds.empty() ? 0 : _weightLegendary;
    uint32 const starterW = _starterFormIds.empty() ? 0 : _weightStarter;
    uint32 const normalW = _normalFormIds.empty() ? 0 : _weightNormal;
    uint32 const total = legendaryW + starterW + normalW;
    if (total == 0)
        return GetForm(_formIds[urand(0, static_cast<uint32>(_formIds.size() - 1))]);

    uint32 const roll = urand(1, total);
    BattlemonForm const* picked = nullptr;
    if (roll <= legendaryW)
        picked = PickForm(_legendaryFormIds, _forms);
    else if (roll <= legendaryW + starterW)
        picked = PickForm(_starterFormIds, _forms);
    else
        picked = PickForm(_normalFormIds, _forms);

    if (!picked)
        picked = PickForm(_normalFormIds, _forms);
    if (!picked)
        picked = GetForm(_formIds[urand(0, static_cast<uint32>(_formIds.size() - 1))]);
    return picked;
}

BattlemonForm const* BattlemonMgr::PickWildForm() const
{
    return RandomForm();
}

bool BattlemonMgr::RollSpawnShiny() const
{
    if (!_shinyEvery)
        return false;
    return urand(1, _shinyEvery) == 1;
}

uint32 BattlemonMgr::CalcHP(uint32 base, uint32 level)
{
    return static_cast<uint32>(((2 * base + 31) * level / 100) + level + 10);
}

uint32 BattlemonMgr::CalcStat(uint32 base, uint32 level)
{
    return static_cast<uint32>(((2 * base + 31) * level / 100) + 5);
}

uint32 BattlemonMgr::ExpAtLevel(std::string const& growth, uint32 level)
{
    if (level <= 1)
        return 0;
    if (level > 100)
        level = 100;
    uint64 n = level;
    uint64 n3 = n * n * n;
    if (growth == "Fast")
        return static_cast<uint32>(n3 * 4 / 5);
    if (growth == "Slow")
        return static_cast<uint32>(n3 * 5 / 4);
    if (growth == "Parabolic" || growth == "MediumSlow")
    {
        int64 v = static_cast<int64>(n3 * 6 / 5) - static_cast<int64>(15 * n * n) + static_cast<int64>(100 * n) - 140;
        return v < 0 ? 0 : static_cast<uint32>(v);
    }
    return static_cast<uint32>(n3);
}

uint32 BattlemonMgr::ScaledEnemyLevel(uint32 playerLevel) const
{
    int32 delta = 0;
    if (playerLevel >= 2)
        delta = static_cast<int32>(urand(0, 2)) - 1;
    int32 lv = static_cast<int32>(playerLevel) + delta;
    if (lv < 1)
        lv = 1;
    if (lv > 100)
        lv = 100;
    return static_cast<uint32>(lv);
}

uint32 BattlemonMgr::ExpYield(BattlemonBattler const& enemy) const
{
    uint32 base = enemy.species ? enemy.species->baseExp : 64;
    uint32 n = (base * enemy.level) / 7;
    return n < 1 ? 1 : n;
}

std::vector<uint32> BattlemonMgr::AddExp(BattlemonOwned& row, uint32 amount) const
{
    row.exp += amount;
    BattlemonSpecies const* s = GetSpecies(row.speciesId);
    std::string growth = s ? s->growthRate : "Medium";
    std::vector<uint32> gained;
    while (row.level < 100)
    {
        uint32 need = ExpAtLevel(growth, row.level + 1);
        if (row.exp >= need)
        {
            ++row.level;
            gained.push_back(row.level);
        }
        else
            break;
    }
    return gained;
}

char BattlemonMgr::RollGender(std::string const& ratio) const
{
    if (ratio == "AlwaysMale")
        return 'M';
    if (ratio == "AlwaysFemale")
        return 'F';
    if (ratio == "Genderless")
        return 'N';
    uint32 female = 50;
    if (ratio == "FemaleOneEighth")
        female = 13;
    else if (ratio == "Female25Percent")
        female = 25;
    else if (ratio == "Female75Percent")
        female = 75;
    else if (ratio == "FemaleSevenEighths")
        female = 87;
    return urand(1, 100) <= female ? 'F' : 'M';
}

std::vector<std::string> BattlemonMgr::PickMoves(uint32 speciesId, uint32 level) const
{
    auto it = _learnsets.find(speciesId);
    std::vector<std::string> order;
    if (it != _learnsets.end())
    {
        for (BattlemonLearn const& e : it->second)
            if (e.level <= level)
                order.push_back(e.moveInternal);
    }
    std::vector<std::string> picked;
    std::vector<std::string> used;
    for (auto r = order.rbegin(); r != order.rend(); ++r)
    {
        if (std::find(used.begin(), used.end(), *r) != used.end())
            continue;
        used.push_back(*r);
        picked.insert(picked.begin(), *r);
        if (picked.size() >= 4)
            break;
    }
    if (picked.empty())
        picked.push_back("TACKLE");
    return picked;
}

void BattlemonMgr::FillMoves(BattlemonBattler& b, std::vector<std::string> const& internals) const
{
    b.moves.clear();
    for (std::string const& name : internals)
    {
        BattlemonMoveDef const* def = GetMove(name);
        if (!def)
            continue;
        BattlemonSlot slot;
        slot.def = def;
        slot.maxPp = def->pp > 0 ? def->pp : 5;
        slot.pp = slot.maxPp;
        b.moves.push_back(slot);
        if (b.moves.size() >= 4)
            break;
    }
    if (b.moves.empty())
    {
        // A battler with no usable move leaves the FIGHT menu empty and the
        // battle unplayable, so fall back to anything the catalog has.
        BattlemonMoveDef const* def = GetMove("TACKLE");
        if (!def && !_moves.empty())
            def = &_moves.begin()->second;
        if (def)
        {
            BattlemonSlot slot;
            slot.def = def;
            slot.maxPp = def->pp > 0 ? def->pp : 5;
            slot.pp = slot.maxPp;
            b.moves.push_back(slot);
        }
    }
}

void BattlemonMgr::ApplyStats(BattlemonBattler& b) const
{
    if (!b.species)
        return;
    b.maxHp = static_cast<int32>(CalcHP(b.species->hp, b.level));
    b.atk = CalcStat(b.species->atk, b.level);
    b.def = CalcStat(b.species->def, b.level);
    b.spa = CalcStat(b.species->spa, b.level);
    b.spd = CalcStat(b.species->spd, b.level);
    b.spe = CalcStat(b.species->spe, b.level);
    if (b.hp > b.maxHp)
        b.hp = b.maxHp;
    if (b.hp < 0)
        b.hp = 0;
}

BattlemonBattler BattlemonMgr::MakeBattler(BattlemonOwned const& row) const
{
    BattlemonBattler b;
    b.ownedId = row.id;
    b.formId = row.formId;
    b.speciesId = row.speciesId;
    b.species = GetSpecies(row.speciesId);
    b.form = GetForm(row.formId);
    b.name = b.form ? b.form->name : (b.species ? b.species->name : "???");
    b.sprite = !row.sprite.empty() ? row.sprite : (b.form ? b.form->sprite : "");
    b.backSprite = b.form ? b.form->backSprite : b.sprite;
    b.level = row.level;
    b.exp = row.exp;
    b.gender = row.gender;
    b.shiny = row.shiny;
    ApplyStats(b);
    b.hp = b.maxHp;
    std::vector<std::string> moves;
    for (int i = 0; i < 4; ++i)
        if (!row.move[i].empty())
            moves.push_back(row.move[i]);
    if (moves.empty())
        moves = PickMoves(row.speciesId, row.level);
    FillMoves(b, moves);
    BmInitBattler(b);
    return b;
}

BattlemonBattler BattlemonMgr::MakeWild(BattlemonForm const& form, uint32 level, bool shiny) const
{
    BattlemonOwned fake;
    fake.formId = form.id;
    fake.speciesId = form.speciesId;
    fake.sprite = form.sprite;
    fake.level = level;
    fake.exp = 0;
    fake.shiny = shiny;
    BattlemonSpecies const* s = GetSpecies(form.speciesId);
    fake.gender = RollGender(s ? s->genderRatio : "Female50Percent");
    BattlemonBattler b = MakeBattler(fake);
    b.ownedId = 0;
    FillMoves(b, PickMoves(form.speciesId, level));
    return b;
}

uint32 BattlemonMgr::MaxHpFor(BattlemonOwned const& row) const
{
    BattlemonSpecies const* sp = GetSpecies(row.speciesId);
    if (!sp)
        return 1;
    uint32 hp = CalcHP(sp->hp, row.level);
    return hp ? hp : 1;
}

// A fainted Pokemon comes round on its own after Battlemon.FaintReviveHours, at
// half health. Every read path calls this, so the timer runs without a
// background task and the player never has to relog to collect it.
void BattlemonMgr::ReviveIfDue(BattlemonOwned& row) const
{
    if (!row.id || row.hp > 0 || !row.faintedAt || !_faintReviveHours)
        return;
    if (NowSeconds() < row.faintedAt + _faintReviveHours * 3600)
        return;
    row.hp = std::max<uint32>(1u, MaxHpFor(row) / 2);
    row.faintedAt = 0;
    CharacterDatabase.Execute(
        "UPDATE battlemon_owned SET hp = {}, fainted_at = 0 WHERE id = {}", row.hp, row.id);
}

uint32 BattlemonMgr::ReviveSecondsLeft(BattlemonOwned const& row) const
{
    if (row.hp > 0 || !row.faintedAt || !_faintReviveHours)
        return 0;
    uint32 const due = row.faintedAt + _faintReviveHours * 3600;
    uint32 const now = NowSeconds();
    return now >= due ? 0 : due - now;
}

void BattlemonMgr::PersistBattler(BattlemonBattler const& b)
{
    if (!b.ownedId)
        return;
    uint32 const hp = b.hp < 0 ? 0 : static_cast<uint32>(b.hp);
    // Stamp the faint time on the way down and clear it on the way back up, but
    // never restart a clock that is already running: healing to 0 twice would
    // otherwise keep a Pokemon down forever.
    CharacterDatabase.Execute(
        "UPDATE battlemon_owned SET level = {}, exp = {}, gender = {}, hp = {}, "
        "fainted_at = IF({} = 0, IF(fainted_at = 0, {}, fainted_at), 0), "
        "move1 = {}, move2 = {}, move3 = {}, move4 = {} WHERE id = {}",
        b.level, b.exp, SqlQuote(std::string(1, b.gender)), hp,
        hp, NowSeconds(),
        SqlQuote(MoveName(b, 0)), SqlQuote(MoveName(b, 1)), SqlQuote(MoveName(b, 2)),
        SqlQuote(MoveName(b, 3)), b.ownedId);
}

// Battle end. Only fainting carries over, so a survivor is banked at full
// health rather than at whatever it limped out with.
void BattlemonMgr::PersistParty(BattlemonEncounter& enc)
{
    for (BattlemonBattler& b : enc.party)
    {
        if (!b.ownedId)
            continue;
        if (!b.fainted && b.hp > 0)
            b.hp = b.maxHp;
        PersistBattler(b);
    }
}

uint32 BattlemonMgr::InsertOwned(BattlemonOwned const& row)
{
    CharacterDatabase.DirectExecute(
        "INSERT INTO battlemon_owned "
        "(guid, form_id, species_id, sprite, level, exp, gender, hp, shiny, move1, move2, move3, move4) "
        "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})",
        row.guid, row.formId, row.speciesId, SqlQuote(row.sprite), row.level, row.exp,
        SqlQuote(std::string(1, row.gender)), row.hp, row.shiny ? 1 : 0,
        SqlQuote(row.move[0]), SqlQuote(row.move[1]), SqlQuote(row.move[2]), SqlQuote(row.move[3]));
    // Duplicates of the same form are allowed, so (guid, form_id) no longer
    // identifies a single row; take the newest, which is the one just inserted.
    // LAST_INSERT_ID() is not usable here: the pool may hand out a different
    // connection than the one that ran the INSERT.
    if (QueryResult result = CharacterDatabase.Query(
            "SELECT MAX(id) FROM battlemon_owned WHERE guid = {} AND form_id = {}", row.guid, row.formId))
    {
        Field* f = result->Fetch();
        if (!f[0].IsNull())
            return f[0].Get<uint32>();
    }
    return 0;
}

void BattlemonMgr::SaveAccount(BattlemonAccount const& acc)
{
    // pokeballs is retired in favour of battlemon_bag, but REPLACE INTO would reset
    // an omitted column to its DEFAULT of 10, which the bag migration would then
    // fold back in as free balls. Write it as a literal 0 to keep it consumed.
    CharacterDatabase.Execute(
        "REPLACE INTO battlemon_account "
        "(guid, next_encounter_at, pokeballs, points, balls_granted_day, encounter_count) "
        "VALUES ({}, {}, 0, {}, {}, {})",
        acc.guid, acc.nextEncounterAt, acc.points, acc.ballsGrantedDay,
        acc.encounterCount);
}

uint32 BattlemonMgr::TodayYYYYMMDD() const
{
    std::tm local = Acore::Time::TimeBreakdown(static_cast<time_t>(NowSeconds()));
    return uint32((local.tm_year + 1900) * 10000 + (local.tm_mon + 1) * 100 + local.tm_mday);
}

BattlemonItemDef const* BattlemonMgr::GetItem(std::string const& internal) const
{
    auto it = _items.find(internal);
    return it == _items.end() ? nullptr : &it->second;
}

BattlemonShopEntry const* BattlemonMgr::GetShopEntry(std::string const& internal) const
{
    for (BattlemonShopEntry const& e : _shop)
        if (e.itemInternal == internal)
            return &e;
    return nullptr;
}

uint32 BattlemonMgr::BagCount(uint32 guid, std::string const& item) const
{
    QueryResult result = CharacterDatabase.Query(
        "SELECT count FROM battlemon_bag WHERE guid = {} AND item_internal_name = {}",
        guid, SqlQuote(item));
    if (!result)
        return 0;
    return result->Fetch()[0].Get<uint32>();
}

void BattlemonMgr::BagAdd(uint32 guid, std::string const& item, uint32 count)
{
    if (!count)
        return;
    CharacterDatabase.DirectExecute(
        "INSERT INTO battlemon_bag (guid, item_internal_name, count) VALUES ({}, {}, LEAST({}, {})) "
        "ON DUPLICATE KEY UPDATE count = LEAST({}, count + {})",
        guid, SqlQuote(item), _bagMaxStack, count, _bagMaxStack, count);
}

bool BattlemonMgr::BagTake(uint32 guid, std::string const& item, uint32 count)
{
    if (!count)
        return true;
    if (BagCount(guid, item) < count)
        return false;
    CharacterDatabase.DirectExecute(
        "UPDATE battlemon_bag SET count = count - {} WHERE guid = {} AND item_internal_name = {} AND count >= {}",
        count, guid, SqlQuote(item), count);
    CharacterDatabase.DirectExecute(
        "DELETE FROM battlemon_bag WHERE guid = {} AND item_internal_name = {} AND count = 0",
        guid, SqlQuote(item));
    return true;
}

void BattlemonMgr::SendBag(Player* player, uint32 guid)
{
    // Chunk 0 tells the client to clear first, so an empty bag still needs one
    // packet or stale stacks would linger after the last item is spent.
    std::string const header = "BM\tBAG";
    uint32 seq = 0;
    std::string chunk = header + "\t0";
    if (QueryResult result = CharacterDatabase.Query(
            "SELECT item_internal_name, count FROM battlemon_bag WHERE guid = {} AND count > 0 "
            "ORDER BY item_internal_name", guid))
    {
        do
        {
            Field* f = result->Fetch();
            std::string next = "\t" + f[0].Get<std::string>() + ":" + std::to_string(f[1].Get<uint32>());
            if (chunk.size() + next.size() > 230)
            {
                SendAddon(player, chunk);
                chunk = header + "\t" + std::to_string(++seq);
            }
            chunk += next;
        } while (result->NextRow());
    }
    SendAddon(player, chunk);
    SendAddon(player, "BM\tBALLS\t" + std::to_string(BagCount(guid, "POKEBALL")));
}

void BattlemonMgr::GrantDailyBalls(BattlemonAccount& acc)
{
    if (!_dailyBalls)
        return;
    uint32 const today = TodayYYYYMMDD();
    if (acc.ballsGrantedDay == today)
        return;
    BagAdd(acc.guid, "POKEBALL", _dailyBalls);
    acc.ballsGrantedDay = today;
    SaveAccount(acc);
}

void BattlemonMgr::GrantStarter(uint32 guid)
{
    BattlemonForm const* form = GetStarterForm();
    if (!form)
    {
        LOG_ERROR("module", "Battlemon: cannot grant starter; world catalog has no form for species {}",
                  _starterSpecies);
        return;
    }
    BattlemonOwned row;
    row.guid = guid;
    row.formId = form->id;
    row.speciesId = form->speciesId;
    row.sprite = form->sprite;
    row.level = _starterLevel;
    row.exp = 0;
    BattlemonSpecies const* s = GetSpecies(form->speciesId);
    row.gender = RollGender(s ? s->genderRatio : "Female50Percent");
    std::vector<std::string> moves = PickMoves(row.speciesId, row.level);
    for (size_t i = 0; i < 4 && i < moves.size(); ++i)
        row.move[i] = moves[i];
    row.hp = CalcHP(s ? s->hp : 35, row.level);
    uint32 ownedId = InsertOwned(row);
    if (ownedId)
        CharacterDatabase.DirectExecute(
            "REPLACE INTO battlemon_party (guid, slot, owned_id) VALUES ({}, 1, {})", guid, ownedId);
}

BattlemonAccount BattlemonMgr::EnsureAccount(uint32 guid)
{
    BattlemonAccount acc;
    acc.guid = guid;
    if (QueryResult result = CharacterDatabase.Query(
            "SELECT next_encounter_at, points, balls_granted_day, encounter_count "
            "FROM battlemon_account WHERE guid = {}",
            acc.guid))
    {
        Field* f = result->Fetch();
        acc.nextEncounterAt = f[0].Get<uint32>();
        acc.points = f[1].Get<uint32>();
        acc.ballsGrantedDay = f[2].Get<uint32>();
        acc.encounterCount = f[3].Get<uint32>();
    }
    else
    {
        acc.nextEncounterAt = 0;
        acc.points = 0;
        acc.ballsGrantedDay = 0;
        acc.encounterCount = 0;
        SaveAccount(acc);
    }

    GrantDailyBalls(acc);

    QueryResult owned = CharacterDatabase.Query(
        "SELECT id FROM battlemon_owned WHERE guid = {} LIMIT 1", acc.guid);
    if (!owned)
        GrantStarter(acc.guid);
    return acc;
}

BattlemonAccount BattlemonMgr::EnsureAccount(Player* player)
{
    return EnsureAccount(SessionLowGuid(player));
}

std::vector<BattlemonOwned> BattlemonMgr::LoadOwned(uint32 guid) const
{
    std::vector<BattlemonOwned> out;
    QueryResult result = CharacterDatabase.Query(
        "SELECT id, form_id, species_id, sprite, level, exp, gender, hp, shiny, "
        "move1, move2, move3, move4, fainted_at "
        "FROM battlemon_owned WHERE guid = {} ORDER BY id", guid);
    if (!result)
        return out;
    do
    {
        Field* f = result->Fetch();
        BattlemonOwned row;
        row.guid = guid;
        row.id = f[0].Get<uint32>();
        row.formId = f[1].Get<uint32>();
        row.speciesId = f[2].Get<uint32>();
        row.sprite = f[3].Get<std::string>();
        row.level = f[4].Get<uint8>();
        row.exp = f[5].Get<uint32>();
        std::string g = f[6].Get<std::string>();
        row.gender = g.empty() ? 'M' : g[0];
        row.hp = f[7].Get<uint32>();
        row.shiny = f[8].Get<uint8>() != 0;
        row.move[0] = f[9].IsNull() ? "" : f[9].Get<std::string>();
        row.move[1] = f[10].IsNull() ? "" : f[10].Get<std::string>();
        row.move[2] = f[11].IsNull() ? "" : f[11].Get<std::string>();
        row.move[3] = f[12].IsNull() ? "" : f[12].Get<std::string>();
        row.faintedAt = f[13].Get<uint32>();
        ReviveIfDue(row);
        out.push_back(row);
    } while (result->NextRow());
    return out;
}

BattlemonOwned BattlemonMgr::LoadOwnedById(uint32 ownedId) const
{
    BattlemonOwned row;
    if (!ownedId)
        return row;
    QueryResult result = CharacterDatabase.Query(
        "SELECT id, guid, form_id, species_id, sprite, level, exp, gender, hp, shiny, "
        "move1, move2, move3, move4, fainted_at "
        "FROM battlemon_owned WHERE id = {}", ownedId);
    if (!result)
        return row;
    Field* f = result->Fetch();
    row.id = f[0].Get<uint32>();
    row.guid = f[1].Get<uint32>();
    row.formId = f[2].Get<uint32>();
    row.speciesId = f[3].Get<uint32>();
    row.sprite = f[4].Get<std::string>();
    row.level = f[5].Get<uint8>();
    row.exp = f[6].Get<uint32>();
    std::string g = f[7].Get<std::string>();
    row.gender = g.empty() ? 'M' : g[0];
    row.hp = f[8].Get<uint32>();
    row.shiny = f[9].Get<uint8>() != 0;
    row.move[0] = f[10].IsNull() ? "" : f[10].Get<std::string>();
    row.move[1] = f[11].IsNull() ? "" : f[11].Get<std::string>();
    row.move[2] = f[12].IsNull() ? "" : f[12].Get<std::string>();
    row.move[3] = f[13].IsNull() ? "" : f[13].Get<std::string>();
    row.faintedAt = f[14].Get<uint32>();
    ReviveIfDue(row);
    return row;
}

uint32 BattlemonMgr::PartyOwnedId(uint32 guid, uint8 slot) const
{
    QueryResult result = CharacterDatabase.Query(
        "SELECT owned_id FROM battlemon_party WHERE guid = {} AND slot = {}", guid, uint32(slot));
    if (!result)
        return 0;
    return result->Fetch()[0].Get<uint32>();
}

uint32 BattlemonMgr::PartyCount(uint32 guid) const
{
    QueryResult result = CharacterDatabase.Query(
        "SELECT COUNT(*) FROM battlemon_party WHERE guid = {}", guid);
    if (!result)
        return 0;
    return result->Fetch()[0].Get<uint32>();
}

std::unordered_set<std::string> BattlemonMgr::TaughtMoves(uint32 ownedId) const
{
    std::unordered_set<std::string> out;
    if (!ownedId)
        return out;
    if (QueryResult result = CharacterDatabase.Query(
            "SELECT move_internal_name FROM battlemon_owned_taught WHERE owned_id = {}", ownedId))
    {
        do
        {
            out.insert(result->Fetch()[0].Get<std::string>());
        } while (result->NextRow());
    }
    return out;
}

std::vector<BattlemonLegalMove> BattlemonMgr::LegalMoves(BattlemonOwned const& row) const
{
    std::vector<BattlemonLegalMove> out;
    std::unordered_set<std::string> seen;

    BattlemonFormMoves const* form = nullptr;
    if (auto it = _formMoves.find(row.formId); it != _formMoves.end())
        form = &it->second;

    // A form that defines its own pool replaces the species one for that
    // method: Alolan Raichu should not inherit Kantonian Raichu's list.
    std::vector<BattlemonLearn> const* levelUp = nullptr;
    if (form && !form->levelUp.empty())
        levelUp = &form->levelUp;
    else if (auto it = _learnsets.find(row.speciesId); it != _learnsets.end())
        levelUp = &it->second;

    if (levelUp)
    {
        for (BattlemonLearn const& l : *levelUp)
        {
            if (l.level > row.level || !GetMove(l.moveInternal))
                continue;
            if (!seen.insert(l.moveInternal).second)
                continue;
            BattlemonLegalMove m;
            m.moveInternal = l.moveInternal;
            m.level = l.level;
            out.push_back(m);
        }
    }

    std::unordered_set<std::string> equipped;
    for (int i = 0; i < 4; ++i)
        if (!row.move[i].empty())
            equipped.insert(row.move[i]);
    std::unordered_set<std::string> taught = TaughtMoves(row.id);

    std::vector<std::string> const* tutor = nullptr;
    if (form && !form->tutor.empty())
        tutor = &form->tutor;
    else if (auto it = _tutorMoves.find(row.speciesId); it != _tutorMoves.end())
        tutor = &it->second;

    if (tutor)
    {
        for (std::string const& name : *tutor)
        {
            if (!GetMove(name) || !seen.insert(name).second)
                continue;
            BattlemonLegalMove m;
            m.moveInternal = name;
            m.tutor = true;
            m.taught = taught.count(name) != 0 || equipped.count(name) != 0;
            out.push_back(m);
        }
    }

    // Whatever it knows right now stays legal even if the pool no longer lists
    // it, so a catalog change can never strand a Pokémon with an illegal set.
    for (std::string const& name : equipped)
    {
        if (!GetMove(name) || !seen.insert(name).second)
            continue;
        BattlemonLegalMove m;
        m.moveInternal = name;
        m.taught = true;
        out.push_back(m);
    }
    return out;
}

bool BattlemonMgr::OwnsForm(uint32 guid, uint32 formId, bool shiny) const
{
    QueryResult result = CharacterDatabase.Query(
        "SELECT id FROM battlemon_owned WHERE guid = {} AND form_id = {} AND shiny = {} LIMIT 1",
        guid, formId, shiny ? 1 : 0);
    return result != nullptr;
}

uint32 BattlemonMgr::SecondsUntilReady(BattlemonAccount const& acc) const
{
    uint32 now = NowSeconds();
    if (acc.nextEncounterAt <= now)
        return 0;
    return acc.nextEncounterAt - now;
}

void BattlemonMgr::ClearEncounter(ObjectGuid guid)
{
    ObjectGuid source;
    {
        std::lock_guard<std::mutex> g(_lock);
        auto it = _encounters.find(guid);
        if (it != _encounters.end())
            source = it->second.sourceCreature;
        _encounters.erase(guid);
    }
    if (Player* player = ObjectAccessor::FindPlayer(guid))
        UnlockSource(player, source);
}

void BattlemonMgr::ResetPlayer(Player* player)
{
    uint32 guid = SessionLowGuid(player);
    CharacterDatabase.DirectExecute("DELETE FROM battlemon_party WHERE guid = {}", guid);
    CharacterDatabase.DirectExecute("DELETE FROM battlemon_owned WHERE guid = {}", guid);
    CharacterDatabase.DirectExecute("DELETE FROM battlemon_account WHERE guid = {}", guid);
    {
        std::lock_guard<std::mutex> g(_lock);
        _encounters.erase(SessionObjectGuid(player));
    }
    EnsureAccount(player);
}

BattlemonBattler* BattlemonMgr::ActiveBattler(BattlemonEncounter& enc)
{
    if (enc.party.size() < 6)
        enc.party.resize(6);
    uint8 idx = enc.activeSlot ? enc.activeSlot - 1 : 0;
    if (idx >= 6)
        idx = 0;
    return &enc.party[idx];
}

uint8 BattlemonMgr::FirstConsciousSlot(BattlemonEncounter const& enc, uint8 except) const
{
    for (uint8 i = 1; i <= 6; ++i)
    {
        if (i == except)
            continue;
        if (i > enc.party.size())
            break;
        BattlemonBattler const& b = enc.party[i - 1];
        if (b.ownedId && !b.fainted && b.hp > 0)
            return i;
    }
    return 0;
}

bool BattlemonMgr::AnyConscious(BattlemonEncounter const& enc) const
{
    return FirstConsciousSlot(enc, 0) != 0;
}

float BattlemonMgr::TypeMult(std::string const& atk, std::string const& def) const
{
    if (atk.empty() || def.empty())
        return 1.f;
    auto it = _typeChart.find(atk);
    if (it == _typeChart.end())
        return 1.f;
    auto jt = it->second.find(def);
    return jt == it->second.end() ? 1.f : jt->second;
}

float BattlemonMgr::Effectiveness(std::string const& atkType, BattlemonBattler const& def) const
{
    if (!def.species)
        return 1.f;
    float m = TypeMult(atkType, def.species->type1);
    if (!def.species->type2.empty())
        m *= TypeMult(atkType, def.species->type2);
    return m;
}

int32 BattlemonMgr::CalcDamage(BattlemonBattler const& atk, BattlemonBattler const& def,
                               BattlemonMoveDef const& move, bool& crit, float& eff) const
{
    crit = false;
    eff = 1.f;
    if (move.category == "Status" || move.power <= 0)
        return 0;
    uint32 attack = move.category == "Physical" ? atk.atk : atk.spa;
    uint32 defense = move.category == "Physical" ? def.def : def.spd;
    if (defense < 1)
        defense = 1;
    int32 dmg = static_cast<int32>(((((2 * atk.level / 5 + 2) * move.power * attack / defense) / 50) + 2));
    if (atk.species && (move.type == atk.species->type1 || move.type == atk.species->type2))
        dmg = dmg * 3 / 2;
    eff = Effectiveness(move.type, def);
    dmg = static_cast<int32>(dmg * eff);
    crit = urand(1, 16) == 1;
    if (crit)
        dmg = dmg * 3 / 2;
    dmg = dmg * static_cast<int32>(urand(85, 100)) / 100;
    if (dmg < 1 && eff > 0.f)
        dmg = 1;
    return dmg;
}

ObjectGuid BattlemonMgr::SessionObjectGuid(Player* player) const
{
    if (_currentSession)
        return _currentSession->playerGuid;
    return player ? player->GetGUID() : ObjectGuid::Empty;
}

uint32 BattlemonMgr::SessionLowGuid(Player* player) const
{
    if (_currentSession)
        return _currentSession->guid;
    return player ? player->GetGUID().GetCounter() : 0;
}

void BattlemonMgr::SendAddon(Player* player, std::string const& payload)
{
    if (_currentSession)
        _currentSession->outbox.push_back(payload);
    if (!player && _currentSession)
        player = _currentSession->player;
    if (!player || !player->GetSession())
        return;
    WorldPacket data;
    ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, payload.c_str(), LANG_ADDON,
                                 CHAT_TAG_NONE, SessionObjectGuid(player), player->GetName());
    player->SendDirectMessage(&data);
}

void BattlemonMgr::Msg(Player* player, std::string const& text)
{
    SendAddon(player, std::string("BM\tMSG\t") + text);
}

void BattlemonMgr::Msg(BattlemonSession& session, std::string const& text)
{
    SendAddon(session.player, std::string("BM\tMSG\t") + text);
}

void BattlemonMgr::SendCombatFx(Player* player, BattlemonEncounter& enc)
{
    BattlemonBattler* cur = ActiveBattler(enc);
    SendAddon(player, std::string("BM\tAIL\tP\t") + (cur ? BmStatusCode(cur->status) : ""));
    SendAddon(player, std::string("BM\tAIL\tE\t") + BmStatusCode(enc.enemy.status));
    SendAddon(player, std::string("BM\tWEATHER\t") + BmWeatherCode(enc.weather));
}

void BattlemonMgr::TryLearnMoves(BattlemonBattler& b, uint32 newLevel, Player* player)
{
    auto it = _learnsets.find(b.speciesId);
    if (it == _learnsets.end())
        return;
    for (BattlemonLearn const& entry : it->second)
    {
        if (entry.level != newLevel)
            continue;
        bool known = false;
        for (BattlemonSlot const& slot : b.moves)
        {
            if (slot.def && slot.def->internalName == entry.moveInternal)
            {
                known = true;
                break;
            }
        }
        if (known)
            continue;
        BattlemonMoveDef const* def = GetMove(entry.moveInternal);
        if (!def)
            continue;
        if (b.moves.size() >= 4)
        {
            SendAddon(player, std::string("BM\tMSG\t") + b.name + " can learn " + def->name
                                  + ", but knows four moves. Swap it in from the move manager.");
            continue;
        }
        BattlemonSlot slot;
        slot.def = def;
        slot.maxPp = def->pp > 0 ? def->pp : 5;
        slot.pp = slot.maxPp;
        b.moves.push_back(slot);
        SendAddon(player, std::string("BM\tMSG\t") + b.name + " learned " + def->name + "!");
    }
}

std::string BattlemonMgr::FormatState(BattlemonBattler const& b, char side) const
{
    std::ostringstream ss;
    ss << "BM\t" << side << '\t' << b.ownedId << '\t' << b.formId << '\t' << b.speciesId << '\t'
       << b.name << '\t' << b.level << '\t' << b.exp << '\t' << b.gender << '\t' << b.hp << '\t'
       << b.maxHp << '\t' << b.sprite << '\t' << b.backSprite << '\t' << uint32(b.partySlot)
       << '\t' << (b.shiny ? 1 : 0);
    for (BattlemonSlot const& m : b.moves)
    {
        if (!m.def)
            continue;
        ss << '\t' << m.def->internalName << '\t' << m.def->name << '\t' << m.pp << '\t' << m.maxPp;
    }
    return ss.str();
}

// The switch menu used to grey out slots using database HP, which is stale the
// moment anything goes down mid-fight. This is the battle's own view of the
// bench and it is the only thing that menu may be drawn from. One line per slot
// rather than one packed line, because six long form names overflow the 255
// byte addon message limit.
void BattlemonMgr::SendBattleParty(Player* player, BattlemonEncounter& enc)
{
    for (uint8 i = 1; i <= 6; ++i)
    {
        BattlemonBattler const& b = enc.party[i - 1];
        std::ostringstream ss;
        ss << "BM\tBPARTY\t" << uint32(i) << '\t' << b.ownedId << '\t'
           << (b.hp < 0 ? 0 : b.hp) << '\t' << b.maxHp << '\t' << b.level << '\t'
           << (b.shiny ? 1 : 0) << '\t' << (i == enc.activeSlot ? 1 : 0) << '\t' << b.name;
        SendAddon(player, ss.str());
    }
}

void BattlemonMgr::SendReady(Player* player, BattlemonAccount const& acc)
{
    uint32 wait = SecondsUntilReady(acc);
    SendAddon(player, std::string("BM\tREADY\t") + (wait == 0 ? "1" : "0") + "\t" + std::to_string(wait));
    SendAddon(player, "BM\tPOINTS\t" + std::to_string(acc.points));
    SendBag(player, acc.guid);
}

void BattlemonMgr::SendOwnedList(Player* player, uint32 guid)
{
    uint32 slots[6] = {};
    for (uint8 i = 1; i <= 6; ++i)
        slots[i - 1] = PartyOwnedId(guid, i);
    std::ostringstream ps;
    ps << "BM\tPARTYSLOTS";
    for (uint32 id : slots)
        ps << '\t' << id;
    SendAddon(player, ps.str());

    for (BattlemonOwned const& row : LoadOwned(guid))
    {
        std::ostringstream ss;
        ss << "BM\tOWNED\t" << row.id << '\t' << row.formId << '\t' << row.level << '\t'
           << row.exp << '\t' << row.gender << '\t' << row.hp;
        for (int i = 0; i < 4; ++i)
            ss << '\t' << row.move[i];
        // Name and sprite trail the moves so the addon can label the party
        // without depending on its own catalog copy.
        BattlemonForm const* form = GetForm(row.formId);
        std::string name = form ? form->name : "";
        std::string sprite = form ? form->sprite : row.sprite;
        if (name.empty())
        {
            BattlemonSpecies const* sp = GetSpecies(form ? form->speciesId : row.speciesId);
            if (sp)
                name = sp->name;
        }
        // Seconds until it comes round on its own, 0 when it is not fainted.
        // Trails everything else so older parsers keep working.
        ss << '\t' << name << '\t' << sprite << '\t' << (row.shiny ? 1 : 0)
           << '\t' << ReviveSecondsLeft(row);
        SendAddon(player, ss.str());
    }
}

void BattlemonMgr::SendDexOwned(Player* player, uint32 guid)
{
    // The two dex tabs are independent: owning a shiny does not light up the
    // normal entry, and vice versa.
    SendDexList(player, guid, false);
    SendDexList(player, guid, true);
}

void BattlemonMgr::SendDexList(Player* player, uint32 guid, bool shiny)
{
    QueryResult result = CharacterDatabase.Query(
        "SELECT DISTINCT form_id FROM battlemon_owned WHERE guid = {} AND shiny = {} ORDER BY form_id",
        guid, shiny ? 1 : 0);
    if (!result)
        return;
    std::string const header = shiny ? "BM\tDEXSHINY" : "BM\tDEXOWNED";
    std::string chunk = header;
    do
    {
        uint32 formId = result->Fetch()[0].Get<uint32>();
        std::string next = "\t" + std::to_string(formId);
        if (chunk.size() + next.size() > 230)
        {
            SendAddon(player, chunk);
            chunk = header;
        }
        chunk += next;
    } while (result->NextRow());
    if (chunk.size() > header.size())
        SendAddon(player, chunk);
}

void BattlemonMgr::SendShop(Player* player)
{
    std::string const header = "BM\tSHOP";
    uint32 seq = 0;
    std::string chunk = header + "\t0";
    for (BattlemonShopEntry const& e : _shop)
    {
        std::string next = "\t" + e.itemInternal + ":" + std::to_string(e.cost);
        if (chunk.size() + next.size() > 230)
        {
            SendAddon(player, chunk);
            chunk = header + "\t" + std::to_string(++seq);
        }
        chunk += next;
    }
    SendAddon(player, chunk);
}

void BattlemonMgr::Buy(Player* player, std::string const& item, uint32 qty)
{
    if (qty < 1)
        return;
    if (qty > 99)
        qty = 99;

    BattlemonShopEntry const* entry = GetShopEntry(item);
    if (!entry)
    {
        SendAddon(player, "BM\tMSG\tThat isn't for sale.");
        return;
    }
    BattlemonItemDef const* def = GetItem(item);
    BattlemonAccount acc = EnsureAccount(player);
    uint32 const cost = entry->cost * qty;
    if (cost > acc.points)
    {
        SendAddon(player, "BM\tMSG\tThat costs " + std::to_string(cost) + " points, you have "
                              + std::to_string(acc.points) + ".");
        return;
    }
    if (BagCount(acc.guid, item) + qty > _bagMaxStack)
    {
        SendAddon(player, "BM\tMSG\tYou can't carry more than "
                              + std::to_string(_bagMaxStack) + " of those.");
        return;
    }

    acc.points -= cost;
    SaveAccount(acc);
    BagAdd(acc.guid, item, qty);

    SendAddon(player, "BM\tMSG\tBought " + std::to_string(qty) + "x "
                          + (def ? def->name : item) + " for " + std::to_string(cost) + " points.");
    SendAddon(player, "BM\tPOINTS\t" + std::to_string(acc.points));
    SendBag(player, acc.guid);
}

void BattlemonMgr::SendLearnset(Player* player, uint32 ownedId)
{
    BattlemonOwned row = LoadOwnedById(ownedId);
    if (!row.id || row.guid != SessionLowGuid(player))
        return;

    SendAddon(player, "BM\tLEARN\t" + std::to_string(ownedId) + "\t" + std::to_string(_tutorMoveCost));

    // Same 230-byte chunking the dex uses; a full tutor pool is ~90 moves.
    std::string const header = "BM\tLEARNADD";
    std::string chunk = header;
    for (BattlemonLegalMove const& m : LegalMoves(row))
    {
        char src = !m.tutor ? 'L' : (m.taught ? 'P' : 'T');
        std::string next = "\t" + m.moveInternal + ":" + src + ":" + std::to_string(m.level);
        if (chunk.size() + next.size() > 230)
        {
            SendAddon(player, chunk);
            chunk = header;
        }
        chunk += next;
    }
    if (chunk.size() > header.size())
        SendAddon(player, chunk);
    SendAddon(player, "BM\tLEARNEND\t" + std::to_string(ownedId));
}

void BattlemonMgr::SetMoves(Player* player, uint32 ownedId, std::vector<std::string> const& moves)
{
    {
        std::lock_guard<std::mutex> g(_lock);
        auto it = _encounters.find(SessionObjectGuid(player));
        if (it != _encounters.end() && it->second.active)
        {
            SendAddon(player, "BM\tMSG\tYou can't change moves during a battle.");
            return;
        }
    }

    uint32 guid = SessionLowGuid(player);
    BattlemonAccount acc = EnsureAccount(player);
    BattlemonOwned row = LoadOwnedById(ownedId);
    if (!row.id || row.guid != guid)
    {
        SendAddon(player, "BM\tMSG\tThat Pokemon isn't yours.");
        return;
    }

    std::unordered_map<std::string, BattlemonLegalMove> pool;
    for (BattlemonLegalMove const& m : LegalMoves(row))
        pool[m.moveInternal] = m;

    std::string picked[4];
    std::unordered_set<std::string> seen;
    uint8 count = 0;
    std::vector<std::string> buying;
    for (std::string const& name : moves)
    {
        if (name.empty() || count >= 4)
            continue;
        auto it = pool.find(name);
        if (it == pool.end())
        {
            SendAddon(player, "BM\tMSG\tIt can't learn " + name + ".");
            return;
        }
        if (!seen.insert(name).second)
        {
            SendAddon(player, "BM\tMSG\tEach move can only be picked once.");
            return;
        }
        if (it->second.tutor && !it->second.taught)
            buying.push_back(name);
        picked[count++] = name;
    }
    if (!count)
    {
        SendAddon(player, "BM\tMSG\tIt needs at least one move.");
        return;
    }

    uint32 cost = uint32(buying.size()) * _tutorMoveCost;
    if (cost > acc.points)
    {
        SendAddon(player, "BM\tMSG\tYou need " + std::to_string(cost) + " Battlemon Points for that ("
                              + std::to_string(acc.points) + " available).");
        return;
    }

    // Charge once per Pokemon and move, so swapping a bought move out and back
    // in later costs nothing.
    for (std::string const& name : buying)
        CharacterDatabase.DirectExecute(
            "REPLACE INTO battlemon_owned_taught (owned_id, move_internal_name) VALUES ({}, {})",
            ownedId, SqlQuote(name));
    if (cost)
    {
        acc.points -= cost;
        SaveAccount(acc);
    }

    CharacterDatabase.DirectExecute(
        "UPDATE battlemon_owned SET move1 = {}, move2 = {}, move3 = {}, move4 = {} WHERE id = {}",
        SqlQuote(picked[0]), SqlQuote(picked[1]), SqlQuote(picked[2]), SqlQuote(picked[3]), ownedId);

    if (cost)
        SendAddon(player, "BM\tMSG\tMoves updated for " + std::to_string(cost) + " points.");
    else
        SendAddon(player, "BM\tMSG\tMoves updated.");
    SendAddon(player, "BM\tPOINTS\t" + std::to_string(acc.points));
    SendOwnedList(player, guid);
    SendLearnset(player, ownedId);
}

void BattlemonMgr::SendStatus(Player* player)
{
    BattlemonAccount acc = EnsureAccount(player);
    uint32 guid = acc.guid;
    SendAddon(player, "BM\tHELLO\tOK");
    SendReady(player, acc);
    SendOwnedList(player, guid);
    SendDexOwned(player, guid);

    std::lock_guard<std::mutex> g(_lock);
    auto it = _encounters.find(SessionObjectGuid(player));
    if (it != _encounters.end() && it->second.active)
    {
        BattlemonEncounter& enc = it->second;
        BattlemonBattler* cur = ActiveBattler(enc);
        SendAddon(player, "BM\tWILD");
        if (cur)
            SendAddon(player, FormatState(*cur, 'P'));
        SendAddon(player, FormatState(enc.enemy, 'E'));
        SendCombatFx(player, enc);
        if (enc.catchPending)
        {
            if (enc.catchAllowed)
                SendAddon(player, std::string("BM\tCATCH\t1\t") + std::to_string(uint32(enc.catchThrowsLeft))
                                      + "\t" + std::to_string(uint32(_catchThrows)));
            else
                SendAddon(player, "BM\tCATCH\t0");
        }
        return;
    }

    uint32 leadId = 0;
    for (uint8 i = 1; i <= 6 && !leadId; ++i)
        leadId = PartyOwnedId(guid, i);
    if (leadId)
    {
        BattlemonBattler b = MakeBattler(LoadOwnedById(leadId));
        b.partySlot = 1;
        SendAddon(player, FormatState(b, 'P'));
    }
}

void BattlemonMgr::BeginCooldown(uint32 guid)
{
    CharacterDatabase.Execute(
        "UPDATE battlemon_account SET next_encounter_at = {} WHERE guid = {}",
        NowSeconds() + _encounterCooldown, guid);
}

void BattlemonMgr::AwardAndPersist(Player* player, BattlemonEncounter& enc)
{
    BattlemonBattler* cur = ActiveBattler(enc);
    if (!cur || !cur->ownedId)
        return;
    BattlemonOwned row = LoadOwnedById(cur->ownedId);
    if (!row.id)
        return;
    uint32 gained = ExpYield(enc.enemy);
    auto levels = AddExp(row, gained);
    cur->exp = row.exp;
    cur->level = row.level;
    ApplyStats(*cur);
    SendAddon(player, std::string("BM\tMSG\t") + cur->name + " gained " + std::to_string(gained) + " EXP. Points!");
    for (uint32 lv : levels)
    {
        SendAddon(player, std::string("BM\tMSG\t") + cur->name + " grew to level " + std::to_string(lv) + "!");
        TryLearnMoves(*cur, lv, player);
    }
    PersistBattler(*cur);
}

void BattlemonMgr::AwardWinPoints(Player* player)
{
    if (!_winPoints)
        return;
    uint32 guid = SessionLowGuid(player);
    CharacterDatabase.DirectExecute(
        "UPDATE battlemon_account SET points = points + {} WHERE guid = {}", _winPoints, guid);
    uint32 total = 0;
    if (QueryResult result = CharacterDatabase.Query(
            "SELECT points FROM battlemon_account WHERE guid = {}", guid))
        total = result->Fetch()[0].Get<uint32>();
    SendAddon(player, "BM\tPOINTS\t" + std::to_string(total));
    SendAddon(player, std::string("BM\tMSG\tYou earned ") + std::to_string(_winPoints) + " Battlemon Points!");
}

void BattlemonMgr::AwardWinBalls(Player* player)
{
    if (!_winBalls)
        return;
    uint32 guid = SessionLowGuid(player);
    BagAdd(guid, "POKEBALL", _winBalls);
    SendBag(player, guid);
}

Creature* BattlemonMgr::FindSourceCreature(Player* player, ObjectGuid guid) const
{
    if (!player || guid.IsEmpty() || !player->GetMap())
        return nullptr;
    return player->GetMap()->GetCreature(guid);
}

void BattlemonMgr::DespawnSource(Player* player, BattlemonEncounter& enc)
{
    Creature* src = FindSourceCreature(player, enc.sourceCreature);
    enc.sourceCreature.Clear();
    if (!src)
        return;
    // World spawn comes back later and remorphs. Temp summons just vanish.
    src->DespawnOrUnsummon(0ms, Seconds(urand(90, 240)));
}

void BattlemonMgr::UnlockSource(Player* player, ObjectGuid guid)
{
    if (Creature* src = FindSourceCreature(player, guid))
        src->RemoveUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
}

void BattlemonMgr::FinishWin(Player* player, BattlemonEncounter& enc)
{
    AwardAndPersist(player, enc);
    PersistParty(enc);
    AwardWinPoints(player);
    AwardWinBalls(player);
    if (!enc.skipCooldown)
        BeginCooldown(SessionLowGuid(player));
    enc.active = false;
    enc.catchPending = false;
    enc.catchThrowsLeft = 0;
    enc.forcedSwitch = false;
    DespawnSource(player, enc);
    SendAddon(player, "BM\tEND\tWIN");
    SendReady(player, EnsureAccount(player));
}

void BattlemonMgr::FinishLose(Player* player, BattlemonEncounter& enc)
{
    PersistParty(enc);
    if (!enc.skipCooldown)
        BeginCooldown(SessionLowGuid(player));
    enc.active = false;
    enc.forcedSwitch = false;
    UnlockSource(player, enc.sourceCreature);
    enc.sourceCreature.Clear();
    SendAddon(player, "BM\tMSG\tAll your Pokémon have fainted. You blacked out!");
    SendAddon(player, "BM\tEND\tLOSE");
    SendReady(player, EnsureAccount(player));
}

void BattlemonMgr::StartWild(Player* player)
{
    StartWild(player, 0, false, false);
}

bool BattlemonMgr::HasActiveEncounter(Player* player)
{
    if (!player)
        return false;
    std::lock_guard<std::mutex> g(_lock);
    auto it = _encounters.find(SessionObjectGuid(player));
    return it != _encounters.end() && it->second.active;
}

void BattlemonMgr::StartWild(Player* player, uint32 formId, bool shiny, bool skipCooldown,
                             ObjectGuid sourceCreature)
{
    if (_forms.empty())
    {
        SendAddon(player, "BM\tMSG\tBattlemon catalog is empty. Import forms.csv into battlemon_forms.");
        return;
    }

    BattlemonForm const* form = formId ? GetForm(formId) : nullptr;
    if (formId && !form)
    {
        SendAddon(player, "BM\tMSG\tThat Battlemon is not in the catalog.");
        return;
    }

    BattlemonAccount acc = EnsureAccount(player);
    if (!skipCooldown)
    {
        uint32 wait = SecondsUntilReady(acc);
        if (wait > 0)
        {
            SendReady(player, acc);
            SendAddon(player, "BM\tMSG\tNo wild Battlemon yet. Check back in a few minutes.");
            return;
        }
    }

    uint32 guid = acc.guid;
    BattlemonEncounter enc;
    enc.party.resize(6);
    bool any = false;
    for (uint8 i = 1; i <= 6; ++i)
    {
        uint32 ownedId = PartyOwnedId(guid, i);
        if (!ownedId)
            continue;
        BattlemonOwned row = LoadOwnedById(ownedId);
        if (!row.id)
            continue;
        enc.party[i - 1] = MakeBattler(row);
        enc.party[i - 1].partySlot = i;
        // Only fainting carries between battles. A bruised Pokemon turns up
        // healthy; a fainted one turns up down and cannot be sent out.
        if (row.hp == 0)
        {
            enc.party[i - 1].hp = 0;
            enc.party[i - 1].fainted = true;
        }
        any = true;
    }
    if (!any)
    {
        SendAddon(player, "BM\tMSG\tYou have no party. Set a lead in the Party screen.");
        return;
    }

    enc.activeSlot = FirstConsciousSlot(enc, 0);
    if (!enc.activeSlot)
    {
        SendAddon(player, "BM\tMSG\tYour whole team has fainted. Use a Revive, or give them time to come round.");
        return;
    }
    BattlemonBattler* lead = ActiveBattler(enc);
    if (!form)
        form = RandomForm();
    if (!form || !lead)
        return;

    if (!skipCooldown)
    {
        // Every _shinyEvery-th addon encounter is a guaranteed shiny.
        ++acc.encounterCount;
        shiny = _shinyEvery > 0 && (acc.encounterCount % _shinyEvery) == 0;
        SaveAccount(acc);
    }

    enc.enemy = MakeWild(*form, ScaledEnemyLevel(lead->level), shiny);
    enc.active = true;
    enc.catchPending = false;
    enc.skipCooldown = skipCooldown;
    enc.sourceCreature = sourceCreature;
    enc.forcedSwitch = false;
    enc.weather = BmWeather::None;
    enc.weatherTurns = 0;
    {
        BmCtx ctx{ _currentSession, this, &enc, false };
        if (BattlemonBattler* p = ActiveBattler(enc))
        {
            BmOnSwitchIn(ctx, *p, enc.enemy);
            BmOnSwitchIn(ctx, enc.enemy, *p);
        }
    }
    {
        std::lock_guard<std::mutex> g(_lock);
        _encounters[SessionObjectGuid(player)] = enc;
    }
    if (Creature* src = FindSourceCreature(player, sourceCreature))
        src->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
    BattlemonBattler* shown = ActiveBattler(enc);
    SendAddon(player, "BM\tWILD");
    if (shown)
        SendAddon(player, FormatState(*shown, 'P'));
    SendAddon(player, FormatState(enc.enemy, 'E'));
    SendCombatFx(player, enc);
    SendBattleParty(player, enc);
    if (enc.enemy.shiny)
    {
        SendAddon(player, "BM\tMSG\tSomething is sparkling...");
        SendAddon(player, std::string("BM\tMSG\tA wild SHINY ") + enc.enemy.name + " appeared!");
    }
    else
        SendAddon(player, std::string("BM\tMSG\tA wild ") + enc.enemy.name + " appeared!");
}

void BattlemonMgr::RunAway(Player* player)
{
    bool wasActive = false;
    bool skipCooldown = false;
    ObjectGuid source;
    {
        std::lock_guard<std::mutex> g(_lock);
        auto it = _encounters.find(SessionObjectGuid(player));
        if (it != _encounters.end() && it->second.active)
        {
            wasActive = true;
            skipCooldown = it->second.skipCooldown;
            source = it->second.sourceCreature;
            PersistParty(it->second);
        }
        _encounters.erase(SessionObjectGuid(player));
    }
    UnlockSource(player, source);
    // Only a real escape from an addon Fight costs the encounter cooldown.
    if (wasActive)
    {
        if (!skipCooldown)
            BeginCooldown(SessionLowGuid(player));
        SendAddon(player, "BM\tMSG\tGot away safely!");
    }
    SendAddon(player, "BM\tEND\tRUN");
    if (wasActive)
        SendReady(player, EnsureAccount(player));
}

void BattlemonMgr::UseMove(Player* player, uint8 slotIndex)
{
    std::lock_guard<std::mutex> g(_lock);
    auto it = _encounters.find(SessionObjectGuid(player));
    if (it == _encounters.end() || !it->second.active || it->second.catchPending)
        return;
    BattlemonEncounter& enc = it->second;
    BattlemonBattler* cur = ActiveBattler(enc);
    if (!cur)
        return;
    // ActiveBattler hands back whatever sits in the slot, fainted or not. Without
    // this the turn runs as a no-op that still reprints the faint, which reads
    // like a real attack that missed.
    if (cur->fainted || cur->hp <= 0)
    {
        cur->fainted = true;
        if (!AnyConscious(enc))
        {
            FinishLose(player, enc);
            return;
        }
        enc.forcedSwitch = true;
        SendAddon(player, std::string("BM\tMSG\t") + cur->name + " can't fight. Choose another Pokémon!");
        SendBattleParty(player, enc);
        SendAddon(player, "BM\tSWITCHNEED");
        return;
    }

    BattlemonSlot* pSlot = nullptr;
    if (!cur->charging && !cur->mustRecharge)
    {
        if (slotIndex >= cur->moves.size() || !cur->moves[slotIndex].def)
            return;
        pSlot = &cur->moves[slotIndex];
        if (pSlot->pp <= 0)
        {
            SendAddon(player, "BM\tMSG\tThere's no PP left for this move!");
            return;
        }
    }

    BattlemonSlot* eSlot = PickEnemyMove(enc);

    auto movePri = [this](BattlemonBattler const& b, BattlemonSlot* slot) -> int32 {
        if (b.charging && !b.chargeMove.empty())
        {
            if (BattlemonMoveDef const* m = GetMove(b.chargeMove))
                return m->priority;
        }
        if (slot && slot->def)
            return slot->def->priority;
        return 0;
    };

    int32 pPri = movePri(*cur, pSlot);
    int32 ePri = movePri(enc.enemy, eSlot);
    uint32 pSpe = BmEffectiveSpeed(*cur, enc);
    uint32 eSpe = BmEffectiveSpeed(enc.enemy, enc);
    bool playerFirst = pPri > ePri || (pPri == ePri && (pSpe > eSpe || (pSpe == eSpe && urand(0, 1))));

    BmCtx ctx{ _currentSession, this, &enc, false };
    if (playerFirst)
    {
        BmRunSingleAction(ctx, *cur, enc.enemy, pSlot, true);
        if (!enc.enemy.fainted && !cur->fainted)
            BmRunSingleAction(ctx, enc.enemy, *cur, eSlot, false);
    }
    else
    {
        BmRunSingleAction(ctx, enc.enemy, *cur, eSlot, false);
        if (!enc.enemy.fainted && !cur->fainted)
            BmRunSingleAction(ctx, *cur, enc.enemy, pSlot, true);
    }

    if (!enc.enemy.fainted && !cur->fainted)
        BmEndOfRound(ctx, *cur, enc.enemy);

    FinishTurn(player, enc, *cur, ctx.uturn);
}

BattlemonSlot* BattlemonMgr::PickEnemyMove(BattlemonEncounter& enc) const
{
    if (enc.enemy.charging || enc.enemy.mustRecharge || enc.enemy.moves.empty())
        return nullptr;
    std::vector<uint8> usable;
    for (uint8 i = 0; i < enc.enemy.moves.size(); ++i)
        if (enc.enemy.moves[i].def && enc.enemy.moves[i].pp > 0)
            usable.push_back(i);
    if (!usable.empty())
        return &enc.enemy.moves[usable[urand(0, static_cast<uint32>(usable.size() - 1))]];
    if (enc.enemy.moves[0].def)
        return &enc.enemy.moves[0];
    return nullptr;
}

// Everything that happens after both sides have acted, shared by attacking and
// by spending the turn on an item.
void BattlemonMgr::FinishTurn(Player* player, BattlemonEncounter& enc, BattlemonBattler& cur, bool uturn)
{
    SendAddon(player, FormatState(cur, 'P'));
    SendAddon(player, FormatState(enc.enemy, 'E'));
    SendCombatFx(player, enc);
    SendBattleParty(player, enc);

    if (enc.enemy.fainted)
    {
        SendAddon(player, std::string("BM\tMSG\t") + enc.enemy.name + " fainted!");
        // Duplicates are allowed, so every faint offers a throw.
        enc.catchPending = true;
        enc.catchAllowed = true;
        enc.catchThrowsLeft = _catchThrows;
        SendAddon(player, std::string("BM\tCATCH\t1\t") + std::to_string(uint32(enc.catchThrowsLeft))
                              + "\t" + std::to_string(uint32(_catchThrows)));
        return;
    }
    // Anything that drove HP to zero counts, not just damage that set the flag,
    // or a Pokemon can sit on the field at 0 HP and the fight never resolves.
    if (cur.fainted || cur.hp <= 0)
    {
        cur.fainted = true;
        PersistBattler(cur);
        SendAddon(player, std::string("BM\tMSG\t") + cur.name + " fainted!");
        SendBattleParty(player, enc);
        uint8 next = FirstConsciousSlot(enc, enc.activeSlot);
        if (!next)
        {
            FinishLose(player, enc);
            return;
        }
        enc.forcedSwitch = true;
        SendAddon(player, "BM\tSWITCHNEED");
        return;
    }
    if (uturn && FirstConsciousSlot(enc, enc.activeSlot))
    {
        enc.forcedSwitch = true;
        SendAddon(player, "BM\tSWITCHNEED");
    }
}

void BattlemonMgr::UseItem(Player* player, std::string const& item, uint8 targetSlot)
{
    std::lock_guard<std::mutex> g(_lock);
    auto it = _encounters.find(SessionObjectGuid(player));
    if (it == _encounters.end() || !it->second.active || it->second.catchPending)
        return;
    BattlemonEncounter& enc = it->second;
    BattlemonBattler* cur = ActiveBattler(enc);
    if (!cur)
        return;

    // Nothing can be used while you still owe a switch: the turn that follows
    // would resolve against a battler that is not standing. Reviving the bench
    // has to wait until something conscious is out, exactly as switching does.
    if (cur->fainted || cur->hp <= 0)
    {
        cur->fainted = true;
        if (!AnyConscious(enc))
        {
            FinishLose(player, enc);
            return;
        }
        enc.forcedSwitch = true;
        SendAddon(player, std::string("BM\tMSG\t") + cur->name + " can't fight. Choose another Pokémon!");
        SendBattleParty(player, enc);
        SendAddon(player, "BM\tSWITCHNEED");
        return;
    }

    BattlemonItemDef const* def = GetItem(item);
    if (!def || def->battleUse != "OnPokemon")
    {
        SendAddon(player, "BM\tMSG\tYou can't use that here.");
        return;
    }

    // A revive names a bench slot; everything else works on whoever is out.
    bool const revive = IsReviveItem(item);
    BattlemonBattler* target = cur;
    if (targetSlot >= 1 && targetSlot <= 6 && enc.party[targetSlot - 1].ownedId)
        target = &enc.party[targetSlot - 1];
    else if (revive)
    {
        SendAddon(player, "BM\tMSG\tChoose a fainted Pokémon to revive.");
        return;
    }

    bool const targetDown = target->fainted || target->hp <= 0;
    if (revive != targetDown)
    {
        SendAddon(player, revive
            ? std::string("BM\tMSG\t") + target->name + " has not fainted."
            : std::string("BM\tMSG\t") + target->name + " has fainted. Use a Revive first.");
        return;
    }
    // Reviving is the one thing that may target the bench; a potion cannot heal
    // a Pokemon that is not on the field.
    if (!revive && target != cur)
    {
        SendAddon(player, "BM\tMSG\tOnly the Pokémon that is out can use that.");
        return;
    }

    int32 heal = 0;
    if (!def->healAmount.empty())
    {
        if (def->healAmount == "full")
            heal = target->maxHp;
        else if (def->healAmount == "half")
            heal = target->maxHp / 2;
        else
            heal = atoi(def->healAmount.c_str());
    }
    BmStatus const cures = CureFor(item);
    bool const curesAll = CuresEverything(item);
    bool const wouldCure = (curesAll || cures != BmStatus::None)
        && target->status != BmStatus::None
        && (curesAll || target->status == cures
            || (cures == BmStatus::PSN && target->status == BmStatus::TOX));

    if (heal <= 0 && !wouldCure)
    {
        // Refusing costs nothing; using it would burn the turn for no gain.
        if (curesAll || cures != BmStatus::None)
            SendAddon(player, "BM\tMSG\t" + target->name + " has nothing to cure.");
        else
            SendAddon(player, "BM\tMSG\tYou can't use that here.");
        return;
    }
    if (heal > 0 && !revive && target->hp >= target->maxHp && !wouldCure)
    {
        SendAddon(player, "BM\tMSG\t" + target->name + " is already at full health.");
        return;
    }

    uint32 guid = SessionLowGuid(player);
    if (!BagTake(guid, item, 1))
    {
        SendAddon(player, "BM\tMSG\tYou have no " + def->name + "s left!");
        return;
    }
    SendBag(player, guid);
    SendAddon(player, "BM\tMSG\tYou used a " + def->name + ".");

    if (revive)
    {
        target->fainted = false;
        target->status = BmStatus::None;
        target->statusTurns = 0;
        target->hp = std::max<int32>(1, std::min<int32>(target->maxHp, heal));
        PersistBattler(*target);
        SendAddon(player, std::string("BM\tMSG\t") + target->name + " was revived!");
    }
    else
    {
        if (heal > 0)
        {
            int32 const before = target->hp;
            target->hp = std::min<int32>(target->maxHp, target->hp + heal);
            SendAddon(player, std::string("BM\tMSG\t") + target->name + " recovered "
                                  + std::to_string(target->hp - before) + " HP!");
        }
        if (wouldCure)
        {
            target->status = BmStatus::None;
            target->statusTurns = 0;
            SendAddon(player, std::string("BM\tMSG\t") + target->name + " shook off its condition!");
        }
    }

    // Using an item is your action for the turn, so the foe still attacks.
    BmCtx ctx{ _currentSession, this, &enc, false };
    if (BattlemonSlot* eSlot = PickEnemyMove(enc))
        BmRunSingleAction(ctx, enc.enemy, *cur, eSlot, false);
    if (!enc.enemy.fainted && !cur->fainted)
        BmEndOfRound(ctx, *cur, enc.enemy);

    FinishTurn(player, enc, *cur, ctx.uturn);
}

// Out of battle a Pokemon is either healthy or fainted, so the only item that
// really does anything here is a revive. The rest are accepted and refused with
// a reason rather than silently ignored.
void BattlemonMgr::BagUse(Player* player, std::string const& item, uint32 ownedId)
{
    {
        std::lock_guard<std::mutex> g(_lock);
        auto it = _encounters.find(SessionObjectGuid(player));
        if (it != _encounters.end() && it->second.active)
        {
            SendAddon(player, "BM\tMSG\tUse the bag inside the battle menu during a fight.");
            return;
        }
    }

    uint32 guid = SessionLowGuid(player);
    EnsureAccount(player);

    BattlemonItemDef const* def = GetItem(item);
    if (!def)
    {
        SendAddon(player, "BM\tMSG\tYou can't use that.");
        return;
    }
    BattlemonOwned row = LoadOwnedById(ownedId);
    if (!row.id || row.guid != guid)
    {
        SendAddon(player, "BM\tMSG\tChoose one of your Pokémon.");
        return;
    }

    BattlemonForm const* form = GetForm(row.formId);
    std::string const name = form ? form->name : "Your Pokémon";
    uint32 const maxHp = MaxHpFor(row);

    if (IsReviveItem(item))
    {
        if (row.hp > 0)
        {
            SendAddon(player, "BM\tMSG\t" + name + " has not fainted.");
            return;
        }
        uint32 restored = maxHp;
        if (def->healAmount == "half")
            restored = std::max<uint32>(1u, maxHp / 2);
        if (!BagTake(guid, item, 1))
        {
            SendAddon(player, "BM\tMSG\tYou have no " + def->name + "s left!");
            return;
        }
        CharacterDatabase.Execute(
            "UPDATE battlemon_owned SET hp = {}, fainted_at = 0 WHERE id = {}", restored, row.id);
        SendBag(player, guid);
        SendOwnedList(player, guid);
        SendAddon(player, "BM\tMSG\tYou used a " + def->name + ". " + name + " was revived!");
        return;
    }

    if (row.hp == 0)
    {
        SendAddon(player, "BM\tMSG\t" + name + " has fainted. Only a Revive will help.");
        return;
    }
    // Damage does not carry between battles, so a healthy Pokemon is always at
    // full health out here and there is nothing for a potion or cure to fix.
    SendAddon(player, "BM\tMSG\t" + name + " is fit and ready. Save that for a battle.");
}

float BattlemonMgr::BallMultiplier(std::string const& ball) const
{
    if (ball == "GREATBALL")
        return _greatBallMult;
    if (ball == "ULTRABALL")
        return _ultraBallMult;
    return 1.f;
}

void BattlemonMgr::ThrowBall(Player* player, std::string const& ballArg)
{
    std::lock_guard<std::mutex> g(_lock);
    auto it = _encounters.find(SessionObjectGuid(player));
    if (it == _encounters.end() || !it->second.active || !it->second.catchPending)
        return;
    BattlemonEncounter& enc = it->second;
    if (!enc.catchThrowsLeft)
    {
        SendAddon(player, "BM\tMSG\tIt got away!");
        FinishWin(player, enc);
        return;
    }

    std::string ball = ballArg.empty() ? "POKEBALL" : ballArg;
    BattlemonItemDef const* def = GetItem(ball);
    if (!def || def->battleUse != "OnFoe")
    {
        SendAddon(player, "BM\tMSG\tYou can't throw that.");
        return;
    }

    BattlemonAccount acc = EnsureAccount(player);
    if (!BagTake(acc.guid, ball, 1))
    {
        // Out of this kind specifically; only end the encounter when every
        // throwable ball is gone, so picking an empty slot is recoverable.
        SendAddon(player, "BM\tMSG\tYou have no " + def->name + "s left!");
        if (!BagCount(acc.guid, "POKEBALL") && !BagCount(acc.guid, "GREATBALL")
            && !BagCount(acc.guid, "ULTRABALL") && !BagCount(acc.guid, "MASTERBALL"))
            FinishWin(player, enc);
        return;
    }
    --enc.catchThrowsLeft;
    SendBag(player, acc.guid);
    SendAddon(player, "BM\tMSG\tYou threw a " + def->name + "!");

    uint32 const odds = static_cast<uint32>(_catchChance * BallMultiplier(ball) * 1000.f);
    bool caught = ball == "MASTERBALL" || urand(1, 1000) <= odds;
    if (caught)
    {
        BattlemonOwned row;
        row.guid = SessionLowGuid(player);
        row.formId = enc.enemy.formId;
        row.speciesId = enc.enemy.speciesId;
        row.sprite = enc.enemy.sprite;
        row.level = enc.enemy.level;
        row.exp = 0;
        row.gender = enc.enemy.gender;
        row.hp = static_cast<uint32>(enc.enemy.maxHp);
        row.shiny = enc.enemy.shiny;
        for (int i = 0; i < 4; ++i)
            row.move[i] = MoveName(enc.enemy, i);
        uint32 ownedId = InsertOwned(row);
        if (ownedId)
        {
            uint8 empty = 0;
            for (uint8 s = 1; s <= 6 && !empty; ++s)
                if (!PartyOwnedId(row.guid, s))
                    empty = s;
            if (empty)
                CharacterDatabase.DirectExecute(
                    "REPLACE INTO battlemon_party (guid, slot, owned_id) VALUES ({}, {}, {})",
                    row.guid, uint32(empty), ownedId);
        }
        SendAddon(player, std::string("BM\tMSG\tGotcha! ")
                              + (enc.enemy.shiny ? "SHINY " : "") + enc.enemy.name + " was caught!");
        SendAddon(player, "BM\tDEX\t" + std::to_string(enc.enemy.formId) + "\t"
                              + (enc.enemy.shiny ? "1" : "0"));
        FinishWin(player, enc);
        return;
    }

    SendAddon(player, std::string("BM\tMSG\tOh no! The wild ") + enc.enemy.name + " broke free!");
    if (!enc.catchThrowsLeft)
    {
        SendAddon(player, "BM\tMSG\tIt got away!");
        FinishWin(player, enc);
        return;
    }
    if (!BagCount(acc.guid, "POKEBALL") && !BagCount(acc.guid, "GREATBALL")
        && !BagCount(acc.guid, "ULTRABALL") && !BagCount(acc.guid, "MASTERBALL"))
    {
        SendAddon(player, "BM\tMSG\tYou have no balls left!");
        FinishWin(player, enc);
        return;
    }
    SendAddon(player, std::string("BM\tCATCH\t1\t") + std::to_string(uint32(enc.catchThrowsLeft))
                          + "\t" + std::to_string(uint32(_catchThrows)));
}

void BattlemonMgr::SkipCatch(Player* player)
{
    std::lock_guard<std::mutex> g(_lock);
    auto it = _encounters.find(SessionObjectGuid(player));
    if (it == _encounters.end() || !it->second.active || !it->second.catchPending)
        return;
    FinishWin(player, it->second);
}

void BattlemonMgr::SwitchParty(Player* player, uint8 slot)
{
    std::lock_guard<std::mutex> g(_lock);
    auto it = _encounters.find(SessionObjectGuid(player));
    if (it == _encounters.end() || !it->second.active || it->second.catchPending)
        return;
    if (slot < 1 || slot > 6)
        return;
    BattlemonEncounter& enc = it->second;
    BattlemonBattler& next = enc.party[slot - 1];
    if (!next.ownedId || next.fainted || next.hp <= 0)
    {
        // With nothing left to send out the fight is over. Saying so beats
        // leaving the player in a switch prompt that has no legal answer.
        if (!AnyConscious(enc))
        {
            FinishLose(player, enc);
            return;
        }
        SendAddon(player, "BM\tMSG\tThere's no fighting-fit Pokémon in that slot!");
        SendBattleParty(player, enc);
        return;
    }
    if (slot == enc.activeSlot)
        return;

    bool const free = enc.forcedSwitch;
    enc.forcedSwitch = false;
    BattlemonBattler* cur = ActiveBattler(enc);
    if (cur)
    {
        BmOnSwitchOut(*cur);
        PersistBattler(*cur);
    }
    enc.activeSlot = slot;
    BmCtx ctx{ _currentSession, this, &enc, false };
    BmOnSwitchIn(ctx, next, enc.enemy);
    SendAddon(player, std::string("BM\tMSG\tGo! ") + next.name + "!");

    if (free)
    {
        // Replacing a Pokemon that just fainted, or the free swap a U-turn
        // grants: no turn passes and the foe does not get to attack.
        SendAddon(player, FormatState(next, 'P'));
        SendAddon(player, FormatState(enc.enemy, 'E'));
        SendCombatFx(player, enc);
        SendBattleParty(player, enc);
        return;
    }

    // Switching by choice is your action for the turn, so the foe attacks.
    if (BattlemonSlot* eSlot = PickEnemyMove(enc))
        BmRunSingleAction(ctx, enc.enemy, next, eSlot, false);
    if (!enc.enemy.fainted && !next.fainted)
        BmEndOfRound(ctx, next, enc.enemy);
    FinishTurn(player, enc, next, ctx.uturn);
}

void BattlemonMgr::SetParty(Player* player, uint32 ownedIds[6])
{
    {
        std::lock_guard<std::mutex> g(_lock);
        auto it = _encounters.find(SessionObjectGuid(player));
        if (it != _encounters.end() && it->second.active)
        {
            SendAddon(player, "BM\tMSG\tYou can't change your party during a battle.");
            return;
        }
    }
    uint32 guid = SessionLowGuid(player);
    EnsureAccount(player);
    std::unordered_set<uint32> used;
    if (!ownedIds[0])
    {
        SendAddon(player, "BM\tMSG\tSlot 1 (lead) cannot be empty.");
        return;
    }
    for (uint8 i = 0; i < 6; ++i)
    {
        uint32 id = ownedIds[i];
        if (!id)
            continue;
        if (!used.insert(id).second)
        {
            SendAddon(player, "BM\tMSG\tEach party member must be unique.");
            return;
        }
        BattlemonOwned row = LoadOwnedById(id);
        if (!row.id || row.guid != guid)
        {
            SendAddon(player, "BM\tMSG\tInvalid party member.");
            return;
        }
    }
    CharacterDatabase.DirectExecute("DELETE FROM battlemon_party WHERE guid = {}", guid);
    for (uint8 i = 0; i < 6; ++i)
        if (ownedIds[i])
            CharacterDatabase.DirectExecute(
                "INSERT INTO battlemon_party (guid, slot, owned_id) VALUES ({}, {}, {})",
                guid, uint32(i + 1), ownedIds[i]);
    SendAddon(player, "BM\tMSG\tParty updated.");
    SendOwnedList(player, guid);
}

void BattlemonMgr::HandleAddon(Player* player, std::string const& msg)
{
    if (!ShouldHandle(player))
        return;
    if (sBattlemonSidecar->HasLease(SessionLowGuid(player)))
    {
        SendAddon(player, "BM\tMSG\tBattlemon is open in Pocketmon.");
        return;
    }
    BattlemonSession session;
    session.guid = SessionLowGuid(player);
    session.playerGuid = SessionObjectGuid(player);
    session.player = player;
    HandleCommand(session, msg);
}

void BattlemonMgr::HandleCommand(BattlemonSession& session, std::string const& msg)
{
    if (!_enabled)
        return;
    if (msg.size() < 3 || msg.compare(0, 3, "BM\t") != 0)
        return;

    if (!session.playerGuid)
        session.playerGuid = ObjectGuid::Create<HighGuid::Player>(session.guid);

    Player* player = session.player;
    _currentSession = &session;
    session.outbox.clear();

    struct SessionGuard
    {
        BattlemonMgr* mgr;
        BattlemonSession* session;
        ~SessionGuard()
        {
            mgr->_currentSession = nullptr;
            session->outbox.push_back("BM\tSYNC\tEND");
        }
    } guard{ this, &session };

    std::string rest = msg.substr(3);
    std::string cmd;
    std::string arg;
    auto tab = rest.find('\t');
    if (tab == std::string::npos)
        cmd = rest;
    else
    {
        cmd = rest.substr(0, tab);
        arg = rest.substr(tab + 1);
    }

    if (cmd == "HELLO" || cmd == "STATUS")
    {
        SendStatus(player);
        return;
    }
    if (cmd == "WILD")
    {
        uint32 formId = 0;
        bool shiny = false;
        if (!arg.empty())
        {
            auto parts = Split(arg, '\t');
            if (!parts.empty())
                formId = static_cast<uint32>(atoi(parts[0].c_str()));
            if (parts.size() > 1)
                shiny = atoi(parts[1].c_str()) != 0;
        }
        if (formId)
            StartWild(player, formId, shiny, true);
        else
            StartWild(player);
        return;
    }
    if (cmd == "RUN")
    {
        RunAway(player);
        return;
    }
    if (cmd == "MOVE")
    {
        uint8 slot = static_cast<uint8>(atoi(arg.c_str()));
        if (slot > 0)
            --slot;
        UseMove(player, slot);
        return;
    }
    if (cmd == "BALL")
    {
        ThrowBall(player, arg);
        return;
    }
    if (cmd == "USEITEM")
    {
        // "ITEM" or "ITEM,slot" - the slot is only meaningful for a revive.
        auto parts = Split(arg, ',');
        if (parts.empty() || parts[0].empty())
            return;
        uint8 slot = parts.size() > 1 ? static_cast<uint8>(atoi(parts[1].c_str())) : 0;
        UseItem(player, parts[0], slot);
        return;
    }
    if (cmd == "BAGUSE")
    {
        auto parts = Split(arg, ',');
        if (parts.size() < 2 || parts[0].empty())
            return;
        BagUse(player, parts[0], static_cast<uint32>(atoi(parts[1].c_str())));
        return;
    }
    if (cmd == "SHOP")
    {
        EnsureAccount(player);
        SendShop(player);
        SendBag(player, SessionLowGuid(player));
        return;
    }
    if (cmd == "BUY")
    {
        auto parts = Split(arg, ',');
        if (parts.empty())
            return;
        uint32 qty = parts.size() > 1 ? static_cast<uint32>(atoi(parts[1].c_str())) : 1;
        Buy(player, parts[0], qty ? qty : 1);
        return;
    }
    if (cmd == "SKIPCATCH")
    {
        SkipCatch(player);
        return;
    }
    if (cmd == "PARTY")
    {
        EnsureAccount(player);
        SendOwnedList(player, SessionLowGuid(player));
        SendDexOwned(player, SessionLowGuid(player));
        return;
    }
    if (cmd == "SETPARTY")
    {
        auto parts = Split(arg, ',');
        uint32 ids[6] = {};
        for (size_t i = 0; i < 6 && i < parts.size(); ++i)
            ids[i] = static_cast<uint32>(atoi(parts[i].c_str()));
        SetParty(player, ids);
        return;
    }
    if (cmd == "LEARNSET")
    {
        EnsureAccount(player);
        SendLearnset(player, static_cast<uint32>(atoi(arg.c_str())));
        return;
    }
    if (cmd == "SETMOVES")
    {
        auto parts = Split(arg, ',');
        if (parts.empty())
            return;
        uint32 ownedId = static_cast<uint32>(atoi(parts[0].c_str()));
        std::vector<std::string> moves;
        for (size_t i = 1; i < parts.size() && moves.size() < 4; ++i)
            if (!parts[i].empty())
                moves.push_back(parts[i]);
        SetMoves(player, ownedId, moves);
        return;
    }
    if (cmd == "SWITCH")
    {
        uint8 slot = static_cast<uint8>(atoi(arg.c_str()));
        SwitchParty(player, slot);
        return;
    }
}
