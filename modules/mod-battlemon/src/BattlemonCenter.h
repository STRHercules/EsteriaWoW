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
    Supplies = 5
};

// Gossip senders for the menu shop (GOSSIP_SENDER_MAIN is the service menu).
enum ShopSender : uint32_t
{
    SENDER_SHOP_CATEGORY = 2001, // action = item pocket, 0 = the category list
    SENDER_SHOP_PAGE = 2002,     // action = pocket * 1000 + page
    SENDER_SHOP_ITEM = 2003      // action = index into the shop list; the player types a quantity
};
}

#endif
