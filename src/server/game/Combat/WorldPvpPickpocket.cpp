/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#include "WorldPvpPickpocket.h"
#include "Chat.h"
#include "CryptoRandom.h"
#include "DatabaseEnv.h"
#include "Item.h"
#include "Mail.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "Random.h"
#include "SpellAuraDefines.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "WildernessPouch.h"
#include "World.h"
#include "WorldPacket.h"
#include "WorldPvpEar.h"
#include "WorldPvpRules.h"
#include "WorldSession.h"
#include <utility>

namespace
{
constexpr uint32 PlayerPickpocketSpell = 921;
}

bool Acore::WorldPvp::CanUsePlayerPickpocket(Player const& player)
{
    return sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP) && CanUseBountyEscrow() &&
        player.HasSpell(PlayerPickpocketSpell);
}

bool Acore::WorldPvp::TryPlayerPickpocket(ChatHandler& handler, ObjectGuid victimGuid)
{
    WorldSession* session = handler.GetSession();
    if (!session || !session->GetPlayer())
        return false;

    Player& thief = *session->GetPlayer();
    if (!CanUsePlayerPickpocket(thief))
    {
        handler.SendErrorMessage("You must know Pick Pocket to pickpocket another player.");
        return false;
    }

    if (!thief.IsInWorld() || thief.IsBeingTeleported())
    {
        handler.SendErrorMessage("You must be in the world to pickpocket another player.");
        return false;
    }

    Player* victim = victimGuid.IsPlayer() ? ObjectAccessor::GetPlayer(thief, victimGuid) : nullptr;
    uint32 const thiefAccount = thief.GetSession()->GetAccountId();
    if (!victim || victim == &thief || victim->GetSession()->GetAccountId() == thiefAccount)
    {
        handler.SendErrorMessage("Choose a player on another account.");
        return false;
    }

    bool const inWilderness = thief.IsInActiveWilderness() && victim->IsInActiveWilderness();
    if (!victim->IsPvP() && !inWilderness)
    {
        handler.SendErrorMessage("Choose a PvP-flagged player or a player in active Wilderness.");
        return false;
    }

    if (!thief.HasStealthAura())
    {
        handler.SendErrorMessage("You must be stealthed to pickpocket another player.");
        return false;
    }

    if (!thief.GetMap()->IsWorldMap() || !thief.IsInMap(victim) || !thief.InSamePhase(victim) ||
        !thief.IsAlive() || !victim->IsAlive() || thief.IsInSanctuary() || victim->IsInSanctuary() ||
        thief.IsGameMaster() || victim->IsGameMaster() || thief.IsSpectator() || victim->IsSpectator() ||
        thief.duel || victim->duel || thief.IsInCombat() || victim->IsInCombat() ||
        thief.IsInFlight() || victim->IsInFlight() || victim->IsBeingTeleported() ||
        thief.GetTradeData() || victim->GetTradeData() || victim->IsImmuneToPC() ||
        thief.GetDigitalInventory().Failed() || victim->GetDigitalInventory().Failed() ||
        !thief.HaveAtClient(victim) || !thief.CanSeeOrDetect(victim) || !thief.IsWithinLOSInMap(victim) ||
        !thief.IsWithinDistInMap(victim, 5.0f, true, false, false))
    {
        handler.SendErrorMessage("You can only pickpocket a visible player within five yards in the open world.");
        return false;
    }

    SpellInfo const* spell = sSpellMgr->GetSpellInfo(PlayerPickpocketSpell);
    if (!spell || thief.HasSpellCooldown(PlayerPickpocketSpell) ||
        thief.GetGlobalCooldownMgr().HasGlobalCooldown(spell) ||
        thief.IsActionPreventedByCasting() || thief.HasUnitState(UNIT_STATE_LOST_CONTROL))
    {
        handler.SendErrorMessage("You are not ready to use Pick Pocket.");
        return false;
    }

    uint32 const available = Acore::WorldPvp::PickpocketGoldAmount(victim->GetMoney(),
        Acore::WorldPvp::WalletRoom(thief));
    Item const* tool = thief.GetItemByEntry(FencePickpocketTool.entry);
    bool const hasTool = sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP_EAR_TROPHIES) && tool &&
        Player::IsInventoryPos(tool->GetPos()) && !tool->IsInTrade();
    bool const succeeded = roll_chance_i(hasTool ? 70 : 60);
    uint32 const amount = succeeded ? available : 0;
    Item* item = nullptr;
    if (succeeded && inWilderness && sWorld->getBoolConfig(CONFIG_ESTERIA_WILDERNESS_ITEM_PICKPOCKET) &&
        roll_chance_i(10))
        item = SelectWildernessSupplyToSteal(*victim);

    uint16 const itemPosition = item ? item->GetPos() : 0;
    uint32 const itemGuid = item ? item->GetGUID().GetCounter() : 0;
    uint32 const itemCount = item ? item->GetCount() : 0;
    std::unique_ptr<Mail> mail;
    if (item)
        mail = MakeWorldPvpItemMail(thief, *item, "Wilderness pickpocket");

    uint32 const thiefBalance = thief.GetMoney() + amount;
    uint32 const victimBalance = victim->GetMoney() - amount;
    uint32 const victimAccount = victim->GetSession()->GetAccountId();
    uint64 nonce;
    Acore::Crypto::GetRandomBytes(reinterpret_cast<uint8*>(&nonce), sizeof(nonce));

    auto const bindReceipt = [&](CharacterDatabasePreparedStatement& statement, uint8 offset)
    {
        statement.SetData(offset, thiefAccount);
        statement.SetData(offset + 1, victimAccount);
        statement.SetData(offset + 2, nonce);
    };

    CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
    if (item)
        victim->SaveInventoryAndGoldToDB(trans);

    auto* reserve = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_PICKPOCKET);
    bindReceipt(*reserve, 0);
    reserve->SetData(3, thief.GetGUID().GetCounter());
    reserve->SetData(4, victim->GetGUID().GetCounter());
    reserve->SetData(5, amount);
    reserve->SetData(6, itemGuid);
    reserve->SetData(7, itemCount);
    reserve->SetData(8, mail ? mail->messageID : 0);
    reserve->SetData(9, thiefAccount);
    reserve->SetData(10, victimAccount);
    trans->Append(reserve);

    auto* settle = CharacterDatabase.GetPreparedStatement(CHAR_SETTLE_WORLD_PVP_PICKPOCKET);
    settle->SetData(0, thiefBalance);
    settle->SetData(1, victimBalance);
    settle->SetData(2, uint32(PLAYER_FLAGS_IN_PVP));
    bindReceipt(*settle, 3);
    settle->SetData(6, amount);
    trans->Append(settle);

    if (mail)
    {
        auto* send = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_PICKPOCKET_MAIL);
        BindWorldPvpItemMail(*send, *mail);
        bindReceipt(*send, 8);
        send->SetData(11, mail->messageID);
        trans->Append(send);

        auto* attach = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_PICKPOCKET_MAIL_ITEM);
        bindReceipt(*attach, 0);
        trans->Append(attach);

        auto* detach = CharacterDatabase.GetPreparedStatement(CHAR_DETACH_WORLD_PVP_PICKPOCKET_ITEM);
        bindReceipt(*detach, 0);
        trans->Append(detach);
    }

    // Both entry points run on the world thread. Keep the wallets and item stable through readback.
    bool const committed = CharacterDatabase.AsyncCommitTransaction(trans).m_future.get();
    auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_PICKPOCKET_RESULT);
    bindReceipt(*check, 0);
    PreparedQueryResult result = CharacterDatabase.Query(check);
    if (!result)
    {
        constexpr char Error[] = "Pickpocket outcome unavailable; reconnect to refresh your saved assets";
        thief.GetDigitalInventory().DisconnectOnPersistenceFailure(Error);
        if (amount || item)
            victim->GetDigitalInventory().DisconnectOnPersistenceFailure(Error);
        return false;
    }

    int64 const settled = result->Fetch()[0].Get<int64>();
    if (settled == 2 || (settled == 1 && item && victim->GetItemByPos(itemPosition) != item))
    {
        constexpr char Error[] = "Pickpocket item delivery could not be verified; reconnect to refresh your inventory";
        thief.GetDigitalInventory().DisconnectOnPersistenceFailure(Error);
        victim->GetDigitalInventory().DisconnectOnPersistenceFailure(Error);
        return false;
    }

    if (settled != 1)
    {
        if (item && !committed)
            victim->GetDigitalInventory().DisconnectOnPersistenceFailure(
                "Pickpocket inventory save failed; reconnect to refresh your inventory");

        handler.SendErrorMessage(settled == -1
            ? "You can attempt to pickpocket that target once every ten minutes."
            : "The pickpocket attempt could not be completed.");
        return false;
    }

    std::string itemName;
    if (item)
    {
        itemName = item->GetTemplate()->Name1;
        victim->MoveItemFromInventory(item->GetBagSlot(), item->GetSlot(), true);
        item->FSetState(ITEM_UNCHANGED);
        PublishWorldPvpItemMail(thief, std::move(mail), std::unique_ptr<Item>(item));
    }

    if (amount)
    {
        thief.SetMoney(thiefBalance);
        victim->SetMoney(victimBalance);
    }

    if (spell->StartRecoveryTime)
        thief.GetGlobalCooldownMgr().AddGlobalCooldown(spell, spell->StartRecoveryTime);
    thief.AddSpellAndCategoryCooldowns(spell, 0);
    thief.SetPlayerFlag(PLAYER_FLAGS_IN_PVP);
    thief.SetWorldPvpPickpocketExposure(result->Fetch()[1].Get<uint64>());
    thief.UpdatePvP(true, true);
    thief.UpdateFFAPvPState();
    thief.RemoveAurasByType(SPELL_AURA_MOD_STEALTH);
    ChatHandler victimHandler(victim->GetSession());
    if (amount)
    {
        handler.SendNotification("You stole {} copper from {}.", amount, victim->GetName());
        victimHandler.SendNotification("{} pickpocketed {} copper from you.", thief.GetName(), amount);
    }
    if (itemCount)
    {
        handler.SendNotification("You stole {} x {} from {}. Check your mailbox.", itemCount, itemName,
            victim->GetName());
        victimHandler.SendNotification("{} pickpocketed {} x {} from you.", thief.GetName(), itemCount, itemName);
    }
    else if (!amount)
    {
        handler.SendNotification("Your pickpocket attempt failed.");
        victimHandler.SendNotification("{} tried to pickpocket you.", thief.GetName());
    }
    handler.SendSysMessage("Pickpocketing revealed you and locked world PvP on for five minutes.");

    return true;
}

void WorldSession::HandleEsteriaPlayerPickpocketOpcode(WorldPacket& packet)
{
    if (packet.size() != sizeof(uint64))
        return;

    ObjectGuid victim;
    packet >> victim;
    ChatHandler handler(this);
    Acore::WorldPvp::TryPlayerPickpocket(handler, victim);
}
