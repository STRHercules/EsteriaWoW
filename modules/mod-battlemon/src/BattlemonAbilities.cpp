#include "BattlemonBattle.h"
#include "BattlemonMgr.h"

#include "Player.h"
#include "Random.h"

#include <algorithm>
#include <cstring>
#include <vector>

bool BmHasAbility(BattlemonBattler const& b, char const* id)
{
    return !b.ability.empty() && b.ability == id;
}

bool BmMoveHasFlag(BattlemonMoveDef const& m, char const* flag)
{
    if (m.flags.empty() || !flag)
        return false;
    std::string const& f = m.flags;
    size_t start = 0;
    size_t n = std::strlen(flag);
    while (start <= f.size())
    {
        size_t comma = f.find(',', start);
        size_t len = (comma == std::string::npos ? f.size() : comma) - start;
        while (len && f[start] == ' ')
        {
            ++start;
            --len;
        }
        if (len == n && f.compare(start, len, flag) == 0)
            return true;
        if (comma == std::string::npos)
            break;
        start = comma + 1;
    }
    return false;
}

bool BmHasType(BattlemonBattler const& b, char const* type)
{
    if (!type)
        return false;
    return BmType1(b) == type || BmType2(b) == type;
}

std::string BmType1(BattlemonBattler const& b)
{
    if (b.typeOverridden)
        return b.typeOverride1;
    return b.species ? b.species->type1 : "";
}

std::string BmType2(BattlemonBattler const& b)
{
    if (b.typeOverridden)
        return b.typeOverride2;
    return b.species ? b.species->type2 : "";
}

std::string BmPickAbility(BattlemonSpecies const* s)
{
    if (!s)
        return "";
    if (!s->ability2.empty() && urand(0, 1))
        return s->ability2;
    return s->ability1;
}

void BmResetStages(BattlemonBattler& b)
{
    for (int i = 0; i < 6; ++i)
        b.stages[i] = 0;
}

void BmInitBattler(BattlemonBattler& b)
{
    b.ability = BmPickAbility(b.species);
    b.status = BmStatus::None;
    b.statusTurns = 0;
    b.confuseTurns = 0;
    b.flinch = false;
    BmResetStages(b);
    b.protectThisTurn = false;
    b.protectLastTurn = false;
    b.charging = false;
    b.chargeMove.clear();
    b.semiInvuln = false;
    b.mustRecharge = false;
    b.flashFire = false;
    b.yawn = 0;
    b.typeOverridden = false;
    b.typeOverride1.clear();
    b.typeOverride2.clear();
}

bool BmStatusImmune(BattlemonBattler const& b, BmStatus st)
{
    switch (st)
    {
        case BmStatus::PAR:
            return BmHasAbility(b, "LIMBER") || BmHasType(b, "ELECTRIC");
        case BmStatus::SLP:
            return BmHasAbility(b, "INSOMNIA") || BmHasAbility(b, "VITALSPIRIT");
        case BmStatus::PSN:
        case BmStatus::TOX:
            return BmHasAbility(b, "IMMUNITY") || BmHasType(b, "POISON") || BmHasType(b, "STEEL");
        case BmStatus::BRN:
            return BmHasAbility(b, "WATERVEIL") || BmHasType(b, "FIRE");
        case BmStatus::FRZ:
            return BmHasAbility(b, "MAGMAARMOR") || BmHasType(b, "ICE");
        default:
            return false;
    }
}

bool BmStatLossBlocked(BattlemonBattler const& target, BattlemonBattler const* source)
{
    if (source == &target)
        return false;
    return BmHasAbility(target, "CLEARBODY") || BmHasAbility(target, "FULLMETALBODY")
        || BmHasAbility(target, "WHITESMOKE");
}

float BmSpeedWeatherMul(BattlemonBattler const& b, BattlemonEncounter const& enc)
{
    if (enc.weather == BmWeather::None)
        return 1.f;
    if (BmHasAbility(b, "AIRLOCK") || BmHasAbility(b, "CLOUDNINE"))
        return 1.f;
    // foe weather suppression checked by caller via enc still applying; Air Lock on either side
    if (enc.weather == BmWeather::Rain)
    {
        if (BmHasAbility(b, "SWIFTSWIM"))
            return 2.f;
    }
    else if (enc.weather == BmWeather::Sun)
    {
        if (BmHasAbility(b, "CHLOROPHYLL"))
            return 2.f;
    }
    else if (enc.weather == BmWeather::Sand)
    {
        if (BmHasAbility(b, "SANDRUSH"))
            return 2.f;
    }
    else if (enc.weather == BmWeather::Hail)
    {
        if (BmHasAbility(b, "SLUSHRUSH"))
            return 2.f;
    }
    return 1.f;
}

bool BmWeatherSuppressed(BattlemonEncounter const& enc, BattlemonBattler const& a, BattlemonBattler const& b)
{
    (void)enc;
    return BmHasAbility(a, "AIRLOCK") || BmHasAbility(a, "CLOUDNINE")
        || BmHasAbility(b, "AIRLOCK") || BmHasAbility(b, "CLOUDNINE");
}

float BmAccuracyAbilityMul(BattlemonBattler const& user, BattlemonBattler const& target)
{
    float m = 1.f;
    if (BmHasAbility(user, "COMPOUNDEYES"))
        m *= 1.3f;
    if (BmHasAbility(user, "HUSTLE") )
        m *= 0.8f;
    return m;
}

float BmEvasionWeatherMul(BattlemonBattler const& target, BattlemonEncounter const& enc, BattlemonBattler const& other)
{
    if (BmWeatherSuppressed(enc, target, other))
        return 1.f;
    if (enc.weather == BmWeather::Sand && BmHasAbility(target, "SANDVEIL"))
        return 0.8f; // applied to accuracy of attacker
    if (enc.weather == BmWeather::Hail && BmHasAbility(target, "SNOWCLOAK"))
        return 0.8f;
    return 1.f;
}

void BmOnSwitchOut(BattlemonBattler& leaving)
{
    if (BmHasAbility(leaving, "NATURALCURE"))
    {
        leaving.status = BmStatus::None;
        leaving.statusTurns = 0;
    }
    leaving.flinch = false;
    leaving.protectThisTurn = false;
    leaving.charging = false;
    leaving.chargeMove.clear();
    leaving.semiInvuln = false;
    leaving.mustRecharge = false;
    leaving.yawn = 0;
    BmResetStages(leaving);
}

void BmOnSwitchIn(BmCtx& ctx, BattlemonBattler& incoming, BattlemonBattler& foe)
{
    if (incoming.fainted || incoming.hp <= 0)
        return;
    if (BmHasAbility(incoming, "INTIMIDATE"))
    {
        BmMsg(ctx, incoming.name + "'s Intimidate cuts " + foe.name + "'s Attack!");
        BmChangeStage(ctx, foe, &incoming, BmStat::Atk, -1, false);
    }
    if (BmHasAbility(incoming, "DRIZZLE"))
        BmSetWeather(ctx, BmWeather::Rain, 255, &incoming);
    if (BmHasAbility(incoming, "DROUGHT"))
        BmSetWeather(ctx, BmWeather::Sun, 255, &incoming);
    if (BmHasAbility(incoming, "SANDSTREAM"))
        BmSetWeather(ctx, BmWeather::Sand, 255, &incoming);
    if (BmHasAbility(incoming, "SNOWWARNING"))
        BmSetWeather(ctx, BmWeather::Hail, 255, &incoming);
    if (BmHasAbility(incoming, "TRACE") && !foe.ability.empty() && foe.ability != "TRACE")
    {
        incoming.ability = foe.ability;
        BmMsg(ctx, incoming.name + " traced " + foe.name + "'s " + incoming.ability + "!");
        if (BmHasAbility(incoming, "INTIMIDATE"))
            BmChangeStage(ctx, foe, &incoming, BmStat::Atk, -1, false);
        if (BmHasAbility(incoming, "DRIZZLE"))
            BmSetWeather(ctx, BmWeather::Rain, 255, &incoming);
        if (BmHasAbility(incoming, "DROUGHT"))
            BmSetWeather(ctx, BmWeather::Sun, 255, &incoming);
        if (BmHasAbility(incoming, "SANDSTREAM"))
            BmSetWeather(ctx, BmWeather::Sand, 255, &incoming);
        if (BmHasAbility(incoming, "SNOWWARNING"))
            BmSetWeather(ctx, BmWeather::Hail, 255, &incoming);
    }
    if (BmHasAbility(incoming, "PRESSURE"))
        BmMsg(ctx, incoming.name + " is exerting its Pressure!");
}

bool BmImmuneToMove(BmCtx& ctx, BattlemonBattler const& user, BattlemonBattler& target, BattlemonMoveDef const& move, bool show)
{
    auto fail = [&](std::string const& why) {
        if (show)
            BmMsg(ctx, why);
        return true;
    };
    if (BmMoveHasFlag(move, "Sound") && BmHasAbility(target, "SOUNDPROOF"))
        return fail(target.name + "'s Soundproof blocked the move!");
    if (BmMoveHasFlag(move, "Powder") && (BmHasAbility(target, "OVERCOAT") || BmHasType(target, "GRASS")))
        return fail("It doesn't affect " + target.name + "...");
    if (BmMoveHasFlag(move, "Bullet") && BmHasAbility(target, "BULLETPROOF"))
        return fail(target.name + "'s Bulletproof blocked the move!");

    if (move.type == "GROUND" && BmHasAbility(target, "LEVITATE"))
        return fail(target.name + "'s Levitate makes it immune to Ground!");
    if (move.type == "FIRE" && BmHasAbility(target, "FLASHFIRE"))
    {
        target.flashFire = true;
        return fail(target.name + "'s Flash Fire absorbed the Fire move!");
    }
    if (move.type == "ELECTRIC")
    {
        if (BmHasAbility(target, "VOLTABSORB"))
        {
            int32 heal = std::max(1, target.maxHp / 4);
            target.hp = std::min(target.maxHp, target.hp + heal);
            return fail(target.name + "'s Volt Absorb restored HP!");
        }
        if (BmHasAbility(target, "LIGHTNINGROD"))
        {
            BmChangeStage(ctx, target, &target, BmStat::Spa, 1, true);
            return fail(target.name + "'s Lightning Rod raised Sp. Atk!");
        }
        if (BmHasAbility(target, "MOTORDRIVE"))
        {
            BmChangeStage(ctx, target, &target, BmStat::Spe, 1, true);
            return fail(target.name + "'s Motor Drive raised Speed!");
        }
    }
    if (move.type == "WATER")
    {
        if (BmHasAbility(target, "WATERABSORB") || BmHasAbility(target, "DRYSKIN"))
        {
            int32 heal = std::max(1, target.maxHp / 4);
            target.hp = std::min(target.maxHp, target.hp + heal);
            return fail(target.name + " restored HP!");
        }
        if (BmHasAbility(target, "STORMDRAIN"))
        {
            BmChangeStage(ctx, target, &target, BmStat::Spa, 1, true);
            return fail(target.name + "'s Storm Drain raised Sp. Atk!");
        }
    }
    if (move.type == "GRASS" && BmHasAbility(target, "SAPSIPPER"))
    {
        BmChangeStage(ctx, target, &target, BmStat::Atk, 1, true);
        return fail(target.name + "'s Sap Sipper raised Attack!");
    }
    if (BmHasAbility(target, "WONDERGUARD"))
    {
        float eff = 1.f;
        if (ctx.mgr)
        {
            bool crit = false;
            // type-only: use TypeMult via a dummy calc path
            std::string t1 = BmType1(target);
            std::string t2 = BmType2(target);
            float m = 1.f;
            // Effectiveness is computed in BmCalcDamage; approximate here
            (void)crit;
            (void)m;
        }
        // Wonder Guard checked after type chart in execute
    }
    (void)user;
    return false;
}

void BmOnBeingHit(BmCtx& ctx, BattlemonBattler& user, BattlemonBattler& target, BattlemonMoveDef const& move)
{
    if (target.fainted || target.hp <= 0)
        return;
    if (BmHasAbility(target, "COLORCHANGE") && !move.type.empty())
    {
        target.typeOverridden = true;
        target.typeOverride1 = move.type;
        target.typeOverride2.clear();
        BmMsg(ctx, target.name + "'s Color Change made it " + move.type + " type!");
    }
    if (!BmMoveHasFlag(move, "Contact"))
        return;
    if (BmHasAbility(target, "ROUGHSKIN") || BmHasAbility(target, "IRONBARBS"))
    {
        if (!BmHasAbility(user, "MAGICGUARD"))
        {
            int32 dmg = std::max(1, user.maxHp / 8);
            BmApplyDamage(ctx, user, dmg, nullptr, nullptr);
            BmMsg(ctx, user.name + " was hurt by " + target.name + "'s " + target.ability + "!");
        }
    }
    if (BmHasAbility(target, "STATIC") && urand(1, 100) <= 30)
        BmTryStatus(ctx, user, &target, BmStatus::PAR, true);
    if (BmHasAbility(target, "POISONPOINT") && urand(1, 100) <= 30)
        BmTryStatus(ctx, user, &target, BmStatus::PSN, true);
    if (BmHasAbility(target, "FLAMEBODY") && urand(1, 100) <= 30)
        BmTryStatus(ctx, user, &target, BmStatus::BRN, true);
    if (BmHasAbility(target, "EFFECTSPORE") && urand(1, 100) <= 30)
    {
        uint32 r = urand(0, 2);
        BmStatus st = r == 0 ? BmStatus::PSN : (r == 1 ? BmStatus::PAR : BmStatus::SLP);
        BmTryStatus(ctx, user, &target, st, true);
    }
}

void BmEndOfRoundAbility(BmCtx& ctx, BattlemonBattler& b, BattlemonEncounter& enc, BattlemonBattler const& other)
{
    if (b.fainted || b.hp <= 0)
        return;
    bool weatherOff = BmWeatherSuppressed(enc, b, other);
    if (BmHasAbility(b, "SPEEDBOOST"))
        BmChangeStage(ctx, b, &b, BmStat::Spe, 1, true);
    if (BmHasAbility(b, "SHEDSKIN") && b.status != BmStatus::None && urand(1, 100) <= 33)
    {
        b.status = BmStatus::None;
        b.statusTurns = 0;
        BmMsg(ctx, b.name + "'s Shed Skin cured its status!");
    }
    if (!weatherOff && enc.weather == BmWeather::Rain && BmHasAbility(b, "HYDRATION") && b.status != BmStatus::None)
    {
        b.status = BmStatus::None;
        b.statusTurns = 0;
        BmMsg(ctx, b.name + "'s Hydration cured its status!");
    }
    if (!weatherOff && enc.weather == BmWeather::Rain && (BmHasAbility(b, "RAINDISH") || BmHasAbility(b, "DRYSKIN")))
    {
        int32 heal = std::max(1, b.maxHp / 16);
        if (BmHasAbility(b, "DRYSKIN"))
            heal = std::max(1, b.maxHp / 8);
        b.hp = std::min(b.maxHp, b.hp + heal);
        BmMsg(ctx, b.name + " restored a little HP!");
    }
    if (!weatherOff && enc.weather == BmWeather::Sun && BmHasAbility(b, "SOLARPOWER") && !BmHasAbility(b, "MAGICGUARD"))
    {
        int32 dmg = std::max(1, b.maxHp / 8);
        BmApplyDamage(ctx, b, dmg, nullptr, nullptr);
        BmMsg(ctx, b.name + " is hurt by Solar Power!");
    }
    if (!weatherOff && enc.weather == BmWeather::Sun && BmHasAbility(b, "DRYSKIN") && !BmHasAbility(b, "MAGICGUARD"))
    {
        int32 dmg = std::max(1, b.maxHp / 8);
        BmApplyDamage(ctx, b, dmg, nullptr, nullptr);
        BmMsg(ctx, b.name + " is hurt by Dry Skin!");
    }
    if (!weatherOff && enc.weather == BmWeather::Hail && BmHasAbility(b, "ICEBODY"))
    {
        int32 heal = std::max(1, b.maxHp / 16);
        b.hp = std::min(b.maxHp, b.hp + heal);
        BmMsg(ctx, b.name + "'s Ice Body restored HP!");
    }
}

float BmUserAtkMul(BattlemonBattler const& user, BattlemonMoveDef const& move)
{
    float m = 1.f;
    if ((BmHasAbility(user, "HUGEPOWER") || BmHasAbility(user, "PUREPOWER")) && move.category == "Physical")
        m *= 2.f;
    if (BmHasAbility(user, "GUTS") && user.status != BmStatus::None && move.category == "Physical")
        m *= 1.5f;
    if (BmHasAbility(user, "HUSTLE") && move.category == "Physical")
        m *= 1.5f;
    if (BmHasAbility(user, "IRONFIST") && (BmMoveHasFlag(move, "Punch") || BmMoveHasFlag(move, "Punching")))
        m *= 1.2f;
    if (BmHasAbility(user, "TECHNICIAN") && move.power > 0 && move.power <= 60)
        m *= 1.5f;
    if (BmHasAbility(user, "SHEERFORCE") && move.effectChance > 0)
        m *= 1.3f;
    if (user.flashFire && move.type == "FIRE")
        m *= 1.5f;
    return m;
}

float BmTargetDefMul(BattlemonBattler const& target, BattlemonMoveDef const& move, bool /*crit*/)
{
    float m = 1.f;
    if (BmHasAbility(target, "MARVELSCALE") && target.status != BmStatus::None && move.category == "Physical")
        m *= 1.5f;
    if (BmHasAbility(target, "THICKFAT") && (move.type == "FIRE" || move.type == "ICE"))
        m *= 0.5f;
    if (BmHasAbility(target, "ICESCALES") && move.category == "Special")
        m *= 0.5f;
    if (BmHasAbility(target, "FLUFFY") && BmMoveHasFlag(move, "Contact"))
        m *= 0.5f;
    if (BmHasAbility(target, "FLUFFY") && move.type == "FIRE")
        m *= 2.f;
    return m;
}

float BmAfterEffMul(BattlemonBattler const& user, BattlemonBattler const& target, float eff)
{
    float m = 1.f;
    if (eff > 1.f && (BmHasAbility(target, "FILTER") || BmHasAbility(target, "SOLIDROCK")))
        m *= 0.75f;
    if (eff > 1.f && BmHasAbility(user, "NEUROFORCE"))
        m *= 1.25f;
    if (eff < 1.f && eff > 0.f && BmHasAbility(user, "TINTEDLENS"))
        m *= 2.f;
    if (target.hp == target.maxHp && BmHasAbility(target, "MULTISCALE"))
        m *= 0.5f;
    return m;
}
