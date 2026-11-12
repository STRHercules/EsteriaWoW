#ifndef ESTERIA_PERK_TRAIT_RULES_H
#define ESTERIA_PERK_TRAIT_RULES_H

#include "PerkTraitWire.h"
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>

// Paths of Fate starting traits: the point budget, who may pick what, and what each trait does. Pure, so it can be
// tested without a server. Merits spend Fate Trait Points, Flaws grant them, Quirks pair an advantage with a drawback
// for free. These points are separate from the perk points of PerkRules.h and never convert.
// The table (PerkTraitCatalog.h) is generated from wowdecomp's Esteria_Fate_Trait_Catalog.json; do not edit it here.
namespace EsteriaTraits
{
    using Selection = CharacterPerkTrait::Selection;

    enum Kind : uint8_t { Neutral, Quirk, Merit, Flaw };

    // What a character must have for a trait to mean anything; a flaw that could never bite is not free points.
    enum Need : uint8_t { NeedNone, NeedMana, NeedPet, NeedHealer };

    // What an effect scales. Values are signed fractions: -0.03 on TakenPhysical is 3% less physical damage taken.
    // Where each is read: game/Handlers/PerkEffects.cpp and scripts/World/esteria_perk_effects.cpp.
    enum Family : uint8_t
    {
        // damage dealt to creatures
        DmgAll, DmgTargetAbove90, DmgTargetAbove75, DmgTargetBelow30, DmgTargetBelow25, DmgFightLong, DmgFightEarly,
        Ambush, AmbushAfter, DmgBeast, DmgHumanoid, DmgUndead, DmgElemental, DmgElite, DmgSingle, DmgCrowd, DmgSolo,
        DmgGrouped, DmgNight, DmgDay, DmgLowHealth, DmgAuto, DmgSpecial, DmgSpell, DmgSpellDirect, DmgSpellPeriodic,
        DmgSpellStill, DmgSpellMoving, DmgSpellInstantMoved, DmgSpellSlow, DmgSpellCast, WildUp, WildDown, PetDmg,
        // damage taken from creatures
        TakenPhysical, TakenMagic, TakenLowHealth, TakenHighHealth, TakenStill, TakenMoving, TakenArea, TakenMelee,
        TakenGrouped, TakenSolo, TakenElite, TakenUndead, TakenLiving, PetTaken,
        // the body
        MaxHealth, MaxMana, HealthRegen, KillHeal, Fall, EnvOther, DeathDurability,
        // movement on foot
        MoveOoc, MoveOutdoorOoc, MoveCombat, MoveNight, MoveDay, MoveTravelLong, MoveTravelEarly, MoveLowHealthProc,
        Swim,
        // healing
        HealSelf, HealOthers, HealLowParty, HealTakenLow, PotionHeal, BandageHeal,
        // durations
        FoodDuration, ElixirDuration, PoisonDuration, DiseaseDuration, SlowDuration, RootDuration, FearDuration,
        StunDuration,
        // spells
        SpellCost, CastTimeSlow, CastTimeDamaging, Hearth,
        // rewards
        QuestXp, KillXp, KillXpUnrested, KillXpGuild, KillXpNoGuild, ExploreXp, Rest, QuestRep, NeutralRep, QuestGold,
        GoldHumanoid, GoldHumanoidCapped, GoldChest,
        // trade and professions
        Buy, Sell, SellGray, Repair, Taxi, Skill, SkillLow, SkillHigh, SkillEngineering, GatherTime, HerbTime,
        MineTime, CraftTime, BonusHerb, BonusOre, BonusGather,
        // stats: armor from gear, mana regeneration in combat, crit chance (percentage points) and crit damage against
        // creatures, dodge and hit chance (percentage points) while drunk, aggro radius of ordinary outdoor creatures
        ArmorGear, ManaRegenCombat, CritSpellNpc, CritChanceNpc, CritDamage, DodgeDrunk, HitDrunk, Aggro,
        // the combat pet, and the owner while one is out
        PetMaxHealth, PetSpeed, OwnerDmgPet, OwnerMovePet,
        // where and how fast on foot: caves, wilderness, rain or snow, clear skies, heavy bags, housing neighborhoods,
        // capital cities
        MoveCave, MoveWild, MoveRain, MoveClear, MoveFullBags, MoveHousing, MoveCapital,
        // attack speed after a kill, and the rest of the time
        AttackSpeedFrenzy, AttackSpeedIdle,
        // loot and professions: skinning, extra cloth, extra salvage, extra gray items, crafting skill-ups
        SkinTime, BonusSkin, ClothDrop, Salvage, GrayExtra, SkillCraft,
        // quests: gold and experience by kind, reputation by place, a clean run, a death on the way
        QuestGoldKill, QuestGoldDelivery, QuestGoldClean, QuestGoldDied, QuestXpKill, QuestXpDelivery, DungeonQuestXp,
        RepDungeon, RepOutdoor, RepHome, RepCapital,
        // the Auction House, food and drink, rest, the House Hearthstone
        AhDeposit, AhCut, FoodHeal, DrinkMana, RestHome, RestInn, HouseHearth,
        FamilyCount
    };

    struct Def
    {
        uint16_t id;
        uint8_t kind;
        uint8_t points;     // a merit's cost or a flaw's grant
        uint8_t need;
        bool implemented;   // both halves have a live effect; the rest are shown locked and refused
        uint32_t conflicts; // one bit per mutual-exclusion group
    };

    struct Effect
    {
        uint16_t trait;
        uint8_t family;
        float value;
    };

#include "PerkTraitCatalog.h"

    inline constexpr size_t DefCount = sizeof(Defs) / sizeof(Defs[0]);
    inline constexpr uint8_t MaxSelected = MaxQuirks + MaxMerits + MaxFlaws;
    static_assert(MaxSelected <= CharacterPerkTrait::MaxTraits);

    // Sent to the client as a byte (PerkWire.h): only append.
    enum Result : uint8_t
    {
        Ok = 0,
        InvalidId = 1,      // no such trait
        Malformed = 2,      // duplicate, unsorted or too many ids
        Ineligible = 3,     // the class cannot feel the trait
        Locked = 4,         // the trait has no effect yet
        Conflict = 5,       // two traits from one mutual-exclusion group
        QuirkCap = 6,
        MeritCap = 7,
        FlawCap = 8,
        FlawPoints = 9,     // flaws grant more than MaxFlawPoints
        Points = 10,        // merits cost more than the budget
        Place = 11,         // rechoose: in combat, or not resting in an inn or city
        Gold = 12,          // rechoose: not enough gold
        Nothing = 13,       // rechoose: the same build
        Version = 14,       // the client speaks another protocol version
    };

    // Classes: bit (class - 1). Mana: Paladin, Hunter, Priest, Shaman, Mage, Warlock, Druid. Pet: Hunter, Death
    // Knight, Warlock. Healer: Paladin, Priest, Shaman, Druid.
    inline constexpr uint32_t ManaClasses = 1u << 1 | 1u << 2 | 1u << 4 | 1u << 6 | 1u << 7 | 1u << 8 | 1u << 10;
    inline constexpr uint32_t PetClasses = 1u << 2 | 1u << 5 | 1u << 8;
    inline constexpr uint32_t HealerClasses = 1u << 1 | 1u << 4 | 1u << 6 | 1u << 10;

    constexpr bool Meets(uint8_t need, uint8_t classId)
    {
        if (need == NeedNone)
            return true;
        if (classId < 1 || classId > 32)
            return false;
        uint32_t const mask = need == NeedMana ? ManaClasses : need == NeedPet ? PetClasses : HealerClasses;
        return (mask & 1u << (classId - 1)) != 0;
    }

    struct Budget
    {
        uint8_t fromFlaws = 0;
        uint8_t spent = 0;
        int remaining() const { return int(BasePoints) + fromFlaws - spent; }
    };

    // Counts known ids only; Validate is what refuses the unknown ones.
    constexpr Budget BudgetOf(Selection const& selection)
    {
        Budget budget;
        for (size_t i = 0; i < selection.count && i < CharacterPerkTrait::MaxTraits; ++i)
        {
            if (selection.ids[i] >= DefCount)
                continue;
            Def const& def = Defs[selection.ids[i]];
            if (def.kind == Flaw)
                budget.fromFlaws += def.points;
            else if (def.kind == Merit)
                budget.spent += def.points;
        }
        return budget;
    }

    // Whether a character of this class may hold exactly this build. Checked in the order a player fixes them.
    constexpr Result Validate(Selection const& selection, uint8_t classId)
    {
        if (!CharacterPerkTrait::Canonical(selection))
            return Malformed;
        uint8_t quirks = 0, merits = 0, flaws = 0;
        uint32_t groups = 0;
        bool conflict = false;
        for (size_t i = 0; i < selection.count; ++i)
        {
            if (selection.ids[i] >= DefCount)
                return InvalidId;
            Def const& def = Defs[selection.ids[i]];
            if (!def.implemented)
                return Locked;
            if (!Meets(def.need, classId))
                return Ineligible;
            quirks += def.kind == Quirk;
            merits += def.kind == Merit;
            flaws += def.kind == Flaw;
            conflict |= (groups & def.conflicts) != 0;
            groups |= def.conflicts;
        }
        if (quirks > MaxQuirks)
            return QuirkCap;
        if (merits > MaxMerits)
            return MeritCap;
        if (flaws > MaxFlaws)
            return FlawCap;
        if (conflict)
            return Conflict;
        Budget const budget = BudgetOf(selection);
        if (budget.fromFlaws > MaxFlawPoints)
            return FlawPoints;
        if (budget.remaining() < 0)
            return Points;
        return Ok;
    }

    constexpr bool Has(Selection const& selection, uint16_t id)
    {
        for (size_t i = 0; i < selection.count; ++i)
            if (selection.ids[i] == id)
                return true;
        return false;
    }

    // What v1 clients and the v1 perk snapshot see: the trait when the build is exactly one original background.
    constexpr uint8_t LegacyTrait(Selection const& selection)
    {
        return selection.count == 1 && selection.ids[0] < CharacterPerkTrait::Count ? uint8_t(selection.ids[0]) : 0;
    }

    // The build's effects, summed per family with gains and losses apart so a cap on one never eats the other.
    struct Mods
    {
        std::array<float, FamilyCount> pos{}, neg{};
        bool any = false;
        float total(uint8_t family) const { return pos[family] + neg[family]; }
    };

    // Traits that are not implemented (a build saved before one was switched off) contribute nothing.
    inline Mods Compose(Selection const& selection)
    {
        Mods mods;
        for (Effect const& effect : Effects)
        {
            if (!Has(selection, effect.trait) || !Defs[effect.trait].implemented)
                continue;
            (effect.value > 0.0f ? mods.pos : mods.neg)[effect.family] += effect.value;
            mods.any = true;
        }
        return mods;
    }

    // Adds up the families that apply to one event, then caps each side once.
    struct Sum
    {
        float pos = 0.0f, neg = 0.0f;
        Sum& add(Mods const& mods, uint8_t family)
        {
            pos += mods.pos[family];
            neg += mods.neg[family];
            return *this;
        }
        // capPos limits the increase, capNeg the decrease (both as positive fractions).
        float total(float capPos = 10.0f, float capNeg = 10.0f) const
        {
            return std::min(pos, capPos) + std::max(neg, -capNeg);
        }
    };

    // Gold to rechoose a build: the first is free, then 50 silver per level up to 50 gold. Counted apart from perk
    // respecs.
    constexpr uint32_t RechooseCost(uint16_t done, uint32_t level)
    {
        return done == 0 ? 0 : std::min<uint32_t>(level * 5000, 500000);
    }
}

#endif
