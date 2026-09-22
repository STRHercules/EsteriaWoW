// SPDX-License-Identifier: GPL-2.0-or-later
#include "ScriptMgr.h"
#include "Player.h"
#include "Spell.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "ObjectAccessor.h"
#include "WorldSession.h"
#include "WorldPacket.h"
#include "Opcodes.h"
#include "Config.h"

void RangedAutoStart(Player*, Unit*);
void RangedAutoStop(Player*);
void RangedAutoClientCancel(Player*);
void RangedAutoUpdate(Player*, uint32);
bool AdaptiveAutoAttackEnabled();

namespace
{
class adaptive_attack_packets : public ServerScript
{
public:
    adaptive_attack_packets() : ServerScript("adaptive_attack_packets", {SERVERHOOK_CAN_PACKET_RECEIVE}) { }
    bool CanPacketReceive(WorldSession* session, WorldPacket const& incoming) override
    {
        Player* player = session ? session->GetPlayer() : nullptr;
        if (!player || !player->IsInWorld()) return true;
        if (incoming.GetOpcode() == CMSG_ATTACKSTOP)
        {
            RangedAutoStop(player);
            return true; // Native handler still clears the victim and melee state.
        }
        if (incoming.GetOpcode() == CMSG_CANCEL_AUTO_REPEAT_SPELL)
        {
            RangedAutoClientCancel(player);
            return true;
        }
        if (!AdaptiveAutoAttackEnabled()) return true;
        // Preserve the native vehicle/possession handlers, including seat permissions.
        if (player->m_mover != player || player->GetVehicle()) return true;
        if (incoming.GetOpcode() == CMSG_ATTACKSWING)
        {
            WorldPacket packet(incoming);
            ObjectGuid guid;
            packet >> guid; // WorldSession catches malformed-packet exceptions.
            Unit* target = ObjectAccessor::GetUnit(*player, guid);
            if (!target || !player->IsValidAttackTarget(target))
            {
                player->SendMeleeAttackStop(target);
                return false;
            }
            RangedAutoStart(player, target);
            return false;
        }
        if (incoming.GetOpcode() != CMSG_CAST_SPELL || incoming.size() < 6) return true;
        WorldPacket packet(incoming);
        uint8 castCount, castFlags;
        uint32 spellId;
        packet >> castCount >> spellId >> castFlags;
        if (spellId != 970100) return true;
        SpellInfo const* info = sSpellMgr->GetSpellInfo(spellId);
        if (!info || !player->HasActiveSpell(spellId) || info->IsPassive()) return false;
        // This is an attack-control command. Do not queue it through the core's
        // direct handler replay (which bypasses packet hooks). The controller
        // waits for an existing non-melee cast before starting ranged fire.
        if (!player->SpellQueue.empty() && player->SpellQueue.front().cancelInProgress)
            return false;
        SpellCastTargets targets;
        targets.Read(packet, player);
        session->HandleClientCastFlags(packet, castFlags, targets);
        RangedAutoStart(player, targets.GetUnitTarget());
        return false;
    }
};

class adaptive_attack_updates : public UnitScript
{
public:
    adaptive_attack_updates() : UnitScript("adaptive_attack_updates", true, {UNITHOOK_ON_UNIT_UPDATE}) { }
    void OnUnitUpdate(Unit* unit, uint32 diff) override
    {
        Player* player = unit->ToPlayer();
        if (!player) return;
        if (!player->IsInWorld() || player->IsBeingTeleported() || player->m_mover != player || player->GetVehicle())
        {
            RangedAutoStop(player);
            return;
        }
        RangedAutoUpdate(player, diff);
    }
};
}

void RegisterAdaptiveAttackHooks()
{
    new adaptive_attack_packets();
    new adaptive_attack_updates();
}
