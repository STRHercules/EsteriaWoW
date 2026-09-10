#ifndef BATTLEMON_SESSION_H
#define BATTLEMON_SESSION_H

#include "ObjectGuid.h"

#include <cstdint>
#include <string>
#include <vector>

class Player;

// One command batch collects outbound BM lines here; sidecar reads them after
// HandleCommand, the WoW client gets the same strings via whisper.
struct BattlemonSession
{
    uint32 guid = 0;
    ObjectGuid playerGuid;
    Player* player = nullptr;
    std::vector<std::string> outbox;
};

#endif
