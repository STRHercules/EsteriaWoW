// Standalone check for src/BattlemonHeldItems.h; tests/test_helditems.py compiles and runs it.
#include "BattlemonHeldItems.h"

#include <cstdio>

using namespace BattlemonHeldItems;

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
    CHECK(IsHoldable("LEFTOVERS") && IsHoldable("EVERSTONE") && !IsHoldable("POTION") && !IsHoldable(""));
    CHECK(IsChoice("CHOICEBAND") && IsChoice("CHOICESCARF") && !IsChoice("LIFEORB"));

    // Attack: a type booster only helps its own type; choice items only their category; nothing else is touched.
    CHECK(AttackMul("CHARCOAL", "Special", "FIRE") == 1.2f && AttackMul("CHARCOAL", "Special", "WATER") == 1.0f);
    CHECK(AttackMul("CHOICEBAND", "Physical", "NORMAL") == 1.5f && AttackMul("CHOICEBAND", "Special", "NORMAL") == 1.0f);
    CHECK(AttackMul("CHOICESPECS", "Special", "NORMAL") == 1.5f && AttackMul("CHOICESPECS", "Physical", "NORMAL") == 1.0f);
    CHECK(AttackMul("MUSCLEBAND", "Physical", "") == 1.1f && AttackMul("WISEGLASSES", "Special", "") == 1.1f);
    CHECK(AttackMul("LIFEORB", "Status", "") == 1.3f);
    CHECK(AttackMul("", "Physical", "FIRE") == 1.0f && AttackMul("LEFTOVERS", "Physical", "FIRE") == 1.0f);

    CHECK(SpeedMul("CHOICESCARF") == 1.5f && SpeedMul("CHOICEBAND") == 1.0f && SpeedMul("") == 1.0f);
    CHECK(AfterEffMul("EXPERTBELT", 2.0f) == 1.2f && AfterEffMul("EXPERTBELT", 1.0f) == 1.0f && AfterEffMul("", 4.0f) == 1.0f);
    CHECK(ExpMul("LUCKYEGG") == 1.5f && ExpMul("") == 1.0f);

    CHECK(LifeOrbRecoil("LIFEORB", 200) == 20 && LifeOrbRecoil("LIFEORB", 5) == 1 && LifeOrbRecoil("CHOICEBAND", 200) == 0);
    CHECK(EndOfRoundHp("LEFTOVERS", 160, false) == 10 && EndOfRoundHp("LEFTOVERS", 8, false) == 1);
    CHECK(EndOfRoundHp("BLACKSLUDGE", 160, true) == 10 && EndOfRoundHp("BLACKSLUDGE", 160, false) == -20);
    CHECK(EndOfRoundHp("", 160, false) == 0);

    CHECK(SashSaves("FOCUSSASH", 100, 100, 100) && SashSaves("FOCUSSASH", 100, 100, 250));
    CHECK(!SashSaves("FOCUSSASH", 99, 100, 250));                // only from full HP
    CHECK(!SashSaves("FOCUSSASH", 100, 100, 40));                // only if it would have fainted
    CHECK(!SashSaves("", 100, 100, 250));

    // Berries: heal at half HP or less, never at full HP or when fainted; status berries cure what they name.
    BerryUse b = Berry("ORANBERRY", 50, 100, 0);
    CHECK(b.eat && b.heal == 10 && !b.cure);
    CHECK(!Berry("ORANBERRY", 51, 100, 0).eat);                  // above half
    CHECK(!Berry("ORANBERRY", 100, 100, 0).eat);                 // full HP
    CHECK(!Berry("ORANBERRY", 0, 100, 0).eat);                   // fainted
    b = Berry("SITRUSBERRY", 40, 200, 0);
    CHECK(b.eat && b.heal == 50);                                // 25% of 200
    CHECK(Berry("CHERIBERRY", 80, 100, 2).cure && !Berry("CHERIBERRY", 80, 100, 1).eat);
    CHECK(Berry("PECHABERRY", 80, 100, 4).cure && Berry("PECHABERRY", 80, 100, 5).cure);   // poison and bad poison
    CHECK(Berry("LUMBERRY", 80, 100, 6).cure && Berry("LUMBERRY", 80, 100, 3).cure);
    CHECK(!Berry("LUMBERRY", 80, 100, 0).eat);                   // nothing to cure
    CHECK(!Berry("LEFTOVERS", 10, 100, 2).eat);
    std::puts("ok");
    return 0;
}
