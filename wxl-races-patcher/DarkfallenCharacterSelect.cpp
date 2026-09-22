// Runtime-only Character Select repair for the Esteria 3.3.5a client.

#include <windows.h>

#include <cstddef>
#include <cstdint>

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

    void SetCustomizationCount(std::uint8_t* customizations, std::size_t race, std::size_t gender,
        std::uint32_t count)
    {
        auto const raceGender = race * 2 + gender;
        auto const entry = reinterpret_cast<std::uint32_t*>(
            customizations + ((raceGender * kCustomizationCategoriesPerRaceGender + kHairCustomizationCategory) *
                kCustomizationEntrySize));
        if (entry[0] >= count)
            entry[0] = count;
    }

    void ApplyDarkfallenHairCounts()
    {
        auto const customizations = *reinterpret_cast<std::uint8_t**>(g_client + kCharacterCustomizationTablePointerOffset);
        if (!customizations)
            return;

        SetCustomizationCount(customizations, 43, 0, 9);
        SetCustomizationCount(customizations, 43, 1, 10);
        SetCustomizationCount(customizations, 44, 0, 9);
        SetCustomizationCount(customizations, 44, 1, 10);
    }

    int __cdecl CycleCharCustomizationDetour(void* lua)
    {
        ApplyDarkfallenHairCounts();
        return g_originalCycleCharCustomization(lua);
    }

    void* __cdecl ResolveModelDescriptorDetour(std::uint32_t race, std::uint32_t gender)
    {
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
