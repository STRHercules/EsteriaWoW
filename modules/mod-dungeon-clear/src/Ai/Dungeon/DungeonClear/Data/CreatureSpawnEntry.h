/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license, you may redistribute it
 * and/or modify it under version 3 of the License, or (at your option), any later version.
 */

#ifndef _PLAYERBOT_DUNGEONCLEAR_CREATURESPAWNENTRY_H
#define _PLAYERBOT_DUNGEONCLEAR_CREATURESPAWNENTRY_H

#include "Define.h"

// Upstream renamed CreatureData::id1 -> id on the acore/pbot test branches.
// Resolve whichever member exists so the module compiles against both layouts
// without an #ifdef on a core version macro. The int/long overload ranking
// prefers `id` when both members are present.
namespace DungeonClear
{
    template <typename T>
    auto SpawnEntry(T const& data, int) -> decltype(data.id)
    {
        return data.id;
    }

    template <typename T>
    auto SpawnEntry(T const& data, long) -> decltype(data.id1)
    {
        return data.id1;
    }

    // Convenience wrapper so callers don't have to pass the disambiguation tag.
    template <typename T>
    uint32 SpawnEntry(T const& data)
    {
        return SpawnEntry(data, 0);
    }
}

#endif
