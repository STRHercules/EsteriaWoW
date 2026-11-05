// Standalone check for src/BattlemonMoveSlots.h; tests/test_moveslots.py compiles and runs it.
#include "BattlemonMoveSlots.h"

#include <cstdio>

using namespace BattlemonMoveSlots;

#define CHECK(x)                                             \
    do                                                       \
    {                                                        \
        if (!(x))                                            \
        {                                                    \
            std::printf("FAIL line %d: %s\n", __LINE__, #x); \
            return 1;                                        \
        }                                                    \
    } while (0)

int main()
{
    std::string forgot;

    std::string full[4] = {"TACKLE", "GROWL", "LEECHSEED", "GROWTH"};
    CHECK(Count(full) == 4 && Knows(full, "GROWL") && !Knows(full, "VINEWHIP"));
    CHECK(Place(full, "VINEWHIP", 2, forgot));          // all four taken: replaces the chosen slot
    CHECK(forgot == "GROWL" && full[1] == "VINEWHIP" && full[0] == "TACKLE" && full[3] == "GROWTH");

    std::string again[4] = {"TACKLE", "GROWL", "LEECHSEED", "GROWTH"};
    CHECK(!Place(again, "VINEWHIP", 0, forgot));        // slot 0 is "decline", never a replacement
    CHECK(!Place(again, "VINEWHIP", 5, forgot));        // out of range
    CHECK(again[0] == "TACKLE" && again[1] == "GROWL" && again[2] == "LEECHSEED" && again[3] == "GROWTH");
    CHECK(!Place(again, "GROWTH", 1, forgot));          // already known: nothing changes
    CHECK(again[0] == "TACKLE");

    std::string roomy[4] = {"TACKLE", "", "LEECHSEED", ""};
    CHECK(Count(roomy) == 2);
    CHECK(Place(roomy, "VINEWHIP", 3, forgot));         // a free slot wins over the requested slot
    CHECK(forgot.empty() && roomy[1] == "VINEWHIP" && roomy[2] == "LEECHSEED");
    CHECK(Place(roomy, "RAZORLEAF", 0, forgot) && roomy[3] == "RAZORLEAF" && Count(roomy) == 4);

    std::string none[4] = {};
    CHECK(!Place(none, "", 1, forgot));                 // an empty name is never a move
    CHECK(Place(none, "TACKLE", 0, forgot) && none[0] == "TACKLE");
    std::puts("ok");
    return 0;
}
