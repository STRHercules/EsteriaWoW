#pragma once

// Retail room-kit geometry, no server types so it can be tested alone (tests/rooms_test.cpp).
// A house is a list of rooms, each a retail HouseRoom kind placed at an offset from the room template's origin and
// turned by a multiple of 90 degrees. Kinds and their pieces come from housing_room_kind / housing_room_kit, generated
// from RoomComponent + RoomComponentOption (wowdecomp docs/housing/tools/phase3/make_kit.py).

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace EsteriaHousing::Rooms
{
    constexpr float Pi = 3.14159265358979f;
    // One floor of a house: retail's stairwell climbs to a landing 12 yd up, where its ceiling and the next floor are.
    constexpr float LevelHeight = 12.0f;

    struct KitPiece
    {
        uint32_t id = 0;     // RoomComponent.ID
        uint8_t type = 0;    // 1 wall, 2 floor, 3 ceiling
        float x = 0, y = 0, z = 0;
        float rotDeg = 0;    // RoomComponent.OffsetRot z
        uint32_t solid = 0, door = 0, wide = 0; // gameobject entries; door != 0 makes the piece a socket
        uint32_t doorFrame = 0, wideFrame = 0;  // frames centred on a joint: they cover the floor strip between rooms
        float width = 0;     // wall length, sockets only
        bool Socket() const { return door != 0; }
    };

    struct Kind
    {
        uint32_t id = 0;     // HouseRoom.ID
        std::string name;
        float min[3] = { 0, 0, 0 }, max[3] = { 0, 0, 0 }; // RoomWmoData.BoundingBox
        std::vector<KitPiece> pieces;
    };

    struct Room
    {
        uint32_t kind = 0;
        float x = 0, y = 0;  // offset from the template origin
        uint8_t quarter = 0; // yaw = quarter * 90 degrees
        int8_t level = 0;    // floor: 0 ground, -1 basement; its z is level * LevelHeight
    };

    struct Pose { float x = 0, y = 0, z = 0, yaw = 0, nx = 0, ny = 0; };
    struct Box { float min[2] = { 0, 0 }, max[2] = { 0, 0 }; };
    enum Variant : uint8_t { Solid, Door, Wide };

    using Kinds = std::map<uint32_t, Kind>;

    inline float QuarterYaw(uint8_t quarter) { return float(quarter % 4) * Pi / 2; }

    inline void Rotate(float yaw, float x, float y, float& ox, float& oy)
    {
        float const c = std::cos(yaw), s = std::sin(yaw);
        ox = x * c - y * s;
        oy = x * s + y * c;
    }

    inline Pose PieceWorld(Room const& room, KitPiece const& p)
    {
        Pose o;
        Rotate(QuarterYaw(room.quarter), p.x, p.y, o.x, o.y);
        o.x += room.x;
        o.y += room.y;
        o.z = p.z + float(room.level) * LevelHeight;
        // Retail's OffsetRot turns clockwise seen from above: only then do the corner pieces sit inside the room.
        o.yaw = QuarterYaw(room.quarter) - p.rotDeg * Pi / 180;
        Rotate(o.yaw, -1, 0, o.nx, o.ny); // a wall's slab lies on its local +x, so -x faces out of the room
        return o;
    }

    inline Box Footprint(Kind const& kind, Room const& room)
    {
        Box b;
        b.min[0] = b.min[1] = 1e9f;
        b.max[0] = b.max[1] = -1e9f;
        for (float cx : { kind.min[0], kind.max[0] })
            for (float cy : { kind.min[1], kind.max[1] })
            {
                float x, y;
                Rotate(QuarterYaw(room.quarter), cx, cy, x, y);
                b.min[0] = std::min(b.min[0], x + room.x); b.max[0] = std::max(b.max[0], x + room.x);
                b.min[1] = std::min(b.min[1], y + room.y); b.max[1] = std::max(b.max[1], y + room.y);
            }
        return b;
    }

    // Neighbours share a wall line, so boxes that only touch (within margin) do not overlap.
    inline bool Overlaps(Box const& a, Box const& b, float margin = 0.25f)
    {
        return a.min[0] < b.max[0] - margin && b.min[0] < a.max[0] - margin
            && a.min[1] < b.max[1] - margin && b.min[1] < a.max[1] - margin;
    }

    inline bool Contains(Box const& b, float x, float y)
    {
        return x >= b.min[0] && x <= b.max[0] && y >= b.min[1] && y <= b.max[1];
    }

    inline bool Joined(Pose const& a, Pose const& b)
    {
        return std::fabs(a.x - b.x) < 0.05f && std::fabs(a.y - b.y) < 0.05f && std::fabs(a.z - b.z) < 0.05f
            && a.nx * b.nx + a.ny * b.ny < -0.99f;
    }

    inline bool AxisAligned(Pose const& p) { return std::fabs(p.nx) > 0.99f || std::fabs(p.ny) > 0.99f; }

    inline uint32_t Model(KitPiece const& p, uint8_t variant)
    {
        if (variant == Wide && p.wide) return p.wide;
        if (variant != Solid && p.door) return p.door;
        return p.solid;
    }

    // One per pair of joined sockets: where the doorway is and which frame covers it (the first room's piece's).
    struct Joint
    {
        Pose pose;
        uint32_t frame = 0;
        size_t room = 0, piece = 0; // the first room's socket the frame belongs to
    };

    // variants[room][piece]: joined sockets open up, a door between full walls, a wide opening where one side is a
    // hallway-width wall (retail's 11 yd opening, RoomComponentOption Type 1 SubType 2).
    inline std::vector<std::vector<uint8_t>> Variants(Kinds const& kinds, std::vector<Room> const& rooms,
        std::vector<Joint>* joints = nullptr)
    {
        std::vector<std::vector<uint8_t>> out(rooms.size());
        for (size_t r = 0; r < rooms.size(); ++r)
            if (auto k = kinds.find(rooms[r].kind); k != kinds.end())
                out[r].assign(k->second.pieces.size(), Solid);
        for (size_t a = 0; a < rooms.size(); ++a)
            for (size_t b = a + 1; b < rooms.size(); ++b)
            {
                auto ka = kinds.find(rooms[a].kind), kb = kinds.find(rooms[b].kind);
                if (ka == kinds.end() || kb == kinds.end())
                    continue;
                for (size_t i = 0; i < ka->second.pieces.size(); ++i)
                    for (size_t j = 0; j < kb->second.pieces.size(); ++j)
                    {
                        KitPiece const& pa = ka->second.pieces[i];
                        KitPiece const& pb = kb->second.pieces[j];
                        Pose const poseA = PieceWorld(rooms[a], pa);
                        if (!pa.Socket() || !pb.Socket() || !Joined(poseA, PieceWorld(rooms[b], pb)))
                            continue;
                        uint8_t const v = std::min(pa.width, pb.width) < 12.0f && pa.wide && pb.wide ? Wide : Door;
                        out[a][i] = v;
                        out[b][j] = v;
                        uint32_t const frame = v == Wide ? pa.wideFrame : pa.doorFrame;
                        if (joints && frame)
                            joints->push_back({ poseA, frame, a, i });
                    }
            }
        return out;
    }

    // Sockets a new room can attach to: axis-aligned and not joined to another room.
    inline bool FreeSocket(Kinds const& kinds, std::vector<Room> const& rooms, size_t room, size_t piece)
    {
        auto k = kinds.find(rooms[room].kind);
        if (k == kinds.end() || piece >= k->second.pieces.size() || !k->second.pieces[piece].Socket())
            return false;
        Pose const p = PieceWorld(rooms[room], k->second.pieces[piece]);
        if (!AxisAligned(p))
            return false;
        for (size_t r = 0; r < rooms.size(); ++r)
            if (auto other = kinds.find(rooms[r].kind); r != room && other != kinds.end())
                for (KitPiece const& q : other->second.pieces)
                    if (q.Socket() && Joined(p, PieceWorld(rooms[r], q)))
                        return false;
        return true;
    }

    // Places a room of `kind` through free socket (room, piece): one of its own sockets is turned to face the
    // target and moved onto it. The first placement that overlaps no existing room wins.
    inline std::optional<Room> Attach(Kinds const& kinds, std::vector<Room> const& rooms, size_t room, size_t piece,
        uint32_t kind)
    {
        auto k = kinds.find(kind);
        if (k == kinds.end() || room >= rooms.size() || !FreeSocket(kinds, rooms, room, piece))
            return std::nullopt;
        KitPiece const& target = kinds.at(rooms[room].kind).pieces[piece];
        Pose const t = PieceWorld(rooms[room], target);
        for (KitPiece const& s : k->second.pieces)
        {
            if (!s.Socket())
                continue;
            for (uint8_t q = 0; q < 4; ++q)
            {
                Room candidate{ kind, 0, 0, q, rooms[room].level };
                Pose const p = PieceWorld(candidate, s);
                if (!AxisAligned(p) || p.nx * t.nx + p.ny * t.ny > -0.99f)
                    continue;
                candidate.x = t.x - p.x;
                candidate.y = t.y - p.y;
                Box const box = Footprint(k->second, candidate);
                bool clear = true;
                for (Room const& r : rooms)
                    if (auto other = kinds.find(r.kind); other != kinds.end() && r.level == candidate.level
                        && Overlaps(box, Footprint(other->second, r)))
                        clear = false;
                if (clear)
                    return candidate;
            }
        }
        return std::nullopt;
    }

    // True when no room on `room`'s floor overlaps it: for a room placed by rule (the stairwell top) rather than a socket.
    inline bool Fits(Kinds const& kinds, std::vector<Room> const& rooms, Room const& room)
    {
        auto k = kinds.find(room.kind);
        if (k == kinds.end())
            return false;
        Box const box = Footprint(k->second, room);
        for (Room const& r : rooms)
            if (auto other = kinds.find(r.kind); other != kinds.end() && r.level == room.level
                && Overlaps(box, Footprint(other->second, r)))
                return false;
        return true;
    }

    // A house exterior on a neighborhood plot. The plot's yaw turns the whole house counter-clockwise (a world facing);
    // each hook's own OffsetRot turns clockwise, as RoomComponent's does. Door pieces face out along their local +x.
    struct Hook { float x = 0, y = 0, z = 0, rotDeg = 0; };

    inline Pose OnPlot(float hx, float hy, float hz, float yaw, Hook const& h)
    {
        Pose p;
        Rotate(yaw, h.x, h.y, p.x, p.y);
        p.x += hx;
        p.y += hy;
        p.z = hz + h.z;
        p.yaw = yaw - h.rotDeg * Pi / 180;
        Rotate(p.yaw, 1, 0, p.nx, p.ny);
        return p;
    }

    // The door hook whose outside faces the plot's cornerstone most squarely: the front of the plot.
    inline size_t FrontDoor(float hx, float hy, float hz, float yaw, std::vector<Hook> const& doors, float cx, float cy)
    {
        size_t best = 0;
        float bestDot = -2;
        for (size_t i = 0; i < doors.size(); ++i)
        {
            Pose const p = OnPlot(hx, hy, hz, yaw, doors[i]);
            float dx = cx - p.x, dy = cy - p.y;
            float const len = std::sqrt(dx * dx + dy * dy);
            if (len < 1e-3f)
                continue;
            float const dot = (p.nx * dx + p.ny * dy) / len;
            if (dot > bestDot) { bestDot = dot; best = i; }
        }
        return best;
    }

    // "north wall" etc. for a socket's outward normal (+x is north, +y west on WoW maps).
    inline char const* Facing(Pose const& p)
    {
        if (p.nx > 0.7f) return "north";
        if (p.nx < -0.7f) return "south";
        if (p.ny > 0.7f) return "west";
        if (p.ny < -0.7f) return "east";
        return "angled";
    }
}
