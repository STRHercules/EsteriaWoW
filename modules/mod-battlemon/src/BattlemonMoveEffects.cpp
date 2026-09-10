#include "BattlemonBattle.h"
#include "BattlemonMgr.h"

#include "Random.h"

#include <algorithm>
#include <cctype>
#include <cstring>
#include <vector>

bool BmIsProtectMove(BattlemonMoveDef const& move)
{
    return move.functionCode.find("ProtectUser") != std::string::npos;
}

bool BmIsOHKOMove(BattlemonMoveDef const& move)
{
    return move.functionCode.find("OHKO") != std::string::npos;
}

bool BmIsTwoTurnMove(BattlemonMoveDef const& move)
{
    return move.functionCode.find("TwoTurnAttack") != std::string::npos
        || move.functionCode == "TwoTurnAttackOneTurnInSun";
}

bool BmIsRechargeMove(BattlemonMoveDef const& move)
{
    return move.functionCode == "AttackAndSkipNextTurn";
}

bool BmDrainsHalf(BattlemonMoveDef const& move)
{
    return move.functionCode.find("HealUserByHalfOfDamageDone") != std::string::npos;
}

uint8 BmHitCount(BattlemonMoveDef const& move)
{
    std::string const& c = move.functionCode;
    if (c.find("HitTwoToFiveTimes") != std::string::npos)
    {
        uint32 r = urand(1, 100);
        if (r <= 35)
            return 2;
        if (r <= 70)
            return 3;
        if (r <= 85)
            return 4;
        return 5;
    }
    if (c.find("HitTwoTimes") != std::string::npos || c.find("HitThreeTimes") != std::string::npos)
        return c.find("HitThreeTimes") != std::string::npos ? 3 : 2;
    return 1;
}

float BmRecoilFraction(BattlemonMoveDef const& move)
{
    std::string const& c = move.functionCode;
    if (c.find("RecoilHalfOfDamageDealt") != std::string::npos)
        return 0.5f;
    if (c.find("RecoilThirdOfDamageDealt") != std::string::npos)
        return 1.f / 3.f;
    if (c.find("RecoilQuarterOfDamageDealt") != std::string::npos
        || c.find("Recoil1/4") != std::string::npos)
        return 0.25f;
    if (c.find("Recoil") != std::string::npos && c.find("Damage") != std::string::npos)
        return 0.25f;
    return 0.f;
}

namespace
{
    int8 DigitAtEnd(std::string const& s)
    {
        if (s.empty())
            return 1;
        char c = s.back();
        if (c >= '1' && c <= '6')
            return static_cast<int8>(c - '0');
        return 1;
    }

    bool StartsWith(std::string const& s, char const* p)
    {
        size_t n = std::strlen(p);
        return s.size() >= n && s.compare(0, n, p) == 0;
    }

    std::vector<BmStat> ParseStats(std::string body)
    {
        std::vector<BmStat> out;
        auto eat = [&](char const* tok, BmStat st) -> bool {
            size_t n = std::strlen(tok);
            if (body.size() >= n && body.compare(0, n, tok) == 0)
            {
                out.push_back(st);
                body.erase(0, n);
                return true;
            }
            return false;
        };
        while (!body.empty())
        {
            if (StartsWith(body, "MainStats"))
            {
                out.push_back(BmStat::Atk);
                out.push_back(BmStat::Def);
                out.push_back(BmStat::Spa);
                out.push_back(BmStat::Spd);
                out.push_back(BmStat::Spe);
                body.erase(0, 9);
                continue;
            }
            if (eat("SpAtk", BmStat::Spa) || eat("SpDef", BmStat::Spd) || eat("Attack", BmStat::Atk)
                || eat("Defense", BmStat::Def) || eat("Speed", BmStat::Spe) || eat("Accuracy", BmStat::Acc)
                || eat("Atk", BmStat::Atk) || eat("Def", BmStat::Def) || eat("Acc", BmStat::Acc)
                || eat("Spe", BmStat::Spe) || eat("Spa", BmStat::Spa) || eat("Spd", BmStat::Spd))
                continue;
            body.erase(0, 1);
        }
        return out;
    }

    bool TryStatCode(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, std::string const& code)
    {
        int sign = 0;
        bool onUser = true;
        std::string rest;
        size_t pos;
        if ((pos = code.find("RaiseTarget")) != std::string::npos)
        {
            sign = 1;
            onUser = false;
            rest = code.substr(pos + 11);
        }
        else if ((pos = code.find("LowerTarget")) != std::string::npos)
        {
            sign = -1;
            onUser = false;
            rest = code.substr(pos + 11);
        }
        else if ((pos = code.find("RaiseUser")) != std::string::npos)
        {
            sign = 1;
            onUser = true;
            rest = code.substr(pos + 9);
        }
        else if ((pos = code.find("LowerUser")) != std::string::npos)
        {
            sign = -1;
            onUser = true;
            rest = code.substr(pos + 9);
        }
        else
            return false;
        if (rest.find("IfTargetFaints") != std::string::npos)
            return true; // handled by caller after faint
        if (rest.find("IfUserStats") != std::string::npos)
            return false;
        int8 mag = DigitAtEnd(rest);
        if (!rest.empty() && std::isdigit(static_cast<unsigned char>(rest.back())))
            rest.pop_back();
        auto stats = ParseStats(rest);
        if (stats.empty())
            return false;
        BattlemonBattler& who = onUser ? user : target;
        for (BmStat st : stats)
            BmChangeStage(ctx, who, &user, st, static_cast<int8>(sign * mag), onUser);
        return true;
    }

    bool TryStatusCode(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, std::string const& code)
    {
        bool matched = false;
        if (code.find("SleepTargetNextTurn") != std::string::npos)
        {
            if (target.yawn == 0 && !BmStatusImmune(target, BmStatus::SLP) && target.status == BmStatus::None)
            {
                target.yawn = 2;
                BmMsg(ctx, user.name + " made " + target.name + " drowsy!");
            }
            return true;
        }
        if (code.find("SleepTarget") != std::string::npos)
        {
            matched = true;
            BmTryStatus(ctx, target, &user, BmStatus::SLP, true);
        }
        if (code.find("BadPoisonTarget") != std::string::npos)
        {
            matched = true;
            BmTryStatus(ctx, target, &user, BmStatus::TOX, true);
        }
        else if (code.find("PoisonTarget") != std::string::npos)
        {
            matched = true;
            BmTryStatus(ctx, target, &user, BmStatus::PSN, true);
        }
        if (code.find("BurnTarget") != std::string::npos)
        {
            matched = true;
            BmTryStatus(ctx, target, &user, BmStatus::BRN, true);
        }
        if (code.find("ParalyzeTarget") != std::string::npos)
        {
            matched = true;
            BmTryStatus(ctx, target, &user, BmStatus::PAR, true);
        }
        if (code.find("FreezeTarget") != std::string::npos)
        {
            matched = true;
            BmTryStatus(ctx, target, &user, BmStatus::FRZ, true);
        }
        if (code.find("ConfuseTarget") != std::string::npos)
        {
            matched = true;
            if (!BmHasAbility(target, "OWNTEMPO") && target.confuseTurns == 0)
            {
                target.confuseTurns = static_cast<uint8>(urand(2, 5));
                BmMsg(ctx, target.name + " became confused!");
            }
        }
        if (code.find("FlinchTarget") != std::string::npos)
        {
            matched = true;
            if (!BmHasAbility(target, "INNERFOCUS"))
                target.flinch = true;
        }
        return matched;
    }
}

bool BmApplyFunctionCode(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target,
                         BattlemonMoveDef const& move, int32 damage, bool targetFainted, bool additional)
{
    std::string const& c = move.functionCode;
    if (c.empty() || c == "None")
        return false;

    bool did = false;
    if (c.find("IfTargetFaints") != std::string::npos)
    {
        if (targetFainted)
            did = TryStatCode(ctx, user, target, c);
        return did;
    }

    if (BmDrainsHalf(move) && damage > 0)
    {
        int32 heal = std::max(1, damage / 2);
        user.hp = std::min(user.maxHp, user.hp + heal);
        BmMsg(ctx, user.name + " restored HP!");
        did = true;
    }
    if (c == "HealUserHalfOfTotalHP")
    {
        int32 heal = std::max(1, user.maxHp / 2);
        user.hp = std::min(user.maxHp, user.hp + heal);
        BmMsg(ctx, user.name + " restored HP!");
        return true;
    }
    if (c == "HealUserDependingOnWeather")
    {
        int32 denom = 2;
        if (ctx.enc && !BmWeatherSuppressed(*ctx.enc, user, target))
        {
            if (ctx.enc->weather == BmWeather::Rain || ctx.enc->weather == BmWeather::Sand
                || ctx.enc->weather == BmWeather::Hail)
                denom = 4;
        }
        int32 heal = std::max(1, user.maxHp / denom);
        if (ctx.enc && !BmWeatherSuppressed(*ctx.enc, user, target) && ctx.enc->weather == BmWeather::Sun)
            heal = std::max(1, user.maxHp * 2 / 3);
        user.hp = std::min(user.maxHp, user.hp + heal);
        BmMsg(ctx, user.name + " restored HP!");
        return true;
    }

    if (c.find("StartRain") != std::string::npos)
    {
        BmSetWeather(ctx, BmWeather::Rain, 5, &user);
        did = true;
    }
    else if (c.find("StartSun") != std::string::npos || c.find("StartSunny") != std::string::npos)
    {
        BmSetWeather(ctx, BmWeather::Sun, 5, &user);
        did = true;
    }
    else if (c.find("StartSandstorm") != std::string::npos)
    {
        BmSetWeather(ctx, BmWeather::Sand, 5, &user);
        did = true;
    }
    else if (c.find("StartHail") != std::string::npos || c.find("StartSnow") != std::string::npos)
    {
        BmSetWeather(ctx, BmWeather::Hail, 5, &user);
        did = true;
    }

    if (c == "SwitchOutUserDamagingMove")
    {
        ctx.uturn = true;
        did = true;
    }

    if (c.find("ChargeRaise") == std::string::npos && TryStatCode(ctx, user, target, c))
        did = true;
    if (TryStatusCode(ctx, user, target, c))
        did = true;
    (void)additional;
    return did;
}
