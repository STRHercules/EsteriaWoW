# mod-wxl-dbc

Load WXL-style DBC continuation files into AzerothCore **in memory** after `LoadDBCStores()`.

- Base `data/dbc/*.dbc` files are **never modified**
- Continuation files live in a separate folder (default `data/dbc-continuations/`)
- Same naming and merge rules as the WXL client extension (`wxl-extended-dbc`)
- New row IDs and single-row overrides both work before world startup validation

---

## Prerequisites

1. Copy this folder to your AzerothCore tree as `modules/mod-wxl-dbc/` (from `server-files/module/mod-wxl-dbc/` in this repository).
2. **One-time core patch** (6 files, below). Required before compile. Short reference: [../../core-patch/README.md](../../core-patch/README.md).
3. Copy `conf/mod_wxl_dbc.conf.dist` into your `etc/modules/` or merge into `worldserver.conf`.

---

## Core patch (required, apply before building)

**6 files. Copy-paste each change below.** Search the file for the **NOW** block; replace it with **CHANGE TO**.

Then rebuild `worldserver`.

---

### File 1: `src/server/game/Scripting/ScriptDefines/WorldScript.h`

#### Edit 1a: end of `enum WorldHook`

**NOW:**
```cpp
    WORLDHOOK_ON_BEFORE_FINALIZE_PLAYER_WORLD_SESSION,
    WORLDHOOK_ON_BEFORE_WORLD_INITIALIZED,
    WORLDHOOK_END
```

**CHANGE TO:**
```cpp
    WORLDHOOK_ON_BEFORE_FINALIZE_PLAYER_WORLD_SESSION,
    WORLDHOOK_ON_BEFORE_WORLD_INITIALIZED,
    WORLDHOOK_ON_AFTER_LOAD_DBC_STORES,
    WORLDHOOK_END
```

#### Edit 1b: end of `class WorldScript`

**NOW:**
```cpp
    /**
     * @brief This hook runs after all scripts loading and before itialized
     */
    virtual void OnBeforeWorldInitialized() { }
};
```

**CHANGE TO:**
```cpp
    /**
     * @brief This hook runs after all scripts loading and before itialized
     */
    virtual void OnBeforeWorldInitialized() { }

    virtual void OnAfterLoadDBCStores() { }
};
```

---

### File 2: `src/server/game/Scripting/ScriptDefines/WorldScript.cpp`

#### Edit 2: after `OnBeforeWorldInitialized()`

**NOW:**
```cpp
void ScriptMgr::OnBeforeWorldInitialized()
{
    CALL_ENABLED_HOOKS(WorldScript, WORLDHOOK_ON_BEFORE_WORLD_INITIALIZED, script->OnBeforeWorldInitialized());
}

WorldScript::WorldScript(char const* name, std::vector<uint16> enabledHooks)
```

**CHANGE TO:**
```cpp
void ScriptMgr::OnBeforeWorldInitialized()
{
    CALL_ENABLED_HOOKS(WorldScript, WORLDHOOK_ON_BEFORE_WORLD_INITIALIZED, script->OnBeforeWorldInitialized());
}

void ScriptMgr::OnAfterLoadDBCStores()
{
    CALL_ENABLED_HOOKS(WorldScript, WORLDHOOK_ON_AFTER_LOAD_DBC_STORES, script->OnAfterLoadDBCStores());
}

WorldScript::WorldScript(char const* name, std::vector<uint16> enabledHooks)
```

> **Note:** If search-replace fails here, your fork may use `const char*` instead of `char const*` on the `WorldScript::WorldScript(...)` line. Same thing. Keep whichever spelling your file already has; only insert the new `OnAfterLoadDBCStores()` function between the two blocks.

---

### File 3: `src/server/game/Scripting/ScriptMgr.h`

#### Edit 3: in `public: /* WorldScript */`

**NOW:**
```cpp
    void OnBeforeWorldInitialized();
    void OnAfterUnloadAllMaps();
```

**CHANGE TO:**
```cpp
    void OnBeforeWorldInitialized();
    void OnAfterLoadDBCStores();
    void OnAfterUnloadAllMaps();
```

---

### File 4: `src/server/game/World/World.cpp`

#### Edit 4: after `LoadDBCStores`

**NOW:**
```cpp
    LOG_INFO("server.loading", "Initialize Data Stores...");
    LoadDBCStores(_dataPath);
    DetectDBCLang();
```

**CHANGE TO:**
```cpp
    LOG_INFO("server.loading", "Initialize Data Stores...");
    LoadDBCStores(_dataPath);
    sScriptMgr->OnAfterLoadDBCStores();
    DetectDBCLang();
```

---

### File 5: `src/server/shared/DataStores/DBCStore.h`

#### Edit 5: add `ReplaceEntry()` and `EnsureCapacity()` next to `SetEntry()` in `class DBCStorage<T>`

**Required.** `SetEntry()` (stock AzerothCore) calls `delete _indexTable.AsT[id]` before
overwriting a slot. That's safe only when the slot never held a real entry (upstream's
only callers are unit tests against an empty store). In a normally-loaded store, every
entry is a pointer into one shared allocation (`AutoProduceData`'s data table, or the
`*_dbc` SQL overlay's data table) that gets freed in bulk, not per-entry — so `SetEntry`
on an **existing** row corrupts the heap (crashes on `delete`, usually inside the
allocator, e.g. jemalloc `je_large_dalloc`). This module injects continuation rows that
can land on IDs already populated by the base file or a `*_dbc` DB overlay, so it must
use a version that never deletes the old value.

`EnsureCapacity()` is a performance fix for the same code path: `ReplaceEntry()` (like
`SetEntry()`) grows the index table one slot at a time (`newSize = id + 1`), so injecting
a continuation file with thousands of new sequential IDs reallocates and copies the whole
table on every single row — O(N²). `WxlDbcInject.h` calls `EnsureCapacity()` once, up
front, to the final size the file needs, so the per-row `ReplaceEntry()` calls are O(1).

**NOW:**
```cpp
    void SetEntry(uint32 id, T* t)
    {
        if (id >= _indexTableSize)
        {
            // Resize
            typedef char* ptr;
            std::size_t newSize = id + 1;
            ptr* newArr = new ptr[newSize];
            memset(newArr, 0, newSize * sizeof(ptr));
            memcpy(newArr, _indexTable.AsChar, _indexTableSize * sizeof(ptr));
            delete[] reinterpret_cast<char*>(_indexTable.AsT);
            _indexTable.AsChar = newArr;
            _indexTableSize = newSize;
        }

        delete _indexTable.AsT[id];
        _indexTable.AsT[id] = t;
    }

    [[nodiscard]] uint32 GetNumRows() const { return _indexTableSize; }
```

**CHANGE TO:**
```cpp
    void SetEntry(uint32 id, T* t)
    {
        if (id >= _indexTableSize)
        {
            // Resize
            typedef char* ptr;
            std::size_t newSize = id + 1;
            ptr* newArr = new ptr[newSize];
            memset(newArr, 0, newSize * sizeof(ptr));
            memcpy(newArr, _indexTable.AsChar, _indexTableSize * sizeof(ptr));
            delete[] reinterpret_cast<char*>(_indexTable.AsT);
            _indexTable.AsChar = newArr;
            _indexTableSize = newSize;
        }

        delete _indexTable.AsT[id];
        _indexTable.AsT[id] = t;
    }

    // Like SetEntry(), but does not delete the previous value at `id`.
    // Use this to override an existing DBC row from outside the normal
    // load path (e.g. this module) -- see mod-wxl-dbc README for why.
    void ReplaceEntry(uint32 id, T* t)
    {
        if (id >= _indexTableSize)
        {
            // Resize
            typedef char* ptr;
            std::size_t newSize = id + 1;
            ptr* newArr = new ptr[newSize];
            memset(newArr, 0, newSize * sizeof(ptr));
            memcpy(newArr, _indexTable.AsChar, _indexTableSize * sizeof(ptr));
            delete[] reinterpret_cast<char*>(_indexTable.AsT);
            _indexTable.AsChar = newArr;
            _indexTableSize = newSize;
        }

        _indexTable.AsT[id] = t;
    }

    // Grows the index table to at least `minSize` in one allocation.
    // SetEntry()/ReplaceEntry() each grow by exactly one slot (newSize =
    // id + 1), so calling either of them in a loop over N new sequential
    // IDs reallocates+memcpys the whole table N times (O(N^2)). Call this
    // once before such a loop, with the final size known up front (e.g.
    // the `indexTableSize` AutoProduceData() already computed), so each
    // ReplaceEntry() call in the loop is then O(1).
    void EnsureCapacity(uint32 minSize)
    {
        if (minSize <= _indexTableSize)
            return;

        typedef char* ptr;
        ptr* newArr = new ptr[minSize];
        memset(newArr, 0, minSize * sizeof(ptr));
        memcpy(newArr, _indexTable.AsChar, _indexTableSize * sizeof(ptr));
        delete[] reinterpret_cast<char*>(_indexTable.AsT);
        _indexTable.AsChar = newArr;
        _indexTableSize = minSize;
    }

    [[nodiscard]] uint32 GetNumRows() const { return _indexTableSize; }
```

---

### File 6: `src/server/game/DataStores/DBCStores.cpp` and `.h`

#### Edit 6: extract the derived-index-building block into a callable `RebuildDbcDerivedIndexes()`

**Required.** `LoadDBCStores()` builds about a dozen secondary lookup structures
once, from the base stores, right after loading them — `SkillRaceClassInfoBySkill`
(used by `GetSkillRaceClassInfo()`), `sTalentSpellPosMap` (used by
`GetTalentSpellPos()`), `sCharStartOutfitMap`, `sSpellsByCategoryStore`, and others.
This module injects continuation rows into those same base stores *after*
`LoadDBCStores()` has already returned, so none of these derived structures ever
learn about the new or overridden rows — code that queries them (e.g. talent
lookups on login) can `ASSERT`-crash or silently reject valid custom-class data.

Move the block that builds these into its own function, clearing each container
first so it's safe to call a second time, and call it both where `LoadDBCStores()`
always did and again from this module after continuations are applied.

In `src/server/game/DataStores/DBCStores.cpp`, find this block (it sits right after
the `#undef LOAD_DBC` inside `LoadDBCStores()`, and runs through the talent-tab-pages
loop, just before the `TaxiPath` handling):

**NOW:**
```cpp
#undef LOAD_DBC

    for (uint32 i = 0; i < sAreaTableStore.GetNumRows(); ++i)    // areaflag numbered from 0
    {
        if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(i))
        {
            // fill AreaId->DBC records
            sAreaFlagByAreaID.insert(AreaFlagByAreaID::value_type(uint16(area->ID), area->exploreFlag));

            // fill MapId->DBC records ( skip sub zones and continents )
            if (area->zone == 0 && area->mapid != 0 && area->mapid != 1 && area->mapid != 530)
                sAreaFlagByMapID.insert(AreaFlagByMapID::value_type(area->mapid, area->exploreFlag));
        }
    }

    for (CharStartOutfitEntry const* outfit : sCharStartOutfitStore)
        sCharStartOutfitMap[outfit->Race | (outfit->Class << 8) | (outfit->Gender << 16)] = outfit;

    for (CharSectionsEntry const* charSection : sCharSectionsStore)
        if (charSection->Race && ((1 << (charSection->Race - 1)) & sRaceMgr->GetPlayableRaceMask()) != 0) //ignore Nonplayable races
            sCharSectionMap.insert({ charSection->GenType | (charSection->Gender << 8) | (charSection->Race << 16), charSection });

    for (FactionEntry const* faction : sFactionStore)
    {
        if (faction->team)
        {
            SimpleFactionsList& flist = sFactionTeamMap[faction->team];
            flist.push_back(faction->ID);
        }
    }

    for (GameObjectDisplayInfoEntry const* info : sGameObjectDisplayInfoStore)
    {
        if (info->maxX < info->minX)
            std::swap(*(float*)(&info->maxX), *(float*)(&info->minX));

        if (info->maxY < info->minY)
            std::swap(*(float*)(&info->maxY), *(float*)(&info->minY));

        if (info->maxZ < info->minZ)
            std::swap(*(float*)(&info->maxZ), *(float*)(&info->minZ));
    }

    for (EmotesTextSoundEntry const* emoteTextSound : sEmotesTextSoundStore)
        sEmotesTextSoundMap[EmotesTextSoundKey(emoteTextSound->EmotesTextId, emoteTextSound->RaceId, emoteTextSound->SexId)] = emoteTextSound;

    // fill data
    for (MapDifficultyEntry const* entry : sMapDifficultyStore)
        sMapDifficultyMap[MAKE_PAIR32(entry->MapId, entry->Difficulty)] = MapDifficulty(entry->resetTime, entry->maxPlayers, entry->areaTriggerText[0] != '\0');

    for (PvPDifficultyEntry const* entry : sPvPDifficultyStore)
        if (entry->bracketId > MAX_BATTLEGROUND_BRACKETS)
            ASSERT(false && "Need update MAX_BATTLEGROUND_BRACKETS by DBC data");

    for (auto i : sSpellStore)
        if (i->Category)
            sSpellsByCategoryStore[i->Category].emplace(false, i->Id);

    for (SkillRaceClassInfoEntry const* entry : sSkillRaceClassInfoStore)
    {
        if (sSkillLineStore.LookupEntry(entry->SkillID))
        {
            SkillRaceClassInfoBySkill.emplace(entry->SkillID, entry);
        }
    }

    for (SkillLineAbilityEntry const* skillLine : sSkillLineAbilityStore)
    {
        SpellEntry const* spellEntry = sSpellStore.LookupEntry(skillLine->Spell);
        if (spellEntry && spellEntry->Attributes & SPELL_ATTR0_PASSIVE)
        {
            for (CreatureFamilyEntry const* cFamily : sCreatureFamilyStore)
            {
                if (skillLine->SkillLine != cFamily->skillLine[0] && skillLine->SkillLine != cFamily->skillLine[1])
                {
                    continue;
                }

                if (spellEntry->SpellLevel)
                {
                    continue;
                }

                if (skillLine->AcquireMethod != SKILL_LINE_ABILITY_LEARNED_ON_SKILL_LEARN)
                {
                    continue;
                }

                sPetFamilySpellsStore[cFamily->ID].insert(spellEntry->Id);
            }
        }
    }

    for (SkillLineAbilityEntry const* skillLine : sSkillLineAbilityStore)
        sSkillLineAbilityIndexBySkillLine[skillLine->SkillLine].push_back(skillLine);

    // Create Spelldifficulty searcher
```

Leave the `SpellDifficulty` loop right after this exactly as it is — do not move it, it has no eDBC content. Immediately after that loop's closing `}`, this follows (still in `LoadDBCStores()`):

**NOW:**
```cpp
    // create talent spells set
    for (TalentEntry const* talentInfo : sTalentStore)
    {
        TalentTabEntry const* talentTab = sTalentTabStore.LookupEntry(talentInfo->TalentTab);

        for (uint8 j = 0; j < MAX_TALENT_RANK; ++j)
        {
            if (talentInfo->RankID[j])
            {
                sTalentSpellPosMap[talentInfo->RankID[j]] = TalentSpellPos(talentInfo->TalentID, j);

                if (talentTab && talentTab->petTalentMask)
                {
                    sPetTalentSpells.insert(talentInfo->RankID[j]);
                }
            }
        }
    }

    // prepare fast data access to bit pos of talent ranks for use at inspecting
    {
        // now have all max ranks (and then bit amount used for store talent ranks in inspect)
        for (uint32 talentTabId = 1; talentTabId < sTalentTabStore.GetNumRows(); ++talentTabId)
        {
            TalentTabEntry const* talentTabInfo = sTalentTabStore.LookupEntry(talentTabId);
            if (!talentTabInfo)
                continue;

            // prevent memory corruption; otherwise cls will become 12 below
            if ((talentTabInfo->ClassMask & CLASSMASK_ALL_PLAYABLE) == 0)
                continue;

            // store class talent tab pages
            for (uint32 cls = 1; cls < MAX_CLASSES; ++cls)
                if (talentTabInfo->ClassMask & (1 << (cls - 1)))
                    sTalentTabPages[cls][talentTabInfo->tabpage] = talentTabId;
        }
    }

    for (uint32 i = 1; i < sTaxiPathStore.GetNumRows(); ++i)
```

**CHANGE TO** (all three blocks above collapse to this): first, immediately above
`void LoadDBCStores(std::string const& dataPath)`, add the new function:

```cpp
// Rebuilds the derived lookup indexes that LoadDBCStores() builds from the
// base stores once at boot. Callable a second time (e.g. by mod-wxl-dbc,
// after it injects continuation rows into these same stores) because every
// container is cleared before being repopulated from scratch -- otherwise a
// second call would duplicate multimap/vector entries. Only covers indexes
// built from tables that WXL eDBC continuations can actually touch
// (AreaTable, CharStartOutfit, CharSections, Faction, GameObjectDisplayInfo,
// EmotesTextSound, Spell, SkillRaceClassInfo, SkillLineAbility,
// CreatureFamily, Talent, TalentTab). SpellDifficulty/TaxiPath/TaxiNodes/
// Transport*/WMOAreaTable have no eDBC content and are left where they were,
// built once in LoadDBCStores() as before.
void RebuildDbcDerivedIndexes()
{
    sAreaFlagByAreaID.clear();
    sAreaFlagByMapID.clear();
    for (uint32 i = 0; i < sAreaTableStore.GetNumRows(); ++i)    // areaflag numbered from 0
    {
        if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(i))
        {
            // fill AreaId->DBC records
            sAreaFlagByAreaID.insert(AreaFlagByAreaID::value_type(uint16(area->ID), area->exploreFlag));

            // fill MapId->DBC records ( skip sub zones and continents )
            if (area->zone == 0 && area->mapid != 0 && area->mapid != 1 && area->mapid != 530)
                sAreaFlagByMapID.insert(AreaFlagByMapID::value_type(area->mapid, area->exploreFlag));
        }
    }

    sCharStartOutfitMap.clear();
    for (CharStartOutfitEntry const* outfit : sCharStartOutfitStore)
        sCharStartOutfitMap[outfit->Race | (outfit->Class << 8) | (outfit->Gender << 16)] = outfit;

    sCharSectionMap.clear();
    for (CharSectionsEntry const* charSection : sCharSectionsStore)
        if (charSection->Race && ((1 << (charSection->Race - 1)) & sRaceMgr->GetPlayableRaceMask()) != 0) //ignore Nonplayable races
            sCharSectionMap.insert({ charSection->GenType | (charSection->Gender << 8) | (charSection->Race << 16), charSection });

    sFactionTeamMap.clear();
    for (FactionEntry const* faction : sFactionStore)
    {
        if (faction->team)
        {
            SimpleFactionsList& flist = sFactionTeamMap[faction->team];
            flist.push_back(faction->ID);
        }
    }

    for (GameObjectDisplayInfoEntry const* info : sGameObjectDisplayInfoStore)
    {
        if (info->maxX < info->minX)
            std::swap(*(float*)(&info->maxX), *(float*)(&info->minX));

        if (info->maxY < info->minY)
            std::swap(*(float*)(&info->maxY), *(float*)(&info->minY));

        if (info->maxZ < info->minZ)
            std::swap(*(float*)(&info->maxZ), *(float*)(&info->minZ));
    }

    sEmotesTextSoundMap.clear();
    for (EmotesTextSoundEntry const* emoteTextSound : sEmotesTextSoundStore)
        sEmotesTextSoundMap[EmotesTextSoundKey(emoteTextSound->EmotesTextId, emoteTextSound->RaceId, emoteTextSound->SexId)] = emoteTextSound;

    sSpellsByCategoryStore.clear();
    for (auto i : sSpellStore)
        if (i->Category)
            sSpellsByCategoryStore[i->Category].emplace(false, i->Id);

    SkillRaceClassInfoBySkill.clear();
    for (SkillRaceClassInfoEntry const* entry : sSkillRaceClassInfoStore)
    {
        if (sSkillLineStore.LookupEntry(entry->SkillID))
        {
            SkillRaceClassInfoBySkill.emplace(entry->SkillID, entry);
        }
    }

    sPetFamilySpellsStore.clear();
    for (SkillLineAbilityEntry const* skillLine : sSkillLineAbilityStore)
    {
        SpellEntry const* spellEntry = sSpellStore.LookupEntry(skillLine->Spell);
        if (spellEntry && spellEntry->Attributes & SPELL_ATTR0_PASSIVE)
        {
            for (CreatureFamilyEntry const* cFamily : sCreatureFamilyStore)
            {
                if (skillLine->SkillLine != cFamily->skillLine[0] && skillLine->SkillLine != cFamily->skillLine[1])
                {
                    continue;
                }

                if (spellEntry->SpellLevel)
                {
                    continue;
                }

                if (skillLine->AcquireMethod != SKILL_LINE_ABILITY_LEARNED_ON_SKILL_LEARN)
                {
                    continue;
                }

                sPetFamilySpellsStore[cFamily->ID].insert(spellEntry->Id);
            }
        }
    }

    sSkillLineAbilityIndexBySkillLine.clear();
    for (SkillLineAbilityEntry const* skillLine : sSkillLineAbilityStore)
        sSkillLineAbilityIndexBySkillLine[skillLine->SkillLine].push_back(skillLine);

    // create talent spells set
    sTalentSpellPosMap.clear();
    sPetTalentSpells.clear();
    for (TalentEntry const* talentInfo : sTalentStore)
    {
        TalentTabEntry const* talentTab = sTalentTabStore.LookupEntry(talentInfo->TalentTab);

        for (uint8 j = 0; j < MAX_TALENT_RANK; ++j)
        {
            if (talentInfo->RankID[j])
            {
                sTalentSpellPosMap[talentInfo->RankID[j]] = TalentSpellPos(talentInfo->TalentID, j);

                if (talentTab && talentTab->petTalentMask)
                {
                    sPetTalentSpells.insert(talentInfo->RankID[j]);
                }
            }
        }
    }

    // prepare fast data access to bit pos of talent ranks for use at inspecting
    {
        memset(sTalentTabPages, 0, sizeof(sTalentTabPages));

        // now have all max ranks (and then bit amount used for store talent ranks in inspect)
        for (uint32 talentTabId = 1; talentTabId < sTalentTabStore.GetNumRows(); ++talentTabId)
        {
            TalentTabEntry const* talentTabInfo = sTalentTabStore.LookupEntry(talentTabId);
            if (!talentTabInfo)
                continue;

            // prevent memory corruption; otherwise cls will become 12 below
            if ((talentTabInfo->ClassMask & CLASSMASK_ALL_PLAYABLE) == 0)
                continue;

            // store class talent tab pages
            for (uint32 cls = 1; cls < MAX_CLASSES; ++cls)
                if (talentTabInfo->ClassMask & (1 << (cls - 1)))
                    sTalentTabPages[cls][talentTabInfo->tabpage] = talentTabId;
        }
    }
}
```

Then, inside `LoadDBCStores()`, replace the three blocks quoted above (from `#undef LOAD_DBC`'s following code through `sSkillLineAbilityIndexBySkillLine[...]`, and separately the talent block through `sTalentTabPages[...]`) with a single call:

```cpp
#undef LOAD_DBC

    RebuildDbcDerivedIndexes();

    // fill data
    for (MapDifficultyEntry const* entry : sMapDifficultyStore)
        sMapDifficultyMap[MAKE_PAIR32(entry->MapId, entry->Difficulty)] = MapDifficulty(entry->resetTime, entry->maxPlayers, entry->areaTriggerText[0] != '\0');

    for (PvPDifficultyEntry const* entry : sPvPDifficultyStore)
        if (entry->bracketId > MAX_BATTLEGROUND_BRACKETS)
            ASSERT(false && "Need update MAX_BATTLEGROUND_BRACKETS by DBC data");

    // Create Spelldifficulty searcher
```

...(leave the `SpellDifficulty` loop exactly as it was)...

```cpp
    for (uint32 i = 1; i < sTaxiPathStore.GetNumRows(); ++i)
```

(the talent block that used to sit between those two is gone — it now lives inside `RebuildDbcDerivedIndexes()`).

Finally, in `src/server/game/DataStores/DBCStores.h`, add the declaration next to `LoadDBCStores`:

**NOW:**
```cpp
void LoadDBCStores(std::string const& dataPath);
```

**CHANGE TO:**
```cpp
void LoadDBCStores(std::string const& dataPath);

// Rebuilds the derived lookup indexes LoadDBCStores() builds once at boot
// (SkillRaceClassInfoBySkill, sTalentSpellPosMap, sCharStartOutfitMap, etc.)
// from the current contents of their source stores. LoadDBCStores() calls
// this itself; call it again after modifying one of those stores in place
// (e.g. mod-wxl-dbc injecting continuation rows after LoadDBCStores()
// returns) so the indexes reflect the change. See DBCStores.cpp for exactly
// which indexes this covers.
void RebuildDbcDerivedIndexes();
```

---

## Server layout

```
data/
  dbc/                          ← vanilla extract (never touched by this module)
  dbc-continuations/            ← your continuation files (configurable)
    wxl-dbc.manifest            ← optional ordering
    Spell.dbc1-test             ← example: new or overridden rows
    CreatureDisplayInfo.dbc1-myproject
    DBFilesClient/              ← subfolders also scanned
      ItemDisplayInfo.dbc2-artpass
```

Config (`mod_wxl_dbc.conf` or `worldserver.conf`):

```ini
[WxlDbc]
WxlDbc.Enable = 1
WxlDbc.ContinuationPath = dbc-continuations
```

---

## Continuation naming (WXL contract)

```
{Table}.dbc                 base (in data/dbc/, unchanged)
{Table}.dbc{N}-{project}    continuation, N = 1..9
```

Examples:

```
Spell.dbc1-hotfix
CreatureDisplayInfo.dbc1-artpass
Item.dbc3-shared-lib
```

### Merge order (later wins on duplicate row ID)

1. Base row already loaded from `data/dbc/{Table}.dbc` (+ any `*_dbc` DB overlay)
2. Tier `1`, then `2`, … `9`
3. Within a tier: manifest line order, then project slug A–Z
4. Same row ID: **later continuation wins**

Backup files (`.bak`, `.backup`, `.old`, `.orig`, `.tmp`) are ignored.

---

## Manifest (optional on server)

On the server, the module **auto-scans** `dbc-continuations/` for `*.dbc[1-9]-*` files. You usually do not need a manifest here. Optional `wxl-dbc.manifest` in that folder only if you want explicit load order (same format as the client extension uses for MPQ packs).

---

## Verify

After starting `worldserver`, check the log for:

```
Applying N continuation file(s) from ...
  Spell.dbc1-hotfix -> X row(s) into Spell.dbc
Done. ... Base data/dbc/ files were not modified.
```

---

## Client side

This module is the **server half** of the WXL client extension in this repository ([../../../README.md](../../../README.md)). Same continuation files, same naming, same merge rules. Deploy the same `.dbc1-*` binaries on the client (loose `Data/DBFilesClient/` or MPQ) with `wxl-extended-dbc` installed. Row IDs must match on both sides.

---

## Notes

- Continuations apply **after** file load and **after** AC's `*_dbc` DB overlays, so continuation rows **win** over DB overlays for the same ID.
- Tables must match the server's WotLK DBC layout (same as today).
- **Custom forks:** if your core loads DBC stores that stock AzerothCore does not, register them in `src/WxlDbcRegistry.cpp` (same `WXL_DBC(...)` pattern as the existing entries). Otherwise continuations for those tables are skipped with "No server store registered".
- A few tables build extra in-memory indexes at the end of `LoadDBCStores()` (e.g. `MapDifficulty` → `sMapDifficultyMap`). `LookupEntry()` on the store is updated; those derived indexes are not rebuilt. For most tables this does not matter.
