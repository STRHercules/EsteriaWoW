#ifndef _STARTINGPET_H_
#define _STARTINGPET_H_

#include "Common.h"
#include "Player.h"
#include "Pet.h"
#include "SpellMgr.h"
#include "SpellInfo.h"
#include "SharedDefines.h"

class StartingPet
{
public:
    static StartingPet* instance();

    void CreateConfiguredPet(Player* player, bool petName, uint32 entry);
    std::string RandName();
    void LearnPetSpells(Player* player);
    void SummonWarlockMinion(Player* player, uint32 minionMask);
    void LearnWarlockSpells(Player* player, uint32 minionMask);
    void LearnSpellAndRanksForLevel(uint32 spellId, Player* player);

private:
    std::string const _vowels = "aeiou";
    std::string const _consonants = "bcdfghjklmnpqrstvw";
    std::vector<uint32> const _hunterPetSpells = {883, 982, 2641, 6991};
    std::vector<uint32> const _warlockSpells = {688, 697, 712, 691, 30146, 1120};
};

#define sStartingPet StartingPet::instance()

#endif
