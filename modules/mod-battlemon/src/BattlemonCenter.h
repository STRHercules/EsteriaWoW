#ifndef BATTLEMON_CENTER_H
#define BATTLEMON_CENTER_H

#include <cstdint>

class Player;

namespace BattlemonCenter
{
// Optional profession integration, registered once during script startup.
inline void (*HealCompanion)(Player*) = nullptr;

enum Service : uint32_t
{
    Heal = 1,
    Shop = 2,
    Party = 3,
    Storage = 4,
    Supplies = 5,
    DayCare = 6
};

// Gossip senders for the menu shop (GOSSIP_SENDER_MAIN is the service menu).
enum ShopSender : uint32_t
{
    SENDER_SHOP_CATEGORY = 2001, // action = item pocket, 0 = the category list
    SENDER_SHOP_PAGE = 2002,     // action = pocket * 1000 + page
    SENDER_SHOP_ITEM = 2003      // action = index into the shop list; the player types a quantity
};

// Gossip senders for the Day Care menu.
enum DayCareSender : uint32_t
{
    SENDER_DAYCARE_PUTLIST = 3001, // action = page of the Pokemon that can be left
    SENDER_DAYCARE_PUT = 3002,     // action = battlemon_owned.id to leave
    SENDER_DAYCARE_TAKE = 3003,    // action = battlemon_owned.id to take back
    SENDER_DAYCARE_CHECK = 3004    // check the pair and hatch ready eggs
};
}

#endif
