#ifndef BATTLEMON_OVERWORLD_H
#define BATTLEMON_OVERWORLD_H

#include "Define.h"
#include "ObjectGuid.h"

#include <mutex>
#include <string>
#include <unordered_map>
#include <vector>

class Creature;
class Player;

// Keep in sync with tools/patch_dbc_csv.py
namespace BattlemonOverworldIds
{
    constexpr uint32 ModelNormalBase = 2252000; // + formId
    constexpr uint32 ModelShinyBase = 2272000;  // + formId
    constexpr uint32 DisplayNormalBase = 50000; // + formId
    constexpr uint32 DisplayShinyBase = 70000;  // + formId; 60000 is reserved by Broken/Sethrak
    // One creature_template per form so the nameplate is not "Cow".
    constexpr uint32 FormEntryBase = 1000000; // + formId
    constexpr uint32 CreatureEntry = 60000;
    constexpr uint32 PikachuFormId = 37; // species 25, empty variant

    inline uint32 FormEntry(uint32 formId)
    {
        return formId ? FormEntryBase + formId : 0;
    }

    inline bool IsFormEntry(uint32 entry)
    {
        return entry > FormEntryBase && entry < FormEntryBase + 10000;
    }
}

class BattlemonOverworld
{
public:
    static BattlemonOverworld* instance();

    void LoadConfig();
    void LoadSpeciesMetrics();

    bool IsEnabled() const { return _enabled; }
    bool MorphCritters() const { return _morphCritters; }
    uint32 RefreshMinSeconds() const { return _refreshMinSeconds; }
    uint32 RefreshMaxSeconds() const { return _refreshMaxSeconds; }
    uint32 FormPool() const { return _formPoolSize; }
    uint32 NudgeOverrideCount() const { return static_cast<uint32>(_nudges.size()); }

    static uint32 DisplayId(uint32 formId, bool shiny);
    static bool ParseDisplay(uint32 displayId, uint32& formId, bool& shiny);
    void ComputeNudge(uint32 formId, float& scale, float& hover) const;

    // Right-click / .bmo spawn. Sends BM\tWILD\tformId\tshiny through
    // BattlemonMgr::HandleAddon. Battlemon uses that form and skips the
    // addon Fight cooldown.
    void StartLinkedWild(Player* player, uint32 formId, bool shiny, ObjectGuid source = ObjectGuid::Empty);

    bool TryStartFromCreature(Player* player, Creature* creature);
    void ApplyLook(Creature* creature, uint32 formId, bool shiny);
    // Re-apply entry/display for an already-morphed overworld sprite (fixes stuck cubes).
    void RefreshLook(Creature* creature);

    bool TryMorphCritter(Creature* creature);
    void TickCreature(Creature* creature, uint32 diff);
    void ForgetCreature(Creature* creature);

private:
    struct Tracked
    {
        uint32 remainingMs = 0;
        ObjectGuid::LowType spawnId = 0;
        uint32 formId = 0;
    };

    BattlemonOverworld() = default;

    struct NudgeOverride
    {
        bool hasScale = false;
        bool hasHover = false;
        float scale = 1.0f;
        float hover = 0.0f;
    };

    void MorphCreature(Creature* creature, uint32 avoidFormId);
    void ApplyNudge(Creature* creature, uint32 formId);
    void ParseNudges(std::string const& raw);
    void EnsurePool();
    uint32 PickFormIdAvoiding(uint32 avoidFormId);
    uint32 RandomRefreshMs() const;
    uint32 LastFormForSpawn(ObjectGuid::LowType spawnId) const;

    bool _enabled = true;
    bool _morphCritters = false;
    uint32 _refreshMinSeconds = 480;
    uint32 _refreshMaxSeconds = 900;
    // 0 = roll the full catalog. Non-zero caps distinct forms (debug only).
    uint32 _formPoolSize = 0;

    float _scale = 1.5f;
    float _hover = 0.0f;
    bool _scaleFromHeight = true;
    float _scaleAtMeters = 1.0f;
    float _scaleMin = 0.7f;
    float _scaleMax = 1.75f;
    float _hoverFlying = 1.25f;
    float _hoverLevitate = 1.0f;
    float _hoverGhost = 0.4f;

    std::unordered_map<uint32, NudgeOverride> _nudges;
    std::unordered_map<uint32, float> _heightBySpecies;

    std::mutex _lock;
    std::unordered_map<ObjectGuid, Tracked> _tracked;
    std::unordered_map<ObjectGuid::LowType, uint32> _lastFormBySpawnId;
    std::vector<uint32> _pool;
};

#define sBattlemonOverworld BattlemonOverworld::instance()

#endif
