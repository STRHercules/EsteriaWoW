#include "BrokenRacialEffects.h"

#include "Utilities/Util.h"

namespace Acore::BrokenRacialEffects
{
float ApplySalvagerRepairDiscount(float discount)
{
    return discount * 0.9f;
}

int32 ReduceManaDrain(int32 amount)
{
    return CalculatePct(amount, 90);
}

int32 EchoHealPerTick(uint32 maxHealth)
{
    return CalculatePct(maxHealth, 3);
}
}
