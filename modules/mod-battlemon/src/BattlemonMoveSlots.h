#ifndef BATTLEMON_MOVE_SLOTS_H
#define BATTLEMON_MOVE_SLOTS_H

// The four move slots of one Pokemon, as the internal names stored in battlemon_owned (empty = free).
// Header-only and free of core types so tests/test_moveslots.cpp can compile it on its own.

#include <cstdint>
#include <string>

namespace BattlemonMoveSlots
{
inline bool Knows(std::string const (&moves)[4], std::string const& move)
{
    for (std::string const& m : moves)
        if (m == move)
            return true;
    return false;
}

inline uint32_t Count(std::string const (&moves)[4])
{
    uint32_t n = 0;
    for (std::string const& m : moves)
        n += m.empty() ? 0 : 1;
    return n;
}

// Learn `move`: the first free slot if there is one, otherwise it replaces slot 1-4. `forgot` is the move that
// was replaced (empty when a slot was free). Returns false and changes nothing when the move is already known,
// or when all four are taken and `slot` is not 1-4.
inline bool Place(std::string (&moves)[4], std::string const& move, uint32_t slot, std::string& forgot)
{
    forgot.clear();
    if (move.empty() || Knows(moves, move))
        return false;
    for (std::string& m : moves)
        if (m.empty())
        {
            m = move;
            return true;
        }
    if (slot < 1 || slot > 4)
        return false;
    forgot = moves[slot - 1];
    moves[slot - 1] = move;
    return true;
}
} // namespace BattlemonMoveSlots

#endif
