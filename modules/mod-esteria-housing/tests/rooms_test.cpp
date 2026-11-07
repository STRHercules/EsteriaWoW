// Room-kit geometry tests, no server needed:
//   g++ -std=c++20 -I modules/mod-esteria-housing/src modules/mod-esteria-housing/tests/rooms_test.cpp -o rooms_test && ./rooms_test
#include "HousingRooms.h"
#include <cstdio>

using namespace EsteriaHousing::Rooms;

static int failures = 0;
#define CHECK(x) do { if (!(x)) { std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #x); ++failures; } } while (0)

static bool Near(float a, float b) { return std::fabs(a - b) < 0.01f; }

int main()
{
    // Retail RoomComponent rows for HouseRoom 1 (RoomWmoData 5) and 2 (RoomWmoData 7); door/wide are fake entries.
    Kind small{ 1, "Square Room (Small)", { -11.5f, -11.5f, 0 }, { 11.5f, 11.5f, 11 }, {} };
    small.pieces = {
        { 25, 2, 0, 0, 0, 0, 10, 0, 0, 0 },
        { 26, 1, -12, 0, 0, 0, 11, 12, 13, 15, 16, 23 },
        { 27, 1, 0, 12, 0, 90, 11, 12, 13, 15, 16, 23 },
        { 28, 1, 0, -12, 0, -90, 11, 12, 13, 15, 16, 23 },
        { 29, 1, 12, 0, 0, -180, 11, 12, 13, 15, 16, 23 },
        { 30, 1, -11.5f, 11.5f, 0, -90, 14, 0, 0, 0 }, // corner: connectable in retail, but no door option
    };
    Kind hall{ 2, "Hallway", { -11.5f, -5.5f, 0 }, { 11.5f, 5.5f, 7 }, {} };
    hall.pieces = {
        { 45, 2, 0, 0, 0, 0, 20, 0, 0, 0 },
        { 46, 1, -12, 0, 0, 0, 21, 22, 23, 25, 26, 11 },
        { 47, 1, 12, 0, 0, -180, 21, 22, 23, 25, 26, 11 },
        { 48, 1, 0, 6, 0, 90, 24, 0, 0, 0 },
    };
    Kinds kinds{ { 1, small }, { 2, hall } };

    // Walls face out of the room; the corner's slab ends up inside the room's corner.
    Pose west = PieceWorld({ 1, 0, 0, 0 }, small.pieces[2]);
    CHECK(Near(west.ny, 1) && std::string(Facing(west)) == "west");
    Pose north = PieceWorld({ 1, 0, 0, 0 }, small.pieces[4]);
    CHECK(Near(north.nx, 1) && std::string(Facing(north)) == "north");
    Pose corner = PieceWorld({ 1, 0, 0, 0 }, small.pieces[5]);
    float cx, cy; // corner bounding box (-1.23..0.03)^2 measured from 6431794; its far point must stay in the room
    Rotate(corner.yaw, -1.23f, -1.23f, cx, cy);
    CHECK(Near(corner.yaw, Pi / 2) && cx + corner.x > -11.6f && cy + corner.y < 11.6f);

    std::vector<Room> rooms{ { 1, 0, 0, 0 } };
    CHECK(FreeSocket(kinds, rooms, 0, 4));
    CHECK(!FreeSocket(kinds, rooms, 0, 5)); // corners are never sockets
    CHECK(!FreeSocket(kinds, rooms, 0, 0)); // floors either

    // A second small room through the north wall sits 24 yd north, joined by doors on both sides.
    auto second = Attach(kinds, rooms, 0, 4, 1);
    CHECK(second && Near(second->x, 24) && Near(second->y, 0));
    rooms.push_back(*second);
    CHECK(!FreeSocket(kinds, rooms, 0, 4));
    auto v = Variants(kinds, rooms);
    CHECK(v[0][4] == Door);
    size_t joined = 0;
    for (uint8_t x : v[1]) joined += x == Door;
    CHECK(joined == 1);
    CHECK(Model(small.pieces[4], v[0][4]) == 12 && Model(small.pieces[1], v[0][1]) == 11);
    // One frame per doorway, centred on the joint (the first room's north wall at x 12) and turned with it.
    std::vector<Joint> joints;
    Variants(kinds, rooms, &joints);
    CHECK(joints.size() == 1 && joints[0].frame == 15 && Near(joints[0].pose.x, 12) && Near(joints[0].pose.y, 0));

    // A hallway through the west wall: hallway-width wall, so both sides get the wide opening.
    auto h = Attach(kinds, rooms, 0, 2, 2);
    CHECK(h && Near(h->x, 0) && Near(h->y, 24) && (h->quarter == 1 || h->quarter == 3));
    rooms.push_back(*h);
    v = Variants(kinds, rooms);
    CHECK(v[0][2] == Wide && Model(small.pieces[2], v[0][2]) == 13);
    joints.clear();
    Variants(kinds, rooms, &joints);
    CHECK(joints.size() == 2 && joints[1].frame == 16); // the hallway joint gets the wide frame

    // Footprints: the hallway runs north-south after its turn and does not overlap the first room.
    Box hb = Footprint(hall, rooms[2]);
    CHECK(Near(hb.max[0] - hb.min[0], 11) && Near(hb.max[1] - hb.min[1], 23));
    CHECK(!Overlaps(hb, Footprint(small, rooms[0])));
    CHECK(Contains(Footprint(small, rooms[1]), 24, 5) && !Contains(Footprint(small, rooms[1]), 40, 0));

    // Only placements that fit are offered. Off the north room's west wall a 47 yd room would be centred at (24, 36)
    // and run into the hallway (x -5.5..5.5, y 12.5..35.5); off its east wall it clears everything.
    Kind large{ 12, "Square Room (Large)", { -23.5f, -23.5f, 0 }, { 23.5f, 23.5f, 11 }, {} };
    large.pieces = { { 41, 1, -24, 0, 0, 0, 31, 32, 33, 35, 36, 47 } };
    kinds[12] = large;
    CHECK(!Attach(kinds, rooms, 1, 2, 12));
    auto east = Attach(kinds, rooms, 1, 3, 12);
    CHECK(east && Near(east->x, 24) && Near(east->y, -36));

    // Floors: a room one floor up sits LevelHeight higher, overlaps nothing below, and joins only rooms on its floor.
    std::vector<Room> stack{ { 1, 0, 0, 0, 0 }, { 1, 0, 0, 0, 1 } };
    CHECK(Near(PieceWorld(stack[1], small.pieces[1]).z, LevelHeight));
    CHECK(Fits(kinds, { stack[0] }, stack[1]) && !Fits(kinds, { stack[0] }, stack[0]));
    auto up = Attach(kinds, stack, 1, 4, 1);
    CHECK(up && up->level == 1 && Near(up->x, 24));
    stack.push_back(*up);
    auto vs = Variants(kinds, stack);
    CHECK(vs[0][4] == Solid && vs[1][4] == Door); // the ground room's north wall stays shut

    // Founder's Point plot 0: house at (2973.1, -245.3), cornerstone at (2942.7, -214.3), to the south-west (-x, +y).
    // The default base's door hooks (12ph_exterior_human_base01): the front door is one of the two on the -x face.
    std::vector<Hook> doors = { { 9.281f, 3.469f, -0.561f, 0 }, { -9.456f, -3.508f, -0.561f, 180 }, { 9.281f, -3.455f, -0.561f, 0 },
        { 0.078f, 10.889f, -0.561f, -90 }, { 0.078f, -10.995f, -0.561f, 90 }, { -9.456f, 3.469f, -0.561f, 180 } };
    size_t const front = FrontDoor(2973.08f, -245.32f, 113.17f, 0, doors, 2942.74f, -214.27f);
    CHECK(front == 5); // the -x face, +y side: nearest the cornerstone
    Pose const door = OnPlot(2973.08f, -245.32f, 113.17f, 0, doors[front]);
    CHECK(Near(door.x, 2963.62f) && Near(door.y, -241.85f) && Near(door.nx, -1) && Near(door.z, 112.61f));
    // A quarter-turned plot turns the hooks with it: the +x door now faces +y.
    Pose const turned = OnPlot(0, 0, 0, Pi / 2, doors[0]);
    CHECK(Near(turned.x, -3.469f) && Near(turned.y, 9.281f) && Near(turned.ny, 1));

    if (failures)
        return 1;
    std::printf("rooms_test passed\n");
    return 0;
}
