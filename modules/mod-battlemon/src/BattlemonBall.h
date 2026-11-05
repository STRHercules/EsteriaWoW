#ifndef BATTLEMON_BALL_H
#define BATTLEMON_BALL_H

#include <cstdint>

// A sealed Pokemon is a real WoW item, so it can be traded, mailed and auctioned. There is one item
// template per species and shiny state (tools/export_ball_items.py writes them), which lets the
// auction house search by species name. The Pokemon itself stays in battlemon_owned with guid = 0 and is
// linked to the item through battlemon_ball_item.
namespace BattlemonBall
{
// Keep in step with tools/export_ball_items.py.
constexpr uint32_t ITEM_BASE = 960000;       // entry = ITEM_BASE + species id
constexpr uint32_t ITEM_SHINY_OFFSET = 2000; // shiny entry = ITEM_BASE + ITEM_SHINY_OFFSET + species id
constexpr uint32_t PAGE_SIZE = 10;

constexpr uint32_t ItemEntry(uint32_t speciesId, bool shiny)
{
    return ITEM_BASE + (shiny ? ITEM_SHINY_OFFSET : 0) + speciesId;
}

// Gossip senders used by the Center's storage menu (GOSSIP_SENDER_MAIN is the existing service menu).
enum Sender : uint32_t
{
    SENDER_SEAL = 1001, // action = battlemon_owned.id to seal
    SENDER_PAGE = 1002  // action = page number
};
}

#endif
