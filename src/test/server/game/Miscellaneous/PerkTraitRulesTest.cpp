/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by the
 * Free Software Foundation; either version 3 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "PerkTraitRules.h"
#include "gtest/gtest.h"
#include <initializer_list>
#include <vector>

using namespace EsteriaTraits;

namespace
{
    constexpr uint8_t Warrior = 1, Hunter = 3, Priest = 5, Mage = 8;
    // Ids from the catalog.
    constexpr uint16_t Wanderer = 1, GlassCannon = 2, Ironbound = 3, FrugalSurvivor = 8, OpeningStrike = 9,
        Executioner = 10, Relentless = 11, Shopkeeper = 111, ManaMiser = 29, Vigorous = 119, CalmMind = 121,
        FastLearner = 126, DeepSleeper = 130, Lightfoot = 131, PetTrainer = 133, Mercantile = 135, Frail = 139,
        PoorNegotiator = 144, ClumsyClimber = 145, ThinBlood = 147, ArcaneSensitivity = 148, Sluggish = 149,
        Wasteful = 152, UnfocusedMage = 161;

    Selection Build(std::initializer_list<uint16_t> ids)
    {
        Selection selection;
        for (uint16_t id : ids)
            selection.ids[selection.count++] = id;
        return selection;
    }

    // What the server's packet reader needs from a ByteBuffer.
    struct Packet
    {
        std::vector<uint8_t> bytes;
        size_t read = 0;
        size_t rpos() const { return read; }
        void rpos(size_t pos) { read = pos; }
        size_t size() const { return bytes.size(); }
        uint8_t const* contents() const { return bytes.data(); }
        void resize(size_t size) { bytes.resize(size); read = 0; }
    };

    Packet WithFooter(Selection const& selection, size_t body = 10)
    {
        Packet packet;
        packet.bytes.assign(body, 0xAB);
        packet.read = 3;
        uint8_t footer[CharacterPerkTrait::MaxFooter2Size];
        size_t const size = CharacterPerkTrait::WriteFooter2(footer, selection);
        packet.bytes.insert(packet.bytes.end(), footer, footer + size);
        return packet;
    }

    void AppendV1(Packet& packet, uint8_t trait)
    {
        for (uint8_t byte : { uint8_t(1), trait, uint8_t('P'), uint8_t('F'), uint8_t('T'), uint8_t('1') })
            packet.bytes.push_back(byte);
    }
}

TEST(PerkTraitRulesTest, CatalogIsContiguousAndStable)
{
    EXPECT_EQ(DefCount, 163u);
    size_t quirks = 0, merits = 0, flaws = 0;
    for (size_t i = 0; i < DefCount; ++i)
    {
        EXPECT_EQ(Defs[i].id, i);
        quirks += Defs[i].kind == Quirk;
        merits += Defs[i].kind == Merit;
        flaws += Defs[i].kind == Flaw;
        if (Defs[i].kind == Merit)
            EXPECT_TRUE(Defs[i].points >= 2 && Defs[i].points <= 4);
        if (Defs[i].kind == Flaw)
            EXPECT_TRUE(Defs[i].points == 2 || Defs[i].points == 3);
        if (Defs[i].kind == Quirk)
            EXPECT_EQ(Defs[i].points, 0);
    }
    EXPECT_EQ(quirks, 118u);
    EXPECT_EQ(merits, 20u);
    EXPECT_EQ(flaws, 24u);
    // The original eight keep their ids and stay available.
    for (uint16_t id = 1; id < CharacterPerkTrait::Count; ++id)
        EXPECT_TRUE(Defs[id].kind == Quirk && Defs[id].implemented);
}

// A trait may only be picked when it does something: a quirk needs a gain and a loss, a merit or flaw one effect.
TEST(PerkTraitRulesTest, ImplementedMeansBothHalvesHaveEffects)
{
    for (size_t i = 1; i < DefCount; ++i)
    {
        size_t effects = 0;
        for (Effect const& effect : Effects)
        {
            effects += effect.trait == i;
            EXPECT_LT(effect.family, FamilyCount);
            EXPECT_NE(effect.value, 0.0f);
        }
        EXPECT_EQ(Defs[i].implemented, effects >= (Defs[i].kind == Quirk ? 2u : 1u)) << "trait " << i;
    }
}

TEST(PerkTraitRulesTest, EmptyBuildIsUnmarked)
{
    Selection const none;
    EXPECT_EQ(Validate(none, Warrior), Ok);
    EXPECT_EQ(BudgetOf(none).remaining(), 4);
    EXPECT_EQ(LegacyTrait(none), 0);
    EXPECT_FALSE(Compose(none).any);
}

TEST(PerkTraitRulesTest, Budget)
{
    // Merits spend the four base points.
    EXPECT_EQ(Validate(Build({ Vigorous }), Warrior), Ok);
    EXPECT_EQ(BudgetOf(Build({ Vigorous })).remaining(), 0);
    EXPECT_EQ(Validate(Build({ Vigorous, FastLearner }), Warrior), Points);
    // Flaws pay for more: 3 + 3 + 2 = the cap of 8, 12 points in all.
    Selection const rich = Build({ Vigorous, FastLearner, DeepSleeper, ClumsyClimber, ThinBlood, Sluggish });
    EXPECT_EQ(BudgetOf(rich).fromFlaws, 8);
    EXPECT_EQ(BudgetOf(rich).remaining(), 3);
    EXPECT_EQ(Validate(rich, Warrior), Ok);
    // Three flaws of three points would grant nine.
    EXPECT_EQ(Validate(Build({ Frail, ThinBlood, Sluggish }), Warrior), FlawPoints);
    // A quirk's drawback pays for nothing.
    EXPECT_EQ(BudgetOf(Build({ Wanderer, OpeningStrike })).remaining(), 4);
}

TEST(PerkTraitRulesTest, Caps)
{
    EXPECT_EQ(Validate(Build({ Wanderer, OpeningStrike, Relentless }), Warrior), QuirkCap);
    EXPECT_EQ(Validate(Build({ DeepSleeper, Lightfoot, Mercantile, 136 }), Warrior), MeritCap);
    EXPECT_EQ(Validate(Build({ PoorNegotiator, ClumsyClimber, Sluggish, 153 }), Warrior), FlawCap);
    // Two quirks, three merits and three flaws: eight traits.
    Selection const full = Build({ FrugalSurvivor, OpeningStrike, DeepSleeper, Lightfoot, Mercantile, ClumsyClimber,
        ThinBlood, Sluggish });
    EXPECT_EQ(full.count, 8);
    EXPECT_EQ(Validate(full, Warrior), Ok);
}

TEST(PerkTraitRulesTest, ConflictsAndBadIds)
{
    EXPECT_EQ(Validate(Build({ GlassCannon, Ironbound }), Warrior), Conflict);    // opposite quirks
    EXPECT_EQ(Validate(Build({ GlassCannon, Vigorous }), Warrior), Conflict);     // same family across kinds
    EXPECT_EQ(Validate(Build({ ThinBlood, ArcaneSensitivity }), Warrior), Conflict);
    EXPECT_EQ(Validate(Build({ PoorNegotiator, Wasteful }), Warrior), Conflict);
    EXPECT_EQ(Validate(Build({ OpeningStrike, Executioner }), Warrior), Ok);      // no shared group
    EXPECT_EQ(Validate(Build({ 163 }), Warrior), InvalidId);
    EXPECT_EQ(Validate(Build({ 0 }), Warrior), Malformed);
    EXPECT_EQ(Validate(Build({ Wanderer, Wanderer }), Warrior), Malformed);
    EXPECT_EQ(Validate(Build({ OpeningStrike, Wanderer }), Warrior), Malformed);  // not ascending
    EXPECT_EQ(Validate(Build({ Shopkeeper }), Warrior), Locked);                  // no effect yet
}

// A flaw that could never bite is not free points.
TEST(PerkTraitRulesTest, ClassMustFeelTheTrait)
{
    EXPECT_EQ(Validate(Build({ UnfocusedMage }), Warrior), Ineligible);
    EXPECT_EQ(Validate(Build({ UnfocusedMage }), Mage), Ok);
    EXPECT_EQ(Validate(Build({ CalmMind }), Warrior), Ineligible);
    EXPECT_EQ(Validate(Build({ ManaMiser }), Priest), Ok);
    EXPECT_EQ(Validate(Build({ PetTrainer }), Mage), Ineligible);
    EXPECT_EQ(Validate(Build({ PetTrainer }), Hunter), Ok);
    EXPECT_EQ(Validate(Build({ 122 }), Warrior), Ineligible); // Natural Healer
    EXPECT_EQ(Validate(Build({ 122 }), Priest), Ok);
}

TEST(PerkTraitRulesTest, LegacyTraitOnlyForASingleBackground)
{
    EXPECT_EQ(LegacyTrait(Build({ Ironbound })), 3);
    EXPECT_EQ(LegacyTrait(Build({ Ironbound, OpeningStrike })), 0);
    EXPECT_EQ(LegacyTrait(Build({ OpeningStrike })), 0);
}

TEST(PerkTraitRulesTest, ComposeKeepsGainsAndLossesApart)
{
    // The original backgrounds keep their numbers.
    Mods const cannon = Compose(Build({ GlassCannon }));
    EXPECT_FLOAT_EQ(cannon.pos[DmgAll], 0.02f);
    EXPECT_FLOAT_EQ(cannon.neg[MaxHealth], -0.04f);
    Mods const wanderer = Compose(Build({ Wanderer }));
    EXPECT_FLOAT_EQ(wanderer.pos[MoveOutdoorOoc], 0.05f);
    EXPECT_FLOAT_EQ(wanderer.neg[QuestRep], -0.10f);

    // A cap trims the gain and leaves the loss whole.
    Mods const mods = Compose(Build({ OpeningStrike, 120 })); // +4% above 90% health, +3% always
    Sum sum;
    sum.add(mods, DmgAll).add(mods, DmgTargetAbove90).add(mods, DmgTargetBelow30);
    EXPECT_FLOAT_EQ(sum.pos, 0.07f);
    EXPECT_FLOAT_EQ(sum.total(0.06f), 0.03f);
    // Damage taken: the cap is on the reduction.
    Sum taken;
    taken.add(Compose(Build({ 19, 21 })), TakenPhysical).add(Compose(Build({ 19, 21 })), TakenLowHealth);
    EXPECT_FLOAT_EQ(taken.total(10.0f, 0.05f), -0.05f);

    // A trait that is not implemented adds nothing, even from a saved build.
    EXPECT_FALSE(Compose(Build({ Shopkeeper })).any);
}

TEST(PerkTraitRulesTest, RechooseCost)
{
    EXPECT_EQ(RechooseCost(0, 80), 0u);
    EXPECT_EQ(RechooseCost(1, 10), 50000u);
    EXPECT_EQ(RechooseCost(7, 80), 400000u);
    EXPECT_EQ(RechooseCost(1, 255), 500000u);
}

TEST(PerkTraitWireTest, V2RoundTrip)
{
    for (Selection const& sent : { Selection{}, Build({ Wanderer }), Build({ 2, 9, 119, 120, 130, 139, 147, 162 }) })
    {
        Packet packet = WithFooter(sent);
        bool present = false;
        Selection got;
        ASSERT_TRUE(CharacterPerkTrait::ReadTail(packet, present, got));
        EXPECT_TRUE(present);
        EXPECT_EQ(packet.size(), 10u);
        EXPECT_EQ(packet.rpos(), 3u); // the read cursor survives the strip
        ASSERT_EQ(got.count, sent.count);
        for (size_t i = 0; i < sent.count; ++i)
            EXPECT_EQ(got.ids[i], sent.ids[i]);
    }
    uint8_t footer[CharacterPerkTrait::MaxFooter2Size];
    EXPECT_EQ(CharacterPerkTrait::WriteFooter2(footer, Build({ 2, 9, 119, 120, 130, 139, 147, 162 })),
        CharacterPerkTrait::MaxFooter2Size);
    EXPECT_EQ(CharacterPerkTrait::WriteFooter2(footer, Build({ 9, 2 })), 0u); // never writes a list it would refuse
}

TEST(PerkTraitWireTest, V1StillReads)
{
    Packet packet;
    packet.bytes.assign(10, 0);
    AppendV1(packet, 8);
    bool present = false;
    Selection got;
    ASSERT_TRUE(CharacterPerkTrait::ReadTail(packet, present, got));
    EXPECT_TRUE(present);
    EXPECT_EQ(packet.size(), 10u);
    ASSERT_EQ(got.count, 1);
    EXPECT_EQ(got.ids[0], 8);

    // v1 Unmarked is an empty build; a v1 id past the eight backgrounds is refused.
    Packet unmarked;
    AppendV1(unmarked, 0);
    present = false;
    ASSERT_TRUE(CharacterPerkTrait::ReadTail(unmarked, present, got));
    EXPECT_TRUE(present);
    EXPECT_EQ(got.count, 0);
    Packet bad;
    AppendV1(bad, 9);
    EXPECT_FALSE(CharacterPerkTrait::ReadTail(bad, present, got));
}

TEST(PerkTraitWireTest, NoFooterIsUnmarked)
{
    Packet packet;
    packet.bytes.assign(12, 0x50);
    bool present = false;
    Selection got;
    EXPECT_TRUE(CharacterPerkTrait::ReadTail(packet, present, got));
    EXPECT_FALSE(present);
    EXPECT_EQ(packet.size(), 12u);
}

TEST(PerkTraitWireTest, MalformedV2IsRefusedAndLeavesThePacket)
{
    bool present = false;
    Selection got;
    auto refused = [&](Packet packet)
    {
        size_t const size = packet.size();
        present = false;
        return !CharacterPerkTrait::ReadTail(packet, present, got) && !present && packet.size() == size;
    };

    Packet const good = WithFooter(Build({ 2, 9 }));
    Packet length = good;
    length.bytes[length.size() - 6] += 2;            // length disagrees with the count
    EXPECT_TRUE(refused(length));
    Packet version = good;
    version.bytes[version.size() - 12] = 3;          // version byte
    EXPECT_TRUE(refused(version));
    Packet unsorted = good;
    std::swap(unsorted.bytes[unsorted.size() - 10], unsorted.bytes[unsorted.size() - 8]); // 9, 2
    EXPECT_TRUE(refused(unsorted));
    Packet duplicate = good;
    duplicate.bytes[duplicate.size() - 8] = 2;       // 2, 2
    EXPECT_TRUE(refused(duplicate));
    Packet zero = good;
    zero.bytes[zero.size() - 10] = 0;                // id 0
    EXPECT_TRUE(refused(zero));
    Packet tooShort;
    tooShort.bytes = { 'P', 'F', 'T', '2' };         // magic with nothing before it
    EXPECT_TRUE(refused(tooShort));
    Packet nine = WithFooter(Selection{});
    nine.bytes[nine.size() - 7] = 9;                 // count past the limit
    EXPECT_TRUE(refused(nine));

    // Two trait footers in a row are ambiguous, whichever order.
    Packet both = good;
    AppendV1(both, 3);
    EXPECT_TRUE(refused(both));
    Packet reversed;
    reversed.bytes.assign(10, 0);
    AppendV1(reversed, 3);
    uint8_t footer[CharacterPerkTrait::MaxFooter2Size];
    size_t const size = CharacterPerkTrait::WriteFooter2(footer, Build({ 2 }));
    reversed.bytes.insert(reversed.bytes.end(), footer, footer + size);
    EXPECT_TRUE(refused(reversed));

    // A wrong magic is simply not a footer: the bytes stay for the footers underneath.
    Packet magic = good;
    magic.bytes.back() = '3';
    present = false;
    EXPECT_TRUE(CharacterPerkTrait::ReadTail(magic, present, got));
    EXPECT_FALSE(present);
    EXPECT_EQ(magic.size(), good.size());
}
