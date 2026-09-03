#ifndef MOD_CUSTOM_SERVER_PROGRESSION_EVENTS_H
#define MOD_CUSTOM_SERVER_PROGRESSION_EVENTS_H

#include "Define.h"
#include "ObjectGuid.h"

#include <vector>

namespace Progression
{
    enum class EventType : uint8
    {
        DUNGEON_RUN_BEGIN = 0,
        DUNGEON_RUN_COMPLETE = 1,
        DUNGEON_RUN_FAIL = 2,
        MYTHIC_PLUS_BEGIN = 3,
        MYTHIC_PLUS_BOSS_KILL = 4,
        MYTHIC_PLUS_COMPLETE = 5,
        MYTHIC_PLUS_TIMER_BEAT = 6,
        MYTHIC_PLUS_FAIL = 7,
        DUNGEON_MASTER_BEGIN = 8,
        DUNGEON_MASTER_COMPLETE = 9,
        DUNGEON_MASTER_FAIL = 10,
        ROGUELIKE_BEGIN = 11,
        ROGUELIKE_FLOOR_COMPLETE = 12,
        ROGUELIKE_RUN_END = 13
    };

    struct DungeonEvent
    {
        EventType type;
        uint64 sourceId = 0;
        uint64 sourceStartedAt = 0;
        uint64 detailId = 0;
        std::vector<ObjectGuid> players;
        uint32 groupSize = 0;
        uint32 mapId = 0;
        uint32 mapDifficulty = 0;
        uint32 difficultyId = 0;
        uint32 level = 0;
        uint32 tier = 0;
        uint32 floor = 0;
        uint32 elapsedSeconds = 0;
        uint32 timeLimitSeconds = 0;
        uint32 themeId = 0;
        uint32 bossEntry = 0;
        bool timerBeat = false;
        bool success = false;
    };

    using Handler = void(*)(DungeonEvent const&);

    void SetHandler(Handler handler);
    void Publish(DungeonEvent const& event);
}

#endif
