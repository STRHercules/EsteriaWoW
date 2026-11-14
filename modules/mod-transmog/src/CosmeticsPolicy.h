#ifndef ESTERIA_COSMETICS_POLICY_H
#define ESTERIA_COSMETICS_POLICY_H

namespace EsteriaCosmetics
{
    inline bool CanApplyBackpack(bool registered, bool owned, bool cloakEquipped, bool alive, bool inCombat)
    {
        return registered && owned && cloakEquipped && alive && !inCombat;
    }

    enum class LearnResult { Invalid, AlreadyKnown, PersistenceFailed, Learned };

    // Never consume a duplicate token or announce ownership before its inventory transaction commits.
    template <class Prepare, class Persist, class Publish>
    LearnResult Learn(bool valid, bool known, Prepare prepare, Persist persist, Publish publish)
    {
        if (!valid)
            return LearnResult::Invalid;
        if (known)
            return LearnResult::AlreadyKnown;
        prepare();
        if (!persist())
            return LearnResult::PersistenceFailed;
        publish();
        return LearnResult::Learned;
    }
}

#endif
