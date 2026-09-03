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

#include "GameObjectScript.h"
#include "AllGameObjectScript.h"
#include "ScriptMgr.h"
#ifdef ELUNA
#include "LuaEngine.h"
#endif
#include "ScriptMgrMacros.h"
#include "ScriptedGossip.h"

bool ScriptMgr::OnGossipHello(Player* player, GameObject* go)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        if (e->OnGossipHello(player, go))
            return true;
#endif
    ASSERT(player);
    ASSERT(go);

    auto ret = IsValidBoolScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        return script->CanGameObjectGossipHello(player, go);
    });

    if (ret && *ret)
    {
        return true;
    }

    auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId());
    ClearGossipMenuFor(player);
    return tempScript && tempScript->OnGossipHello(player, go);
}

bool ScriptMgr::OnGossipSelect(Player* player, GameObject* go, uint32 sender, uint32 action)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        if (e->OnGossipSelect(player, go, sender, action))
            return true;
#endif
    ASSERT(player);
    ASSERT(go);

    auto ret = IsValidBoolScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        return script->CanGameObjectGossipSelect(player, go, sender, action);
    });

    if (ret && *ret)
    {
        return true;
    }

    auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId());
    return tempScript ? tempScript->OnGossipSelect(player, go, sender, action) : false;
}

bool ScriptMgr::OnGossipSelectCode(Player* player, GameObject* go, uint32 sender, uint32 action, char const* code)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        if (e->OnGossipSelectCode(player, go, sender, action, code))
            return true;
#endif
    ASSERT(player);
    ASSERT(go);
    ASSERT(code);

    auto ret = IsValidBoolScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        return script->CanGameObjectGossipSelectCode(player, go, sender, action, code);
    });

    if (ret && *ret)
    {
        return true;
    }

    auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId());
    return tempScript ? tempScript->OnGossipSelectCode(player, go, sender, action, code) : false;
}

bool ScriptMgr::OnQuestAccept(Player* player, GameObject* go, Quest const* quest)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        if (e->OnQuestAccept(player, go, quest))
            return true;
#endif
    ASSERT(player);
    ASSERT(go);
    ASSERT(quest);

    auto ret = IsValidBoolScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        return script->CanGameObjectQuestAccept(player, go, quest);
    });

    if (ret && *ret)
    {
        return true;
    }

    auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId());
    ClearGossipMenuFor(player);
    return tempScript ? tempScript->OnQuestAccept(player, go, quest) : false;
}

bool ScriptMgr::OnQuestReward(Player* player, GameObject* go, Quest const* quest, uint32 opt)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        if (e->OnQuestReward(player, go, quest, opt))
            return true;
#endif
    ASSERT(player);
    ASSERT(go);
    ASSERT(quest);

    auto ret = IsValidBoolScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        return script->CanGameObjectQuestReward(player, go, quest, opt);
    });

    if (ret && *ret)
    {
        return false;
    }

    auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId());
    ClearGossipMenuFor(player);
    return tempScript ? tempScript->OnQuestReward(player, go, quest, opt) : false;
}

uint32 ScriptMgr::GetDialogStatus(Player* player, GameObject* go)
{
    ASSERT(player);
    ASSERT(go);

    auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId());
    return tempScript ? tempScript->GetDialogStatus(player, go) : DIALOG_STATUS_SCRIPTED_NO_STATUS;
}

void ScriptMgr::OnGameObjectDestroyed(GameObject* go, Player* player)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        e->OnDestroyed(go, player);
#endif
    ASSERT(go);

    ExecuteScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        script->OnGameObjectDestroyed(go, player);
    });

    if (auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId()))
    {
        tempScript->OnDestroyed(go, player);
    }
}

void ScriptMgr::OnGameObjectDamaged(GameObject* go, Player* player)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        e->OnDamaged(go, player);
#endif
    ASSERT(go);

    ExecuteScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        script->OnGameObjectDamaged(go, player);
    });

    if (auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId()))
    {
        tempScript->OnDamaged(go, player);
    }
}

void ScriptMgr::OnGameObjectModifyHealth(GameObject* go, Unit* attackerOrHealer, int32& change, SpellInfo const* spellInfo)
{
    ASSERT(go);

    ExecuteScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        script->OnGameObjectModifyHealth(go, attackerOrHealer, change, spellInfo);
    });

    if (auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId()))
    {
        tempScript->OnModifyHealth(go, attackerOrHealer, change, spellInfo);
    }
}

void ScriptMgr::OnGameObjectLootStateChanged(GameObject* go, uint32 state, Unit* unit)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        e->OnLootStateChanged(go, state);
#endif
    ASSERT(go);

    ExecuteScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        script->OnGameObjectLootStateChanged(go, state, unit);
    });

    if (auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId()))
    {
        tempScript->OnLootStateChanged(go, state, unit);
    }
}

void ScriptMgr::OnGameObjectStateChanged(GameObject* go, uint32 state)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        e->OnGameObjectStateChanged(go, state);
#endif
    ASSERT(go);

    ExecuteScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        script->OnGameObjectStateChanged(go, state);
    });

    if (auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId()))
    {
        tempScript->OnGameObjectStateChanged(go, state);
    }
}

void ScriptMgr::OnGameObjectUpdate(GameObject* go, uint32 diff)
{
#ifdef ELUNA
    if (Eluna* e = go->GetEluna())
        e->UpdateAI(go, diff);
#endif
    ASSERT(go);

    ExecuteScript<AllGameObjectScript>([&](AllGameObjectScript* script)
    {
        script->OnGameObjectUpdate(go, diff);
    });

    if (auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId()))
    {
        tempScript->OnUpdate(go, diff);
    }
}

GameObjectAI* ScriptMgr::GetGameObjectAI(GameObject* go)
{
    ASSERT(go);

    auto retAI = GetReturnAIScript<AllGameObjectScript, GameObjectAI>([go](AllGameObjectScript* script)
    {
        return script->GetGameObjectAI(go);
    });

    if (retAI)
    {
        return retAI;
    }

    auto tempScript = ScriptRegistry<GameObjectScript>::GetScriptById(go->GetScriptId());
    return tempScript ? tempScript->GetAI(go) : nullptr;
}

GameObjectScript::GameObjectScript(char const* name)
    : ScriptObject(name)
{
    ScriptRegistry<GameObjectScript>::AddScript(this);
}

template class AC_GAME_API ScriptRegistry<GameObjectScript>;
