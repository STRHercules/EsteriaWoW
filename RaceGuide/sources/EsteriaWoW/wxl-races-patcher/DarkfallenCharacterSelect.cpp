// Runtime-only Character Select repair for the Esteria 3.3.5a client.

#include <windows.h>

#include <cstddef>
#include <cstdint>
#include <cstring>

namespace
{
    struct WXL_PluginInfo
    {
        std::uint32_t structSize;
        std::uint32_t apiVersion;
        char const* id;
        std::uint32_t priority;
        std::uint32_t clientBuild;
    };

    struct WXL_Api
    {
        std::uint32_t structSize;
        std::uint32_t apiVersion;
        void(__cdecl* log)(int level, char const* tag, char const* fmt, ...);
        void* subscribe;
        void* emit;
        int(__cdecl* hookAttach)(char const* name, std::uintptr_t target, void* detour, void** original,
            int priority);
    };

    constexpr std::uint32_t kWxlApiVersion = 1;
    constexpr std::uint32_t kWxlClientBuild = 12340;
    constexpr std::size_t kCharacterCustomizationTablePointerOffset = 0x0076B864;
    constexpr std::size_t kCharacterCreateObjectPointerOffset = 0x0076B1A0;
    constexpr std::size_t kCycleCharCustomizationOffset = 0x000E0B50;
    constexpr std::size_t kResolveModelDescriptorOffset = 0x002DC810;
    constexpr std::size_t kCharacterListLoadOffset = 0x000E3CD0;
    constexpr std::size_t kCharacterModelTableReferenceOffset = 0x000E157D;
    constexpr std::size_t kUpdateSelectionCustomizationSceneOffset = 0x000E2FD0;
    constexpr std::size_t kSelectedCharacterIndexOffset = 0x006C436C;
    constexpr std::size_t kCharacterCountOffset = 0x0076B23C;
    constexpr std::size_t kCharacterListOffset = 0x0076B240;
    constexpr std::size_t kCharacterRecordSize = 0x198;
    constexpr std::size_t kCharacterRaceOffset = 0x178;
    constexpr std::size_t kCharacterClassOffset = 0x179;
    constexpr std::size_t kCharacterGenderOffset = 0x17A;
    constexpr std::size_t kCharacterModelOffset = 0x188;
    constexpr std::size_t kCustomizationCategoriesPerRaceGender = 5;
    constexpr std::size_t kHairCustomizationCategory = 3;
    constexpr std::size_t kCustomizationEntrySize = 8;
    constexpr std::size_t kValidateNameOffset = 0x002B0390;
    constexpr std::uint8_t kValidateNameStockBytes[] = { 0x55, 0x8B, 0xEC, 0x8B, 0x45, 0x08 };
    constexpr std::uint8_t kValidateNameTwoNamesBytes[] = { 0xB8, 0x57, 0x00, 0x00, 0x00, 0xC3 };

    using CycleCharCustomizationFn = int(__cdecl*)(void* lua);
    using ResolveModelDescriptorFn = void* (__cdecl*)(std::uint32_t race, std::uint32_t gender);
    using CharacterListLoadFn = void(__cdecl*)();

    std::uint8_t* g_client = nullptr;
    CycleCharCustomizationFn g_originalCycleCharCustomization = nullptr;
    ResolveModelDescriptorFn g_originalResolveModelDescriptor = nullptr;
    CharacterListLoadFn g_originalCharacterListLoad = nullptr;
    WXL_Api const* g_api = nullptr;
    int(__cdecl* g_originalUpdateSelectionCustomizationScene)() = nullptr;
    bool g_loggedCharacterSelectModelSlots = false;
    bool g_loggedWaitingForCharacterRecord = false;
    bool g_loggedModelDescriptors[2][2] = {};
    bool g_loggedCharacterListLoads[2][2] = {};

    bool ApplyTwoNamesClientPatch()
    {
        auto* target = g_client + kValidateNameOffset;
        auto constexpr patchSize = sizeof(kValidateNameTwoNamesBytes);
        if (std::memcmp(target, kValidateNameTwoNamesBytes, patchSize) == 0)
            return true;

        if (std::memcmp(target, kValidateNameStockBytes, patchSize) != 0)
        {
            if (g_api && g_api->log)
                g_api->log(4, "two-names", "ValidateName bytes do not match stock build 12340 at +0x%08X", kValidateNameOffset);
            return false;
        }

        DWORD oldProtect = 0;
        if (!VirtualProtect(target, patchSize, PAGE_EXECUTE_READWRITE, &oldProtect))
            return false;

        std::memcpy(target, kValidateNameTwoNamesBytes, patchSize);
        FlushInstructionCache(GetCurrentProcess(), target, patchSize);

        DWORD restoredProtect = 0;
        VirtualProtect(target, patchSize, oldProtect, &restoredProtect);
        if (g_api && g_api->log)
            g_api->log(2, "two-names", "enabled first + last names in client ValidateName");
        return true;
    }

    std::uint32_t* GetCustomizationEntry(std::uint8_t* customizations, std::size_t race,
        std::size_t gender, std::size_t category)
    {
        auto const raceGender = race * 2 + gender;
        return reinterpret_cast<std::uint32_t*>(
            customizations + ((raceGender * kCustomizationCategoriesPerRaceGender + category) *
                kCustomizationEntrySize));
    }

    void SetCustomizationCount(std::uint8_t* customizations, std::size_t race, std::size_t gender,
        std::uint32_t count)
    {
        auto const entry = GetCustomizationEntry(customizations, race, gender, kHairCustomizationCategory);
        if (entry[0] >= count)
            entry[0] = count;
    }

    void ApplyRuntimeCustomizationCounts()
    {
        auto const customizations = *reinterpret_cast<std::uint8_t**>(g_client + kCharacterCustomizationTablePointerOffset);
        if (!customizations)
            return;

        // Preserve the existing Darkfallen safety clamp.
        SetCustomizationCount(customizations, 43, 0, 9);
        SetCustomizationCount(customizations, 43, 1, 10);
        SetCustomizationCount(customizations, 44, 0, 9);
        SetCustomizationCount(customizations, 44, 1, 10);

        // Do not mutate Mag'har's native customization table here. The 3.3.5a
        // client builds Race45's {count,pointer} hierarchy directly from the full
        // CharSections.dbc. Overwriting entry[0] with UI option counts corrupts
        // those native variation counts and can leave skin/face lookups invalid.
    }

    void LogCharacterCreateCustomizationState(char const* phase)
    {
        if (!g_api || !g_client)
            return;

        auto const character = *reinterpret_cast<std::uint8_t* const*>(
            g_client + kCharacterCreateObjectPointerOffset);
        if (!character)
            return;

        auto const race = *reinterpret_cast<std::uint32_t const*>(character + 0x18);
        auto const gender = *reinterpret_cast<std::uint32_t const*>(character + 0x1C);
        auto const characterClass = *reinterpret_cast<std::uint32_t const*>(character + 0x20);
        auto const hairStyle = *reinterpret_cast<std::uint32_t const*>(character + 0x24);
        auto const skin = *reinterpret_cast<std::uint32_t const*>(character + 0x28);
        auto const face = *reinterpret_cast<std::uint32_t const*>(character + 0x2C);
        auto const hairColor = *reinterpret_cast<std::uint32_t const*>(character + 0x30);
        auto const facialFeature = *reinterpret_cast<std::uint32_t const*>(character + 0x34);

        std::uint32_t skinVariations = 0;
        std::uint32_t skinColors = 0;
        std::uint32_t faceVariations = 0;
        std::uint32_t faceColors = 0;
        auto const customizations = *reinterpret_cast<std::uint8_t* const*>(
            g_client + kCharacterCustomizationTablePointerOffset);
        if (customizations && race < 64 && gender < 2)
        {
            auto const skinEntry = GetCustomizationEntry(customizations, race, gender, 0);
            skinVariations = skinEntry[0];
            if (skinEntry[1] && skinVariations > 0)
            {
                auto const variations = reinterpret_cast<std::uint32_t const*>(skinEntry[1]);
                skinColors = variations[0];
            }

            auto const faceEntry = GetCustomizationEntry(customizations, race, gender, 1);
            faceVariations = faceEntry[0];
            if (faceEntry[1] && face < faceVariations)
            {
                auto const variations = reinterpret_cast<std::uint32_t const*>(faceEntry[1]);
                faceColors = variations[face * 2];
            }
        }

        g_api->log(2, "maghar-customization",
            "%s race=%u gender=%u class=%u hair=%u skin=%u face=%u hairColor=%u feature=%u "
            "skinVars=%u skinColors=%u faceVars=%u faceColors=%u",
            phase, race, gender, characterClass, hairStyle, skin, face, hairColor, facialFeature,
            skinVariations, skinColors, faceVariations, faceColors);
    }

    int __cdecl CycleCharCustomizationDetour(void* lua)
    {
        ApplyRuntimeCustomizationCounts();
        auto const result = g_originalCycleCharCustomization(lua);
        LogCharacterCreateCustomizationState("stock-cycle");
        return result;
    }

    void* __cdecl ResolveModelDescriptorDetour(std::uint32_t race, std::uint32_t gender)
    {
        ApplyRuntimeCustomizationCounts();
        auto const descriptor = g_originalResolveModelDescriptor(race, gender);
        if ((race != 43 && race != 44) || gender > 1 || g_loggedModelDescriptors[race - 43][gender])
            return descriptor;

        g_loggedModelDescriptors[race - 43][gender] = true;
        auto const bytes = static_cast<std::uint8_t*>(descriptor);
        auto const modelId = bytes ? *reinterpret_cast<std::uint32_t const*>(bytes + 4) : 0;
        auto const resource = bytes ? *reinterpret_cast<void* const*>(bytes + 8) : nullptr;
        auto const resourceReady = resource ? *static_cast<std::uint8_t const*>(resource) : 0;
        g_api->log(2, "darkfallen-charselect", "descriptor race=%u gender=%u ptr=%p model=%u resource=%p ready=%u",
            race, gender, descriptor, modelId, resource, resourceReady);
        return descriptor;
    }

    void __cdecl CharacterListLoadDetour()
    {
        g_originalCharacterListLoad();
        auto const selected = *reinterpret_cast<std::uint32_t const*>(g_client + kSelectedCharacterIndexOffset);
        auto const characterCount = *reinterpret_cast<std::uint32_t const*>(g_client + kCharacterCountOffset);
        auto const characters = *reinterpret_cast<std::uint8_t* const*>(g_client + kCharacterListOffset);
        if (!characters || selected >= characterCount)
            return;

        auto const character = characters + selected * kCharacterRecordSize;
        auto const race = character[kCharacterRaceOffset];
        auto const gender = character[kCharacterGenderOffset];
        if ((race != 43 && race != 44) || gender > 1 || g_loggedCharacterListLoads[race - 43][gender])
            return;

        g_loggedCharacterListLoads[race - 43][gender] = true;
        auto const model = *reinterpret_cast<void* const*>(character + kCharacterModelOffset);
        auto const renderer = model ? *reinterpret_cast<void* const*>(static_cast<std::uint8_t*>(model) + 0x38) : nullptr;
        g_api->log(2, "darkfallen-charselect", "list-load index=%u race=%u gender=%u model=%p renderer=%p", selected,
            race, gender, model, renderer);
    }

    int __cdecl UpdateSelectionCustomizationSceneDetour()
    {
        ApplyRuntimeCustomizationCounts();
        auto const result = g_originalUpdateSelectionCustomizationScene();
        if (g_loggedCharacterSelectModelSlots)
            return result;

        auto const table = reinterpret_cast<void* const*>(
            *reinterpret_cast<std::uintptr_t const*>(g_client + kCharacterModelTableReferenceOffset));
        auto const selected = *reinterpret_cast<std::uint32_t const*>(g_client + kSelectedCharacterIndexOffset);
        auto const characterCount = *reinterpret_cast<std::uint32_t const*>(g_client + kCharacterCountOffset);
        auto const characters = *reinterpret_cast<std::uint8_t* const*>(g_client + kCharacterListOffset);
        if (!characters || selected >= characterCount)
        {
            if (!g_loggedWaitingForCharacterRecord)
            {
                g_loggedWaitingForCharacterRecord = true;
                g_api->log(2, "darkfallen-charselect", "waiting for selected character: selected=%u count=%u list=%p",
                    selected, characterCount, characters);
            }
            return result;
        }

        g_loggedCharacterSelectModelSlots = true;
        g_api->log(2, "darkfallen-charselect", "model slots: bloodelf=%p/%p darkfallen=%p/%p",
            table[20], table[21], table[86], table[87]);
        for (std::uint32_t index = 0; index < characterCount; ++index)
        {
            auto const character = characters + index * kCharacterRecordSize;
            if (character[kCharacterRaceOffset] != 43 && character[kCharacterRaceOffset] != 44)
                continue;

            g_api->log(2, "darkfallen-charselect", "darkfallen index=%u name=%s race=%u class=%u gender=%u model=%p",
                index, reinterpret_cast<char const*>(character + 8), character[kCharacterRaceOffset],
                character[kCharacterClassOffset], character[kCharacterGenderOffset],
                *reinterpret_cast<void* const*>(character + kCharacterModelOffset));
        }
        return result;
    }
}

extern "C" __declspec(dllexport) WXL_PluginInfo const* __cdecl WXL_Query()
{
    static WXL_PluginInfo const info = {
        sizeof(WXL_PluginInfo),
        kWxlApiVersion,
        "darkfallen-character-select",
        307,
        kWxlClientBuild,
    };
    return &info;
}

extern "C" __declspec(dllexport) int __cdecl WXL_Load(WXL_Api const* api)
{
    auto const client = reinterpret_cast<std::uint8_t*>(GetModuleHandleW(nullptr));
    if (!client)
        return 0;

    g_client = client;
    g_api = api;
    if (!ApplyTwoNamesClientPatch())
        return 0;

    ApplyRuntimeCustomizationCounts();
    return api && api->hookAttach && api->hookAttach("Darkfallen_CycleCharCustomization",
        reinterpret_cast<std::uintptr_t>(client) + kCycleCharCustomizationOffset,
        reinterpret_cast<void*>(&CycleCharCustomizationDetour),
        reinterpret_cast<void**>(&g_originalCycleCharCustomization), 0) && api->hookAttach(
        "Darkfallen_ModelDescriptorProbe",
        reinterpret_cast<std::uintptr_t>(client) + kResolveModelDescriptorOffset,
        reinterpret_cast<void*>(&ResolveModelDescriptorDetour),
        reinterpret_cast<void**>(&g_originalResolveModelDescriptor), 0) && api->hookAttach(
        "Darkfallen_CharacterListLoadProbe",
        reinterpret_cast<std::uintptr_t>(client) + kCharacterListLoadOffset,
        reinterpret_cast<void*>(&CharacterListLoadDetour),
        reinterpret_cast<void**>(&g_originalCharacterListLoad), 0) && api->hookAttach(
        "Darkfallen_CharacterSelectModelProbe",
        reinterpret_cast<std::uintptr_t>(client) + kUpdateSelectionCustomizationSceneOffset,
        reinterpret_cast<void*>(&UpdateSelectionCustomizationSceneDetour),
        reinterpret_cast<void**>(&g_originalUpdateSelectionCustomizationScene), 0);
}
