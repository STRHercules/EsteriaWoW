// Placement validation tests. No server needed:
//   g++ -std=c++20 -I modules/mod-esteria-housing/src modules/mod-esteria-housing/tests/rules_test.cpp -o rules_test && ./rules_test
#include "HousingRules.h"
#include <cstdio>
#include <initializer_list>
#include <limits>

using namespace EsteriaHousing;

static int failures = 0;
#define EXPECT(cond) do { if (!(cond)) { std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #cond); ++failures; } } while (0)

static Facts Good()
{
    Facts f;
    f.enabled = f.inHouse = f.isOwner = f.decorKnown = f.placementKnown = true;
    f.lastSeq = 4;
    f.revision = 7;
    f.available = 2;
    f.placed = 3;
    f.maxDecor = 50;
    for (int i = 0; i < 3; ++i) { f.boundsMin[i] = -10; f.boundsMax[i] = 10; }
    return f;
}

static Edit Place()
{
    Edit e;
    e.seq = 5;
    e.baseRevision = 7;
    e.op = OpPlace;
    e.decorId = 498;
    e.pos[0] = 1; e.pos[1] = 2; e.pos[2] = 3;
    return e;
}

static Result Run(Edit const& e, Facts const& f) { Final out; return Check(e, f, out); }

int main()
{
    Final out;
    EXPECT(Check(Place(), Good(), out) == Ok);
    EXPECT(out.pos[0] == 1 && out.pos[2] == 3 && out.yaw == 0 && out.rot[3] == 1);

    // Disabled / not in a house / not the owner (visitor), in that order.
    { Facts f = Good(); f.enabled = false; f.isOwner = false; EXPECT(Run(Place(), f) == Disabled); }
    { Facts f = Good(); f.inHouse = false; EXPECT(Run(Place(), f) == NotInHouse); }
    { Facts f = Good(); f.isOwner = false; EXPECT(Run(Place(), f) == NoPermission); }

    // Duplicate and replayed seq; permission is checked first so a visitor learns nothing from seq.
    { Edit e = Place(); e.seq = 4; EXPECT(Run(e, Good()) == DuplicateSeq); }
    { Edit e = Place(); e.seq = 1; EXPECT(Run(e, Good()) == DuplicateSeq); }
    { Edit e = Place(); e.seq = 4; Facts f = Good(); f.isOwner = false; EXPECT(Run(e, f) == NoPermission); }

    { Facts f = Good(); f.rateOk = false; EXPECT(Run(Place(), f) == RateLimited); }
    { Edit e = Place(); e.op = 9; EXPECT(Run(e, Good()) == BadOp); }
    { Edit e = Place(); e.baseRevision = 6; EXPECT(Run(e, Good()) == StaleRevision); }

    // Bad IDs.
    { Facts f = Good(); f.decorKnown = false; EXPECT(Run(Place(), f) == UnknownDecor); }
    { Edit e = Place(); e.placedId = 99; EXPECT(Run(e, Good()) == UnknownDecor); }
    { Facts f = Good(); f.available = 0; EXPECT(Run(Place(), f) == NoneLeft); }
    { Edit e = Place(); e.op = OpMove; e.placedId = 12; Facts f = Good(); f.placementKnown = false;
      EXPECT(Run(e, f) == UnknownPlacement); }
    { Edit e = Place(); e.op = OpRemove; e.placedId = 12; Facts f = Good(); f.placementKnown = false;
      EXPECT(Run(e, f) == UnknownPlacement); }

    // Out of bounds on each axis and each side; the edge itself is inside.
    for (int axis = 0; axis < 3; ++axis)
    {
        Edit e = Place(); e.pos[axis] = 10.01f; EXPECT(Run(e, Good()) == OutOfBounds);
        e.pos[axis] = -10.01f; EXPECT(Run(e, Good()) == OutOfBounds);
        e.pos[axis] = 10; EXPECT(Run(e, Good()) == Ok);
    }
    // Move is bounds-checked; remove of something already outside still works.
    { Edit e = Place(); e.op = OpMove; e.placedId = 12; e.pos[0] = 50; EXPECT(Run(e, Good()) == OutOfBounds); }
    { Edit e = Place(); e.op = OpRemove; e.placedId = 12; e.pos[0] = 50; EXPECT(Run(e, Good()) == Ok); }

    // NaN / infinite / degenerate quaternion / scale.
    float const nan = std::numeric_limits<float>::quiet_NaN(), inf = std::numeric_limits<float>::infinity();
    { Edit e = Place(); e.pos[1] = nan; EXPECT(Run(e, Good()) == BadTransform); }
    { Edit e = Place(); e.rot[2] = inf; EXPECT(Run(e, Good()) == BadTransform); }
    { Edit e = Place(); e.rot[3] = 0; EXPECT(Run(e, Good()) == BadTransform); }
    { Edit e = Place(); e.rot[3] = 3; EXPECT(Run(e, Good()) == BadTransform); }
    { Edit e = Place(); e.scale = 2; EXPECT(Run(e, Good()) == BadTransform); }
    { Edit e = Place(); e.scale = nan; EXPECT(Run(e, Good()) == BadTransform); }

    // Over budget: place only.
    { Facts f = Good(); f.placed = 50; EXPECT(Run(Place(), f) == OverBudget); }
    { Facts f = Good(); f.placed = 49; EXPECT(Run(Place(), f) == Ok); }
    { Edit e = Place(); e.op = OpMove; e.placedId = 12; Facts f = Good(); f.placed = 50; EXPECT(Run(e, f) == Ok); }

    // Rotation: a turn about Z alone snaps (20 degrees to 15, -10 to 345); a tilted, unnormalised quaternion is kept
    // whole (Expert mode turns decor about every axis), only normalised.
    {
        double const pi = 3.14159265358979323846;
        auto yawOf = [&](double degrees, float tilt, float length) {
            Edit e = Place();
            double const half = degrees * pi / 360.0;
            e.rot[0] = tilt; e.rot[1] = 0; e.rot[2] = float(std::sin(half) * length); e.rot[3] = float(std::cos(half) * length);
            Final o;
            EXPECT(Check(e, Good(), o) == Ok);
            EXPECT(tilt != 0 || (o.rot[0] == 0 && o.rot[1] == 0));
            EXPECT(std::fabs(o.rot[0] * o.rot[0] + o.rot[1] * o.rot[1] + o.rot[2] * o.rot[2] + o.rot[3] * o.rot[3] - 1) < 1e-5);
            return o.yaw * 180.0 / pi;
        };
        EXPECT(std::fabs(yawOf(20, 0, 1) - 15) < 1e-3);
        EXPECT(std::fabs(yawOf(-10, 0, 1) - 345) < 1e-3);
        EXPECT(std::fabs(yawOf(359, 0, 1) - 0) < 1e-3);
        EXPECT(std::fabs(yawOf(90, 0, 1.5f) - 90) < 1e-3);
        EXPECT(std::fabs(yawOf(44, 0, 1) - 45) < 1e-3);
        EXPECT(std::fabs(yawOf(44, 0.3f, 1) - 45) > 0.5); // tilted: not snapped
    }

    // shops and commissions
    {
        EXPECT(ValidListing(5, 20, 20, 100));
        EXPECT(!ValidListing(0, 20, 20, 100));
        EXPECT(!ValidListing(21, 40, 20, 100)); // more than one stack at a time
        EXPECT(!ValidListing(5, 4, 20, 100));   // more than it holds
        EXPECT(!ValidListing(1, 1, 1, 0));      // free
        EXPECT(!ValidListing(1, 1, 1, MaxListingPrice + 1));
        EXPECT(OrderCan(OrderOpen, OrderAccepted) && OrderCan(OrderAccepted, OrderCompleted) && OrderCan(OrderAccepted, OrderOpen));
        EXPECT(!OrderCan(OrderOpen, OrderCompleted)); // nobody took it
        for (uint8_t done : { OrderCompleted, OrderCancelled, OrderExpired })
            for (uint8_t to = 0; to < 5; ++to)
                EXPECT(!OrderCan(done, to)); // no double payout or refund
    }

    std::printf(failures ? "%d failure(s)\n" : "all housing rule tests passed\n", failures);
    return failures ? 1 : 0;
}
