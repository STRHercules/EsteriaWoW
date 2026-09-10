#ifndef BATTLEMON_BATTLE_H
#define BATTLEMON_BATTLE_H

#include "BattlemonSession.h"
#include "BattlemonTypes.h"

#include <string>

class BattlemonMgr;

struct BmCtx
{
    BattlemonSession* session = nullptr;
    BattlemonMgr* mgr = nullptr;
    BattlemonEncounter* enc = nullptr;
    bool uturn = false;
};

bool BmHasAbility(BattlemonBattler const& b, char const* id);
bool BmMoveHasFlag(BattlemonMoveDef const& m, char const* flag);
bool BmHasType(BattlemonBattler const& b, char const* type);
std::string BmType1(BattlemonBattler const& b);
std::string BmType2(BattlemonBattler const& b);
std::string BmPickAbility(BattlemonSpecies const* s);
void BmInitBattler(BattlemonBattler& b);
void BmResetStages(BattlemonBattler& b);

float BmStageMul(int8 stage);
float BmAccStageMul(int8 stage);
uint32 BmEffectiveSpeed(BattlemonBattler const& b, BattlemonEncounter const& enc);
std::string BmStatusCode(BmStatus s);
std::string BmWeatherCode(BmWeather w);

void BmMsg(BmCtx& ctx, std::string const& text);
void BmApplyDamage(BmCtx& ctx, BattlemonBattler& target, int32 dmg, BattlemonBattler* user, BattlemonMoveDef const* move);
bool BmTryStatus(BmCtx& ctx, BattlemonBattler& target, BattlemonBattler* source, BmStatus st, bool silentFail);
bool BmChangeStage(BmCtx& ctx, BattlemonBattler& target, BattlemonBattler* source, BmStat stat, int8 delta, bool selfChange);
void BmSetWeather(BmCtx& ctx, BmWeather w, uint8 turns, BattlemonBattler* setter);

bool BmImmuneToMove(BmCtx& ctx, BattlemonBattler const& user, BattlemonBattler& target, BattlemonMoveDef const& move, bool show);
bool BmCanAct(BmCtx& ctx, BattlemonBattler& b, BattlemonBattler& foe);
void BmOnSwitchIn(BmCtx& ctx, BattlemonBattler& incoming, BattlemonBattler& foe);
void BmOnSwitchOut(BattlemonBattler& leaving);
void BmOnBeingHit(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, BattlemonMoveDef const& move);
void BmEndOfRound(BmCtx& ctx, BattlemonBattler& a, BattlemonBattler& b);
void BmEndOfRoundAbility(BmCtx& ctx, BattlemonBattler& b, BattlemonEncounter& enc, BattlemonBattler const& other);

bool BmStatusImmune(BattlemonBattler const& b, BmStatus st);
bool BmStatLossBlocked(BattlemonBattler const& target, BattlemonBattler const* source);
bool BmWeatherSuppressed(BattlemonEncounter const& enc, BattlemonBattler const& a, BattlemonBattler const& b);
float BmSpeedWeatherMul(BattlemonBattler const& b, BattlemonEncounter const& enc);
float BmAccuracyAbilityMul(BattlemonBattler const& user, BattlemonBattler const& target);
float BmEvasionWeatherMul(BattlemonBattler const& target, BattlemonEncounter const& enc, BattlemonBattler const& other);
float BmUserAtkMul(BattlemonBattler const& user, BattlemonMoveDef const& move);
float BmTargetDefMul(BattlemonBattler const& target, BattlemonMoveDef const& move, bool crit);
float BmAfterEffMul(BattlemonBattler const& user, BattlemonBattler const& target, float eff);

int32 BmCalcDamage(BmCtx& ctx, BattlemonBattler const& atk, BattlemonBattler const& def,
                   BattlemonMoveDef const& move, bool& crit, float& eff, uint8 hitCount);
void BmExecuteMove(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, BattlemonSlot& slot, bool isPlayer);
void BmRunSingleAction(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, BattlemonSlot* slot, bool isPlayer);
bool BmApplyFunctionCode(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target,
                         BattlemonMoveDef const& move, int32 damage, bool targetFainted, bool additional);
bool BmIsProtectMove(BattlemonMoveDef const& move);
bool BmIsOHKOMove(BattlemonMoveDef const& move);
bool BmIsTwoTurnMove(BattlemonMoveDef const& move);
bool BmIsRechargeMove(BattlemonMoveDef const& move);
uint8 BmHitCount(BattlemonMoveDef const& move);
float BmRecoilFraction(BattlemonMoveDef const& move);
bool BmDrainsHalf(BattlemonMoveDef const& move);

#endif
