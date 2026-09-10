/*
 *  Module for AzerothCore by Gozzim (https://github.com/Gozzim)
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as published
 *  by the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "StartingPet.h"
#include "Player.h"
#include "Chat.h"
#include "WorldSession.h"
#include "ScriptMgr.h"
#include "Config.h"

static bool StartingPetEnable;
static bool StartingPetAnnounce;
static bool StartingPetHunter;
static bool StartingPetName;
static uint32 StartingMinion;
static uint32 StartingPetOrc;
static uint32 StartingPetDwarf;
static uint32 StartingPetNightElf;
static uint32 StartingPetTauren;
static uint32 StartingPetTroll;
static uint32 StartingPetBloodElf;
static uint32 StartingPetDraenei;
static uint32 StartingPetHighElf;
static uint32 StartingPetBroken;

class StartingPetBeforeConfigLoad : public WorldScript
{
public:
    StartingPetBeforeConfigLoad() : WorldScript("StartingPetBeforeConfigLoad") { }

    void OnBeforeConfigLoad(bool /*reload*/) override
    {
        StartingPetEnable = sConfigMgr->GetOption<bool>("StartingPet.Enable", 1);
        StartingPetAnnounce = sConfigMgr->GetOption<bool>("StartingPet.Announce", 1);
        StartingPetHunter = sConfigMgr->GetOption<bool>("StartingPet.HunterPet", 1);
        StartingPetName = sConfigMgr->GetOption<bool>("StartingPet.RandName", 1);
        StartingPetOrc = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.Orc", 3098);
        StartingPetDwarf = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.Dwarf", 1128);
        StartingPetNightElf = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.NightElf", 2031);
        StartingPetTauren = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.Tauren", 2955);
        StartingPetTroll = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.Troll", 3122);
        StartingPetBloodElf = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.BloodElf", 15649);
        StartingPetDraenei = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.Draenei", 17199);
        StartingPetHighElf = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.HighElf", 15366);
        StartingPetBroken = sConfigMgr->GetOption<uint32>("StartingPet.HunterPet.Broken", 18464);
        StartingMinion = sConfigMgr->GetOption<int>("StartingPet.WarlockMinion", 1);
    }
};

class StartingPetScripts : public PlayerScript
{
public:
    StartingPetScripts() : PlayerScript("StartingPetScripts") { }

    void OnPlayerFirstLogin(Player* player) override
    {
        if (StartingPetEnable)
        {
            if (StartingPetAnnounce)
            {
                ChatHandler(player->GetSession()).SendSysMessage("This server is running the |cff4CFF00StartingPet |rmodule.");
            }

            if (StartingPetHunter && player->getClass() == CLASS_HUNTER)
            {
                uint32 petEntry = 0;
                switch (player->getRace())
                {
                    case RACE_ORC:
                        petEntry = StartingPetOrc;
                        break;
                    case RACE_DWARF:
                        petEntry = StartingPetDwarf;
                        break;
                    case RACE_NIGHTELF:
                        petEntry = StartingPetNightElf;
                        break;
                    case RACE_TAUREN:
                        petEntry = StartingPetTauren;
                        break;
                    case RACE_TROLL:
                        petEntry = StartingPetTroll;
                        break;
                    case RACE_BLOODELF:
                        petEntry = StartingPetBloodElf;
                        break;
                    case RACE_DRAENEI:
                        petEntry = StartingPetDraenei;
                        break;
                    case RACE_HIGHELF:
                        petEntry = StartingPetHighElf;
                        break;
                    case RACE_BROKEN_PLAYER:
                        petEntry = StartingPetBroken;
                        break;
                    default:
                        LOG_ERROR("module", "StartingPetScripts - No configured Hunter pet for race {}", player->getRace());
                        break;
                }

                if (petEntry)
                    sStartingPet->CreateConfiguredPet(player, StartingPetName, petEntry);
                else
                    LOG_ERROR("module", "StartingPetScripts - Hunter pet entry is disabled for race {}", player->getRace());

                sStartingPet->LearnPetSpells(player);
            }

            if (StartingMinion > 0 && player->getClass() == CLASS_WARLOCK)
            {
                sStartingPet->LearnWarlockSpells(player, StartingMinion);
                sStartingPet->SummonWarlockMinion(player, StartingMinion);
            }
        }
    }
};

void AddStartingPetScripts()
{
    new StartingPetBeforeConfigLoad();
    new StartingPetScripts();
}
