#ifndef ESTERIA_PERK_WIRE_H
#define ESTERIA_PERK_WIRE_H

#include <cstdint>

// Shared verbatim between the client (Extensions/EsteriaPerks/src/PerkWire.h) and the server
// (src/server/shared/PerkWire.h). Do not let the copies drift.
//
// Paths of Fate in game. Little-endian integers.
//   CMSG_ESTERIA_PERK_SNAPSHOT_REQUEST  proto(u8)
//   CMSG_ESTERIA_PERK_PURCHASE          perk(u8) rank(u8)            the rank wanted: current rank + 1
//   CMSG_ESTERIA_PERK_RESPEC            none
//   SMSG_ESTERIA_PERK_RESULT            action(u8) perk(u8) rank(u8) result(u8); a snapshot follows unless the result
//                                       is Version or Disabled
//   SMSG_ESTERIA_PERK_SNAPSHOT          proto(u8) earned(u8) spent(u8) trait(u8) respecs(u8) respecCost(u32, copper)
//                                       respecLock(u8, a Result) count(u8), then per card:
//                                       perk(u8) path(u8) tier(u8) rank(u8) maxRank(u8) cost(u8) lock(u8) flags(u8)
// `lock` is the Result buying the card's next rank would get now (Ok when it can be bought, Rank when it is maxed).
// Cards the player's class can never use are left out.
namespace EsteriaPerkWire
{
    inline constexpr uint8_t Proto = 1;

    inline constexpr uint32_t CMSG_SNAPSHOT_REQUEST = 0x52B;
    inline constexpr uint32_t SMSG_SNAPSHOT = 0x52C;
    inline constexpr uint32_t CMSG_PURCHASE = 0x52D;
    inline constexpr uint32_t CMSG_RESPEC = 0x52E;
    inline constexpr uint32_t SMSG_RESULT = 0x52F;

    enum Action : uint8_t
    {
        ActionSnapshot = 0,
        ActionPurchase = 1,
        ActionRespec = 2,
    };

    enum Result : uint8_t
    {
        Ok = 0,
        Unknown = 1,        // no such card
        Rank = 2,           // not the next rank, or already at max rank
        Level = 3,          // below the tier's level
        PathPoints = 4,     // too few points spent in the path
        Points = 5,         // too few unspent points
        LegendaryOwned = 6, // another legendary is owned
        Feat = 7,           // the legendary's feat is not done
        Planned = 8,        // the card has no effect yet
        Class = 9,          // the class can never use the card
        Disabled = 10,      // Paths of Fate is off on this realm
        Place = 11,         // respec: in combat, or not resting in an inn or city
        Gold = 12,          // respec: not enough gold
        Nothing = 13,       // respec: nothing to reset
        Version = 14,       // the client speaks another protocol version
    };

    enum CardFlags : uint8_t
    {
        CardPlanned = 0x01, // shown as a preview: it has no effect yet
    };
}

#endif
