/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under
 * GNU AGPL v3 license.
 */

#include "InstanceMode.h"

#include "Map.h"

namespace
{
    constexpr char STATE_KEY[] = "InstanceMode";
}

namespace InstanceMode
{
    State* GetState(Map* map)
    {
        if (!map || !map->IsDungeon())
            return nullptr;

        return map->CustomData.GetDefault<State>(STATE_KEY);
    }

    bool IsOwnedBy(Map const* map, Type type)
    {
        if (!map || !map->IsDungeon() || type == Type::Normal)
            return false;

        State const* state = map->CustomData.Get<State>(STATE_KEY);
        return state && state->type == type;
    }

    bool CanClaim(Map const* map, Type type)
    {
        // A scripted private instance (a Manastorm run) already has an owner with its own scaling.
        if (!map || !map->IsDungeon() || type == Type::Normal || map->IsScriptedPrivateInstance())
            return false;

        State const* state = map->CustomData.Get<State>(STATE_KEY);
        return !state || state->type == Type::Normal || state->type == type;
    }

    bool TryClaim(Map* map, Type type)
    {
        if (!CanClaim(map, type))
            return false;

        GetState(map)->type = type;
        return true;
    }

    bool IsSpecial(Map const* map)
    {
        if (!map || !map->IsDungeon())
            return false;

        // Manastorm scales its own runs (level, depth, group size); autobalance must not scale them again.
        if (map->IsScriptedPrivateInstance())
            return true;

        State const* state = map->CustomData.Get<State>(STATE_KEY);
        return state && state->type != Type::Normal;
    }
}

void AddSC_instance_mode()
{
}
