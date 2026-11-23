/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 *
 * This program is free software; you can redistribute it and/or modify it under the terms of
 * the GNU General Public License as published by the Free Software Foundation, version 2 or later.
 */

#include "CharacterCache.h"
#include "Chat.h"
#include "DatabaseEnv.h"
#include "DBCStores.h"
#include "GameTime.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "PlayerScript.h"
#include "StringConvert.h"
#include "StringFormat.h"
#include "WildernessPouch.h"
#include "World.h"
#include "WorldPvpWilderness.h"
#include "WorldPvpBountyTargets.h"
#include "WorldPvpRules.h"
#include "WorldSession.h"

// Implemented in WorldPvpEscrowCommands.cpp so the window and .bountyescrow post share one escrow path.
bool PostWorldPvpBounty(ChatHandler& handler, ObjectGuid target, std::string const& name, uint32 copper);
uint32 CollectWorldPvpClaims(ChatHandler& handler);

namespace
{
constexpr char Prefix[] = "EsteriaCrime\t";
constexpr uint32 WantedDebuff = 955080;
constexpr uint32 ThiefDebuff = 955083;
constexpr uint32 RowLimit = 50;

bool IsCrimeAddon(uint32 lang, std::string const& msg)
{
    return lang == LANG_ADDON && msg.starts_with(Prefix);
}

void Reply(Player* player, std::string const& body)
{
    WorldPacket packet;
    ChatHandler::BuildChatPacket(packet, CHAT_MSG_WHISPER, LANG_ADDON, player, player, Prefix + body);
    player->SendDirectMessage(&packet);
}

// Field values never contain tabs: names are validated and numbers are formatted here.
void ReplyRows(WorldSession* session, ObjectGuid viewer, std::string const& kind, QueryResult result,
    std::function<std::string(Field*)> format)
{
    Player* player = session->GetPlayer();
    if (!player || player->GetGUID() != viewer)
        return;

    if (result)
    {
        do
            Reply(player, kind + "\t" + format(result->Fetch()));
        while (result->NextRow());
    }
    Reply(player, "E\t" + kind);
}

void Query(Player* player, std::string const& kind, std::string const& sql, std::function<std::string(Field*)> format)
{
    WorldSession* session = player->GetSession();
    ObjectGuid const viewer = player->GetGUID();
    session->GetQueryProcessor().AddCallback(CharacterDatabase.AsyncQuery(sql).WithCallback(
        [session, viewer, kind, format = std::move(format)](QueryResult result)
        { ReplyRows(session, viewer, kind, std::move(result), format); }));
}

std::string ZoneName(uint32 zone)
{
    AreaTableEntry const* area = sAreaTableStore.LookupEntry(zone);
    return area ? area->area_name[sWorld->GetDefaultDbcLocale()] : "Unknown";
}

void SendStatus(Player* player)
{
    using namespace Acore::WorldPvp;
    uint32 const guid = player->GetGUID().GetCounter();
    uint32 const now = GameTime::GetGameTime().count();
    uint32 const wantedUntil = player->GetPlayerSetting(CrimeSettingsSource, WantedUntil).value;
    uint64 const bounty = CanUseBountyEscrow() ? ActiveBountyCopper(guid).value_or(0) : 0;
    std::string const header = Acore::StringFormat("{}\t{}\t{}\t{}\t{}\t{}",
        sWorld->getBoolConfig(CONFIG_ESTERIA_WORLD_PVP) ? 1 : 0,
        player->HasAura(WantedDebuff) ? 1 : 0, player->HasAura(ThiefDebuff) ? 1 : 0,
        player->GetPlayerSetting(CrimeSettingsSource, Notoriety).value, bounty,
        wantedUntil > now ? wantedUntil - now : 0);

    // Lifetime totals come from the ledgers so the window survives death clearing notoriety.
    Query(player, "S", Acore::StringFormat(
        "SELECT (SELECT COUNT(*) FROM character_world_pvp_murder_log WHERE killer_guid = {0}), "
        "(SELECT CAST(COALESCE(SUM(amount), 0) AS UNSIGNED) FROM character_world_pvp_pickpocket "
        "WHERE thief_guid = {0} AND settled = 1)", guid),
        [header](Field* row)
        { return Acore::StringFormat("{}\t{}\t{}", header, row[0].Get<uint64>(), row[1].Get<uint64>()); });
}

void SendBoard(Player* player)
{
    Query(player, "B",
        "SELECT c.name, c.class, c.level, CAST(SUM(IF(b.sponsor_guid = 0, b.amount, 0)) AS UNSIGNED), "
        "CAST(SUM(IF(b.sponsor_guid <> 0, b.amount, 0)) AS UNSIGNED) "
        "FROM character_world_pvp_bounty b JOIN characters c ON c.guid = b.target_guid "
        "AND c.deleteDate IS NULL AND c.account <> b.sponsor_account "
        "WHERE b.state = 1 AND (b.expires_at IS NULL OR b.expires_at > UTC_TIMESTAMP()) "
        "GROUP BY c.guid, c.name, c.class, c.level ORDER BY SUM(b.amount) DESC, c.guid LIMIT 50",
        [](Field* row)
        {
            return Acore::StringFormat("{}\t{}\t{}\t{}\t{}", row[0].Get<std::string>(), row[1].Get<uint8>(),
                row[2].Get<uint8>(), row[3].Get<uint64>(), row[4].Get<uint64>());
        });
}

void SendLog(Player* player)
{
    // Kinds: 1 murder, 2 theft, 3 failed theft. Times are seconds since the Unix epoch in UTC.
    Query(player, "L", Acore::StringFormat(
        "SELECT 1, COALESCE(c.name, '?'), 0, 0, l.zone_id, "
        "CAST(TIMESTAMPDIFF(SECOND, '1970-01-01 00:00:00', l.occurred_at) AS UNSIGNED) AS t "
        "FROM character_world_pvp_murder_log l LEFT JOIN characters c ON c.guid = l.victim_guid "
        "WHERE l.killer_guid = {0} "
        "UNION ALL SELECT IF(p.amount > 0 OR p.item_guid > 0, 2, 3), COALESCE(c.name, '?'), p.amount, "
        "p.item_count, 0, CAST(TIMESTAMPDIFF(SECOND, '1970-01-01 00:00:00', p.attempted_at) AS UNSIGNED) "
        "FROM character_world_pvp_pickpocket p LEFT JOIN characters c ON c.guid = p.victim_guid "
        "WHERE p.thief_guid = {0} AND p.settled = 1 ORDER BY t DESC LIMIT {1}",
        player->GetGUID().GetCounter(), RowLimit),
        [](Field* row)
        {
            uint32 const zone = uint32(row[4].Get<uint64>());
            return Acore::StringFormat("{}\t{}\t{}\t{}\t{}\t{}", row[0].Get<uint64>(), row[1].Get<std::string>(),
                row[2].Get<uint64>(), row[3].Get<uint64>(), zone ? ZoneName(zone) : "", row[5].Get<uint64>());
        });
}

void SendLeaders(Player* player)
{
    auto const format = [](Field* row)
    { return Acore::StringFormat("{}\t{}\t{}", row[0].Get<uint64>(), row[1].Get<std::string>(), row[2].Get<uint64>()); };
    Query(player, "T",
        "(SELECT 1, c.name, CAST(COUNT(*) AS UNSIGNED) AS v FROM character_world_pvp_murder_log l "
        "JOIN characters c ON c.guid = l.killer_guid AND c.deleteDate IS NULL "
        "GROUP BY l.killer_guid, c.name ORDER BY v DESC LIMIT 10) "
        "UNION ALL (SELECT 2, c.name, CAST(SUM(p.amount) AS UNSIGNED) AS v FROM character_world_pvp_pickpocket p "
        "JOIN characters c ON c.guid = p.thief_guid AND c.deleteDate IS NULL WHERE p.settled = 1 AND p.amount > 0 "
        "GROUP BY p.thief_guid, c.name ORDER BY v DESC LIMIT 10) "
        "UNION ALL (SELECT 3, c.name, CAST(SUM(b.amount) AS UNSIGNED) AS v FROM character_world_pvp_bounty b "
        "JOIN characters c ON c.guid = b.target_guid AND c.deleteDate IS NULL AND c.account <> b.sponsor_account "
        "WHERE b.state = 1 AND (b.expires_at IS NULL OR b.expires_at > UTC_TIMESTAMP()) "
        "GROUP BY b.target_guid, c.name ORDER BY v DESC LIMIT 10)",
        format);
}

void SendClaims(Player* player)
{
    WorldSession* session = player->GetSession();
    ObjectGuid const viewer = player->GetGUID();
    auto* stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WORLD_PVP_CLAIMS);
    stmt->SetData(0, viewer.GetCounter());
    stmt->SetData(1, session->GetAccountId());
    session->GetQueryProcessor().AddCallback(CharacterDatabase.AsyncQuery(stmt).WithPreparedCallback(
        [session, viewer](PreparedQueryResult result)
        {
            Player* hunter = session->GetPlayer();
            if (!hunter || hunter->GetGUID() != viewer)
                return;

            if (result)
            {
                do
                {
                    Field* row = result->Fetch();
                    std::string name = "?";
                    sCharacterCache->GetCharacterNameByGuid(
                        ObjectGuid::Create<HighGuid::Player>(row[2].Get<uint32>()), name);
                    Reply(hunter, Acore::StringFormat("C\t{}\t{}\t{}", row[0].Get<uint32>() ? 1 : 0, name,
                        row[3].Get<uint32>()));
                }
                while (result->NextRow());
            }
            Reply(hunter, "E\tC");
        }));
}

// One line: seconds until the next rotation, hours per rotation, then each active zone name.
void SendWilderness(Player* player)
{
    std::string body = Acore::StringFormat("W\t{}\t{}",
        Acore::WorldPvp::SecondsUntilWildernessRotation(GameTime::GetGameTime().count()),
        std::max(sWorld->getIntConfig(CONFIG_ESTERIA_WILDERNESS_HOURS), 1u));
    for (uint32 zone : Acore::WorldPvp::ActiveWildernessZones())
        body += "\t" + ZoneName(zone);
    Reply(player, body);
}

void SendAuction(Player* player)
{
    using namespace Acore::WorldPvp;
    auto* query = CharacterDatabase.GetPreparedStatement(CHAR_SEL_WILDERNESS_AUCTION_POUCHES);
    query->SetData(0, player->GetGUID().GetCounter());
    query->SetData(1, player->GetSession()->GetAccountId());
    query->SetData(2, uint64(0));
    query->SetData(3, uint64(0));
    if (PreparedQueryResult rows = CharacterDatabase.Query(query))
    {
        do
        {
            Field* row = rows->Fetch();
            uint32 const copper = row[1].Get<uint32>();
            bool const owner = row[2].Get<uint64>() != 0;
            uint32 const entry = row[4].Get<uint32>();
            ItemTemplate const* proto = entry ? sObjectMgr->GetItemTemplate(entry) : nullptr;
            uint32 const price = entry ? WildernessItemAuctionFee(row[5].Get<uint32>(), owner) :
                WildernessAuctionFee(copper, owner);
            // id, owner, copper inside, item entry, item count, item name, price to buy
            Reply(player, Acore::StringFormat("A\t{}\t{}\t{}\t{}\t{}\t{}\t{}", row[0].Get<uint64>(), owner ? 1 : 0,
                copper, entry, row[6].Get<uint64>(), proto ? proto->Name1 : "", price));
        }
        while (rows->NextRow());
    }
    Reply(player, "E\tA");
}

void Buy(Player* player, std::string_view args)
{
    ChatHandler handler(player->GetSession());
    if (uint64 const id = Acore::StringTo<uint64>(args).value_or(0))
        Acore::WorldPvp::InteractWithBloodyAuctionHouse(handler, id, false);
    SendAuction(player);
    SendStatus(player);
}

void Collect(Player* player)
{
    ChatHandler handler(player->GetSession());
    if (!player->IsAlive() || player->IsInCombat())
        handler.SendErrorMessage("You can't collect bounties while dead or in combat.");
    else if (!CollectWorldPvpClaims(handler))
        handler.SendErrorMessage("You have no bounty claims that fit in your wallet.");
    SendClaims(player);
    SendStatus(player);
}

void Post(Player* player, std::string_view args)
{
    ChatHandler handler(player->GetSession());
    auto const tab = args.find('\t');
    std::string name(args.substr(0, tab));
    uint64 gold = 0;
    if (tab != std::string_view::npos)
        gold = Acore::StringTo<uint64>(args.substr(tab + 1)).value_or(0);

    if (!normalizePlayerName(name) || gold == 0 || gold > MAX_MONEY_AMOUNT / GOLD)
    {
        handler.SendErrorMessage("Enter a character name and a whole number of gold.");
        return;
    }

    ObjectGuid const target = sCharacterCache->GetCharacterGuidByName(name);
    if (!target)
    {
        handler.SendErrorMessage("No character named {} was found.", name);
        return;
    }

    if (PostWorldPvpBounty(handler, target, name, uint32(gold * GOLD)))
        Reply(player, "P\t1");
    SendBoard(player);
    SendStatus(player);
}

class world_pvp_crime_ui final : public PlayerScript
{
public:
    world_pvp_crime_ui() : PlayerScript("world_pvp_crime_ui",
        { PLAYERHOOK_ON_BEFORE_SEND_CHAT_MESSAGE, PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT }) { }

    void OnPlayerBeforeSendChatMessage(Player* player, uint32& /*type*/, uint32& lang, std::string& msg) override
    {
        if (!IsCrimeAddon(lang, msg))
            return;

        std::string_view const body = std::string_view(msg).substr(sizeof(Prefix) - 1);
        auto const tab = body.find('\t');
        std::string_view const command = body.substr(0, tab);
        if (command == "status")
            SendStatus(player);
        else if (command == "board")
            SendBoard(player);
        else if (command == "log")
            SendLog(player);
        else if (command == "top")
            SendLeaders(player);
        else if (command == "claims")
            SendClaims(player);
        else if (command == "collect")
            Collect(player);
        else if (command == "wild")
            SendWilderness(player);
        else if (command == "auction")
            SendAuction(player);
        else if (command == "buy" && tab != std::string_view::npos)
            Buy(player, body.substr(tab + 1));
        else if (command == "post" && tab != std::string_view::npos)
            Post(player, body.substr(tab + 1));
    }

    bool OnPlayerCanUseChat(Player* /*player*/, uint32 /*type*/, uint32 lang, std::string& msg, Player* /*receiver*/)
        override
    {
        return !IsCrimeAddon(lang, msg);
    }
};
}

void AddWorldPvpCrimeUi()
{
    new world_pvp_crime_ui();
}
