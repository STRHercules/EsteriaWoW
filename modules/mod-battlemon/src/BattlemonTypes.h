#ifndef BATTLEMON_TYPES_H
#define BATTLEMON_TYPES_H

#include "Define.h"
#include "ObjectGuid.h"

#include <string>
#include <vector>

enum class BmStatus : uint8
{
    None = 0,
    BRN,
    PAR,
    SLP,
    PSN,
    TOX,
    FRZ
};

enum class BmWeather : uint8
{
    None = 0,
    Rain,
    Sun,
    Sand,
    Hail
};

enum class BmStat : uint8
{
    Atk = 0,
    Def = 1,
    Spa = 2,
    Spd = 3,
    Spe = 4,
    Acc = 5
};

struct BattlemonSpecies
{
    uint32 id = 0;
    std::string internalName;
    std::string name;
    std::string type1;
    std::string type2;
    uint32 hp = 1;
    uint32 atk = 1;
    uint32 def = 1;
    uint32 spa = 1;
    uint32 spd = 1;
    uint32 spe = 1;
    std::string genderRatio;
    std::string growthRate;
    uint32 baseExp = 0;
    std::string sprite;
    std::string ability1;
    std::string ability2;
    std::string hiddenAbility;
};

struct BattlemonForm
{
    uint32 id = 0;
    uint32 speciesId = 0;
    std::string sprite;
    std::string variant;
    std::string name;
    std::string backSprite;
};

struct BattlemonMoveDef
{
    uint32 id = 0;
    std::string internalName;
    std::string name;
    std::string type;
    std::string category;
    int32 power = 0;
    int32 accuracy = 100;
    int32 pp = 5;
    int32 priority = 0;
    std::string functionCode;
    std::string flags;
    int32 effectChance = 0;
};

struct BattlemonItemDef
{
    std::string internalName;
    std::string name;
    std::string battleUse;  // "OnPokemon", "OnFoe", or empty
    std::string healAmount; // a number, "full", "half", or empty
};

// One line in the shop. Priced in Battlemon Points rather than the catalog's
// Pokemon dollars, which are on a completely different scale.
struct BattlemonShopEntry
{
    std::string itemInternal;
    uint32 cost = 0;
    uint32 sortOrder = 0;
};

struct BattlemonLearn
{
    uint32 level = 1;
    std::string moveInternal;
};

// Per-form replacements for the species pools; only forms Essentials actually
// defines (Alolan, Galarian, Rotom appliances, ...) have these.
struct BattlemonFormMoves
{
    std::vector<BattlemonLearn> levelUp;
    std::vector<std::string> tutor;
};

// One entry the move manager may offer for an owned Pokémon.
struct BattlemonLegalMove
{
    std::string moveInternal;
    uint32 level = 0;   // level it is learned at; 0 for tutor moves
    bool tutor = false; // tutor moves cost points unless already taught
    bool taught = false;
};

struct BattlemonSlot
{
    BattlemonMoveDef const* def = nullptr;
    int32 pp = 0;
    int32 maxPp = 0;
};

struct BattlemonOwned
{
    uint32 id = 0;
    uint32 guid = 0;
    uint32 formId = 0;
    uint32 speciesId = 25;
    std::string sprite;
    uint32 level = 1;
    uint32 exp = 0;
    char gender = 'M';
    // hp 0 means fainted. faintedAt is the unix time it went down, so the
    // revive timer can run without a background task.
    uint32 hp = 0;
    uint32 faintedAt = 0;
    bool shiny = false;
    std::string move[4];
};

struct BattlemonAccount
{
    uint32 guid = 0;
    uint32 nextEncounterAt = 0;
    uint32 points = 0;
    uint32 ballsGrantedDay = 0;
    uint32 encounterCount = 0;
};

struct BattlemonBattler
{
    uint32 ownedId = 0;
    uint32 formId = 0;
    uint32 speciesId = 0;
    uint32 partySlot = 0;
    BattlemonSpecies const* species = nullptr;
    BattlemonForm const* form = nullptr;
    std::string name;
    std::string sprite;
    std::string backSprite;
    uint32 level = 1;
    uint32 exp = 0;
    char gender = 'M';
    bool shiny = false;
    int32 hp = 1;
    int32 maxHp = 1;
    uint32 atk = 1;
    uint32 def = 1;
    uint32 spa = 1;
    uint32 spd = 1;
    uint32 spe = 1;
    std::vector<BattlemonSlot> moves;
    bool fainted = false;

    std::string ability;
    BmStatus status = BmStatus::None;
    uint8 statusTurns = 0;
    uint8 confuseTurns = 0;
    bool flinch = false;
    int8 stages[6] = {};
    bool protectThisTurn = false;
    bool protectLastTurn = false;
    bool charging = false;
    std::string chargeMove;
    bool semiInvuln = false;
    bool mustRecharge = false;
    bool flashFire = false;
    uint8 yawn = 0;
    bool typeOverridden = false;
    std::string typeOverride1;
    std::string typeOverride2;
};

struct BattlemonEncounter
{
    std::vector<BattlemonBattler> party;
    uint8 activeSlot = 1;
    BattlemonBattler enemy;
    bool active = false;
    bool catchPending = false;
    bool catchAllowed = false;
    uint8 catchThrowsLeft = 0;
    // Overworld clicks skip the addon Fight cooldown entirely.
    bool skipCooldown = false;
    // World sprite this fight was started from. Empty for addon Fight.
    ObjectGuid sourceCreature;
    // A switch you were forced into by a faint is free. A voluntary one is your
    // action for the turn, so the foe gets to attack.
    bool forcedSwitch = false;
    BmWeather weather = BmWeather::None;
    uint8 weatherTurns = 0;
};

#endif
