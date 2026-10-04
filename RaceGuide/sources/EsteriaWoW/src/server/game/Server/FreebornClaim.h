/*
 * The Freeborn claim and status: how a character chosen as Freeborn on the creation screen becomes
 * Freeborn, and how a player checks which team their character is on.
 *
 * Why the team cannot be carried by the create packet
 * ==================================================
 * At character creation the only field GlueXML can influence is the name -- the client's creation
 * binding table has no outfit/team setter -- and a Freeborn name has to follow exactly the same
 * rules as an Alliance or Horde one. So the creation screen only records the choice, and the team
 * is applied once the character exists.
 *
 * Transport
 * =========
 * The addon `Interface/AddOns/FreebornClaim` reads the choice the create screen left in the
 * `freebornPending` CVar and whispers one of the envelopes below to itself as an addon message,
 * which is the same channel the Classless Wildcard addon already uses for client -> server
 * traffic. Addon messages are only accepted while `AddonChannel` is enabled.
 *
 * Trust
 * =====
 * A client may send these envelopes at any time and for any character it controls. That is
 * deliberate: Freeborn is a choice a player makes about their own character, not a privilege, and
 * neither envelope can touch anyone else's character. `status` only reads. The team is applied
 * through `Player::SetPersistentTeamId`, which validates the enum, updates the database and the
 * character cache, and fires the team-changed notification. Claiming twice is a no-op.
 */

#ifndef AZEROTHCORE_FREEBORNCLAIM_H
#define AZEROTHCORE_FREEBORNCLAIM_H

#include "Chat.h"
#include "Log.h"
#include "Player.h"

#include <string>

namespace FreebornClaim
{
    /// Sent as the body of the addon message; prefix and body are tab separated on the wire.
    inline constexpr char const* AddonPrefix = "FREEBORN";
    inline constexpr char const* ClaimBody = "claim";
    inline constexpr char const* StatusBody = "status";
    inline constexpr char const* ClaimEnvelope = "FREEBORN\tclaim";
    inline constexpr char const* StatusEnvelope = "FREEBORN\tstatus";

    /// Human-readable persistent team, for player-facing output.
    inline char const* TeamIdName(TeamId teamId)
    {
        switch (teamId)
        {
            case TEAM_ALLIANCE:
                return "Alliance";
            case TEAM_HORDE:
                return "Horde";
            case TEAM_FREEBORN:
                return "Freeborn";
            default:
                return "Neutral";
        }
    }

    /// Handles one of this addon's envelopes. Returns true when the message was ours, i.e. when
    /// the caller must not treat it as chat.
    inline bool HandleAddonMessage(Player* player, std::string const& msg)
    {
        if (!player)
            return false;

        ChatHandler handler(player->GetSession());

        // Both identities are reported because they answer different questions: the persistent
        // team is the character's team, the origin team is what its race still implies for start
        // data, taxi nodes and reputations. They differ for exactly one case -- Freeborn.
        //
        // The answer goes out on the ADDON channel, which the client hands to the addon and never
        // shows in chat: the client asks this on every login to keep the character-select emblem
        // fresh, and that must not put a line in front of the player every time.
        //
        // LANG_ADDON is what marks the message as addon traffic; the *type* still has to be a real,
        // in-range chat type. `BuildChatPacket` writes the type as a single byte (Chat.cpp:391), and
        // the 3.3.5 client validates that byte and raises its own fatal condition on anything >= 62.
        // `CHAT_MSG_ADDON` is 0xFFFFFFFF, i.e. 0xFF on the wire, so passing it as the type crashed
        // the client with ERROR #134 (0x85100086) as soon as the reply was sent -- and since the
        // addon asks on every login, that was every login. `CHAT_MSG_WHISPER` is the type the core
        // uses for the same job (`AddonChannelCommandHandler::Send`, Chat.cpp:1107) and the type the
        // addon itself asks with ("WHISPER"), so both halves of the exchange agree.
        if (msg == StatusEnvelope)
        {
            WorldPacket data;
            ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player,
                std::string(AddonPrefix) + "\tteam\t" + std::to_string(uint32(player->GetTeamId())));
            player->GetSession()->SendPacket(&data);
            return true;
        }

        if (msg != ClaimEnvelope)
            return false;

        if (player->GetTeamId() == TEAM_FREEBORN)
            return true;

        if (!player->SetPersistentTeamId(TEAM_FREEBORN))
        {
            handler.SendSysMessage("|cff00ccff[Freeborn]|r This character could not be made Freeborn.");
            return true;
        }

        LOG_INFO("entities.player.character", "Player {} (account {}) claimed Freeborn",
            player->GetName(), player->GetSession()->GetAccountId());
        return true;
    }
}

#endif
