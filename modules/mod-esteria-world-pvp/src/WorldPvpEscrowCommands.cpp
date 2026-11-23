/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 *
 * This program is free software; you can redistribute it and/or modify it under the terms of
 * the GNU General Public License as published by the Free Software Foundation, version 2 or later.
 */

#include "CharacterCache.h"
#include "Chat.h"
#include "CommandScript.h"
#include "Creature.h"
#include "CreatureScript.h"
#include "DatabaseEnv.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "RBAC.h"
#include "ScriptedGossip.h"
#include "StringFormat.h"
#include "WildernessPouch.h"
#include "World.h"
#include "WorldPvpBountyTargets.h"
#include "WorldPvpEar.h"
#include "WorldPvpRules.h"
#include "WorldSession.h"
#include <limits>

using namespace Acore::ChatCommands;
void AddWorldPvpPickpocketCommands();

namespace
{
using Acore::WorldPvp::BountyEscrowState;
using Acore::WorldPvp::WalletRoom;

bool CanMoveEscrowGold(ChatHandler& handler, Player const& sponsor)
{
    // Keeping the wallet write on the single worker orders it after earlier character saves.
    if (!Acore::WorldPvp::CanUseBountyEscrow())
    {
        handler.SendErrorMessage("Bounty escrow preview requires one character DB worker and a non-clustered realm.");
        return false;
    }

    if (sponsor.GetDigitalInventory().Failed())
    {
        handler.SendErrorMessage("Reconnect before moving bounty gold.");
        return false;
    }

    return true;
}

void BindContribution(CharacterDatabasePreparedStatement& statement, Player const& sponsor, uint64 id, uint8 offset = 0)
{
    statement.SetData(offset, sponsor.GetGUID().GetCounter());
    statement.SetData(offset + 1, id);
    statement.SetData(offset + 2, sponsor.GetSession()->GetAccountId());
}

void BindClaim(CharacterDatabasePreparedStatement& statement, Player const& hunter,
    uint32 sponsorGuid, uint64 id, uint8 offset = 0)
{
    statement.SetData(offset, sponsorGuid);
    statement.SetData(offset + 1, id);
    statement.SetData(offset + 2, hunter.GetGUID().GetCounter());
    statement.SetData(offset + 3, hunter.GetSession()->GetAccountId());
}

bool ApplyWalletChange(ChatHandler& handler, Player& player, CharacterDatabaseTransaction trans,
    CharacterDatabasePreparedStatement* check, uint32 newBalance, BountyEscrowState expected)
{
    // The wallet and receipt move in one SQL statement. A retry cannot move either after the state changes.
    CharacterDatabase.AsyncCommitTransaction(trans).m_future.get();
    PreparedQueryResult result = CharacterDatabase.Query(check);
    if (!result)
    {
        player.GetDigitalInventory().DisconnectOnPersistenceFailure(
            "Bounty escrow outcome unavailable; reconnect to recover your saved balance");
        return false;
    }

    auto const stored = static_cast<BountyEscrowState>(result->Fetch()[0].Get<int64>());
    if (!Acore::WorldPvp::IsBountyWalletChangeCommitted(expected, stored))
    {
        handler.SendErrorMessage("Bounty escrow could not be updated. Your current balance was kept.");
        return false;
    }

    player.SetMoney(newBalance);
    return true;
}

bool MoveContribution(ChatHandler& handler, Player& sponsor, CharacterDatabaseTransaction trans,
    uint64 id, uint32 newBalance, BountyEscrowState expected)
{
    auto const operation = expected == BountyEscrowState::Funded
        ? CHAR_FUND_WORLD_PVP_BOUNTY : CHAR_REFUND_WORLD_PVP_BOUNTY;
    auto* move = CharacterDatabase.GetPreparedStatement(operation);
    move->SetData(0, newBalance);
    BindContribution(*move, sponsor, id, 1);
    trans->Append(move);

    auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_BOUNTY_STATE);
    BindContribution(*check, sponsor, id);
    return ApplyWalletChange(handler, sponsor, trans, check, newBalance, expected);
}

std::string DescribeBountyGold(uint64 copper)
{
    return Acore::StringFormat("{}g {}s {}c", copper / GOLD, copper % GOLD / SILVER, copper % SILVER);
}

class world_pvp_escrow_commandscript final : public CommandScript
{
public:
    world_pvp_escrow_commandscript() : CommandScript("world_pvp_escrow_commandscript") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable escrow =
        {
            { "post", HandlePost, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
            { "board", ShowBounties, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
            { "list", HandleList, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
            { "refund", HandleRefund, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
            { "claims", HandleClaims, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
            { "collect", CollectClaim, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
        };
        static ChatCommandTable wilderness =
        {
            { "pouches", ListPouches, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
            { "loot", LootPouch, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
        };
        static ChatCommandTable bloodyAuction =
        {
            { "list", ListAuctionPouches, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
            { "buy", BuyAuctionPouch, rbac::RBAC_PERM_COMMAND_DEV, Console::No },
        };
        return { { "bountyescrow", escrow }, { "wilderness", wilderness }, { "bloodyauction", bloodyAuction } };
    }

private:
    static bool ListAuctionPouches(ChatHandler* handler)
    {
        return Acore::WorldPvp::InteractWithBloodyAuctionHouse(*handler, 0);
    }

    static bool BuyAuctionPouch(ChatHandler* handler, uint64 id)
    {
        if (!id)
        {
            handler->SendErrorMessage("Specify a pouch ID from .bloodyauction list.");
            return false;
        }

        return Acore::WorldPvp::InteractWithBloodyAuctionHouse(*handler, id);
    }

    static bool ListPouches(ChatHandler* handler)
    {
        return Acore::WorldPvp::InteractWithWildernessPouch(*handler, 0);
    }

    static bool LootPouch(ChatHandler* handler, uint64 id)
    {
        if (!id)
        {
            handler->SendErrorMessage("Specify a pouch ID from .wilderness pouches.");
            return false;
        }

        return Acore::WorldPvp::InteractWithWildernessPouch(*handler, id);
    }

    static bool HandlePost(ChatHandler* handler, PlayerIdentifier target, uint32 copper)
    {
        return Post(*handler, target.GetGUID(), target.GetName(), copper);
    }

public:
    static bool Post(ChatHandler& handlerRef, ObjectGuid targetGuid, std::string const& targetName, uint32 copper)
    {
        ChatHandler* handler = &handlerRef;
        Player& sponsor = *handler->GetSession()->GetPlayer();
        if (!sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP))
        {
            handler->SendErrorMessage("World PvP is disabled.");
            return false;
        }

        if (!Acore::WorldPvp::MeetsPlayerBountyMinimum(copper))
        {
            handler->SendErrorMessage("Each contribution must be at least 100 gold (1000000 copper).");
            return false;
        }

        if (!sponsor.HasEnoughMoney(copper))
        {
            handler->SendErrorMessage("You do not have enough gold for that contribution.");
            return false;
        }

        uint32 const targetAccount = sCharacterCache->GetCharacterAccountIdByGuid(targetGuid);
        if (!targetAccount || targetAccount == sponsor.GetSession()->GetAccountId())
        {
            handler->SendErrorMessage("Choose a character on another account.");
            return false;
        }

        if (!CanMoveEscrowGold(*handler, sponsor))
            return false;

        auto* lastId = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_BOUNTY_LAST_ID);
        lastId->SetData(0, sponsor.GetGUID().GetCounter());
        PreparedQueryResult result = CharacterDatabase.Query(lastId);
        if (!result || result->Fetch()[0].Get<uint64>() == std::numeric_limits<uint64>::max())
        {
            handler->SendErrorMessage("Bounty escrow is currently unavailable.");
            return false;
        }

        uint64 const id = result->Fetch()[0].Get<uint64>() + 1;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        auto* create = CharacterDatabase.GetPreparedStatement(CHAR_INS_WORLD_PVP_BOUNTY);
        BindContribution(*create, sponsor, id);
        create->SetData(3, targetGuid.GetCounter());
        create->SetData(4, copper);
        trans->Append(create);

        Acore::WorldPvp::InvalidateBountyTarget(targetGuid.GetCounter());
        if (!MoveContribution(*handler, sponsor, trans, id, sponsor.GetMoney() - copper, BountyEscrowState::Funded))
            return false;
        Acore::WorldPvp::InvalidateBountyTarget(targetGuid.GetCounter());

        handler->PSendSysMessage("Escrow #{} posts {} for {} for up to seven days.", id, DescribeBountyGold(copper), targetName);
        return true;
    }

private:
    static bool HandleList(ChatHandler* handler, Optional<uint64> after)
    {
        WorldSession* session = handler->GetSession();
        ObjectGuid const sponsor = session->GetPlayer()->GetGUID();
        auto* stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_BOUNTIES_BY_SPONSOR);
        stmt->SetData(0, sponsor.GetCounter());
        stmt->SetData(1, session->GetAccountId());
        stmt->SetData(2, after.value_or(0));
        session->GetQueryProcessor().AddCallback(CharacterDatabase.AsyncQuery(stmt).WithPreparedCallback(
            [session, sponsor](PreparedQueryResult result)
            {
                if (!session->GetPlayer() || session->GetPlayer()->GetGUID() != sponsor)
                    return;

                ChatHandler reply(session);
                if (!result)
                {
                    reply.SendSysMessage("No funded contributions found.");
                    return;
                }

                do
                {
                    Field* row = result->Fetch();
                    reply.PSendSysMessage("Escrow #{} for character {} holds {} copper.",
                        row[0].Get<uint64>(), row[1].Get<uint32>(), row[2].Get<uint32>());
                }
                while (result->NextRow());
            }));
        return true;
    }

    static bool HandleRefund(ChatHandler* handler, uint64 id)
    {
        Player& sponsor = *handler->GetSession()->GetPlayer();
        if (!CanMoveEscrowGold(*handler, sponsor))
            return false;

        auto* stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_BOUNTY_BY_ID);
        BindContribution(*stmt, sponsor, id);
        PreparedQueryResult result = CharacterDatabase.Query(stmt);
        if (!result)
        {
            handler->SendErrorMessage("No funded contribution with that ID was found for this character.");
            return false;
        }

        uint32 const copper = result->Fetch()[0].Get<uint32>();
        if (copper > WalletRoom(sponsor))
        {
            handler->SendErrorMessage("Make room in your wallet before taking the refund.");
            return false;
        }

        Acore::WorldPvp::InvalidateBountyTarget(result->Fetch()[1].Get<uint32>());
        if (!MoveContribution(*handler, sponsor, CharacterDatabase.BeginTransaction(), id,
            sponsor.GetMoney() + copper, BountyEscrowState::Refunded))
            return false;

        handler->PSendSysMessage("Refunded {} copper from escrow #{}.", copper, id);
        return true;
    }

    static bool HandleClaims(ChatHandler* handler)
    {
        WorldSession* session = handler->GetSession();
        ObjectGuid const hunter = session->GetPlayer()->GetGUID();
        auto* stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_CLAIMS);
        stmt->SetData(0, hunter.GetCounter());
        stmt->SetData(1, session->GetAccountId());
        session->GetQueryProcessor().AddCallback(CharacterDatabase.AsyncQuery(stmt).WithPreparedCallback(
            [session, hunter](PreparedQueryResult result)
            {
                if (!session->GetPlayer() || session->GetPlayer()->GetGUID() != hunter)
                    return;

                ChatHandler reply(session);
                if (!result)
                {
                    reply.SendSysMessage("No bounty claims are ready to collect.");
                    return;
                }

                do
                {
                    Field* row = result->Fetch();
                    uint32 const sponsor = row[0].Get<uint32>();
                    reply.PSendSysMessage("{} claim {} {} for character {} pays {}.",
                        sponsor ? "Player-funded" : "Automatic", sponsor, row[1].Get<uint64>(),
                        row[2].Get<uint32>(), DescribeBountyGold(row[3].Get<uint32>()));
                }
                while (result->NextRow());
            }));
        return true;
    }

public:
    static bool ShowBounties(ChatHandler* handler)
    {
        WorldSession* session = handler->GetSession();
        ObjectGuid const viewer = session->GetPlayer()->GetGUID();
        auto* stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_BOUNTY_BOARD);
        session->GetQueryProcessor().AddCallback(CharacterDatabase.AsyncQuery(stmt).WithPreparedCallback(
            [session, viewer](PreparedQueryResult result)
            {
                if (!session->GetPlayer() || session->GetPlayer()->GetGUID() != viewer)
                    return;

                ChatHandler reply(session);
                if (!result)
                {
                    reply.SendSysMessage("There are no active bounties.");
                    return;
                }

                do
                {
                    Field* row = result->Fetch();
                    uint64 const automatic = row[1].Get<uint64>();
                    uint64 const funded = row[2].Get<uint64>();
                    reply.PSendSysMessage("{}: {} total ({} automatic, {} player-funded).", row[0].Get<std::string>(),
                        DescribeBountyGold(automatic + funded), DescribeBountyGold(automatic),
                        DescribeBountyGold(funded));
                }
                while (result->NextRow());
            }));
        return true;
    }

    static bool CollectClaim(ChatHandler* handler, uint32 sponsorGuid, uint64 id)
    {
        return Collect(*handler, sponsorGuid, id, true);
    }

    // The PvP window collects anywhere; capital collectors and the command keep the capital rule.
    static bool Collect(ChatHandler& handlerRef, uint32 sponsorGuid, uint64 id, bool requireCapital)
    {
        ChatHandler* handler = &handlerRef;
        Player& hunter = *handler->GetSession()->GetPlayer();
        if (requireCapital && (!hunter.GetMap()->IsWorldMap() ||
            !Acore::WorldPvp::IsCapital(sAreaTableStore.LookupEntry(hunter.GetAreaId()))))
        {
            handler->SendErrorMessage("Bounty claims can only be collected in a capital city.");
            return false;
        }

        if (!CanMoveEscrowGold(*handler, hunter))
            return false;

        auto* stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_CLAIM_AMOUNT);
        BindClaim(*stmt, hunter, sponsorGuid, id);
        PreparedQueryResult result = CharacterDatabase.Query(stmt);
        if (!result)
        {
            handler->SendErrorMessage("No uncollected bounty claim with that ID was found for this character.");
            return false;
        }

        uint32 const copper = result->Fetch()[0].Get<uint32>();
        if (copper > WalletRoom(hunter))
        {
            handler->SendErrorMessage("Make room in your wallet before collecting that bounty.");
            return false;
        }

        uint32 const newBalance = hunter.GetMoney() + copper;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        auto* redeem = CharacterDatabase.GetPreparedStatement(CHAR_REDEEM_WORLD_PVP_CLAIM);
        redeem->SetData(0, newBalance);
        BindClaim(*redeem, hunter, sponsorGuid, id, 1);
        trans->Append(redeem);
        auto* check = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_CLAIM_STATE);
        BindClaim(*check, hunter, sponsorGuid, id);
        if (!ApplyWalletChange(*handler, hunter, trans, check, newBalance, BountyEscrowState::Redeemed))
            return false;

        handler->PSendSysMessage("Collected a {} bounty.", DescribeBountyGold(copper));
        return true;
    }
};

class npc_esteria_bounty_collector final : public CreatureScript
{
public:
    npc_esteria_bounty_collector() : CreatureScript("npc_esteria_bounty_collector") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        bool const showBoard = sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP);
        bool const canAuction = showBoard;
        if (!showBoard && !canAuction)
            return true;

        ClearGossipMenuFor(player);
        if (showBoard)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "View the bounty board.", GOSSIP_SENDER_MAIN, ViewBounties);
        if (showBoard)
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, "Collect my next bounty.", GOSSIP_SENDER_MAIN, CollectNext);
        if (canAuction)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Browse the Bloody Auction House.",
                GOSSIP_SENDER_MAIN, ViewBloodyAuction);
        if (Acore::WorldPvp::CanBuyEarRewards(*player))
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Browse Ear Trophy rewards.", GOSSIP_SENDER_MAIN, ViewEarRewards);
        SendGossipMenuFor(player, player->GetGossipTextId(creature), creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        if (sender != GOSSIP_SENDER_MAIN)
            return true;

        if (action == ViewEarRewards && Acore::WorldPvp::CanBuyEarRewards(*player))
        {
            ClearGossipMenuFor(player);
            for (auto const& reward : Acore::WorldPvp::EarRewards)
            {
                if (ItemTemplate const* item = sObjectMgr->GetItemTemplate(reward.entry))
                {
                    std::string const offer = Acore::StringFormat("{} for {} Ear Trophies", item->Name1,
                        uint32(reward.cost));
                    AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, offer, GOSSIP_SENDER_MAIN, reward.entry,
                        Acore::StringFormat("Exchange {}? Your reward will arrive by mail.", offer), 0, false);
                }
            }
            SendGossipMenuFor(player, player->GetGossipTextId(creature), creature->GetGUID());
            return true;
        }

        CloseGossipMenuFor(player);
        for (auto const& reward : Acore::WorldPvp::EarRewards)
        {
            if (action == reward.entry)
            {
                Acore::WorldPvp::BuyEarReward(*player, reward.entry);
                return true;
            }
        }

        ChatHandler handler(player->GetSession());
        if (action == ViewBounties)
        {
            if (sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP))
                world_pvp_escrow_commandscript::ShowBounties(&handler);
            return true;
        }

        if (action == ViewBloodyAuction)
        {
            Acore::WorldPvp::InteractWithBloodyAuctionHouse(handler, 0);
            return true;
        }

        if (action != CollectNext || !sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP))
            return true;

        auto* next = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_NEXT_CLAIM);
        next->SetData(0, player->GetGUID().GetCounter());
        next->SetData(1, player->GetSession()->GetAccountId());
        next->SetData(2, WalletRoom(*player));
        PreparedQueryResult result = CharacterDatabase.Query(next);
        if (!result)
        {
            handler.SendSysMessage("You have no bounty claims you can collect right now.");
            return true;
        }

        Field* row = result->Fetch();
        world_pvp_escrow_commandscript::CollectClaim(&handler, row[0].Get<uint32>(), row[1].Get<uint64>());
        return true;
    }

private:
    enum GossipAction : uint32
    {
        CollectNext = GOSSIP_ACTION_INFO_DEF + 1,
        ViewBounties,
        ViewBloodyAuction,
        ViewEarRewards
    };
};

}

bool PostWorldPvpBounty(ChatHandler& handler, ObjectGuid target, std::string const& name, uint32 copper)
{
    return world_pvp_escrow_commandscript::Post(handler, target, name, copper);
}

uint32 CollectWorldPvpClaims(ChatHandler& handler)
{
    Player& hunter = *handler.GetSession()->GetPlayer();
    uint32 collected = 0;
    // Each pass pays the oldest claim that fits the wallet; a failed payout stops the loop.
    while (collected < 20)
    {
        auto* next = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_NEXT_CLAIM);
        next->SetData(0, hunter.GetGUID().GetCounter());
        next->SetData(1, hunter.GetSession()->GetAccountId());
        next->SetData(2, WalletRoom(hunter));
        PreparedQueryResult result = CharacterDatabase.Query(next);
        if (!result)
            break;

        Field* row = result->Fetch();
        if (!world_pvp_escrow_commandscript::Collect(handler, row[0].Get<uint32>(), row[1].Get<uint64>(), false))
            break;
        ++collected;
    }
    return collected;
}

void AddWorldPvpCrimeUi();

void Addmod_esteria_world_pvpScripts()
{
    new world_pvp_escrow_commandscript();
    new npc_esteria_bounty_collector();
    AddWorldPvpPickpocketCommands();
    AddWorldPvpCrimeUi();
}
