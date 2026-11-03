#ifndef ESTERIA_WORLD_CHAT_DISCORD_BRIDGE_H
#define ESTERIA_WORLD_CHAT_DISCORD_BRIDGE_H

#include <string>

class Player;

namespace WC::DiscordBridge
{
    void Configure(bool crossFaction);
    void Start();
    void Stop();
    void Tick();
    void Publish(Player const& sender, std::string const& message, int team);
}

#endif // ESTERIA_WORLD_CHAT_DISCORD_BRIDGE_H
