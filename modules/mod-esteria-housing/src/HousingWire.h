#ifndef ESTERIA_HOUSING_WIRE_H
#define ESTERIA_HOUSING_WIRE_H

#include <cstdint>

// Shared verbatim between the client (wowdecomp Extensions/Housing/src/HousingWire.h) and the server
// (EsteriaWoW modules/mod-esteria-housing/src/HousingWire.h). Do not let the copies drift.
// Little-endian integers, IEEE floats, NUL-terminated strings. docs/housing/protocol.md has the design.
//
//   CMSG_HELLO    proto(u16) clientFeatures(u32)
//   SMSG_HELLO    proto(u16) enabled(u8) serverFeatures(u32) catalogVersion(u32) maxDecor(u16)
//                 minScale(f32) maxScale(f32) snapDegrees(f32)
//   CMSG_CATALOG  page(u32)
//   SMSG_CATALOG  page(u32) pageCount(u32) n(u16), then n x
//                 decorId(u32) gameobjectEntry(u32) modelFileDataId(u32) available(u16) placed(u16)
//                 category(u8) surface(u8) price(u32 copper) name(string)
//   CMSG_EDIT     seq(u32) baseRevision(u32) op(u8) placedId(u64) decorId(u32) pos(f32 x3) rot(f32 x4 xyzw) scale(f32)
//   SMSG_EDIT_ACK seq(u32) result(u8) revision(u32) placedId(u64) pos(f32 x3) rot(f32 x4) scale(f32)
//                 the transform is the server-final one; it is zero when result != Ok
//   CMSG_ENTER    action(u8): 0 send me SMSG_STATE, 1 leave the house
//   SMSG_STATE    inHouse(u8) isOwner(u8) houseId(u32) revision(u32) placed(u16) maxDecor(u16)
//                 boundsMin(f32 x3) boundsMax(f32 x3) n(u16), then n x
//                 placedId(u64) decorId(u32) pos(f32 x3) rot(f32 x4, xyzw) scale(f32)
//                 sent on entering a house, after every accepted edit (to everyone inside) and on request
//   CMSG_ACTION   action(u8), then for ActionAddRoom room(u8) piece(u8) kind(u32), ActionRoomStyle room(u8) part(u8)
//                 theme(u32), ActionRoomCeiling room(u8) hidden(u8), ActionStairsUp room(u8), ActionBuyDecor decorId(u32)
//                 count(u16); nothing for the others.
//                 Rooms cost gold. A kind of StairsDownBase + stairwell builds that stairwell down from the socket.
//                 Plot actions act on the plot whose cornerstone the player last clicked, and re-check range.
//   SMSG_PLOT     plot(u16, 1-based) status(u8 PlotStatus) price(u32 copper) houseElsewhere(u8)
//                 neighborhood(string) owner(string) message(string)
//                 sent when a cornerstone is clicked (the client opens the plot window) and after a plot action
//   SMSG_LAYOUT   maxRooms(u8) originX(f32) originY(f32)
//                 kinds n(u8), then n x kind(u32) sizeX(f32) sizeY(f32) price(u32 copper) name(string)
//                 rooms n(u8), then n x kind(u32) x(f32) y(f32) quarter(u8) wallTheme floorTheme ceilingTheme(u32)
//                 ceilingHidden(u8) level(i8: floor, 0 ground, -1 basement)
//                 sockets n(u16), then n x room(u8) piece(u8) level(i8) x(f32) y(f32) nx(f32) ny(f32)
//                 fits n(u8) x kind(u32)
//                 themes n(u8), then n x theme(u32) name(string)
//                 maxFloors(u8) floorPrice(u32 copper, 0 at the cap) decorPrice(u32, 0 at the cap) decorStep(u16)
//                 decorCap(u16)
//                 room offsets and socket poses are relative to the origin; sent to the owner with each SMSG_STATE
namespace EsteriaHousingWire
{
    inline constexpr uint16_t Proto = 8;

    inline constexpr uint32_t CMSG_HELLO = 0x537;
    inline constexpr uint32_t SMSG_HELLO = 0x538;
    inline constexpr uint32_t CMSG_CATALOG = 0x539;
    inline constexpr uint32_t SMSG_CATALOG = 0x53A;
    inline constexpr uint32_t CMSG_EDIT = 0x53B;
    inline constexpr uint32_t SMSG_EDIT_ACK = 0x53C;
    inline constexpr uint32_t CMSG_ENTER = 0x53D;
    inline constexpr uint32_t SMSG_STATE = 0x53E;
    inline constexpr uint32_t CMSG_ACTION = 0x53F;
    inline constexpr uint32_t SMSG_PLOT = 0x540;
    inline constexpr uint32_t SMSG_LAYOUT = 0x541;

    inline constexpr uint16_t CatalogPageSize = 50;
    inline constexpr uint16_t MaxStateEntries = 5000; // the largest decor budget

    enum Op : uint8_t
    {
        OpPlace = 1,
        OpMove = 2,
        OpRemove = 3,
    };

    enum EnterAction : uint8_t
    {
        EnterSync = 0,
        EnterLeave = 1,
    };

    enum Action : uint8_t
    {
        ActionBuyPlot = 1,
        ActionEnterPlot = 2,
        ActionAddRoom = 3,
        ActionRemoveRoom = 4, // the newest room
        ActionRoomStyle = 5,  // room(u8) part(u8: 1 walls 2 floor 3 ceiling) theme(u32)
        ActionRoomCeiling = 6, // room(u8) hidden(u8)
        ActionStairsUp = 7,   // room(u8): a stairwell's top becomes another stairwell, with a new top above
        ActionBuyDecor = 8,   // decorId(u32) count(u16): the catalog's price each, into storage
        ActionUpgrade = 9,    // what(u8 Upgrade): buy the house's next floor or decor budget step
    };

    inline constexpr uint32_t StairsDownBase = 1000;

    enum Upgrade : uint8_t
    {
        UpgradeFloors = 1, // one more floor above the ground, 4 to 15
        UpgradeDecor = 2,  // the decor budget, 200 to 5000 in steps of 100
    };

    enum PlotStatus : uint8_t
    {
        PlotForSale = 0,
        PlotYours = 1,
        PlotVisitable = 2, // someone's, and you may go in (grouped with the owner)
        PlotPrivate = 3,
    };

    enum Result : uint8_t
    {
        Ok = 0,
        Disabled = 1,
        NotInHouse = 2,
        NoPermission = 3,
        DuplicateSeq = 4,
        StaleRevision = 5,
        UnknownDecor = 6,
        NoneLeft = 7,
        UnknownPlacement = 8,
        OutOfBounds = 9,
        BadTransform = 10,
        OverBudget = 11,
        RateLimited = 12,
        Internal = 13,
        BadOp = 14,
    };

    enum Category : uint8_t
    {
        CategoryMisc = 0,
        CategoryFurniture = 1,
        CategoryAccents = 2,
        CategoryLighting = 3,
        CategoryNature = 4,
        CategoryStructural = 5,
    };

    enum Surface : uint8_t
    {
        SurfaceFloor = 0,
        SurfaceWall = 1,
        SurfaceCeiling = 2,
        SurfaceOnDecor = 3,
    };
}

#endif
