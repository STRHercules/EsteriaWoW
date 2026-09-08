#ifndef DEF_TRANSMOG_ADDON_PROTOCOL_H
#define DEF_TRANSMOG_ADDON_PROTOCOL_H

#include "Player.h"
#include <string>

// See TransmogAddonProtocol.cpp for the full design notes on how this
// replaces the CMaNGOS whisper-disguise / fake-slash-command transport
// with AzerothCore's native addon message channel.

namespace TransmogAddon
{
    constexpr char const* PREFIX = "transmog";

    // Tells the client addon to hide the gossip frame and show the
    // Transmog overlay instead. Call this from npc_transmogrifier's
    // OnGossipHello.
    void SendOpen(Player* player);

    // Parses one decoded "transmog\t<payload>" addon message body
    // (payload only, prefix/tab already stripped) and runs the matching
    // backend action, replying via the same addon channel.
    void Dispatch(Player* player, std::string const& message);
}

#endif
