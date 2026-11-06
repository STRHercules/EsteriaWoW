#include "BattlemonBattle.h"
#include "BattlemonHeldItems.h"
#include "BattlemonMgr.h"

#include "Player.h"
#include "Random.h"

#include <algorithm>
#include <sstream>
#include <string>

void BmMsg(BmCtx& ctx, std::string const& text)
{
    if (ctx.output)
        ctx.output(text);
    else if (ctx.mgr && ctx.session)
        ctx.mgr->Msg(*ctx.session, text);
}

std::string BmStatusCode(BmStatus s)
{
    switch (s)
    {
        case BmStatus::BRN: return "BRN";
        case BmStatus::PAR: return "PAR";
        case BmStatus::SLP: return "SLP";
        case BmStatus::PSN: return "PSN";
        case BmStatus::TOX: return "TOX";
        case BmStatus::FRZ: return "FRZ";
        default: return "";
    }
}

std::string BmWeatherCode(BmWeather w)
{
    switch (w)
    {
        case BmWeather::Rain: return "Rain";
        case BmWeather::Sun: return "Sun";
        case BmWeather::Sand: return "Sand";
        case BmWeather::Hail: return "Hail";
        default: return "";
    }
}

float BmStageMul(int8 stage)
{
    if (stage > 6)
        stage = 6;
    if (stage < -6)
        stage = -6;
    if (stage >= 0)
        return (2.f + stage) / 2.f;
    return 2.f / (2.f - stage);
}

float BmAccStageMul(int8 stage)
{
    if (stage > 6)
        stage = 6;
    if (stage < -6)
        stage = -6;
    if (stage >= 0)
        return (3.f + stage) / 3.f;
    return 3.f / (3.f - stage);
}

// The held-item rules number statuses like BmStatus.
static_assert(static_cast<int>(BmStatus::BRN) == 1 && static_cast<int>(BmStatus::PAR) == 2 &&
              static_cast<int>(BmStatus::SLP) == 3 && static_cast<int>(BmStatus::PSN) == 4 &&
              static_cast<int>(BmStatus::TOX) == 5 && static_cast<int>(BmStatus::FRZ) == 6,
              "BattlemonHeldItems.h status numbers must match BmStatus");

static std::string BmItemName(BmCtx& ctx, std::string const& item)
{
    BattlemonItemDef const* def = ctx.mgr ? ctx.mgr->GetItem(item) : nullptr;
    return def ? def->name : item;
}

bool BmMoveAllowed(BattlemonBattler const& b, BattlemonSlot const& slot)
{
    if (b.choiceMove.empty() || !BattlemonHeldItems::IsChoice(b.heldItem) || !slot.def
        || slot.def->internalName == b.choiceMove)
        return true;
    for (BattlemonSlot const& m : b.moves)
        if (m.def && m.def->internalName == b.choiceMove)
            return m.pp <= 0;
    return true;
}

void BmHeldItemCheck(BmCtx& ctx, BattlemonBattler& b)
{
    if (b.heldItem.empty() || b.fainted || b.hp <= 0)
        return;
    BattlemonHeldItems::BerryUse const use =
        BattlemonHeldItems::Berry(b.heldItem, b.hp, b.maxHp, static_cast<uint8>(b.status));
    if (!use.eat)
        return;
    BmMsg(ctx, b.name + " ate its " + BmItemName(ctx, b.heldItem) + "!");
    b.heldItem.clear();
    if (use.heal)
    {
        b.hp = std::min(b.maxHp, b.hp + use.heal);
        BmMsg(ctx, b.name + " restored its HP!");
    }
    if (use.cure)
    {
        b.status = BmStatus::None;
        b.statusTurns = 0;
        BmMsg(ctx, b.name + " shook off its condition!");
    }
}

uint32 BmEffectiveSpeed(BattlemonBattler const& b, BattlemonEncounter const& enc)
{
    float s = static_cast<float>(b.spe) * BmStageMul(b.stages[static_cast<int>(BmStat::Spe)]);
    s *= BmSpeedWeatherMul(b, enc);
    s *= BattlemonHeldItems::SpeedMul(b.heldItem);
    if (b.status == BmStatus::PAR && !BmHasAbility(b, "QUICKFEET"))
        s *= 0.5f;
    if (s < 1.f)
        s = 1.f;
    return static_cast<uint32>(s);
}

void BmApplyDamage(BmCtx& ctx, BattlemonBattler& target, int32 dmg, BattlemonBattler* user, BattlemonMoveDef const* move)
{
    if (dmg < 0)
        dmg = 0;
    if (move && BmHasAbility(target, "STURDY") && target.hp == target.maxHp && dmg >= target.hp)
    {
        dmg = target.hp - 1;
        BmMsg(ctx, target.name + " held on with Sturdy!");
    }
    else if (move && BattlemonHeldItems::SashSaves(target.heldItem, target.hp, target.maxHp, dmg))
    {
        dmg = target.hp - 1;
        target.heldItem.clear();
        BmMsg(ctx, target.name + " hung on using its Focus Sash!");
    }
    target.hp -= dmg;
    if (target.hp < 0)
        target.hp = 0;
    if (target.hp == 0)
        target.fainted = true;
    (void)user;
}

bool BmTryStatus(BmCtx& ctx, BattlemonBattler& target, BattlemonBattler* source, BmStatus st, bool silentFail)
{
    if (target.fainted || target.hp <= 0)
        return false;
    if (st == BmStatus::None)
        return false;
    if (target.status != BmStatus::None)
        return false;
    if (BmStatusImmune(target, st))
    {
        if (!silentFail)
            BmMsg(ctx, "It doesn't affect " + target.name + "...");
        return false;
    }
    if (source && source != &target && BmHasAbility(*source, "SHEERFORCE"))
        return false;
    target.status = st;
    if (st == BmStatus::SLP)
        target.statusTurns = static_cast<uint8>(urand(1, 3));
    else if (st == BmStatus::TOX)
        target.statusTurns = 1;
    else
        target.statusTurns = 0;
    char const* word = "afflicted";
    switch (st)
    {
        case BmStatus::BRN: word = "burned"; break;
        case BmStatus::PAR: word = "paralyzed"; break;
        case BmStatus::SLP: word = "asleep"; break;
        case BmStatus::PSN:
        case BmStatus::TOX: word = "poisoned"; break;
        case BmStatus::FRZ: word = "frozen"; break;
        default: break;
    }
    BmMsg(ctx, target.name + " was " + word + "!");
    if (source && BmHasAbility(target, "SYNCHRONIZE")
        && (st == BmStatus::BRN || st == BmStatus::PAR || st == BmStatus::PSN))
        BmTryStatus(ctx, *source, &target, st, true);
    return true;
}

bool BmChangeStage(BmCtx& ctx, BattlemonBattler& target, BattlemonBattler* source, BmStat stat, int8 delta, bool selfChange)
{
    if (delta < 0 && !selfChange && BmStatLossBlocked(target, source))
    {
        BmMsg(ctx, target.name + "'s stats weren't lowered!");
        return false;
    }
    int idx = static_cast<int>(stat);
    int8 next = static_cast<int8>(target.stages[idx] + delta);
    if (next > 6)
        next = 6;
    if (next < -6)
        next = -6;
    if (next == target.stages[idx])
        return false;
    target.stages[idx] = next;
    char const* names[] = { "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "accuracy" };
    std::string how = delta >= 2 ? " sharply rose" : (delta <= -2 ? " harshly fell" : (delta > 0 ? " rose" : " fell"));
    BmMsg(ctx, target.name + "'s " + names[idx] + how + "!");
    return true;
}

void BmSetWeather(BmCtx& ctx, BmWeather w, uint8 turns, BattlemonBattler* setter)
{
    if (!ctx.enc)
        return;
    ctx.enc->weather = w;
    ctx.enc->weatherTurns = turns;
    std::string name = BmWeatherCode(w);
    if (setter)
        BmMsg(ctx, setter->name + " whipped up " + name + "!");
    else if (!name.empty())
        BmMsg(ctx, name + " started to fall!");
}

void BmMsgAil(BmCtx& ctx)
{
    if (!ctx.mgr || !ctx.session || !ctx.enc)
        return;
    ctx.mgr->SendCombatFx(ctx.session->player, *ctx.enc);
}

bool BmCanAct(BmCtx& ctx, BattlemonBattler& b, BattlemonBattler& /*foe*/)
{
    if (b.fainted || b.hp <= 0)
        return false;
    if (b.mustRecharge)
    {
        b.mustRecharge = false;
        BmMsg(ctx, b.name + " must recharge!");
        return false;
    }
    if (b.status == BmStatus::SLP)
    {
        if (b.statusTurns <= 1)
        {
            b.status = BmStatus::None;
            b.statusTurns = 0;
            BmMsg(ctx, b.name + " woke up!");
        }
        else
        {
            --b.statusTurns;
            BmMsg(ctx, b.name + " is fast asleep!");
            return false;
        }
    }
    if (b.status == BmStatus::FRZ)
    {
        if (urand(1, 100) <= 20)
        {
            b.status = BmStatus::None;
            BmMsg(ctx, b.name + " thawed out!");
        }
        else
        {
            BmMsg(ctx, b.name + " is frozen solid!");
            return false;
        }
    }
    if (b.status == BmStatus::PAR && urand(1, 100) <= 25)
    {
        BmMsg(ctx, b.name + " is paralyzed! It can't move!");
        return false;
    }
    if (b.flinch)
    {
        b.flinch = false;
        if (BmHasAbility(b, "INNERFOCUS"))
            return true;
        BmMsg(ctx, b.name + " flinched!");
        if (BmHasAbility(b, "STEADFAST"))
            BmChangeStage(ctx, b, &b, BmStat::Spe, 1, true);
        return false;
    }
    if (b.confuseTurns > 0)
    {
        --b.confuseTurns;
        if (b.confuseTurns == 0)
            BmMsg(ctx, b.name + " snapped out of confusion!");
        else
        {
            BmMsg(ctx, b.name + " is confused!");
            if (urand(1, 100) <= 33)
            {
                BmMsg(ctx, "It hurt itself in its confusion!");
                int32 dmg = static_cast<int32>(((2 * b.level / 5 + 2) * 40 * b.atk / std::max(1u, b.def)) / 50 + 2);
                if (dmg < 1)
                    dmg = 1;
                if (!BmHasAbility(b, "MAGICGUARD"))
                    BmApplyDamage(ctx, b, dmg, nullptr, nullptr);
                return false;
            }
        }
    }
    return true;
}

int32 BmCalcDamage(BmCtx& ctx, BattlemonBattler const& atk, BattlemonBattler const& def,
                   BattlemonMoveDef const& move, bool& crit, float& eff, uint8 hitCount)
{
    crit = false;
    eff = 1.f;
    if (move.category == "Status" || move.power <= 0)
        return 0;
    if (!ctx.mgr)
        return 1;

    int32 power = move.power;
    if (hitCount > 1)
        ; // per-hit power stays
    float atkMul = BmUserAtkMul(atk, move);
    if (BmHasAbility(atk, "RECKLESS") && BmRecoilFraction(move) > 0.f)
        atkMul *= 1.2f;
    if (BmHasAbility(atk, "ADAPTABILITY") && (move.type == BmType1(atk) || move.type == BmType2(atk)))
        atkMul *= 1.0f; // STAB handled below as 2.0 instead of 1.5

    uint32 attack = move.category == "Physical" ? atk.atk : atk.spa;
    uint32 defense = move.category == "Physical" ? def.def : def.spd;
    int8 aStage = move.category == "Physical" ? atk.stages[0] : atk.stages[2];
    int8 dStage = move.category == "Physical" ? def.stages[1] : def.stages[3];
    attack = static_cast<uint32>(std::max(1.f, attack * BmStageMul(aStage) * atkMul));
    float defMul = BmTargetDefMul(def, move, false);
    defense = static_cast<uint32>(std::max(1.f, defense * BmStageMul(dStage) * defMul));

    if (atk.status == BmStatus::BRN && move.category == "Physical" && !BmHasAbility(atk, "GUTS"))
        attack = std::max(1u, attack / 2);

    int32 dmg = static_cast<int32>(((((2 * static_cast<int32>(atk.level) / 5 + 2) * power * static_cast<int32>(attack)
                                      / static_cast<int32>(defense)) / 50) + 2));

    bool stab = move.type == BmType1(atk) || move.type == BmType2(atk);
    if (stab)
        dmg = BmHasAbility(atk, "ADAPTABILITY") ? dmg * 2 : dmg * 3 / 2;

    float t1 = ctx.mgr->TypeChartMul(move.type, BmType1(def));
    float t2 = BmType2(def).empty() ? 1.f : ctx.mgr->TypeChartMul(move.type, BmType2(def));
    eff = t1 * t2;
    dmg = static_cast<int32>(dmg * eff);
    dmg = static_cast<int32>(dmg * BmAfterEffMul(atk, def, eff));

    if (!BmWeatherSuppressed(*ctx.enc, atk, def))
    {
        if (ctx.enc->weather == BmWeather::Rain)
        {
            if (move.type == "WATER")
                dmg = dmg * 3 / 2;
            if (move.type == "FIRE")
                dmg /= 2;
        }
        if (ctx.enc->weather == BmWeather::Sun)
        {
            if (move.type == "FIRE")
                dmg = dmg * 3 / 2;
            if (move.type == "WATER")
                dmg /= 2;
        }
    }

    uint8 critStage = 0;
    if (BmMoveHasFlag(move, "HighCriticalHitRate"))
        ++critStage;
    if (move.functionCode == "AlwaysCriticalHit")
        critStage = 3;
    if (BmHasAbility(def, "BATTLEARMOR") || BmHasAbility(def, "SHELLARMOR"))
        crit = false;
    else if (critStage >= 3)
        crit = true;
    else if (critStage == 2)
        crit = urand(1, 2) == 1;
    else if (critStage == 1)
        crit = urand(1, 8) == 1;
    else
        crit = urand(1, 16) == 1;
    if (crit)
    {
        dmg = dmg * 3 / 2;
        if (BmHasAbility(atk, "SNIPER"))
            dmg = dmg * 3 / 2;
    }

    dmg = dmg * static_cast<int32>(urand(85, 100)) / 100;
    if (dmg < 1 && eff > 0.f)
        dmg = 1;
    return dmg;
}

void BmEndOfRound(BmCtx& ctx, BattlemonBattler& a, BattlemonBattler& b)
{
    auto residual = [&](BattlemonBattler& x) {
        if (x.fainted || x.hp <= 0)
            return;
        if (BmHasAbility(x, "MAGICGUARD"))
            return;
        if (x.status == BmStatus::BRN)
        {
            int32 dmg = std::max(1, x.maxHp / 16);
            BmApplyDamage(ctx, x, dmg, nullptr, nullptr);
            BmMsg(ctx, x.name + " is hurt by its burn!");
        }
        else if (x.status == BmStatus::PSN)
        {
            int32 dmg = std::max(1, x.maxHp / 8);
            BmApplyDamage(ctx, x, dmg, nullptr, nullptr);
            BmMsg(ctx, x.name + " is hurt by poison!");
        }
        else if (x.status == BmStatus::TOX)
        {
            if (x.statusTurns < 15)
                ++x.statusTurns;
            int32 dmg = std::max(1, x.maxHp * x.statusTurns / 16);
            BmApplyDamage(ctx, x, dmg, nullptr, nullptr);
            BmMsg(ctx, x.name + " is hurt by poison!");
        }
    };
    auto weatherChip = [&](BattlemonBattler& x) {
        if (!ctx.enc || x.fainted || x.hp <= 0 || BmHasAbility(x, "MAGICGUARD"))
            return;
        if (BmWeatherSuppressed(*ctx.enc, a, b))
            return;
        if (ctx.enc->weather == BmWeather::Sand)
        {
            if (BmHasType(x, "ROCK") || BmHasType(x, "STEEL") || BmHasType(x, "GROUND")
                || BmHasAbility(x, "SANDVEIL") || BmHasAbility(x, "SANDRUSH") || BmHasAbility(x, "SANDFORCE"))
                return;
            int32 dmg = std::max(1, x.maxHp / 16);
            BmApplyDamage(ctx, x, dmg, nullptr, nullptr);
            BmMsg(ctx, x.name + " is buffeted by the sandstorm!");
        }
        if (ctx.enc->weather == BmWeather::Hail)
        {
            if (BmHasType(x, "ICE") || BmHasAbility(x, "ICEBODY") || BmHasAbility(x, "SNOWCLOAK")
                || BmHasAbility(x, "SLUSHRUSH"))
                return;
            int32 dmg = std::max(1, x.maxHp / 16);
            BmApplyDamage(ctx, x, dmg, nullptr, nullptr);
            BmMsg(ctx, x.name + " is buffeted by the hail!");
        }
    };

    a.protectLastTurn = a.protectThisTurn;
    b.protectLastTurn = b.protectThisTurn;
    a.protectThisTurn = false;
    b.protectThisTurn = false;
    a.flinch = false;
    b.flinch = false;

    if (ctx.enc && ctx.enc->weather != BmWeather::None && ctx.enc->weatherTurns != 255)
    {
        if (ctx.enc->weatherTurns > 0)
            --ctx.enc->weatherTurns;
        if (ctx.enc->weatherTurns == 0)
        {
            BmMsg(ctx, "The weather returned to normal!");
            ctx.enc->weather = BmWeather::None;
        }
    }

    auto heldTick = [&](BattlemonBattler& x) {
        if (x.fainted || x.hp <= 0)
            return;
        int32 const change = BattlemonHeldItems::EndOfRoundHp(x.heldItem, x.maxHp, BmHasType(x, "POISON"));
        if (change > 0 && x.hp < x.maxHp)
        {
            x.hp = std::min(x.maxHp, x.hp + change);
            BmMsg(ctx, x.name + " restored a little HP using its " + BmItemName(ctx, x.heldItem) + "!");
        }
        else if (change < 0 && !BmHasAbility(x, "MAGICGUARD"))
        {
            BmApplyDamage(ctx, x, -change, nullptr, nullptr);
            BmMsg(ctx, x.name + " was hurt by its " + BmItemName(ctx, x.heldItem) + "!");
        }
    };

    weatherChip(a);
    weatherChip(b);
    residual(a);
    residual(b);
    heldTick(a);
    heldTick(b);
    BmHeldItemCheck(ctx, a);
    BmHeldItemCheck(ctx, b);
    BmEndOfRoundAbility(ctx, a, *ctx.enc, b);
    BmEndOfRoundAbility(ctx, b, *ctx.enc, a);

    auto yawnTick = [&](BattlemonBattler& x) {
        if (x.yawn == 0 || x.fainted)
            return;
        --x.yawn;
        if (x.yawn == 0)
            BmTryStatus(ctx, x, nullptr, BmStatus::SLP, true);
    };
    yawnTick(a);
    yawnTick(b);
}

void BmExecuteMove(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, BattlemonSlot& slot, bool isPlayer)
{
    BattlemonMoveDef const* mv = slot.def;
    if (!mv)
        return;

    if (user.charging && !user.chargeMove.empty())
    {
        // forced continuation
    }

    if (ctx.animation)
        ctx.animation(isPlayer, mv->internalName);
    else if (ctx.session && ctx.session->player && ctx.mgr)
        ctx.mgr->SendMoveAnimation(ctx.session->player, isPlayer, mv->internalName);

    bool twoTurn = BmIsTwoTurnMove(*mv);
    bool sunSkip = twoTurn && mv->functionCode.find("OneTurnInSun") != std::string::npos
        && ctx.enc && ctx.enc->weather == BmWeather::Sun && !BmWeatherSuppressed(*ctx.enc, user, target);

    if (twoTurn && !user.charging && !sunSkip)
    {
        user.charging = true;
        user.chargeMove = mv->internalName;
        user.semiInvuln = mv->functionCode.find("Invulnerable") != std::string::npos;
        BmMsg(ctx, user.name + " used " + mv->name + "!");
        if (user.semiInvuln)
            BmMsg(ctx, user.name + " sprang up!");
        else
            BmMsg(ctx, user.name + " is charging up!");
        if (mv->functionCode.find("ChargeRaiseUserDefense1") != std::string::npos)
            BmChangeStage(ctx, user, &user, BmStat::Def, 1, true);
        if (mv->functionCode.find("ChargeRaiseUserSpAtk1") != std::string::npos)
            BmChangeStage(ctx, user, &user, BmStat::Spa, 1, true);
        return;
    }
    if (user.charging)
    {
        user.charging = false;
        user.semiInvuln = false;
        user.chargeMove.clear();
    }

    BmMsg(ctx, user.name + " used " + mv->name + "!");

    if (BmIsProtectMove(*mv))
    {
        if (user.protectLastTurn)
        {
            BmMsg(ctx, "But it failed!");
            return;
        }
        user.protectThisTurn = true;
        BmMsg(ctx, user.name + " protected itself!");
        return;
    }

    if (target.protectThisTurn && mv->power > 0)
    {
        BmMsg(ctx, target.name + " protected itself!");
        return;
    }
    if (target.semiInvuln)
    {
        BmMsg(ctx, user.name + "'s attack missed!");
        return;
    }

    if (BmImmuneToMove(ctx, user, target, *mv, true))
        return;

    if (BmIsOHKOMove(*mv))
    {
        if (user.level < target.level || (mv->functionCode.find("Ice") != std::string::npos && BmHasType(target, "ICE")))
        {
            BmMsg(ctx, "It doesn't affect " + target.name + "...");
            return;
        }
        if (urand(1, 100) > 30)
        {
            BmMsg(ctx, user.name + "'s attack missed!");
            return;
        }
        BmApplyDamage(ctx, target, target.hp, &user, mv);
        BmMsg(ctx, "It's a one-hit KO!");
        BmOnBeingHit(ctx, user, target, *mv);
        return;
    }

    int32 acc = mv->accuracy;
    if (acc > 0)
    {
        float aMul = BmAccStageMul(user.stages[5]) / BmAccStageMul(0);
        // target acc stage is used as evasion inverse: we only stored Acc, not Eva.
        aMul *= BmAccuracyAbilityMul(user, target);
        aMul *= BmEvasionWeatherMul(target, *ctx.enc, user);
        int32 chance = static_cast<int32>(acc * aMul);
        if (chance < 1)
            chance = 1;
        if (urand(1, 100) > chance)
        {
            BmMsg(ctx, user.name + "'s attack missed!");
            return;
        }
    }

    bool statusMove = mv->category == "Status" || mv->power <= 0;
    if (statusMove)
    {
        if (mv->functionCode.empty() || mv->functionCode == "None")
        {
            BmMsg(ctx, "But it failed!");
            return;
        }
        if (!BmApplyFunctionCode(ctx, user, target, *mv, 0, false, false))
            BmMsg(ctx, "But it failed!");
        if (BmIsRechargeMove(*mv))
            user.mustRecharge = true;
        return;
    }

    float typeEff = 1.f;
    if (ctx.mgr)
    {
        typeEff = ctx.mgr->TypeChartMul(mv->type, BmType1(target));
        if (!BmType2(target).empty())
            typeEff *= ctx.mgr->TypeChartMul(mv->type, BmType2(target));
    }
    if (BmHasAbility(target, "WONDERGUARD") && typeEff <= 1.f)
    {
        BmMsg(ctx, "It doesn't affect " + target.name + "...");
        return;
    }
    if (typeEff == 0.f)
    {
        BmMsg(ctx, "It doesn't affect " + target.name + "...");
        return;
    }

    uint8 hits = BmHitCount(*mv);
    int32 total = 0;
    bool anyCrit = false;
    float lastEff = 1.f;
    for (uint8 h = 0; h < hits && !target.fainted && target.hp > 0; ++h)
    {
        bool crit = false;
        float eff = 1.f;
        int32 dmg = BmCalcDamage(ctx, user, target, *mv, crit, eff, hits);
        lastEff = eff;
        if (crit)
            anyCrit = true;
        BmApplyDamage(ctx, target, dmg, &user, mv);
        total += dmg;
    }
    if (hits > 1)
        BmMsg(ctx, "Hit " + std::to_string(uint32(std::min<uint8>(hits, 5))) + " times!");
    if (anyCrit)
        BmMsg(ctx, "A critical hit!");
    if (lastEff > 1.f)
        BmMsg(ctx, "It's super effective!");
    else if (lastEff > 0.f && lastEff < 1.f)
        BmMsg(ctx, "It's not very effective...");

    if (BmHasAbility(user, "SHEERFORCE") && mv->effectChance > 0)
        ;
    else
    {
        int32 chance = mv->effectChance;
        if (BmHasAbility(user, "SERENEGRACE"))
            chance *= 2;
        bool applyAdd = chance <= 0 || urand(1, 100) <= static_cast<uint32>(std::min(chance, 100));
        if (BmHasAbility(target, "SHIELDDUST") && chance > 0)
            applyAdd = false;
        if (applyAdd)
            BmApplyFunctionCode(ctx, user, target, *mv, total, target.fainted, chance > 0);
    }

    float recoil = BmRecoilFraction(*mv);
    if (recoil > 0.f && total > 0 && !BmHasAbility(user, "ROCKHEAD") && !BmHasAbility(user, "MAGICGUARD"))
    {
        int32 rd = std::max(1, static_cast<int32>(total * recoil));
        BmApplyDamage(ctx, user, rd, nullptr, nullptr);
        BmMsg(ctx, user.name + " is damaged by recoil!");
    }

    if (total > 0 && !user.fainted && !BmHasAbility(user, "MAGICGUARD"))
    {
        int32 const orb = BattlemonHeldItems::LifeOrbRecoil(user.heldItem, user.maxHp);
        if (orb > 0)
        {
            BmApplyDamage(ctx, user, orb, nullptr, nullptr);
            BmMsg(ctx, user.name + " lost some of its HP!");
        }
    }

    if (mv->type == "FIRE" && target.status == BmStatus::FRZ)
    {
        target.status = BmStatus::None;
        BmMsg(ctx, target.name + " thawed out!");
    }

    BmOnBeingHit(ctx, user, target, *mv);
    BmHeldItemCheck(ctx, target);
    BmHeldItemCheck(ctx, user);

    if (BmIsRechargeMove(*mv))
        user.mustRecharge = true;
}

void BmRunSingleAction(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, BattlemonSlot* slot, bool isPlayer)
{
    if (user.charging)
    {
        BattlemonSlot dummy;
        dummy.def = ctx.mgr ? ctx.mgr->GetMove(user.chargeMove) : nullptr;
        if (!dummy.def && slot)
            dummy.def = slot->def;
        if (dummy.def)
            BmExecuteMove(ctx, user, target, dummy, isPlayer);
        return;
    }
    if (!BmCanAct(ctx, user, target))
        return;
    if (!slot || !slot->def)
        return;
    if (slot->pp > 0)
        --slot->pp;
    // A Choice item locks the holder into the first move it uses, until it leaves the field.
    if (BattlemonHeldItems::IsChoice(user.heldItem) && user.choiceMove.empty())
        user.choiceMove = slot->def->internalName;
    BmExecuteMove(ctx, user, target, *slot, isPlayer);
}
