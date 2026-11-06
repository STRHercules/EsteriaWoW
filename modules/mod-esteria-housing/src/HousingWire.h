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
//                 category(u8) surface(u8) name(string)
//   CMSG_EDIT     seq(u32) baseRevision(u32) op(u8) placedId(u64) decorId(u32) pos(f32 x3) rot(f32 x4 xyzw) scale(f32)
//   SMSG_EDIT_ACK seq(u32) result(u8) revision(u32) placedId(u64) pos(f32 x3) rot(f32 x4) scale(f32)
//                 the transform is the server-final one; it is zero when result != Ok
//   CMSG_ENTER    action(u8): 0 send me SMSG_STATE, 1 leave the house
//   SMSG_STATE    inHouse(u8) isOwner(u8) houseId(u32) revision(u32) placed(u16) maxDecor(u16)
//                 boundsMin(f32 x3) boundsMax(f32 x3) n(u16), then n x
//                 placedId(u64) decorId(u32) pos(f32 x3) yaw(f32, radians)
//                 sent on entering a house, after every accepted edit (to everyone inside) and on request
namespace EsteriaHousingWire
{
    inline constexpr uint16_t Proto = 1;

    inline constexpr uint32_t CMSG_HELLO = 0x537;
    inline constexpr uint32_t SMSG_HELLO = 0x538;
    inline constexpr uint32_t CMSG_CATALOG = 0x539;
    inline constexpr uint32_t SMSG_CATALOG = 0x53A;
    inline constexpr uint32_t CMSG_EDIT = 0x53B;
    inline constexpr uint32_t SMSG_EDIT_ACK = 0x53C;
    inline constexpr uint32_t CMSG_ENTER = 0x53D;
    inline constexpr uint32_t SMSG_STATE = 0x53E;

    inline constexpr uint16_t CatalogPageSize = 50;
    inline constexpr uint16_t MaxStateEntries = 1000;

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
