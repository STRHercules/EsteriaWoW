#include "Define.h"
#include "gtest/gtest.h"

namespace Acore::BrokenRacialEffects
{
float ApplySalvagerRepairDiscount(float discount);
int32 ReduceManaDrain(int32 amount);
int32 EchoHealPerTick(uint32 maxHealth);
}

TEST(BrokenRacialEffects, AppliesSalvagerRepairDiscount)
{
    EXPECT_FLOAT_EQ(Acore::BrokenRacialEffects::ApplySalvagerRepairDiscount(1.0f), 0.9f);
}

TEST(BrokenRacialEffects, ReducesManaDrainByTenPercent)
{
    EXPECT_EQ(Acore::BrokenRacialEffects::ReduceManaDrain(1000), 900);
    EXPECT_EQ(Acore::BrokenRacialEffects::ReduceManaDrain(9), 8);
}

TEST(BrokenRacialEffects, SplitsEchoIntoFiveThreePercentTicks)
{
    EXPECT_EQ(Acore::BrokenRacialEffects::EchoHealPerTick(100000), 3000);
}
