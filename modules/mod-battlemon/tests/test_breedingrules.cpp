// Standalone check for src/BattlemonBreedingRules.h; tests/test_breedingrules.py compiles and runs it.
#include "BattlemonBreedingRules.h"

#include <cstdio>

using namespace BattlemonBreedingRules;

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
    Parent bulbasaur{"Monster,Grass", 'F', 1, 1};
    Parent charmander{"Monster,Dragon", 'M', 4, 2};
    Parent pikachu{"Field,Fairy", 'M', 25, 1};
    Parent ditto{"Ditto", 'N', 132, 1};
    Parent pichu{"Undiscovered", 'M', 172, 1};
    Parent magnemite{"Mineral", 'N', 81, 1};
    Parent ivysaur{"Monster,Grass", 'F', 2, 1};

    CHECK(HasGroup("Monster,Grass", "Grass") && HasGroup("Monster,Grass", "Monster") && !HasGroup("Monster,Grass", "Gras"));
    CHECK(!HasGroup("", "Monster"));
    CHECK(SharesGroup("Monster,Grass", "Dragon,Grass") && !SharesGroup("Field", "Mineral"));

    CHECK(Check(bulbasaur, charmander) == Match::Ok);                 // shared Monster group, opposite genders
    CHECK(Check(bulbasaur, ivysaur) == Match::SameGender);
    CHECK(Check(bulbasaur, pikachu) == Match::NoSharedGroup);
    CHECK(Check(bulbasaur, pichu) == Match::Undiscovered);            // either side
    CHECK(Check(pichu, bulbasaur) == Match::Undiscovered);
    CHECK(Check(magnemite, magnemite) == Match::Genderless);          // two genderless never breed
    CHECK(Check(ditto, bulbasaur) == Match::Ok && Check(pikachu, ditto) == Match::Ok);
    CHECK(Check(ditto, magnemite) == Match::Ok);                      // Ditto can breed a genderless Pokemon
    CHECK(Check(ditto, ditto) == Match::DittoPair);
    CHECK(Check(ditto, pichu) == Match::Undiscovered);                // Ditto cannot rescue an Undiscovered one

    CHECK(EggChancePercent(true, false) == 70 && EggChancePercent(false, false) == 50);
    CHECK(EggChancePercent(true, true) == 50 && EggChancePercent(false, true) == 20);

    CHECK(MotherIndex(bulbasaur, charmander) == 0 && MotherIndex(charmander, bulbasaur) == 1);
    CHECK(MotherIndex(ditto, bulbasaur) == 1 && MotherIndex(pikachu, ditto) == 0);

    // IV inheritance with a scripted RNG. Each pick is (stat, parent) with parent 0 = B and 1 = A; a repeated stat is
    // skipped. Stats 1, 3 and 5 are inherited, and the remaining three get the scripted "random" values.
    uint8_t ivA[6] = {1, 2, 3, 4, 5, 6};
    uint8_t ivB[6] = {31, 30, 29, 28, 27, 26};
    uint8_t out[6];
    uint32_t script[] = {1, 0,     // stat 1, from B
                         3, 1,     // stat 3, from A
                         1,        // stat 1 again: skipped
                         5, 1,     // stat 5, from A
                         7, 8, 9}; // the three random stats (0, 2, 4)
    size_t at = 0;
    auto rng = [&](uint32_t, uint32_t) { return script[at++]; };
    InheritIvs(ivA, ivB, rng, out);
    CHECK(out[1] == 30 && out[3] == 4 && out[5] == 6);
    CHECK(out[0] == 7 && out[2] == 8 && out[4] == 9);

    // A Destiny Knot makes it five inherited stats: only stat 2 is left to chance.
    uint32_t script5[] = {0, 1, 1, 1, 3, 0, 4, 1, 5, 1, 17}; // (stat,parent) x5 from A/B, then one random value
    at = 0;
    auto rng5 = [&](uint32_t, uint32_t) { return script5[at++]; };
    InheritIvs(ivA, ivB, rng5, out, 5);
    CHECK(out[0] == 1 && out[1] == 2 && out[3] == 28 && out[4] == 5 && out[5] == 6 && out[2] == 17);

    // Everstone: the holder's nature wins; two holders flip a coin; none means random.
    bool none[2] = {false, false}, first[2] = {true, false}, second[2] = {false, true}, both[2] = {true, true};
    auto zero = [](uint32_t, uint32_t) { return 0u; };
    auto one = [](uint32_t, uint32_t) { return 1u; };
    CHECK(NatureParent(none, zero) == -1 && NatureParent(first, zero) == 0 && NatureParent(second, zero) == 1);
    CHECK(NatureParent(both, zero) == 0 && NatureParent(both, one) == 1);

    CHECK(HatchSeconds(5120, 60, 100) == 20 * 60);                    // 5120 steps = 20 cycles
    CHECK(HatchSeconds(30720, 60, 100) == 120 * 60);
    CHECK(HatchSeconds(5120, 60, 50) == 10 * 60);
    CHECK(HatchSeconds(0, 60, 100) == 60 && HatchSeconds(5120, 0, 100) == 1); // never instant, never zero

    std::vector<std::string> base = {"TACKLE", "GROWL"};
    auto merged = MergeMoves(base, {"VINEWHIP", "TACKLE"});           // an already-known move moves to the end
    CHECK(merged.size() == 3 && merged[0] == "GROWL" && merged[1] == "VINEWHIP" && merged[2] == "TACKLE");
    auto full = MergeMoves({"A", "B", "C", "D"}, {"E", "F"});         // the oldest fall off
    CHECK(full.size() == 4 && full[0] == "C" && full[3] == "F");
    CHECK(MergeMoves({"A"}, {"", "B"}).size() == 2);
    std::puts("ok");
    return 0;
}
