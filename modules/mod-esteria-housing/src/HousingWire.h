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
//   SMSG_STATE    inHouse(u8) isOwner(u8) outdoors(u8) houseId(u32) revision(u32) placed(u16) maxDecor(u16)
//                 (outdoors: the owner on their own plot, editing its outdoor decor; inHouse is then 1 too)
//                 boundsMin(f32 x3) boundsMax(f32 x3) n(u16), then n x
//                 placedId(u64) decorId(u32) pos(f32 x3) rot(f32 x4, xyzw) scale(f32)
//                 then the plot's house (outdoors; zeros otherwise): spot x y z (f32) yaw (f32 radians), its offset dx dy dz
//                 (f32 yd), turn (f32 degrees), scale (f32) and reach (f32 yd)
//                 sent on entering a house, after every accepted edit (to everyone inside) and on request
//   CMSG_ACTION   action(u8), then for ActionAddRoom room(u8) piece(u8) kind(u32), ActionRoomStyle room(u8) part(u8)
//                 theme(u32), ActionRoomCeiling room(u8) hidden(u8), ActionStairsUp room(u8), ActionBuyDecor decorId(u32)
//                 count(u16), ActionHouseAccess access(u8 Access bits), ActionPlotFixture type(u8) component(u32),
//                 ActionPlotSpot spot(u8, as SMSG_PLOT lists them) type(u8 FixtureType, 0 empty);
//                 nothing for the others.
//                 Rooms cost gold. A kind of StairsDownBase + stairwell builds that stairwell down from the socket.
//                 Plot actions act on the plot whose cornerstone the player last clicked, and re-check range.
//   SMSG_PLOT     plot(u16, 1-based) status(u8 PlotStatus) price(u32 copper) unused(u8, 0)
//                 neighborhood(string) owner(string) message(string)
//                 then style(u32) dx(f32) dy(f32) dz(f32) turn(f32 degrees) scale(f32) reach(f32 yd)
//                 styles n(u8) x style(u32) name(string)
//                 (your plot only; n 0 otherwise)
//                 fixtures n(u8) x type(u8 FixtureType) chosen(u32 component) options n(u16) x component(u32)
//                 parent(u32: a colour variant's shape, 0 for a shape) name(string)  (your plot only; n 0 otherwise)
//                 spots n(u8) x x y z(f32, world) accepts(u8 SpotAccepts bits) type(u8 FixtureType, 0 empty): the places on
//                 the walls and roof a dormer, tower or chimney can go (your plot only)
//                 then neighborhood(u32) favorite(u8: the plot's house is one of yours) house(u32, 0 none) canBuy(u8)
//                 choices n(u8) x house(u32) label(string): your houses not yet in this neighborhood, to mirror here
//                 sent when a cornerstone is clicked (the client opens the plot window) and after a plot action
//   SMSG_LAYOUT   maxRooms(u8) originX(f32) originY(f32)
//                 kinds n(u8), then n x kind(u32) sizeX(f32) sizeY(f32) price(u32 copper) name(string)
//                 rooms n(u8), then n x kind(u32) x(f32) y(f32) quarter(u8) wallTheme floorTheme ceilingTheme(u32)
//                 ceilingHidden(u8) level(i8: floor, 0 ground, -1 basement)
//                 sockets n(u16), then n x room(u8) piece(u8) level(i8) x(f32) y(f32) nx(f32) ny(f32)
//                 fits n(u8) x kind(u32)
//                 themes n(u8), then n x theme(u32) name(string)
//                 maxFloors(u8) floorPrice(u32 copper, 0 at the cap) decorPrice(u32, 0 at the cap) decorStep(u16)
//                 decorCap(u16) roomPrice(u32, 0 at the cap) roomStep(u8) roomCap(u8)
//                 room offsets and socket poses are relative to the origin; sent to the owner with each SMSG_STATE
//   SMSG_NEIGHBORHOOD the Neighborhood window's contents: the answer to every ActionNeighborhood and ActionTravel*
//                 the neighborhood shown: id(u32) kind(u8 0 an account's, 1 a guild's) map(u8: 0 Founder's Point,
//                 1 Razorwind Shores) name(string) mapName(string) plotPrice(u32 copper) where(u8 Where) message(string)
//                 rights(u8 Right bits, yours there) here(u8: you are in it) choose(u8: your account has not picked its
//                 neighborhood's map yet; ActionHoodMap on it picks, the same map included)
//                 plots n(u16) x plot(u16) status(u8 PlotStatus) name(string: the owner's character, yours or visitable)
//                 homes n(u8) x house(u32) neighborhood(u32) plot(u16) neighborhoodName(string) rooms(u8) placed(u16)
//                 maxDecor(u16) access(u8 Access bits): a row per plot each of your houses stands on (0 0: saved, on none)
//                 neighborhoods n(u8) x id(u32) kind(u8) role(u8: 0 yours, 1 invited, 2 your guild's, 3 visiting) map(u8)
//                 freePlots(u16) name(string)
//                 favorites n(u8), recent n(u8), each x house(u32) neighborhood(u32) plot(u16, 0 gone) owner(string)
//                 neighborhoodName(string) ok(u8: you may go in)
//                 members n(u8) x account(u32) name(string): who the shown neighborhood invited (if you may invite)
//                 guild(u32, 0 none) leader(u8) neighborhoodPrice(u32 copper) bank(u32 copper) canBuy(u8)
//                 ranks n(u8) x rights(u8 Right bits) for guild ranks 1.. (to the leader only)
//   SMSG_COMMERCE text(string): newline-separated records of tab-separated fields, read by Commerce.lua
namespace EsteriaHousingWire
{
    inline constexpr uint16_t Proto = 18;

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
    inline constexpr uint32_t SMSG_NEIGHBORHOOD = 0x542;
    inline constexpr uint32_t SMSG_COMMERCE = 0x543;

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
        ActionBuyPlot = 1,             // house(u32, 0: build a new one): put a house on the viewed plot
        ActionEnterPlot = 2,
        ActionAddRoom = 3,
        ActionRemoveRoom = 4, // the newest room
        ActionRoomStyle = 5,  // room(u8) part(u8: 1 walls 2 floor 3 ceiling) theme(u32)
        ActionRoomCeiling = 6, // room(u8) hidden(u8)
        ActionStairsUp = 7,   // room(u8): a stairwell's top becomes another stairwell, with a new top above
        ActionBuyDecor = 8,   // decorId(u32) count(u16): the catalog's price each, into storage
        ActionUpgrade = 9,    // what(u8 Upgrade): buy the house's next floor or decor budget step
        ActionPlotStyle = 10, // style(u32): rebuild your plot's house in another exterior style
        ActionPlotPlace = 11, // dx dy dz(f32 yd) turnDegrees(f32) scale(f32): where the house stands on your plot, from its spot
        ActionNeighborhood = 12,       // neighborhood(u32, 0: the one you are in, else yours): send me SMSG_NEIGHBORHOOD
        ActionTravelNeighborhood = 13, // neighborhood(u32, 0 yours): go to its entry, from anywhere travel is allowed
        ActionTravelBack = 14,         // leave the neighborhood for where you came from
        ActionTravelPlot = 15,         // neighborhood(u32) plot(u16, 1-based): go to that plot, beside its cornerstone
        ActionHouseAccess = 16,        // house(u32) access(u8 Access bits): who may visit it; visitors who no longer may leave
        ActionPlotFixture = 17,        // type(u8 FixtureType) component(u32, 0: the style's default): swap a part of your house
        ActionPlotSpot = 18,           // spot(u8) type(u8): what stands on one of your house's wall or roof spots
        ActionFavorite = 19,           // house(u32) neighborhood(u32) on(u8)
        ActionInvite = 20,             // neighborhood(u32) name(string): that character's account may come in and buy plots
        ActionUninvite = 21,           // neighborhood(u32) account(u32)
        ActionHoodMap = 22,            // neighborhood(u32) map(u8): move it to the other map
        ActionBuyGuildHood = 23,       // map(u8): the Guild Master buys a guild neighborhood from the guild bank
        ActionGuildRights = 24,        // rank(u8, 1-9) rights(u8 Right bits): the Guild Master sets a rank's rights
        ActionMoveOut = 25,            // take your house off the viewed plot (it is saved)
        ActionEnterHouse = 26,         // house(u32): go into one of your houses
        ActionCommerce = 27,           // text(string): a shop or commission command, tab-separated
    };

    // What a player may do in a neighborhood (SMSG_NEIGHBORHOOD rights, guild rank rights).
    enum Right : uint8_t
    {
        RightBuy = 1,    // buy plots
        RightInvite = 2, // invite others in
        RightManage = 4, // move it to the other map
    };

    // Which of the spot types a wall or roof spot takes (SMSG_PLOT spots).
    enum SpotAccepts : uint8_t
    {
        SpotDormer = 1,
        SpotTower = 2,
        SpotChimney = 4,
    };

    // The parts of a house exterior an owner may swap (retail ExteriorComponentType).
    enum FixtureType : uint8_t
    {
        FixtureBase = 9, // the walls
        FixtureRoof = 10,
        FixtureDoor = 11,
        FixtureWindow = 12,
        FixtureDormer = 14, // on a roof spot
        FixtureTower = 15,  // on a wall or roof spot
        FixtureChimney = 16, // on a roof spot
    };

    // Who may go into a house besides its owner (housing_permission.scope n is bit 1 << n).
    enum Access : uint8_t
    {
        AccessEveryone = 1 << 0,
        AccessFriends = 1 << 1, // the owner's friends (any of the owner's characters)
        AccessGuild = 1 << 2,   // members of a guild one of the owner's characters is in
        AccessParty = 1 << 4,   // grouped with the owner; a new house's only setting
    };

    inline constexpr uint32_t StairsDownBase = 1000;

    enum Upgrade : uint8_t
    {
        UpgradeFloors = 1, // one more floor above the ground, 4 to 15
        UpgradeDecor = 2,  // the decor budget, 200 to 5000 in steps of 100
        UpgradeRooms = 3,  // the room limit, the realm's base (16) to 64 in steps of 4
    };

    enum PlotStatus : uint8_t
    {
        PlotForSale = 0,
        PlotYours = 1,
        PlotVisitable = 2, // someone's, and you may go in (its Access lets you)
        PlotPrivate = 3,
    };

    enum Where : uint8_t
    {
        WhereAway = 0,
        WhereNeighborhood = 1,
        WhereHouse = 2,
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
        ShopHasStock = 15, // removing a shop (merchant, case, shelf, rack, counter) that still has items for sale
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
