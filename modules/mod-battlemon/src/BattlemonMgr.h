#ifndef BATTLEMON_MGR_H
#define BATTLEMON_MGR_H

#include "BattlemonSession.h"
#include "BattlemonExtension.h"
#include "BattlemonTypes.h"
#include "ObjectGuid.h"

#include <mutex>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

class Creature;
class Item;
class Player;

class BattlemonMgr
{
public:
    static BattlemonMgr* instance();

    void SetExtension(BattlemonExtension* extension) { _extension = extension; }
    bool IsExternallyReserved(ObjectGuid guid) const;
    bool HasRemoteSession(Player* player) const;
    bool GetBattleSnapshot(Player* player, BattlemonEncounter& snapshot);
    std::vector<BattlemonBattler> BuildDuelParty(Player* player, uint8 limit);
    std::vector<BattlemonBattler> BuildGeneratedTeam(uint32 averageLevel, uint32 trainerLevel, uint8 limit) const;
    std::vector<BattlemonBattler> BuildTrainerTeam(uint32 entry, uint32 level, uint8 limit) const;
    std::string FormatBattlerState(BattlemonBattler const& battler, char side) const;

    void LoadConfig();
    void LoadCatalog();

    bool IsEnabled() const { return _enabled; }
    bool Announce() const { return _announce; }
    bool GrantToBots() const { return _grantToBots; }
    bool ShouldHandle(Player* player) const;

    BattlemonSpecies const* GetSpecies(uint32 id) const;
    BattlemonForm const* GetBattlemonForm(uint32 id) const;
    BattlemonForm const* GetStarterForm() const;
    BattlemonMoveDef const* GetMove(std::string const& internal) const;
    // Same legendary/starter/normal weights as the addon Fight button.
    BattlemonForm const* PickWildForm() const;
    // Zone-aware pick (falls back to the old global one when spawning is switched off).
    BattlemonForm const* PickWildForm(uint32 zoneId, uint32 level) const;
    std::vector<uint32> const& FormIds() const { return _formIds; }
    std::unordered_map<uint32, BattlemonSpecies> const& SpeciesMap() const { return _species; }
    // 0 normal, 1 starter, 2 legendary: the encounter-weight class a species belongs to.
    uint32 SpawnClass(uint32 speciesId) const;
    uint32 ScaledEnemyLevel(uint32 playerLevel) const;
    // ShinyEvery as 1-in-N for world spawns (not the per-player encounter counter).
    bool RollSpawnShiny() const;

    BattlemonAccount EnsureAccount(Player* player);
    BattlemonAccount EnsureAccount(uint32 guid);
    std::vector<BattlemonOwned> LoadOwned(uint32 guid) const;
    uint32 PartyOwnedId(uint32 guid, uint8 slot) const; // 1-6
    BattlemonOwned LoadOwnedById(uint32 ownedId) const;
    bool OwnsForm(uint32 guid, uint32 formId, bool shiny) const;
    BattlemonItemDef const* GetItem(std::string const& internal) const;
    BattlemonShopEntry const* GetShopEntry(std::string const& internal) const;
    std::vector<BattlemonShopEntry> const& ShopEntries() const { return _shop; }
    // Shared by the addon's BUY and the Center's menu shop; message is what the player should be told.
    bool TryBuy(Player* player, std::string const& item, uint32 qty, std::string& message);
    uint32 BagCount(uint32 guid, std::string const& item) const;
    void BagAdd(uint32 guid, std::string const& item, uint32 count);
    bool BagTake(uint32 guid, std::string const& item, uint32 count);
    std::vector<BattlemonLegalMove> LegalMoves(BattlemonOwned const& row) const;
    std::unordered_set<std::string> TaughtMoves(uint32 ownedId) const;
    uint32 SecondsUntilReady(BattlemonAccount const& acc) const;
    uint32 PartyCount(uint32 guid) const;

    void ResetPlayer(Player* player);
    void StartWild(Player* player);
    // formId 0 = random. skipCooldown: overworld; does not check or start EncounterCooldown.
    // sourceCreature: overworld sprite to despawn after a catch or KO.
    void StartWild(Player* player, uint32 formId, bool shiny, bool skipCooldown,
                   ObjectGuid sourceCreature = ObjectGuid::Empty);
    bool HasActiveEncounter(Player* player);
    void UseMove(Player* player, uint8 slotIndex);
    void RunAway(Player* player);
    void ThrowBall(Player* player, std::string const& ballArg = "");
    // targetSlot 0 means the battler that is out; a revive names a bench slot.
    void UseItem(Player* player, std::string const& item, uint8 targetSlot = 0);
    void BagUse(Player* player, std::string const& item, uint32 ownedId);
    void SkipCatch(Player* player);
    void SwitchParty(Player* player, uint8 slot);
    void SetParty(Player* player, uint32 ownedIds[6]);
    void ClearEncounter(ObjectGuid guid);
    void SendStatus(Player* player);
    void UseCenterService(Player* player, uint32 action);
    // False (and tells the player) while they are in a battle, a duel or in combat.
    bool CanBoxAction(Player* player);
    // A message for `player` only. SendAddon also copies into the current sender's sidecar outbox, which is
    // wrong when the message is for somebody else (the other side of a trade).
    void SendAddonDirect(Player* player, std::string const& payload);
    // Held items: one per Pokemon, taken from and returned to the bag. Replies go to the addon.
    bool GiveHeldItem(Player* player, uint32 ownedId, std::string const& item);
    bool TakeHeldItem(Player* player, uint32 ownedId);
    // Day Care: two compatible Pokemon left here may produce eggs, which hatch after a while. Replies go to chat.
    bool BreedingEnabled() const { return _breedEnable; }
    std::vector<BattlemonOwned> DaycareParents(Player* player);
    bool DaycareDeposit(Player* player, uint32 ownedId);
    bool DaycareTake(Player* player, uint32 ownedId);
    void DaycareCheck(Player* player);  // how the pair gets along; adds the eggs found since the last visit
    void DaycareHatch(Player* player);  // hatches the eggs that are ready
    // Re-sends the collection and party after something outside the addon changed them (a trade).
    void SyncCollection(Player* player);
    void HandleAdmin(Player* player, std::string const& arg);
    void MakeEgg(uint32 guid, BattlemonOwned const (&parents)[2]);
    // Move learning with a full set of four: the level-up queues an offer, and once the battle is over the
    // player is asked which move to forget (or to skip it). LEARNQ asks for the next offer, LEARNREPLY answers it.
    void SendLearnOffer(Player* player);
    void AnswerLearnOffer(Player* player, uint32 ownedId, std::string const& move, uint32 slot);
    // BM\tFOLLOW\t<battlemon_owned.id>, 0 for none: lets the addon mark and toggle the follower.
    void NotifyFollower(Player* player, uint32 ownedId);
    // Pokemon not in the party, i.e. what sits in storage.
    std::vector<BattlemonOwned> LoadBoxed(uint32 guid) const;
    // Sealing turns a stored Pokemon into a Poke Ball item; using the ball releases it to the user.
    bool SealPokemon(Player* player, uint32 ownedId);
    bool UnsealPokemon(Player* player, Item* item);
    void HandleAddon(Player* player, std::string const& msg);
    void HandleCommand(BattlemonSession& session, std::string const& msg);

    void Msg(Player* player, std::string const& text);
    void Msg(BattlemonSession& session, std::string const& text);
    void SendCombatFx(Player* player, BattlemonEncounter& enc);
    void SendMoveAnimation(Player* player, bool playerSide, std::string const& move);
    float TypeChartMul(std::string const& atk, std::string const& def) const { return TypeMult(atk, def); }

    static uint32 ExpAtLevel(std::string const& growth, uint32 level);

private:
    BattlemonMgr() = default;

    uint32 NowSeconds() const;
    BattlemonForm const* RandomForm() const;
    uint32 ExpYield(BattlemonBattler const& enemy) const;
    std::vector<uint32> AddExp(BattlemonOwned& row, uint32 amount, uint32 levelCap = 100) const;
    char RollGender(std::string const& ratio) const;
    BattlemonStats::Individual RollIndividual(BattlemonSpecies const* species) const;
    std::vector<std::string> PickMoves(uint32 speciesId, uint32 level, uint32 formId = 0) const;
    void FillMoves(BattlemonBattler& b, std::vector<std::string> const& internals) const;
    void ApplyStats(BattlemonBattler& b) const;
    BattlemonBattler MakeBattler(BattlemonOwned const& row) const;
    BattlemonBattler MakeWild(BattlemonForm const& form, uint32 level, bool shiny = false,
                              bool rollIndividual = false) const;
    void PersistBattler(BattlemonBattler const& b);
    uint32 InsertOwned(BattlemonOwned const& row);
    void SaveAccount(BattlemonAccount const& acc);
    void GrantStarter(uint32 guid);
    BattlemonBattler* ActiveBattler(BattlemonEncounter& enc);
    BattlemonSlot* PickEnemyMove(BattlemonEncounter& enc) const;
    void FinishTurn(Player* player, BattlemonEncounter& enc, BattlemonBattler& cur, bool uturn);
    uint8 FirstConsciousSlot(BattlemonEncounter const& enc, uint8 except = 0) const;
    bool AnyConscious(BattlemonEncounter const& enc) const;
    uint32 MaxHpFor(BattlemonOwned const& row) const;
    void ReviveIfDue(BattlemonOwned& row) const;
    uint32 ReviveSecondsLeft(BattlemonOwned const& row) const;
    void PersistParty(BattlemonEncounter& enc);
    void SendBattleParty(Player* player, BattlemonEncounter& enc);
    float BallMultiplier(std::string const& ball) const;
    float TypeMult(std::string const& atk, std::string const& def) const;
    float Effectiveness(std::string const& atkType, BattlemonBattler const& def) const;
    int32 CalcDamage(BattlemonBattler const& atk, BattlemonBattler const& def, BattlemonMoveDef const& move, bool& crit, float& eff) const;
    void TryLearnMoves(BattlemonBattler& b, uint32 newLevel, Player* player);
    std::string FormatState(BattlemonBattler const& b, char side) const;
    void SendAddon(Player* player, std::string const& payload);
    ObjectGuid SessionObjectGuid(Player* player) const;
    uint32 SessionLowGuid(Player* player) const;
    void SendReady(Player* player, BattlemonAccount const& acc);
    void SendOwnedList(Player* player, uint32 guid);
    void SendDexOwned(Player* player, uint32 guid);
    void SendDexList(Player* player, uint32 guid, bool shiny);
    void SendBag(Player* player, uint32 guid);
    void SendShop(Player* player);
    void SendLearnset(Player* player, uint32 ownedId);
    void SetMoves(Player* player, uint32 ownedId, std::vector<std::string> const& moves);
    void Buy(Player* player, std::string const& item, uint32 qty);
    void AwardAndPersist(Player* player, BattlemonEncounter& enc);
    void AwardWinPoints(Player* player);
    void AwardWinBalls(Player* player);
    void GrantDailyBalls(BattlemonAccount& acc);
    uint32 TodayYYYYMMDD() const;
    void FinishWin(Player* player, BattlemonEncounter& enc);
    void FinishLose(Player* player, BattlemonEncounter& enc);
    Creature* FindSourceCreature(Player* player, ObjectGuid guid) const;
    void DespawnSource(Player* player, BattlemonEncounter& enc);
    void UnlockSource(Player* player, ObjectGuid guid);
    void BeginCooldown(uint32 guid);

    BattlemonExtension* _extension = nullptr;
    bool _enabled = true;
    bool _announce = true;
    bool _grantToBots = false;
    uint32 _starterSpecies = 25;
    uint32 _starterLevel = 1;
    uint32 _encounterCooldown = 300;
    float _catchChance = 0.5f;
    uint32 _dailyBalls = 5;
    uint32 _winBalls = 1;
    uint32 _bagMaxStack = 99;
    uint8 _catchThrows = 3;
    uint32 _weightLegendary = 1;
    uint32 _weightStarter = 5;
    uint32 _weightNormal = 94;
    uint32 _winPoints = 10;
    uint32 _shinyEvery = 10;
    uint32 _tutorMoveCost = 25;
    bool _breedEnable = true;
    uint32 _breedInterval = 900;        // seconds between egg rolls for a pair
    uint32 _breedMaxEggs = 3;
    uint32 _hatchSecondsPer256 = 60;    // one 256-step cycle
    uint32 _hatchTimePercent = 100;
    uint32 _hatchLevel = 1;
    uint32 _faintReviveHours = 1;
    float _greatBallMult = 1.5f;
    float _ultraBallMult = 2.0f;

    std::unordered_map<uint32, BattlemonSpecies> _species;
    std::unordered_map<uint32, BattlemonForm> _forms;
    std::unordered_map<std::string, BattlemonMoveDef> _moves;
    std::unordered_map<uint32, std::vector<BattlemonLearn>> _learnsets;
    std::unordered_map<uint32, std::vector<std::string>> _tutorMoves;
    std::unordered_map<uint32, std::vector<std::string>> _eggMoves;
    std::unordered_map<uint32, BattlemonFormMoves> _formMoves;
    std::unordered_map<std::string, BattlemonItemDef> _items;
    std::vector<BattlemonShopEntry> _shop;
    std::unordered_map<std::string, std::unordered_map<std::string, float>> _typeChart;
    std::vector<uint32> _formIds;
    std::vector<uint32> _legendaryFormIds;
    std::vector<uint32> _starterFormIds;
    std::vector<uint32> _normalFormIds;
    uint32 _starterFormId = 0;

    std::mutex _lock;
    std::unordered_map<ObjectGuid, BattlemonEncounter> _encounters;
    BattlemonSession* _currentSession = nullptr;
};

#define sBattlemonMgr BattlemonMgr::instance()

#endif
