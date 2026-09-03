/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under
 * GNU AGPL v3 license.
 */

#ifndef MOD_CUSTOM_SERVER_INSTANCE_MODE_H
#define MOD_CUSTOM_SERVER_INSTANCE_MODE_H

#include "DataMap.h"

class Map;

namespace InstanceMode
{
    enum class Type
    {
        Normal,
        MythicPlus,
        DungeonMaster,
        Roguelike
    };

    struct State final : DataMap::Base
    {
        Type type = Type::Normal;
    };

    State* GetState(Map* map);
    bool IsOwnedBy(Map const* map, Type type);
    bool CanClaim(Map const* map, Type type);
    bool TryClaim(Map* map, Type type);
    bool IsSpecial(Map const* map);
};

#endif
