#ifndef ASCENSION_CLIENT_LUA_H
#define ASCENSION_CLIENT_LUA_H

#include "Define.h"
#include <string>

class Player;

struct AscensionClientLuaChunk
{
    uint32 RequirementTypeId = 0;
    uint32 RequirementId = 0;
    std::string Token;
    std::string Lua;
    std::string TargetAddon;
};

// shortcut: CoA pushes Lua through the Ascension client's challenge formatter, which Esteria's client lacks.
// The corrected Manastorm UI ships in Esteria's MPQ instead; give this a real channel if pushed Lua is needed.
inline void RunAscensionClientLua(Player* /*player*/, AscensionClientLuaChunk const& /*chunk*/) { }

#endif
