#ifndef BATTLEMON_CENTER_H
#define BATTLEMON_CENTER_H

#include <cstdint>

class Player;

namespace BattlemonCenter
{
// Optional profession integration, registered once during script startup.
inline void (*HealCompanion)(Player*) = nullptr;

enum Service : uint32_t
{
    Heal = 1,
    Shop = 2,
    Party = 3,
    Storage = 4
};
}

#endif
