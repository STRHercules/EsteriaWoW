#include "AscensionRaidReleasePolicy.h"

// shortcut: Esteria has no staged raid release, so every cache tier is open; port CoA's
// AscensionRaidRelease config if staged releases are ever wanted.
std::uint32_t RaidRelease::ReleasedStage()
{
    return RaidRelease::AllReleased;
}
