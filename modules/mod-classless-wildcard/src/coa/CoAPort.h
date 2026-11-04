/*
 * mod-classless-wildcard
 * Copyright (C) 2026 Dustin Hendrickson
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 */

// What the Conquest of Azeroth class code in this folder needs from Esteria.
//
// The files beside this one are CoA's own (azerothcore-wotlk-coa
// src/server/coa), changed only where they asked what class the player is.
// Every Hero is the Paladin chassis, so that question becomes "does this Hero
// own anything of that CoA class's kit?": the code's own checks for the
// specific talent, aura or spell still decide what actually happens.

#ifndef MOD_CW_COA_PORT_H
#define MOD_CW_COA_PORT_H

#include "Define.h"
#include "ObjectGuid.h"
#include "SpellAuraDefines.h"
#include <cstdint>

// CoA's Dazed (stock id 1604) is Esteria's too, so the import carries CoA's under a new id (client-patch/lib/coa.py
// CLONES); code that cast it by id casts the clone
constexpr uint32 COA_CLONE_DAZED = 14000001;

#define ESTERIA_COA_BLOCK_HOOK
#define ESTERIA_COA_SPELL_POWER_COEFFICIENT_FLAT
#define ESTERIA_COA_POWER_COST_HOOK
#define ESTERIA_COA_SPELL_CHARGES
#define ESTERIA_COA_CONDITIONAL_COMBAT
#define ESTERIA_COA_TALENT_REPLACEMENTS
#define ESTERIA_COA_SPELL_REPLACEMENT
#define ESTERIA_COA_SPELL_VISUAL_OVERRIDE       // SMSG_ESTERIA_SPELL_VISUAL_OVERRIDE (0x536): Cultist visuals

class Player;
class Unit;

// CoA's class ids and names (its SharedDefines.h). Esteria's own classes stop
// at 11, so these do not collide; the odd names are CoA's (Felsworn is
// CLASS_DEMON_HUNTER, Templar CLASS_MONK, Venomancer CLASS_PROPHET).
enum CoAClasses : uint8
{
    CLASS_BARBARIAN      = 12,
    CLASS_WITCH_DOCTOR   = 13,
    CLASS_DEMON_HUNTER   = 14,
    CLASS_WITCH_HUNTER   = 15,
    CLASS_STORMBRINGER   = 16,
    CLASS_FLESHWARDEN    = 17,
    CLASS_GUARDIAN       = 18,
    CLASS_MONK           = 19,
    CLASS_SON_OF_ARUGAL  = 20,
    CLASS_RANGER         = 21,
    CLASS_CHRONOMANCER   = 22,
    CLASS_NECROMANCER    = 23,
    CLASS_PYROMANCER     = 24,
    CLASS_CULTIST        = 25,
    CLASS_STARCALLER     = 26,
    CLASS_SUN_CLERIC     = 27,
    CLASS_TINKER         = 28,
    CLASS_PROPHET        = 29,
    CLASS_REAPER         = 30,
    CLASS_WILDWALKER     = 31,
    CLASS_SPIRIT_MAGE    = 32
};

// "player->getClass() == CLASS_X" in CoA code.
uint32 SynchronizeAscensionTalentReplacements(Player* player);
// Esteria's core (SpellEffects.cpp) has CoA's cooldown modifier; Spell.h does not declare it
void ModifyAscensionCooldown(Player* player, uint32 spellId, int32 delta, bool resetCategory);
bool HasCoAKit(Player const* player, uint8 coaClass);
bool HasCoAKit(Unit const* unit, uint8 coaClass);

#endif
