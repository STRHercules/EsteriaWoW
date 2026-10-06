#ifndef BROKEN_RACIAL_EFFECTS_H
#define BROKEN_RACIAL_EFFECTS_H

#include "Define.h"

namespace Acore::BrokenRacialEffects
{
float ApplySalvagerRepairDiscount(float discount);
int32 ReduceManaDrain(int32 amount);
int32 EchoHealPerTick(uint32 maxHealth);
}

#endif
