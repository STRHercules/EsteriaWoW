/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

// Paths of Fate debug commands: .perk info shows a character's points and ranks, .perk reset refunds them all.

#include "Chat.h"
#include "CommandScript.h"
#include "PerkRules.h"
#include "Player.h"
#include "RBAC.h"

using namespace Acore::ChatCommands;

namespace
{
    constexpr uint8 AUDIT_GM_RESET = 4;
}

class perk_commandscript : public CommandScript
{
public:
    perk_commandscript() : CommandScript("perk_commandscript") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable perkCommandTable =
        {
            { "info",  HandlePerkInfoCommand,  rbac::RBAC_PERM_COMMAND_DEBUG, Console::No },
            { "reset", HandlePerkResetCommand, rbac::RBAC_PERM_COMMAND_DEBUG, Console::No }
        };

        static ChatCommandTable commandTable =
        {
            { "perk", perkCommandTable }
        };
        return commandTable;
    }

    static Player* Target(ChatHandler* handler, Optional<PlayerIdentifier> target)
    {
        if (!target)
            target = PlayerIdentifier::FromTargetOrSelf(handler);
        return target && target->IsConnected() ? target->GetConnectedPlayer() : nullptr;
    }

    static bool HandlePerkInfoCommand(ChatHandler* handler, Optional<PlayerIdentifier> target)
    {
        Player* player = Target(handler, target);
        if (!player)
        {
            handler->SendErrorMessage("No online character selected.");
            return false;
        }

        EsteriaPerks::Ranks const& ranks = player->GetEsteriaPerkRanks();
        handler->PSendSysMessage("{}: level {}, {} of {} perk points spent, trait {}, {} respecs.", player->GetName(),
            player->GetLevel(), EsteriaPerks::Spent(ranks), EsteriaPerks::Earned(player->GetLevel()),
            player->GetEsteriaTrait(), player->GetEsteriaPerkRespecs());
        for (size_t i = 0; i < EsteriaPerks::CardCount; ++i)
            if (ranks[i])
                handler->PSendSysMessage("  perk {} (path {}, tier {}): rank {} of {}", EsteriaPerks::Cards[i].id,
                    EsteriaPerks::Cards[i].path, EsteriaPerks::Cards[i].tier, ranks[i], EsteriaPerks::Cards[i].maxRank);
        return true;
    }

    static bool HandlePerkResetCommand(ChatHandler* handler, Optional<PlayerIdentifier> target)
    {
        Player* player = Target(handler, target);
        if (!player)
        {
            handler->SendErrorMessage("No online character selected.");
            return false;
        }

        uint8 const refunded = EsteriaPerks::Spent(player->GetEsteriaPerkRanks());
        player->ResetEsteriaPerks(AUDIT_GM_RESET, false, 0);
        player->SendEsteriaPerkSnapshot();
        handler->PSendSysMessage("{}: {} perk points refunded.", player->GetName(), refunded);
        return true;
    }
};

void AddSC_perk_commandscript()
{
    new perk_commandscript();
}
