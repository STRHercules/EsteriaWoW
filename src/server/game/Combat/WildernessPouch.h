/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information.
 * Distributed under the GNU General Public License, version 2 or later.
 */

#ifndef AC_WILDERNESS_POUCH_H
#define AC_WILDERNESS_POUCH_H

#include "DatabaseEnvFwd.h"
#include "Define.h"
#include <algorithm>
#include <memory>

class ChatHandler;
class Item;
class Map;
class Player;
struct Mail;

namespace Acore::WorldPvp
{
constexpr uint32 WildernessPouchCopper(uint32 wallet, bool freebornKillingBlow = false)
{
    return freebornKillingBlow ? std::min(wallet / 50, 100000u) : std::min(wallet / 100, 50000u);
}

constexpr uint32 WildernessDeathXpLoss(uint32 xp)
{
    return xp / 20;
}

constexpr uint32 WildernessAuctionFee(uint32 copper, bool owner)
{
    return copper / (owner ? 10 : 4);
}

constexpr uint64 WildernessItemAuctionValue(uint32 vendorPrice, uint32 count)
{
    return std::max(uint64(100), uint64(vendorPrice) * count);
}

constexpr uint32 WildernessItemAuctionFee(uint32 value, bool owner)
{
    return owner ? value / 4 : value;
}

Item* SelectWildernessSupplyToSteal(Player const& player);
std::unique_ptr<Mail> MakeWorldPvpItemMail(Player const& receiver, Item const& item, char const* subject);
void BindWorldPvpItemMail(CharacterDatabasePreparedStatement& statement, Mail const& mail);
void PublishWorldPvpItemMail(Player& receiver, std::unique_ptr<Mail> mail, std::unique_ptr<Item> item);

void LoadWildernessPouches(Map& map, uint32 gridX, uint32 gridY);
AC_GAME_API bool InteractWithWildernessPouch(ChatHandler& handler, uint64 id);
// The PvP window passes requireCapital = false; bounty collectors and the command keep the capital rule.
AC_GAME_API bool InteractWithBloodyAuctionHouse(ChatHandler& handler, uint64 id, bool requireCapital = true);
}

#endif
