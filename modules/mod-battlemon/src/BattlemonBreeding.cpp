#include "BattlemonBreedingRules.h"
#include "BattlemonFollower.h"
#include "BattlemonHeldItems.h"
#include "BattlemonMgr.h"
#include "BattlemonModelCatalog.h"
#include "BattlemonSpawns.h"
#include "BattlemonSql.h"

#include "Chat.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "Player.h"
#include "Random.h"
#include "StringFormat.h"

#include <algorithm>
#include <unordered_set>

namespace Rules = BattlemonBreedingRules;

namespace
{
// The Day Care is driven from a gossip menu, so replies go to the chat window and need no addon.
void Tell(Player* player, std::string const& text)
{
    if (player && player->GetSession())
        ChatHandler(player->GetSession()).SendSysMessage(text);
}

bool Knows(BattlemonOwned const& row, std::string const& move)
{
    return std::find(std::begin(row.move), std::end(row.move), move) != std::end(row.move);
}
}

std::vector<BattlemonOwned> BattlemonMgr::DaycareParents(Player* player)
{
    std::vector<BattlemonOwned> out;
    if (QueryResult result = CharacterDatabase.Query(
            "SELECT owned_id FROM battlemon_daycare WHERE guid = {} ORDER BY slot", player->GetGUID().GetCounter()))
        do
        {
            BattlemonOwned row = LoadOwnedById(result->Fetch()[0].Get<uint32>());
            if (row.id)
                out.push_back(row);
        } while (result->NextRow());
    return out;
}

bool BattlemonMgr::DaycareDeposit(Player* player, uint32 ownedId)
{
    if (!_breedEnable)
    {
        Tell(player, "The Day Care is closed.");
        return false;
    }
    if (!CanBoxAction(player))
        return false;
    uint32 const guid = player->GetGUID().GetCounter();
    BattlemonOwned const row = LoadOwnedById(ownedId);
    if (!row.id || row.guid != guid)
    {
        Tell(player, "That Pokémon is not yours.");
        return false;
    }
    for (uint8 slot = 1; slot <= 6; ++slot)
        if (PartyOwnedId(guid, slot) == ownedId)
        {
            Tell(player, "Take it out of your party first.");
            return false;
        }

    std::unordered_set<uint32> used;
    if (QueryResult result = CharacterDatabase.Query("SELECT slot FROM battlemon_daycare WHERE guid = {}", guid))
        do
            used.insert(result->Fetch()[0].Get<uint32>());
        while (result->NextRow());
    if (used.size() >= 2)
    {
        Tell(player, "The Day Care is full. Take one of your Pokémon back first.");
        return false;
    }
    uint32 const slot = used.count(1) ? 2 : 1;
    uint32 const now = NowSeconds();

    // The row leaves the trainer's collection (guid 0) and the Day Care remembers whose it is, in one transaction.
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    trans->Append("UPDATE battlemon_owned SET guid = 0 WHERE id = {} AND guid = {}", ownedId, guid);
    trans->Append("INSERT INTO battlemon_daycare (guid, slot, owned_id, checked_at) VALUES ({}, {}, {}, {})", guid, slot,
                  ownedId, now);
    // A new pair starts its clock now.
    trans->Append("UPDATE battlemon_daycare SET checked_at = {} WHERE guid = {}", now, guid);
    CharacterDatabase.CommitTransaction(trans);

    if (sBattlemonFollower->Chosen(player) == ownedId)
        sBattlemonFollower->Choose(player, 0);
    SyncCollection(player);
    BattlemonForm const* form = GetBattlemonForm(row.formId);
    Tell(player, (form ? form->name : std::string("Your Pokémon")) + " is staying at the Day Care.");
    return true;
}

bool BattlemonMgr::DaycareTake(Player* player, uint32 ownedId)
{
    if (!CanBoxAction(player))
        return false;
    uint32 const guid = player->GetGUID().GetCounter();
    if (!CharacterDatabase.Query("SELECT 1 FROM battlemon_daycare WHERE guid = {} AND owned_id = {}", guid, ownedId))
    {
        Tell(player, "That Pokémon is not at your Day Care.");
        return false;
    }
    BattlemonOwned const row = LoadOwnedById(ownedId);
    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    trans->Append("UPDATE battlemon_owned SET guid = {} WHERE id = {} AND guid = 0", guid, ownedId);
    trans->Append("DELETE FROM battlemon_daycare WHERE guid = {} AND owned_id = {}", guid, ownedId);
    // A pair that has been split starts over when a new partner arrives.
    trans->Append("UPDATE battlemon_daycare SET checked_at = {} WHERE guid = {}", NowSeconds(), guid);
    CharacterDatabase.CommitTransaction(trans);
    SyncCollection(player);
    BattlemonForm const* form = GetBattlemonForm(row.formId);
    Tell(player, "You took " + (form ? form->name : std::string("your Pokémon")) + " back from the Day Care.");
    return true;
}

// Rolls everything about the baby now, so the egg is the same whenever and however it is hatched.
void BattlemonMgr::MakeEgg(uint32 guid, BattlemonOwned const (&parents)[2])
{
    Rules::Parent p[2];
    for (int i = 0; i < 2; ++i)
    {
        BattlemonSpecies const* sp = GetSpecies(parents[i].speciesId);
        p[i] = { sp ? sp->eggGroups : "", parents[i].gender, parents[i].speciesId, parents[i].ind.otGuid };
    }
    BattlemonOwned const& mother = parents[Rules::MotherIndex(p[0], p[1])];
    BattlemonOwned const& other = parents[1 - Rules::MotherIndex(p[0], p[1])];

    uint32 const baseId = sBattlemonSpawns->BaseSpecies(mother.speciesId);
    BattlemonSpecies const* base = GetSpecies(baseId);
    if (!base)
        return;
    // The base species' ordinary form: the lowest id without a variant tag.
    BattlemonForm const* form = nullptr;
    for (uint32 formId : _formIds)
    {
        BattlemonForm const* f = GetBattlemonForm(formId);
        if (f && f->speciesId == baseId && f->variant.empty() && (!form || f->id < form->id))
            form = f;
    }
    if (!form)
        return;

    BattlemonStats::Individual ind;
    auto rng = [](uint32 lo, uint32 hi) { return urand(lo, hi); };
    using BattlemonHeldItems::Kind;
    bool const knot = BattlemonHeldItems::Is(parents[0].heldItem, Kind::DestinyKnot)
        || BattlemonHeldItems::Is(parents[1].heldItem, Kind::DestinyKnot);
    Rules::InheritIvs(parents[0].ind.iv, parents[1].ind.iv, rng, ind.iv, knot ? 5 : 3);
    bool const stone[2] = { BattlemonHeldItems::Is(parents[0].heldItem, Kind::Everstone),
                            BattlemonHeldItems::Is(parents[1].heldItem, Kind::Everstone) };
    int const natureFrom = Rules::NatureParent(stone, rng);
    ind.nature = natureFrom >= 0 ? parents[natureFrom].ind.nature
                                 : static_cast<uint8>(urand(0, BattlemonStats::NATURE_COUNT - 1));
    // The mother's ability usually carries over (the hidden one less often); otherwise it is rolled.
    uint8 const slot = mother.ind.abilitySlot;
    bool const keep = slot == 2 ? urand(1, 100) <= 60 : urand(1, 100) <= 80;
    ind.abilitySlot = keep && (slot != 2 || !base->hiddenAbility.empty()) ? slot : RollIndividual(base).abilitySlot;

    // Level-1 moves first, then whatever the parents can pass on: shared level-up moves, shared TMs, and
    // egg moves either parent knows (last, so they are the ones kept).
    std::vector<std::string> inherited;
    if (auto it = _learnsets.find(baseId); it != _learnsets.end())
        for (BattlemonLearn const& l : it->second)
            if (Knows(mother, l.moveInternal) && Knows(other, l.moveInternal))
                inherited.push_back(l.moveInternal);
    if (auto it = _tutorMoves.find(baseId); it != _tutorMoves.end())
        for (std::string const& move : it->second)
            if (Knows(mother, move) && Knows(other, move))
                inherited.push_back(move);
    if (auto it = _eggMoves.find(baseId); it != _eggMoves.end())
        for (std::string const& move : it->second)
            if (Knows(mother, move) || Knows(other, move))
                inherited.push_back(move);
    std::vector<std::string> moves = Rules::MergeMoves(PickMoves(baseId, 1, form->id), inherited);
    moves.resize(4);

    bool const shiny = BattlemonModels::PreferredShiny(form->id, RollSpawnShiny());
    uint32 const hatchAt = NowSeconds() + Rules::HatchSeconds(base->hatchSteps, _hatchSecondsPer256, _hatchTimePercent);
    CharacterDatabase.Execute(
        "INSERT INTO battlemon_egg (guid, species_id, form_id, shiny, gender, iv_hp, iv_atk, iv_def, iv_spa, iv_spd, "
        "iv_spe, nature, ability_slot, move1, move2, move3, move4, hatch_at) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, "
        "{}, {}, {}, {}, {}, {}, {}, {}, {})",
        guid, baseId, form->id, shiny ? 1 : 0, SqlQuote(std::string(1, RollGender(base->genderRatio))), ind.iv[0],
        ind.iv[1], ind.iv[2], ind.iv[3], ind.iv[4], ind.iv[5], ind.nature, ind.abilitySlot, SqlQuote(moves[0]),
        SqlQuote(moves[1]), SqlQuote(moves[2]), SqlQuote(moves[3]), hatchAt);
}

void BattlemonMgr::DaycareCheck(Player* player)
{
    if (!_breedEnable)
    {
        Tell(player, "The Day Care is closed.");
        return;
    }
    if (!CanBoxAction(player))
        return;
    uint32 const guid = player->GetGUID().GetCounter();
    std::vector<BattlemonOwned> const parents = DaycareParents(player);
    if (parents.size() < 2)
    {
        Tell(player, parents.empty() ? "Your Day Care is empty. Leave two Pokémon to see if they get along."
                                     : "One Pokémon is staying here. Leave a second one to see if they get along.");
        return;
    }

    BattlemonOwned const pair[2] = { parents[0], parents[1] };
    Rules::Parent p[2];
    for (int i = 0; i < 2; ++i)
    {
        BattlemonSpecies const* sp = GetSpecies(pair[i].speciesId);
        p[i] = { sp ? sp->eggGroups : "", pair[i].gender, pair[i].speciesId, pair[i].ind.otGuid };
    }
    switch (Rules::Check(p[0], p[1]))
    {
        case Rules::Match::Ok:
            break;
        case Rules::Match::Undiscovered:
            Tell(player, "One of them is too young, or too rare, to ever have an egg.");
            return;
        case Rules::Match::DittoPair:
            Tell(player, "Two Ditto cannot make an egg.");
            return;
        case Rules::Match::Genderless:
            Tell(player, "A genderless Pokémon only gets along with a Ditto.");
            return;
        case Rules::Match::SameGender:
            Tell(player, "They are the same gender, so they will not make an egg.");
            return;
        case Rules::Match::NoSharedGroup:
            Tell(player, "They have nothing in common. They do not seem to like each other.");
            return;
    }

    bool const sameSpecies = p[0].species == p[1].species;
    bool const sameOt = p[0].ot && p[0].ot == p[1].ot;
    uint32 const chance = Rules::EggChancePercent(sameSpecies, sameOt);
    char const* verdict = chance >= 70 ? "get along very well" : chance >= 50 ? "seem to get along" : "do not seem to like each other much";

    uint32 eggs = 0;
    if (QueryResult result = CharacterDatabase.Query("SELECT COUNT(*) FROM battlemon_egg WHERE guid = {}", guid))
        eggs = result->Fetch()[0].Get<uint32>();
    uint32 checkedAt = NowSeconds();
    if (QueryResult result = CharacterDatabase.Query("SELECT MIN(checked_at) FROM battlemon_daycare WHERE guid = {}", guid))
        if (!result->Fetch()[0].IsNull())
            checkedAt = result->Fetch()[0].Get<uint32>();

    // One roll for every full interval since the last visit, up to the number of eggs a trainer may hold.
    uint32 const now = NowSeconds();
    uint32 const intervals = _breedInterval ? (now - std::min(now, checkedAt)) / _breedInterval : 0;
    uint32 made = 0;
    for (uint32 i = 0; i < intervals && eggs + made < _breedMaxEggs; ++i)
        if (urand(1, 100) <= chance)
        {
            MakeEgg(guid, pair);
            ++made;
        }
    // When the trainer is full of eggs the clock restarts, so a long absence cannot be cashed in all at once.
    uint32 const next = eggs + made >= _breedMaxEggs ? now : checkedAt + intervals * _breedInterval;
    CharacterDatabase.Execute("UPDATE battlemon_daycare SET checked_at = {} WHERE guid = {}", next, guid);

    std::string text = Acore::StringFormat("Your Pokémon {}.", verdict);
    if (made)
        text += made == 1 ? " They have an egg for you!" : Acore::StringFormat(" They have {} eggs for you!", made);
    else if (eggs >= _breedMaxEggs)
        text += " You are holding as many eggs as you can carry.";
    Tell(player, text);
}

void BattlemonMgr::DaycareHatch(Player* player)
{
    // A hatch puts a Pokemon in the party, which nothing else may do during a battle.
    if (!CanBoxAction(player))
        return;
    uint32 const guid = player->GetGUID().GetCounter();
    QueryResult result = CharacterDatabase.Query(
        "SELECT id, species_id, form_id, shiny, gender, iv_hp, iv_atk, iv_def, iv_spa, iv_spd, iv_spe, nature, "
        "ability_slot, move1, move2, move3, move4, hatch_at FROM battlemon_egg WHERE guid = {} ORDER BY id", guid);
    if (!result)
    {
        Tell(player, "You are not holding any eggs.");
        return;
    }

    uint32 const now = NowSeconds();
    uint32 waiting = 0;
    uint32 soonest = 0;
    do
    {
        Field* f = result->Fetch();
        uint32 const eggId = f[0].Get<uint32>();
        uint32 const hatchAt = f[17].Get<uint32>();
        if (hatchAt > now)
        {
            ++waiting;
            soonest = soonest ? std::min(soonest, hatchAt - now) : hatchAt - now;
            continue;
        }

        BattlemonForm const* form = GetBattlemonForm(f[2].Get<uint32>());
        BattlemonSpecies const* species = GetSpecies(f[1].Get<uint32>());
        if (!form || !species)
        {
            CharacterDatabase.Execute("DELETE FROM battlemon_egg WHERE id = {}", eggId);
            continue;
        }
        BattlemonOwned row;
        row.guid = guid;
        row.formId = form->id;
        row.speciesId = species->id;
        row.sprite = form->sprite;
        row.level = _hatchLevel;
        row.exp = ExpAtLevel(species->growthRate, _hatchLevel);
        row.shiny = f[3].Get<uint8>() != 0;
        std::string const gender = f[4].Get<std::string>();
        row.gender = gender.empty() ? 'M' : gender[0];
        for (int i = 0; i < 6; ++i)
            row.ind.iv[i] = f[5 + i].Get<uint8>();
        row.ind.nature = f[11].Get<uint8>();
        row.ind.abilitySlot = f[12].Get<uint8>();
        row.ind.otGuid = guid; // the trainer who hatched it is its original trainer
        for (int i = 0; i < 4; ++i)
            row.move[i] = f[13 + i].IsNull() ? "" : f[13 + i].Get<std::string>();
        row.hp = MaxHpFor(row);

        uint32 const ownedId = InsertOwned(row);
        if (!ownedId)
            continue; // leave the egg; it will be tried again
        CharacterDatabase.Execute("DELETE FROM battlemon_egg WHERE id = {}", eggId);
        // Straight into the party when there is room, like a catch.
        for (uint8 slot = 1; slot <= 6; ++slot)
            if (!PartyOwnedId(guid, slot))
            {
                CharacterDatabase.DirectExecute(
                    "REPLACE INTO battlemon_party (guid, slot, owned_id) VALUES ({}, {}, {})", guid, slot, ownedId);
                break;
            }
        Tell(player, Acore::StringFormat("Oh? The egg hatched into {}{}!", row.shiny ? "a shiny " : "", form->name));
        SyncCollection(player);
    } while (result->NextRow());

    if (waiting)
        Tell(player, Acore::StringFormat("{} {} still waiting; the next hatches in about {} minute(s).", waiting,
                                         waiting == 1 ? "egg is" : "eggs are", std::max<uint32>(1, soonest / 60)));
}
