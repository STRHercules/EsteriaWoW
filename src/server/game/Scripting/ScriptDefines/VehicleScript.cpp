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

#include "VehicleScript.h"
#include "ScriptMgr.h"
#ifdef ELUNA
#include "LuaEngine.h"
#endif
#include "Vehicle.h"

void ScriptMgr::OnInstall(Vehicle* veh)
{
#ifdef ELUNA
    if (Eluna* e = veh->GetBase()->GetEluna())
        e->OnInstall(veh);
#endif
    ASSERT(veh);
    ASSERT(veh->GetBase()->IsCreature());

    if (auto tempScript = ScriptRegistry<VehicleScript>::GetScriptById(veh->GetBase()->ToCreature()->GetScriptId()))
    {
        tempScript->OnInstall(veh);
    }
}

void ScriptMgr::OnUninstall(Vehicle* veh)
{
#ifdef ELUNA
    if (Eluna* e = veh->GetBase()->GetEluna())
        e->OnUninstall(veh);
#endif
    ASSERT(veh);
    ASSERT(veh->GetBase()->IsCreature());

    if (auto tempScript = ScriptRegistry<VehicleScript>::GetScriptById(veh->GetBase()->ToCreature()->GetScriptId()))
    {
        tempScript->OnUninstall(veh);
    }
}

void ScriptMgr::OnReset(Vehicle* veh)
{
    ASSERT(veh);
    ASSERT(veh->GetBase()->IsCreature());

    if (auto tempScript = ScriptRegistry<VehicleScript>::GetScriptById(veh->GetBase()->ToCreature()->GetScriptId()))
    {
        tempScript->OnReset(veh);
    }
}

void ScriptMgr::OnInstallAccessory(Vehicle* veh, Creature* accessory)
{
#ifdef ELUNA
    if (Eluna* e = veh->GetBase()->GetEluna())
        e->OnInstallAccessory(veh, accessory);
#endif
    ASSERT(veh);
    ASSERT(veh->GetBase()->IsCreature());
    ASSERT(accessory);

    if (auto tempScript = ScriptRegistry<VehicleScript>::GetScriptById(veh->GetBase()->ToCreature()->GetScriptId()))
    {
        tempScript->OnInstallAccessory(veh, accessory);
    }
}

void ScriptMgr::OnAddPassenger(Vehicle* veh, Unit* passenger, int8 seatId)
{
#ifdef ELUNA
    if (Eluna* e = veh->GetBase()->GetEluna())
        e->OnAddPassenger(veh, passenger, seatId);
#endif
    ASSERT(veh);
    ASSERT(veh->GetBase()->IsCreature());
    ASSERT(passenger);

    if (auto tempScript = ScriptRegistry<VehicleScript>::GetScriptById(veh->GetBase()->ToCreature()->GetScriptId()))
    {
        tempScript->OnAddPassenger(veh, passenger, seatId);
    }
}

void ScriptMgr::OnRemovePassenger(Vehicle* veh, Unit* passenger)
{
#ifdef ELUNA
    if (Eluna* e = veh->GetBase()->GetEluna())
        e->OnRemovePassenger(veh, passenger);
#endif
    ASSERT(veh);
    ASSERT(veh->GetBase()->IsCreature());
    ASSERT(passenger);

    if (auto tempScript = ScriptRegistry<VehicleScript>::GetScriptById(veh->GetBase()->ToCreature()->GetScriptId()))
    {
        tempScript->OnRemovePassenger(veh, passenger);
    }
}

VehicleScript::VehicleScript(char const* name)
    : ScriptObject(name)
{
    ScriptRegistry<VehicleScript>::AddScript(this);
}

template class AC_GAME_API ScriptRegistry<VehicleScript>;
