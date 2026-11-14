#include "../src/CosmeticsPolicy.h"
#include <cassert>
#include <vector>

int main()
{
    using namespace EsteriaCosmetics;
    assert(CanApplyBackpack(true, true, true, true, false));
    assert(!CanApplyBackpack(false, true, true, true, false));
    assert(!CanApplyBackpack(true, false, true, true, false));
    assert(!CanApplyBackpack(true, true, false, true, false));
    assert(!CanApplyBackpack(true, true, true, false, false));
    assert(!CanApplyBackpack(true, true, true, true, true));
    std::vector<int> events;
    auto prepare = [&] { events.push_back(1); };
    auto persist = [&] { events.push_back(2); return true; };
    auto publish = [&] { events.push_back(3); };
    assert(Learn(false, false, prepare, persist, publish) == LearnResult::Invalid);
    assert(events.empty());
    assert(Learn(true, true, prepare, persist, publish) == LearnResult::AlreadyKnown);
    assert(events.empty());
    assert(Learn(true, false, prepare, persist, publish) == LearnResult::Learned);
    assert((events == std::vector<int>{1, 2, 3}));
    events.clear();
    auto failedCommit = [&] { events.push_back(2); return false; };
    assert(Learn(true, false, prepare, failedCommit, publish) == LearnResult::PersistenceFailed);
    assert((events == std::vector<int>{1, 2}));
}
