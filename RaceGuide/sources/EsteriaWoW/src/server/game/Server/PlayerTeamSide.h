/*
 * This file is part of the AzerothCore project.
 *
 * The two-sided PvP stores (battlegrounds, battlefields, outdoor PvP) keep exactly one entry per
 * side. A Freeborn character has no side of its own there, so it counts as the team its race
 * implies -- the same side it would have had before the Freeborn team existed.
 *
 * The mapping is the identity for TEAM_ALLIANCE and TEAM_HORDE, so it changes nothing for any
 * character that is not Freeborn. It exists so that a Freeborn can never index one of those
 * two-element stores with TEAM_FREEBORN, which read out of bounds.
 */

#ifndef ESTERIA_PLAYER_TEAM_SIDE_H
#define ESTERIA_PLAYER_TEAM_SIDE_H

#include "Player.h"

/// The side a character counts as in the two-sided PvP stores.
inline TeamId PvpSideOfTeam(TeamId persistent, TeamId origin)
{
    if (persistent == TEAM_ALLIANCE || persistent == TEAM_HORDE)
        return persistent;

    // TEAM_NEUTRAL and TEAM_FREEBORN have no PvP side of their own.
    if (origin == TEAM_ALLIANCE || origin == TEAM_HORDE)
        return origin;

    return TEAM_ALLIANCE;   // no race implies anything else, so this is unreachable in practice
}

inline TeamId PvpSideOf(Player const* player)
{
    return PvpSideOfTeam(player->GetTeamId(), player->GetOriginTeamId());
}

#endif // ESTERIA_PLAYER_TEAM_SIDE_H
