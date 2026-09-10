#include "BattlemonOverworld.h"

#include "BattlemonMgr.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "Random.h"
#include "StringFormat.h"
#include "Tokenize.h"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <string>
#include <utility>

BattlemonOverworld* BattlemonOverworld::instance()
{
    static BattlemonOverworld inst;
    return &inst;
}

void BattlemonOverworld::LoadConfig()
{
    _enabled = sConfigMgr->GetOption<bool>("BattlemonOverworld.Enable", true);
    _morphCritters = sConfigMgr->GetOption<bool>("BattlemonOverworld.MorphCritters", false);
    _refreshMinSeconds = sConfigMgr->GetOption<uint32>("BattlemonOverworld.RefreshMin", 480);
    _refreshMaxSeconds = sConfigMgr->GetOption<uint32>("BattlemonOverworld.RefreshMax", 900);
    _formPoolSize = sConfigMgr->GetOption<uint32>("BattlemonOverworld.FormPool", 0);
    if (_refreshMinSeconds > _refreshMaxSeconds)
        std::swap(_refreshMinSeconds, _refreshMaxSeconds);

    _scale = sConfigMgr->GetOption<float>("BattlemonOverworld.Scale", 1.5f);
    _hover = sConfigMgr->GetOption<float>("BattlemonOverworld.Hover", 0.0f);
    _scaleFromHeight = sConfigMgr->GetOption<bool>("BattlemonOverworld.ScaleFromHeight", true);
    _scaleAtMeters = sConfigMgr->GetOption<float>("BattlemonOverworld.ScaleAtMeters", 1.0f);
    _scaleMin = sConfigMgr->GetOption<float>("BattlemonOverworld.ScaleMin", 0.7f);
    _scaleMax = sConfigMgr->GetOption<float>("BattlemonOverworld.ScaleMax", 1.75f);
    if (_scaleAtMeters < 0.1f)
        _scaleAtMeters = 0.1f;
    if (_scaleMin > _scaleMax)
        std::swap(_scaleMin, _scaleMax);

    _hoverFlying = sConfigMgr->GetOption<float>("BattlemonOverworld.Hover.Flying", 1.25f);
    _hoverLevitate = sConfigMgr->GetOption<float>("BattlemonOverworld.Hover.Levitate", 1.0f);
    _hoverGhost = sConfigMgr->GetOption<float>("BattlemonOverworld.Hover.Ghost", 0.4f);
    ParseNudges(sConfigMgr->GetOption<std::string>("BattlemonOverworld.Nudge", ""));
}

uint32 BattlemonOverworld::DisplayId(uint32 formId, bool shiny)
{
    if (!formId)
        return 0;
    return (shiny ? BattlemonOverworldIds::DisplayShinyBase : BattlemonOverworldIds::DisplayNormalBase) + formId;
}

bool BattlemonOverworld::ParseDisplay(uint32 displayId, uint32& formId, bool& shiny)
{
    if (displayId > BattlemonOverworldIds::DisplayShinyBase
        && displayId < BattlemonOverworldIds::DisplayShinyBase + 10000)
    {
        formId = displayId - BattlemonOverworldIds::DisplayShinyBase;
        shiny = true;
        return formId > 0;
    }
    if (displayId > BattlemonOverworldIds::DisplayNormalBase
        && displayId < BattlemonOverworldIds::DisplayNormalBase + 10000)
    {
        formId = displayId - BattlemonOverworldIds::DisplayNormalBase;
        shiny = false;
        return formId > 0;
    }
    return false;
}

void BattlemonOverworld::StartLinkedWild(Player* player, uint32 formId, bool shiny, ObjectGuid source)
{
    if (!player)
        return;
    sBattlemonMgr->StartWild(player, formId, shiny, true, source);
}

bool BattlemonOverworld::TryStartFromCreature(Player* player, Creature* creature)
{
    if (!_enabled || !player || !creature)
        return false;
    if (!sBattlemonMgr->IsEnabled() || !sBattlemonMgr->ShouldHandle(player))
        return false;
    if (sBattlemonMgr->HasActiveEncounter(player))
        return true;

    uint32 formId = 0;
    bool shiny = false;
    if (!ParseDisplay(creature->GetDisplayId(), formId, shiny))
        return false;
    if (!sBattlemonMgr->GetForm(formId))
        return false;

    StartLinkedWild(player, formId, shiny, creature->GetGUID());
    return true;
}

void BattlemonOverworld::ApplyLook(Creature* creature, uint32 formId, bool shiny)
{
    if (!creature || !formId)
        return;
    uint32 display = DisplayId(formId, shiny);
    if (!display)
        return;

    // Nameplates cache by entry. SetName only changes the server string.
    uint32 const entry = BattlemonOverworldIds::FormEntry(formId);
    if (entry && sObjectMgr->GetCreatureTemplate(entry))
    {
        // Always re-init from the form template. Skipping when entry already matches
        // leaves critters stuck with a partial UpdateEntry (wrong display, cube on client)
        // if the first morph ran before overworld SQL/model info was ready.
        creature->UpdateEntry(entry);
        creature->SetDisplayId(display);
        creature->SetNativeDisplayId(display);
        ApplyNudge(creature, formId);
    }
    else
    {
        if (BattlemonForm const* form = sBattlemonMgr->GetForm(formId))
            creature->SetName(form->name);
        creature->SetDisplayId(display);
        creature->SetNativeDisplayId(display);
        ApplyNudge(creature, formId);
    }

    // Outdoor critters morph in place. Clients can keep the old critter model
    // (checkerboard cube) unless we force a fresh create with the new display.
    creature->DestroyForVisiblePlayers();
    creature->UpdateObjectVisibility(true);
}

void BattlemonOverworld::RefreshLook(Creature* creature)
{
    if (!creature || !_enabled)
        return;

    uint32 formId = 0;
    bool shiny = false;
    if (!ParseDisplay(creature->GetDisplayId(), formId, shiny) || !formId)
    {
        MorphCreature(creature, 0);
        return;
    }

    ApplyLook(creature, formId, shiny);
    creature->SetNpcFlag(UNIT_NPC_FLAG_GOSSIP);
    creature->SetUnitFlag(UNIT_FLAG_NON_ATTACKABLE);
    creature->SetUnitFlag(UNIT_FLAG_IMMUNE_TO_PC);
    creature->SetFaction(35);
}

static bool IEquals(std::string const& a, char const* b)
{
    if (!b)
        return false;
    size_t n = 0;
    while (b[n])
        ++n;
    if (a.size() != n)
        return false;
    for (size_t i = 0; i < n; ++i)
        if (std::tolower(static_cast<unsigned char>(a[i])) != std::tolower(static_cast<unsigned char>(b[i])))
            return false;
    return true;
}

static bool HasType(BattlemonSpecies const* s, char const* type)
{
    return s && (IEquals(s->type1, type) || IEquals(s->type2, type));
}

static bool HasAbility(BattlemonSpecies const* s, char const* ability)
{
    return s && (IEquals(s->ability1, ability) || IEquals(s->ability2, ability) || IEquals(s->hiddenAbility, ability));
}

static bool ParseFloatToken(std::string_view s, float& out)
{
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front())))
        s.remove_prefix(1);
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back())))
        s.remove_suffix(1);
    if (s.empty())
        return false;
    try
    {
        size_t n = 0;
        out = std::stof(std::string(s), &n);
        return n > 0;
    }
    catch (...)
    {
        return false;
    }
}

void BattlemonOverworld::LoadSpeciesMetrics()
{
    _heightBySpecies.clear();
    QueryResult result = WorldDatabase.Query("SELECT id, height FROM battlemon_species");
    if (!result)
        return;
    do
    {
        Field* f = result->Fetch();
        uint32 id = f[0].Get<uint32>();
        float height = f[1].Get<float>();
        if (id && height > 0.0f)
            _heightBySpecies[id] = height;
    } while (result->NextRow());
}

void BattlemonOverworld::ParseNudges(std::string const& raw)
{
    _nudges.clear();
    for (std::string_view token : Acore::Tokenize(raw, ',', false))
    {
        std::vector<std::string_view> parts = Acore::Tokenize(token, ':', true);
        if (parts.empty())
            continue;
        uint32 formId = 0;
        try
        {
            formId = static_cast<uint32>(std::stoul(std::string(parts[0])));
        }
        catch (...)
        {
            continue;
        }
        if (!formId)
            continue;
        NudgeOverride nudge;
        if (parts.size() > 1)
            nudge.hasScale = ParseFloatToken(parts[1], nudge.scale);
        if (parts.size() > 2)
            nudge.hasHover = ParseFloatToken(parts[2], nudge.hover);
        if (nudge.hasScale || nudge.hasHover)
            _nudges[formId] = nudge;
    }
}

void BattlemonOverworld::ComputeNudge(uint32 formId, float& scale, float& hover) const
{
    BattlemonForm const* form = sBattlemonMgr->GetForm(formId);
    BattlemonSpecies const* species = form ? sBattlemonMgr->GetSpecies(form->speciesId) : nullptr;

    float autoScale = 1.0f;
    if (_scaleFromHeight && species)
    {
        float height = 0.0f;
        if (auto it = _heightBySpecies.find(species->id); it != _heightBySpecies.end())
            height = it->second;
        if (height > 0.0f)
            autoScale = height / _scaleAtMeters;
        autoScale = std::clamp(autoScale, _scaleMin, _scaleMax);
    }

    float autoHover = 0.0f;
    if (HasType(species, "FLYING"))
        autoHover = std::max(autoHover, _hoverFlying);
    if (HasAbility(species, "LEVITATE"))
        autoHover = std::max(autoHover, _hoverLevitate);
    if (HasType(species, "GHOST"))
        autoHover = std::max(autoHover, _hoverGhost);

    scale = autoScale * _scale;
    hover = autoHover + _hover;
    if (scale < 0.05f)
        scale = 0.05f;

    if (auto it = _nudges.find(formId); it != _nudges.end())
    {
        if (it->second.hasScale)
            scale = it->second.scale;
        if (it->second.hasHover)
            hover = it->second.hover;
    }
}

void BattlemonOverworld::ApplyNudge(Creature* creature, uint32 formId)
{
    if (!creature)
        return;
    float scale = 1.0f;
    float hover = 0.0f;
    ComputeNudge(formId, scale, hover);
    creature->SetObjectScale(scale);

    if (creature->IsHovering() && hover <= 0.01f)
        creature->SetHover(false);

    creature->SetFloatValue(UNIT_FIELD_HOVERHEIGHT, hover > 0.01f ? hover : 0.0f);
    if (hover > 0.01f)
    {
        if (!creature->IsHovering())
            creature->SetHover(true);
        else if (creature->GetMap())
        {
            float ground = creature->GetFloorZ();
            creature->Relocate(creature->GetPositionX(), creature->GetPositionY(), ground + hover);
        }
    }
}

uint32 BattlemonOverworld::PickFormIdAvoiding(uint32 avoidFormId)
{
    EnsurePool();
    std::vector<uint32> pool;
    {
        std::lock_guard<std::mutex> g(_lock);
        if (_formPoolSize && !_pool.empty())
            pool = _pool;
    }

    auto usable = [](BattlemonForm const* form) -> bool
    {
        return form && !form->sprite.empty();
    };

    uint32 formId = BattlemonOverworldIds::PikachuFormId;
    if (!pool.empty())
    {
        for (uint32 i = 0; i < 12; ++i)
        {
            formId = pool[urand(0, static_cast<uint32>(pool.size() - 1))];
            if (!avoidFormId || formId != avoidFormId)
                break;
        }
        return formId;
    }

    for (uint32 i = 0; i < 12; ++i)
    {
        BattlemonForm const* form = sBattlemonMgr->PickWildForm();
        if (!usable(form))
            continue;
        formId = form->id;
        if (!avoidFormId || formId != avoidFormId)
            break;
    }
    return formId;
}

void BattlemonOverworld::EnsurePool()
{
    if (!_formPoolSize)
        return;
    {
        std::lock_guard<std::mutex> g(_lock);
        if (_pool.size() >= _formPoolSize)
            return;
    }

    std::vector<uint32> built;
    built.reserve(_formPoolSize);
    for (uint32 n = 0; n < _formPoolSize * 8 && built.size() < _formPoolSize; ++n)
    {
        BattlemonForm const* form = sBattlemonMgr->PickWildForm();
        if (!form || form->sprite.empty())
            continue;
        if (std::find(built.begin(), built.end(), form->id) != built.end())
            continue;
        built.push_back(form->id);
    }
    if (built.empty())
        built.push_back(BattlemonOverworldIds::PikachuFormId);

    std::lock_guard<std::mutex> g(_lock);
    if (_pool.size() < _formPoolSize)
        _pool = std::move(built);
}

uint32 BattlemonOverworld::RandomRefreshMs() const
{
    if (!_refreshMaxSeconds)
        return 0;
    uint32 lo = _refreshMinSeconds;
    uint32 hi = _refreshMaxSeconds;
    if (lo > hi)
        std::swap(lo, hi);
    return urand(lo, hi) * 1000;
}

uint32 BattlemonOverworld::LastFormForSpawn(ObjectGuid::LowType spawnId) const
{
    if (!spawnId)
        return 0;
    auto it = _lastFormBySpawnId.find(spawnId);
    return it == _lastFormBySpawnId.end() ? 0 : it->second;
}

void BattlemonOverworld::MorphCreature(Creature* creature, uint32 avoidFormId)
{
    uint32 formId = PickFormIdAvoiding(avoidFormId);
    bool shiny = sBattlemonMgr->RollSpawnShiny();
    ApplyLook(creature, formId, shiny);
    creature->SetNpcFlag(UNIT_NPC_FLAG_GOSSIP);
    creature->SetUnitFlag(UNIT_FLAG_NON_ATTACKABLE);
    creature->SetUnitFlag(UNIT_FLAG_IMMUNE_TO_PC);
    creature->SetFaction(35);

    ObjectGuid::LowType const spawnId = creature->GetSpawnId();
    std::lock_guard<std::mutex> g(_lock);
    if (spawnId)
        _lastFormBySpawnId[spawnId] = formId;
    if (uint32 wait = RandomRefreshMs())
        _tracked[creature->GetGUID()] = Tracked{ wait, spawnId, formId };
    else
        _tracked.erase(creature->GetGUID());
}

bool BattlemonOverworld::TryMorphCritter(Creature* creature)
{
    if (!_enabled || !_morphCritters)
        return false;
    if (!creature || creature->GetEntry() == BattlemonOverworldIds::CreatureEntry)
        return false;
    if (BattlemonOverworldIds::IsFormEntry(creature->GetEntry()))
        return false;
    if (!creature->IsCritter() || creature->GetScriptId() || creature->IsTrigger())
        return false;
    Map const* map = creature->GetMap();
    if (!map || map->Instanceable())
        return false;

    uint32 avoid = 0;
    ObjectGuid::LowType const spawnId = creature->GetSpawnId();
    if (spawnId)
    {
        std::lock_guard<std::mutex> g(_lock);
        avoid = LastFormForSpawn(spawnId);
    }
    MorphCreature(creature, avoid);
    return true;
}

void BattlemonOverworld::TickCreature(Creature* creature, uint32 diff)
{
    if (!_refreshMaxSeconds || !creature)
        return;

    uint32 shown = 0;
    bool shiny = false;
    if (!ParseDisplay(creature->GetDisplayId(), shown, shiny))
        return;

    uint32 avoid = 0;
    {
        std::lock_guard<std::mutex> g(_lock);
        auto it = _tracked.find(creature->GetGUID());
        if (it == _tracked.end())
            return;
        if (it->second.remainingMs > diff)
        {
            it->second.remainingMs -= diff;
            return;
        }
        avoid = it->second.formId ? it->second.formId : shown;
        it->second.remainingMs = RandomRefreshMs();
    }

    MorphCreature(creature, avoid);
}

void BattlemonOverworld::ForgetCreature(Creature* creature)
{
    if (!creature)
        return;
    std::lock_guard<std::mutex> g(_lock);
    _tracked.erase(creature->GetGUID());
}
