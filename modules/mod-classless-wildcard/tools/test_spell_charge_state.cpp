#include "SpellChargeState.h"
#include <cassert>

int main()
{
    SpellChargeState state{3, 0, 1000};
    assert(state.Consume(3, 1000, 100));
    assert(state.Available == 2 && state.NextRecovery == 1100);
    assert(state.Consume(3, 1000, 200));
    assert(state.Consume(3, 1000, 300));
    assert(!state.Consume(3, 1000, 400));
    state.Update(3, 1099);
    assert(state.Available == 0);
    state.Update(3, 2100);
    assert(state.Available == 2 && state.NextRecovery == 3100);
    state.Restore(3, 1, 2200);
    assert(state.Available == 3 && state.NextRecovery == 0);
    assert(state.Consume(3, 500, 2300));
    assert(state.NextRecovery == 2800 && state.RecoveryTime == 500);
    SpellChargeState restored = state;
    restored.Update(3, 5000);
    assert(restored.Available == 3 && restored.NextRecovery == 0);

    SpellChargeState corrupt{0, 0, 1000};
    corrupt.Update(3, 5000);
    assert(corrupt.Available == 3 && corrupt.NextRecovery == 0);
    SpellChargeState lowered{5, 9000, 1000};
    lowered.Update(2, 5000);
    assert(lowered.Available == 2 && lowered.NextRecovery == 0);
}
