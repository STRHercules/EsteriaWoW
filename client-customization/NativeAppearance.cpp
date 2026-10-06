// Esteria native appearance helpers. Loaded by Wow.exe's permanent import table.
// No WarcraftXL API, loader, events, or runtime patching is used.
#include <windows.h>

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
#include <array>
#include <unordered_map>
#include <random>
#include <algorithm>
#include <string>
#include <memory>
#include <wincodec.h>
#include <wrl/client.h>
#pragma comment(lib, "windowscodecs.lib")
#pragma comment(lib, "ole32.lib")
#include "../src/server/shared/HighmountainAppearance.h"
#include "../src/server/shared/EarthenAppearance.h"
#include "../src/server/shared/HaranirAppearance.h"
#include "../src/server/shared/VulperaAppearance.h"
#include "../src/server/shared/CreatureAppearance.h"

namespace
{
    bool HighmountainGeometry(void* character);
    bool HighmountainCycle(void* state, char const* command);
    bool PreviewAppearance(void* character, char const* command);
    bool dropdownWheelBlocked = false;
}

namespace
{
    FILE* CatalogFile(wchar_t const* name)
    {
        wchar_t path[MAX_PATH] = {};
        if (!GetModuleFileNameW(nullptr, path, MAX_PATH))
            return nullptr;
        wchar_t* slash = std::wcsrchr(path, L'\\');
        if (!slash || slash - path + 1 + std::wcslen(name) >= MAX_PATH)
            return nullptr;
        std::wcscpy(slash + 1, name);
        FILE* file = nullptr;
        return _wfopen_s(&file, path, L"rb") ? nullptr : file;
    }

    struct Option
    {
        std::uint32_t offset;
        std::uint32_t count;
        std::uint32_t factor;
        std::uint32_t geometryOffset;
        std::uint32_t geometryChoices[32];
    };

    struct Profile
    {
        std::uint32_t race;
        std::uint32_t gender;
        std::uint32_t optionCount;
        Option options[16];
    };

    std::vector<Profile> const& Profiles()
    {
        static std::vector<Profile> const profiles = []
        {
            std::vector<Profile> result;
            FILE* file = CatalogFile(L"EsteriaAppearance.bin");
            if (!file)
                return result;
            std::uint32_t header[3] = {};
            if (std::fread(header, sizeof(header), 1, file) != 1 || header[0] != 0x50504145
                || header[1] != 2 || header[2] > 64)
            {
                std::fclose(file);
                return result;
            }
            for (std::uint32_t i = 0; i < header[2]; ++i)
            {
                Profile profile{};
                if (std::fread(&profile, sizeof(profile), 1, file) != 1)
                    break;
                bool valid = profile.race < 64 && profile.gender < 2
                    && profile.optionCount > 0 && profile.optionCount <= 16;
                for (std::uint32_t j = 0; valid && j < profile.optionCount; ++j)
                {
                    auto const& option = profile.options[j];
                    valid = (option.offset == 0x24 || option.offset == 0x28 || option.offset == 0x2C
                        || option.offset == 0x30 || option.offset == 0x34)
                        && option.count && option.factor && option.count <= 256
                        && option.factor <= 256 / option.count
                        && (!option.geometryOffset || (option.count <= 32
                            && option.geometryOffset >= 0x144 && option.geometryOffset < 0x190
                            && option.geometryOffset % 4 == 0));
                }
                if (valid)
                    result.push_back(profile);
            }
            std::fclose(file);
            return result;
        }();
        return profiles;
    }

    template<class T>
    T& Field(void* object, std::size_t offset)
    {
        return *reinterpret_cast<T*>(static_cast<unsigned char*>(object) + offset);
    }

    struct Geometry
    {
        char model[128];
        std::vector<unsigned char> skin;
    };

    struct MaterialSelector
    {
        unsigned offset;
        unsigned factor;
        unsigned count;
        unsigned value;
    };

    struct AppearanceMaterial
    {
        unsigned race;
        unsigned gender;
        unsigned slot;
        MaterialSelector selectors[3];
        char path[128];
    };

    std::vector<AppearanceMaterial> const& AppearanceMaterials()
    {
        static std::vector<AppearanceMaterial> const materials = []
        {
            std::vector<AppearanceMaterial> result;
            FILE* file = CatalogFile(L"EsteriaAppearanceMaterials.bin");
            if (!file)
                return result;
            unsigned header[3] = {};
            if (std::fread(header, sizeof(header), 1, file) == 1 && header[0] == 0x544D4145
                && header[1] == 1 && header[2] <= 4096)
                for (unsigned i = 0; i < header[2]; ++i)
                {
                    AppearanceMaterial material{};
                    if (std::fread(&material, sizeof(material), 1, file) != 1)
                        break;
                    bool valid = material.race == 47 && material.gender < 2
                        && material.slot == 5 && material.path[0]
                        && std::memchr(material.path, 0, sizeof(material.path));
                    for (auto const& selector : material.selectors)
                        valid = valid && (selector.offset == 0x24 || selector.offset == 0x28
                            || selector.offset == 0x30) && selector.factor && selector.count
                            && selector.count <= 256 && selector.factor <= 256 / selector.count
                            && selector.value < selector.count;
                    if (valid)
                        result.push_back(material);
                }
            std::fclose(file);
            return result;
        }();
        return materials;
    }

    bool ValidGeometry(std::vector<unsigned char>& skin)
    {
        if (skin.size() < 48 || Field<unsigned>(skin.data(), 0) != 0x4E494B53)
            return false;
        unsigned const strides[] = {2, 2, 4, 48, 24};
        for (unsigned i = 0; i < 5; ++i)
        {
            unsigned count = Field<unsigned>(skin.data(), 4 + i * 8);
            unsigned offset = Field<unsigned>(skin.data(), 8 + i * 8);
            if (offset > skin.size() || count > (skin.size() - offset) / strides[i])
                return false;
        }
        unsigned vertices = Field<unsigned>(skin.data(), 4);
        unsigned indices = Field<unsigned>(skin.data(), 12);
        unsigned meshes = Field<unsigned>(skin.data(), 28);
        if (!vertices || vertices > 65535 || !indices || !meshes || meshes > 4096)
            return false;
        auto* sections = skin.data() + Field<unsigned>(skin.data(), 32);
        for (unsigned i = 0; i < meshes; ++i)
        {
            auto* section = sections + i * 48;
            unsigned start = Field<std::uint16_t>(section, 8)
                | (Field<std::uint16_t>(section, 2) << 16);
            if (start > indices || Field<std::uint16_t>(section, 10) > indices - start
                || unsigned(Field<std::uint16_t>(section, 4)) + Field<std::uint16_t>(section, 6) > vertices
                || Field<std::uint16_t>(section, 12) > 75)
                return false;
        }
        return true;
    }

    std::vector<Geometry>& Geometries()
    {
        static std::vector<Geometry> geometries = []
        {
            std::vector<Geometry> result;
            FILE* file = CatalogFile(L"EsteriaAppearanceGeometry.bin");
            if (!file)
                return result;
            unsigned header[3] = {};
            if (std::fread(header, sizeof(header), 1, file) == 1 && header[0] == 0x4D474145
                && header[1] == 1 && header[2] <= 64)
                for (unsigned i = 0; i < header[2]; ++i)
                {
                    Geometry geometry{};
                    unsigned length = 0;
                    if (std::fread(geometry.model, sizeof(geometry.model), 1, file) != 1
                        || !std::memchr(geometry.model, 0, sizeof(geometry.model))
                        || std::fread(&length, sizeof(length), 1, file) != 1 || length > 16 * 1024 * 1024)
                        break;
                    geometry.skin.resize(length);
                    if (std::fread(geometry.skin.data(), length, 1, file) != 1 || !ValidGeometry(geometry.skin))
                        break;
                    result.push_back(std::move(geometry));
                }
            std::fclose(file);
            return result;
        }();
        return geometries;
    }

    std::uintptr_t Address(std::uintptr_t preferred)
    {
        return reinterpret_cast<std::uintptr_t>(GetModuleHandleW(nullptr)) + preferred - 0x00400000;
    }

    template<class T>
    T Native(std::uintptr_t preferred)
    {
        return reinterpret_cast<T>(Address(preferred));
    }

    void Refresh(void* character)
    {
        // These are the setters the stock component initializer itself calls.
        Native<void(__thiscall*)(void*, unsigned, int, int)>(0x004EA2F0)(
            character, Field<unsigned>(character, 0x24), 0, 0);
        Native<void(__thiscall*)(void*, unsigned, int, int, int)>(0x004EA6B0)(
            character, Field<unsigned>(character, 0x28), 0, 1, 0);
        Native<void(__thiscall*)(void*, unsigned, int, int)>(0x004EA490)(
            character, Field<unsigned>(character, 0x2C), 0, 0);
        Native<void(__thiscall*)(void*, unsigned, int)>(0x004EA3E0)(
            character, Field<unsigned>(character, 0x34), 0);
        Native<void(__thiscall*)(void*, unsigned, int, int)>(0x004EA590)(
            character, Field<unsigned>(character, 0x30), 0, 0);
        *reinterpret_cast<unsigned*>(Address(0x00B6B18C)) = Field<unsigned>(character, 0x28);
        Native<void(__cdecl*)(void*, int)>(0x004E6AE0)(character, 1);
    }
}

#include "CosmeticWings.inl"

extern "C" __declspec(dllexport) void __cdecl EsteriaSkin(void* model)
{
    if (!model)
        return;
    void* skin = Field<void*>(model, 0x170);
    if (!skin)
        return;
    for (auto& geometry : Geometries())
    {
        if (_stricmp(static_cast<char*>(model) + 0x3C, geometry.model))
            continue;
        // Restore the prepared Wrath arrays if another asset reader parked wide-index meshes.
        // The engine still owns and frees its original profile block. Catalog arrays live until exit.
        for (unsigned i = 0; i < 5; ++i)
        {
            Field<unsigned>(skin, 4 + i * 8) = Field<unsigned>(geometry.skin.data(), 4 + i * 8);
            Field<void*>(skin, 8 + i * 8) = geometry.skin.data()
                + Field<unsigned>(geometry.skin.data(), 8 + i * 8);
        }
        Field<unsigned>(skin, 44) = 75;
        return;
    }
}

extern "C" __declspec(dllexport) void __cdecl EsteriaGeometry(void* character)
{
    if (!character)
        return;
    UpdateCosmeticWing(character);
    if (HighmountainGeometry(character))
        return;
    for (auto const& profile : Profiles())
    {
        if (profile.race != Field<unsigned>(character, 0x18)
            || profile.gender != Field<unsigned>(character, 0x1C))
            continue;
        for (unsigned i = 0; i < profile.optionCount; ++i)
        {
            auto const& option = profile.options[i];
            if (option.geometryOffset)
            {
                unsigned choice = (Field<unsigned>(character, option.offset) / option.factor) % option.count;
                Field<unsigned>(character, option.geometryOffset) = option.geometryChoices[choice];
            }
        }
        if (profile.race == 47 && profile.optionCount == 12)
        {
            auto choice = [&](unsigned index)
            {
                auto const& option = profile.options[index];
                return (Field<unsigned>(character, option.offset) / option.factor) % option.count;
            };
            unsigned modification = choice(7);
            unsigned visor = modification / 4;
            Field<unsigned>(character, 0x148) = choice(4) ? 101 + choice(4) : 100;
            Field<unsigned>(character, 0x150) = 301 + choice(5);
            Field<unsigned>(character, 0x158) = 501 + choice(6);
            Field<unsigned>(character, 0x16C) = 1001 + choice(6);
            Field<unsigned>(character, 0x160) = 702 + modification % 4;
            Field<unsigned>(character, 0x184) = visor ? 1601 + (visor == 4 ? 2 : visor) : 1600;
            Field<unsigned>(character, 0x18C) = visor == 2 ? 1803 : 1800;
            unsigned eye = choice(8);
            unsigned primal = profile.options[8].count - 4;
            Field<unsigned>(character, 0x188) = eye >= primal ? 1702 + eye - primal : eye == 14 ? 1701 : 1700;
            void* instance = Field<void*>(character, 0x38);
            if (instance)
            {
                unsigned boundSlots = 0;
                for (auto const& material : AppearanceMaterials())
                {
                    if (material.gender != profile.gender || (boundSlots & (1u << material.slot)))
                        continue;
                    bool selected = true;
                    for (auto const& selector : material.selectors)
                        selected = selected && (Field<unsigned>(character, selector.offset)
                            / selector.factor) % selector.count == selector.value;
                    if (!selected)
                        continue;
                    // Same load/set/release sequence used by the native extra-head setter.
                    void* texture = Native<void*(__cdecl*)(char const*, void*)>(0x004E8D30)(
                        material.path, reinterpret_cast<void*>(Address(0x00AC46D0)));
                    if (texture)
                    {
                        Native<void(__thiscall*)(void*, unsigned, void*)>(0x00825260)(
                            instance, material.slot, texture);
                        Native<void(__cdecl*)(void*)>(0x0047BF30)(texture);
                    }
                    boundSlots |= 1u << material.slot;
                }
            }
        }
        if (profile.optionCount > 7 && profile.options[2].geometryOffset == 0x184)
        {
            auto const& enabled = profile.options[6];
            auto const& color = profile.options[7];
            unsigned feather = Field<unsigned>(character, 0x184);
            unsigned toggle = (Field<unsigned>(character, enabled.offset) / enabled.factor) % enabled.count;
            unsigned palette = (Field<unsigned>(character, color.offset) / color.factor) % color.count;
            Field<unsigned>(character, 0x184) = feather && toggle ? feather + palette * 100 : 1600;
            void* instance = Field<void*>(character, 0x38);
            if (instance)
                Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(instance, 4000, 4799, 0);
        }
        break;
    }
}

extern "C" __declspec(dllexport) bool __cdecl EsteriaDropdownWheelBlocked()
{
    return dropdownWheelBlocked;
}

namespace
{
    void ScaleVrykulPreview(void* character)
    {
        if (!character || (Field<unsigned>(character, 0x18) != 56 && Field<unsigned>(character, 0x18) != 57))
            return;
        void* instance = Field<void*>(character, 0x38);
        void* model = instance ? Field<void*>(instance, 0x2C) : nullptr;
        if (!model || _strnicmp(static_cast<char*>(model) + 0x3C, "custom\\vrykul\\", 14))
            return;
        auto const* matrix = reinterpret_cast<float const*>(static_cast<unsigned char*>(instance) + 0xB4);
        float current = std::hypot(matrix[0], matrix[1]);
        float position[] = {matrix[12], matrix[13], matrix[14]};
        if (!std::isfinite(current) || current < .001f
            || !std::all_of(std::begin(position), std::end(position), [](float v) { return std::isfinite(v); })
            || std::abs(current - .55f) < .0001f)
            return;
        // Verified 12340 UI placement ABI: position, yaw, uniform scale. Preserve facing and pedestal position.
        Native<void(__thiscall*)(void*, float const*, float, float)>(0x008251D0)(
            instance, position, std::atan2(matrix[1], matrix[0]), .55f);
    }
}

extern "C" __declspec(dllexport) int __cdecl EsteriaCycle(void* state)
{
    auto const isNumber = Native<int(__cdecl*)(void*, int)>(0x0084DF20);
    if (isNumber(state, 1))
        return Native<int(__cdecl*)(void*)>(0x004E0B50)(state);
    auto const getTop = Native<int(__cdecl*)(void*)>(0x0084DBD0);
    auto const number = Native<double(__cdecl*)(void*, int)>(0x0084E030);
    auto const string = Native<char const*(__cdecl*)(void*, int, std::size_t*)>(0x0084E0E0);
    auto const pushNumber = Native<void(__cdecl*)(void*, double)>(0x0084E2A0);
    char const* command = string(state, 1, nullptr);
    if (!command || getTop(state) < 2 || !isNumber(state, 2))
        return 0;
    if (std::strcmp(command, "EA_WHEEL_BLOCK") == 0)
    {
        double active = number(state, 2);
        if (active == 0 || active == 1)
            dropdownWheelBlocked = active == 1;
        return 0;
    }
    if (std::strcmp(command, "EA_SELECT") == 0)
    {
        double index = number(state, 2);
        unsigned count = *reinterpret_cast<unsigned*>(Address(0x00B6B23C));
        auto* rows = *reinterpret_cast<unsigned char**>(Address(0x00B6B240));
        if (!rows || count > 100 || !std::isfinite(index) || index < 1 || index > count
            || index != std::floor(index))
            return 0;
        auto* row = rows + (static_cast<unsigned>(index) - 1) * 0x198;
        pushNumber(state, row[0x178]);
        pushNumber(state, row[0x17A]);
        return 2;
    }
    if (std::strcmp(command, "EA_PREVIEW_SCALE") == 0)
    {
        double index = number(state, 2);
        if (!std::isfinite(index) || index < 0 || index > 100 || index != std::floor(index))
            return 0;
        if (index == 0)
            ScaleVrykulPreview(*reinterpret_cast<void**>(Address(0x00B6B1A0)));
        else
        {
            unsigned count = *reinterpret_cast<unsigned*>(Address(0x00B6B23C));
            auto* rows = *reinterpret_cast<unsigned char**>(Address(0x00B6B240));
            if (rows && count <= 100 && index <= count)
                ScaleVrykulPreview(Field<void*>(rows + (static_cast<unsigned>(index) - 1) * 0x198, 0x188));
        }
        return 0;
    }
    void* character = *reinterpret_cast<void**>(Address(0x00B6B1A0));
    if (!character)
        return 0;
    if (std::strcmp(command, "EA_PREVIEW_SAVE") == 0 || std::strcmp(command, "EA_PREVIEW_RESTORE") == 0
        || std::strcmp(command, "EA_PREVIEW_END") == 0)
    {
        pushNumber(state, PreviewAppearance(character, command) ? 1 : 0);
        return 1;
    }
    if (std::strcmp(command, "EA_SET") == 0 && (getTop(state) != 3 || !isNumber(state, 3)))
        return 0;
    if (std::strcmp(command, "EA_STOCK_GET") == 0 || std::strcmp(command, "EA_STOCK_CHOICES") == 0)
    {
        double requested = number(state, 2);
        unsigned race = Field<unsigned>(character, 0x18);
        unsigned gender = Field<unsigned>(character, 0x1C);
        if (!std::isfinite(requested) || requested < 1 || requested > 5
            || requested != std::floor(requested) || race >= 64 || gender > 1)
            return 0;
        unsigned index = static_cast<unsigned>(requested) - 1;
        constexpr unsigned offsets[] = {0x28, 0x2C, 0x34, 0x24, 0x30};
        constexpr unsigned categories[] = {0, 1, 3, 3, 2};
        void* table = *reinterpret_cast<void**>(Address(0x00B6B864));
        if (!table)
            return 0;
        auto variations = Native<unsigned(__cdecl*)(void*, unsigned, unsigned, unsigned)>(0x004F3AE0);
        auto colors = Native<unsigned(__cdecl*)(void*, unsigned, unsigned, unsigned, unsigned)>(0x004F3B10);
        auto section = Native<unsigned const*(__cdecl*)(void*, unsigned, unsigned, unsigned,
            unsigned, unsigned, bool*)>(0x004F3BA0);
        unsigned flags = Native<unsigned(__cdecl*)(unsigned, unsigned)>(0x004F3A40)(
            0, Field<unsigned>(character, 0x20));
        auto allowed = [&](unsigned category, unsigned variation, unsigned color)
        {
            auto row = section(table, race, gender, category, variation, color, nullptr);
            return row && Native<bool(__cdecl*)(unsigned, unsigned)>(0x004F39A0)(row[7], flags);
        };
        unsigned category = categories[index];
        unsigned style = Field<unsigned>(character, 0x34);
        bool texturedFeature = false;
        if (index == 4)
            section(table, race, gender, 2, Field<unsigned>(character, 0x30),
                Field<unsigned>(character, 0x24), &texturedFeature);
        auto featureCounts = *reinterpret_cast<unsigned**>(Address(0x00B6B860));
        unsigned count = index == 0 ? colors(table, race, gender, 0, 0)
            : index == 3 ? colors(table, race, gender, 3, style)
            : index == 4 && !texturedFeature ? (featureCounts ? featureCounts[race * 2 + gender] : 0)
            : variations(table, race, gender, category);
        if (count > 256)
            return 0;
        if (std::strcmp(command, "EA_STOCK_GET") == 0)
        {
            pushNumber(state, Field<unsigned>(character, offsets[index]));
            pushNumber(state, count);
            return 2;
        }
        std::string choices;
        for (unsigned value = 0; value < count; ++value)
        {
            bool valid = index == 4 && !texturedFeature;
            if (index == 0)
                valid = allowed(0, 0, value) && allowed(1, Field<unsigned>(character, 0x2C), value);
            else if (index == 3)
                valid = allowed(3, style, value);
            else if (!valid)
                for (unsigned color = 0, total = (std::min)(colors(table, race, gender, category, value), 256u);
                    color < total && !valid; ++color)
                    valid = allowed(category, value, color);
            if (valid)
                choices += std::to_string(value) + ",";
        }
        Native<void(__cdecl*)(void*, char const*)>(0x0084E350)(state, choices.c_str());
        return 1;
    }
    if (HighmountainCycle(state, command))
        return std::strcmp(command, "EA_GET") == 0 ? 3 : std::strcmp(command, "EA_CHOICES") == 0 ? 1 : 0;
    Profile const* profile = nullptr;
    for (auto const& candidate : Profiles())
        if (candidate.race == Field<unsigned>(character, 0x18)
            && candidate.gender == Field<unsigned>(character, 0x1C))
        {
            profile = &candidate;
            break;
        }
    double requested = number(state, 2);
    if (!profile || !std::isfinite(requested) || requested < 1 || requested > profile->optionCount
        || requested != std::floor(requested))
        return 0;
    auto const& option = profile->options[static_cast<unsigned>(requested) - 1];
    unsigned& encoded = Field<unsigned>(character, option.offset);
    unsigned const value = (encoded / option.factor) % option.count;
    if (std::strcmp(command, "EA_GET") == 0)
    {
        pushNumber(state, value);
        pushNumber(state, option.count);
        return 2;
    }
    if (std::strcmp(command, "EA_CHOICES") == 0)
    {
        std::string choices;
        for (unsigned i = 0; i < option.count; ++i)
            choices += std::to_string(i) + ",";
        Native<void(__cdecl*)(void*, char const*)>(0x0084E350)(state, choices.c_str());
        return 1;
    }
    bool direct = std::strcmp(command, "EA_SET") == 0;
    if ((!direct && std::strcmp(command, "EA_CYCLE") != 0) || getTop(state) != 3 || !isNumber(state, 3))
        return 0;
    double delta = number(state, 3);
    if (direct ? (!std::isfinite(delta) || delta < 0 || delta >= option.count || delta != std::floor(delta))
        : (delta != 1 && delta != -1))
        return 0;
    unsigned const next = direct ? static_cast<unsigned>(delta)
        : (value + option.count + static_cast<int>(delta)) % option.count;
    unsigned const replacement = encoded - value * option.factor + next * option.factor;
    if (replacement > 255)
        return 0;
    encoded = replacement;
    Refresh(character);
    return 0;
}

extern "C" __declspec(dllexport) unsigned __cdecl EsteriaSkillRace(unsigned race)
{
    // Match the server's legacy eligibility masks without changing character identity.
    switch (race)
    {
        case 45: return 2;
        case 46: return 6;
        case 47: return 7;
        case 48: return 3;
        case 49: return 2;
        case 50: return 4;
        case 51: return 8;
        case 52: return 13;
        case 53: return 10;
        case 54: return 10;
        case 55: return 3;
        case 56:
        case 58: return 1;
        case 57:
        case 59: return 2;
        case 60: return 2;
        case 61: return 4;
        default: return race;
    }
}


extern "C" __declspec(dllexport) std::uint32_t __cdecl EsteriaWideSource(void const* section, void const* skin)
{
    if (!section)
        return 0;
    auto const* data = static_cast<unsigned char const*>(section);
    std::uint32_t const low = *reinterpret_cast<std::uint16_t const*>(data + 8);
    std::uint32_t const high = *reinterpret_cast<std::uint16_t const*>(data + 2);
    std::uint32_t const count = *reinterpret_cast<std::uint16_t const*>(data + 10);
    std::uint32_t const wide = (high << 16) | low;
    if (skin)
    {
        std::uint32_t const total = *reinterpret_cast<std::uint32_t const*>(
            static_cast<unsigned char const*>(skin) + 0x0C);
        if (wide <= total && count <= total - wide)
            return wide;
    }
    return low;
}

extern "C" __declspec(dllexport) std::uint32_t __cdecl EsteriaDrawStart(void const* section, void* context)
{
    void* instance = context ? Field<void*>(context, 0x60) : nullptr;
    void* model = instance ? Field<void*>(instance, 0x2C) : nullptr;
    void* skin = model ? Field<void*>(model, 0x170) : nullptr;
    return EsteriaWideSource(section, skin);
}

namespace
{
    bool ExtendedRace(unsigned race)
    {
        return race == 20 || race == 46 || race == 48 || race == 49 || race == 50 || race == 51
            || CreatureAppearance::Uses(race);
    }

    bool ValidateExtended(unsigned race, unsigned gender, std::array<std::uint8_t, 13> const& fields)
    {
        if (CreatureAppearance::Uses(race))
        {
            std::array<std::uint8_t, 5> appearance{};
            std::copy_n(fields.begin(), appearance.size(), appearance.begin());
            return std::all_of(fields.begin() + 5, fields.end(), [](std::uint8_t value) { return value == 0; })
                && CreatureAppearance::Validate(race, gender, appearance);
        }
        if (race == 20)
        {
            std::array<std::uint8_t, 5> vulpera{};
            std::copy_n(fields.begin(), vulpera.size(), vulpera.begin());
            return std::all_of(fields.begin() + 5, fields.end(), [](std::uint8_t value) { return value == 0; })
                && VulperaAppearance::Validate(gender, vulpera);
        }
        if (race == 50 || race == 51)
            return HaranirAppearance::Validate(gender, fields);
        std::array<std::uint8_t, 6> legacy{};
        std::copy_n(fields.begin(), legacy.size(), legacy.begin());
        return std::all_of(fields.begin() + 6, fields.end(), [](std::uint8_t value) { return value == 0; })
            && (race == 46 ? HighmountainAppearance::Validate(gender, legacy)
                : EarthenAppearance::Validate(gender, legacy));
    }

    std::unordered_map<void*, std::array<std::uint8_t, 13>> earthenNetworkAppearance;

    void CaptureEarthenAppearance(void* character, unsigned char const* network, std::uint64_t extra)
    {
        unsigned race = Field<unsigned>(character, 0x18);
        if ((race != 20 && race != 48 && race != 49 && race != 50 && race != 51
            && !CreatureAppearance::Uses(race)) || !network)
            return;
        std::array<std::uint8_t, 13> values{};
        std::memcpy(values.data(), network, 5);
        for (unsigned i = 0; i < 8; ++i)
            values[5 + i] = race == 20 || CreatureAppearance::Uses(race) ? 0
                : static_cast<std::uint8_t>(extra >> (i * 8));
        if (!ValidateExtended(race, Field<unsigned>(character, 0x1C), values))
            return;
        earthenNetworkAppearance[character] = values;
    }

    std::uint64_t UnitAppearanceExtra(void* unit)
    {
        auto* fields = Field<unsigned char*>(unit, 0xD0);
        if (!fields)
            return 0;
        std::uint64_t extra = Field<unsigned>(fields, 0x8D * 4);
        void* character = Field<void*>(unit, 0xB4C);
        if (Field<unsigned>(unit, 0x14) == 4 && character
            && (Field<unsigned>(character, 0x18) == 50 || Field<unsigned>(character, 0x18) == 51))
        {
            auto* objectFields = Field<unsigned char*>(unit, 8);
            if (objectFields)
                extra |= std::uint64_t{Field<unsigned>(objectFields, 5 * 4)} << 32;
        }
        return extra;
    }

    void CaptureEarthenOwner(void* character)
    {
        auto* connection = *reinterpret_cast<unsigned char**>(Address(0x00C79CE0));
        if (!connection)
            return;
        auto* manager = Field<unsigned char*>(connection, 0x2ED0);
        if (!manager)
            return;
        auto* unit = Field<unsigned char*>(manager, 0xAC);
        // ponytail: bounded owner lookup during dirty component rebuilds; index by GUID if profiling warrants it.
        for (unsigned i = 0; unit && !(reinterpret_cast<std::uintptr_t>(unit) & 1) && i < 4096; ++i)
        {
            if (Field<unsigned>(unit, 0x14) == 4 && Field<void*>(unit, 0xB4C) == character)
            {
                auto* playerData = Field<unsigned char*>(unit, 0x1008);
                auto* fields = Field<unsigned char*>(unit, 0xD0);
                if (playerData && fields)
                    CaptureEarthenAppearance(character, playerData + 0x14, UnitAppearanceExtra(unit));
                return;
            }
            unit = Field<unsigned char*>(unit, 0x3C);
        }
    }

    std::unordered_map<void*, std::uint64_t> highmountainExtra;
    std::unordered_map<std::uint64_t, std::uint64_t> highmountainRoster;
    thread_local void* highmountainContext = nullptr;
    constexpr unsigned appearanceOffsets[] = {0x28, 0x2C, 0x34, 0x24, 0x30};

    std::array<std::uint8_t, 13> HighmountainFields(void* character)
    {
        std::array<std::uint8_t, 13> result{};
        for (unsigned i = 0; i < 5; ++i)
            result[i] = static_cast<std::uint8_t>(Field<unsigned>(character, appearanceOffsets[i]));
        auto it = highmountainExtra.find(character);
        std::uint64_t extra = it == highmountainExtra.end() ? 0 : it->second;
        for (unsigned i = 0; i < 8; ++i)
            result[5 + i] = Field<unsigned>(character, 0x18) == 20
                || CreatureAppearance::Uses(Field<unsigned>(character, 0x18)) ? 0
                : static_cast<std::uint8_t>(extra >> (i * 8));
        return result;
    }

    void SetHighmountainFields(void* character, std::array<std::uint8_t, 13> const& values)
    {
        for (unsigned i = 0; i < 5; ++i)
            Field<unsigned>(character, appearanceOffsets[i]) = values[i];
        highmountainExtra[character] = HaranirAppearance::Extra(values);
    }

    bool PreviewAppearance(void* character, char const* command)
    {
        // Character Create owns one model; keep its complete packed appearance for transient hovers.
        static void* owner = nullptr;
        static unsigned race = 0, gender = 0, characterClass = 0;
        static std::array<std::uint8_t, 13> saved{};
        if (std::strcmp(command, "EA_PREVIEW_END") == 0)
        {
            owner = nullptr;
            return true;
        }
        if (std::strcmp(command, "EA_PREVIEW_SAVE") == 0)
        {
            owner = character;
            race = Field<unsigned>(character, 0x18);
            gender = Field<unsigned>(character, 0x1C);
            characterClass = Field<unsigned>(character, 0x20);
            saved = HighmountainFields(character);
            return true;
        }
        if (owner != character || race != Field<unsigned>(character, 0x18)
            || gender != Field<unsigned>(character, 0x1C) || characterClass != Field<unsigned>(character, 0x20))
            return false;
        SetHighmountainFields(character, saved);
        Refresh(character);
        return true;
    }

    // Explicit descriptor/rule tables come from the pinned Retail choices; version-2 profiles stay intact.
    template<class Options, class Labels, class Requirements>
    bool HighmountainControl(void* state, char const* command, void* character, Options const& options,
        Labels const& labels, Requirements const& requirements)
    {
        auto const number = Native<double(__cdecl*)(void*, int)>(0x0084E030);
        auto const pushNumber = Native<void(__cdecl*)(void*, double)>(0x0084E2A0);
        auto const pushString = Native<void(__cdecl*)(void*, char const*)>(0x0084E350);
        double requested = number(state, 2);
        if (!std::isfinite(requested) || requested < 1 || requested > options.size()
            || requested != std::floor(requested))
        {
            if (std::strcmp(command, "EA_GET") == 0)
            {
                pushNumber(state, 0);
                pushNumber(state, 1);
                pushString(state, "");
            }
            else if (std::strcmp(command, "EA_CHOICES") == 0)
                pushString(state, "");
            return true;
        }
        unsigned index = static_cast<unsigned>(requested) - 1;
        auto fields = HighmountainFields(character);
        unsigned race = Field<unsigned>(character, 0x18);
        unsigned gender = Field<unsigned>(character, 0x1C);
        unsigned characterClass = Field<unsigned>(character, 0x20);
        auto normalize = [&](std::array<std::uint8_t, 13>& values)
        {
            if (race != 20)
                return;
            std::array<std::uint8_t, 5> vulpera{};
            std::copy_n(values.begin(), vulpera.size(), vulpera.begin());
            vulpera = VulperaAppearance::Normalize(gender, characterClass, vulpera);
            std::copy(vulpera.begin(), vulpera.end(), values.begin());
        };
        auto allowed = [&](std::array<std::uint8_t, 13> const& values)
        {
            if (!ValidateExtended(race, gender, values))
                return false;
            if (race != 20)
                return true;
            std::array<std::uint8_t, 5> vulpera{};
            std::copy_n(values.begin(), vulpera.size(), vulpera.begin());
            return VulperaAppearance::ValidateClass(gender, characterClass, vulpera);
        };
        auto original = fields;
        normalize(fields);
        if (fields != original)
        {
            SetHighmountainFields(character, fields);
            Refresh(character);
        }
        if (std::strcmp(command, "EA_RANDOM") == 0)
        {
            static std::mt19937 random(GetTickCount());
            fields = {};
            normalize(fields);
            for (unsigned i = 0; i < options.size(); ++i)
            {
                auto const& descriptor = options[i];
                unsigned first = std::uniform_int_distribution<unsigned>(0, descriptor.count - 1)(random);
                for (unsigned attempt = 0; attempt < descriptor.count; ++attempt)
                {
                    auto candidate = fields;
                    unsigned value = (first + attempt) % descriptor.count;
                    unsigned prior = candidate[descriptor.field] / descriptor.factor % descriptor.count;
                    candidate[descriptor.field] = static_cast<std::uint8_t>(
                        candidate[descriptor.field] - prior * descriptor.factor + value * descriptor.factor);
                    if (allowed(candidate))
                    {
                        fields = candidate;
                        break;
                    }
                }
            }
            SetHighmountainFields(character, fields);
            Refresh(character);
            return true;
        }
        auto const& option = options[index];
        unsigned value = (fields[option.field] / option.factor) % option.count;
        if (std::strcmp(command, "EA_GET") == 0)
        {
            pushNumber(state, value);
            unsigned count = option.count;
            if (race == 20 && index == 9)
            {
                auto candidate = fields;
                candidate[option.field] = static_cast<std::uint8_t>(candidate[option.field] - value * option.factor
                    + option.factor);
                if (!allowed(candidate))
                    count = 1;
            }
            pushNumber(state, count);
            pushString(state, labels[index]);
            return true;
        }
        bool choices = std::strcmp(command, "EA_CHOICES") == 0;
        bool direct = std::strcmp(command, "EA_SET") == 0;
        if (!choices && !direct && std::strcmp(command, "EA_CYCLE") != 0)
            return true;
        double direction = choices ? 1 : number(state, 3);
        if (direct ? (!std::isfinite(direction) || direction < 0 || direction >= option.count
            || direction != std::floor(direction)) : (direction != 1 && direction != -1))
            return true;
        std::string available;
        for (unsigned step = 1; step <= (direct ? 1u : option.count); ++step)
        {
            unsigned next = choices ? step - 1 : direct ? static_cast<unsigned>(direction)
                : static_cast<unsigned>((static_cast<int>(value) + static_cast<int>(option.count) * 2
                    + static_cast<int>(step) * static_cast<int>(direction)) % static_cast<int>(option.count));
            auto candidate = fields;
            candidate[option.field] = static_cast<std::uint8_t>(
                candidate[option.field] - value * option.factor + next * option.factor);
            // Changing a prerequisite resets incompatible dependent accessories to their authored default.
            for (unsigned pass = 0; pass < options.size(); ++pass)
                for (auto const& rule : requirements)
                {
                    auto const& selected = options[rule.option];
                    auto const& required = options[rule.required];
                    unsigned dependent = (candidate[selected.field] / selected.factor) % selected.count;
                    unsigned prerequisite = (candidate[required.field] / required.factor) % required.count;
                    if (rule.option != index && dependent == rule.value
                        && !(rule.mask & (std::uint64_t{1} << prerequisite)))
                        candidate[selected.field] -= static_cast<std::uint8_t>(dependent * selected.factor);
                }
            if (!allowed(candidate))
                continue;
            if (choices)
            {
                available += std::to_string(next) + ",";
                continue;
            }
            SetHighmountainFields(character, candidate);
            Refresh(character);
            break;
        }
        if (choices)
            pushString(state, available.c_str());
        return true;
    }

    bool HighmountainCycle(void* state, char const* command)
    {
        void* character = *reinterpret_cast<void**>(Address(0x00B6B1A0));
        if (!character || !ExtendedRace(Field<unsigned>(character, 0x18)))
            return false;
        if (Field<unsigned>(character, 0x18) == 54)
        {
            constexpr std::array<char const*, 5> maleLabels =
                {"Skin Color", "Face", "Crest Style", "Eye Color", "Facial Features"};
            constexpr std::array<char const*, 5> femaleLabels =
                {"Skin Color", "Face", "Hair Style", "Hair Color", "Facial Features"};
            constexpr std::array<VulperaAppearance::Requirement, 0> requirements{};
            unsigned gender = Field<unsigned>(character, 0x1C);
            return HighmountainControl(state, command, character, CreatureAppearance::Options(54, gender),
                gender ? femaleLabels : maleLabels, requirements);
        }
        if (CreatureAppearance::Uses(Field<unsigned>(character, 0x18)))
            return false;
        if (Field<unsigned>(character, 0x18) == 20)
        {
            if (Field<unsigned>(character, 0x1C) == 0)
                return HighmountainControl(state, command, character, VulperaAppearance::MaleOptions,
                    VulperaAppearance::MaleLabels, VulperaAppearance::MaleRequirements);
            return HighmountainControl(state, command, character, VulperaAppearance::FemaleOptions,
                VulperaAppearance::FemaleLabels, VulperaAppearance::FemaleRequirements);
        }
        if (Field<unsigned>(character, 0x18) == 50 || Field<unsigned>(character, 0x18) == 51)
        {
            if (Field<unsigned>(character, 0x1C) == 0)
                return HighmountainControl(state, command, character, HaranirAppearance::MaleOptions,
                    HaranirAppearance::MaleLabels, HaranirAppearance::MaleRequirements);
            return HighmountainControl(state, command, character, HaranirAppearance::FemaleOptions,
                HaranirAppearance::FemaleLabels, HaranirAppearance::FemaleRequirements);
        }
        if (Field<unsigned>(character, 0x18) != 46)
        {
            if (Field<unsigned>(character, 0x1C) == 0)
                return HighmountainControl(state, command, character, EarthenAppearance::MaleOptions,
                    EarthenAppearance::MaleLabels, EarthenAppearance::MaleRequirements);
            return HighmountainControl(state, command, character, EarthenAppearance::FemaleOptions,
                EarthenAppearance::FemaleLabels, EarthenAppearance::FemaleRequirements);
        }
        if (Field<unsigned>(character, 0x1C) == 0)
            return HighmountainControl(state, command, character, HighmountainAppearance::MaleOptions,
                HighmountainAppearance::MaleLabels, HighmountainAppearance::MaleRequirements);
        return HighmountainControl(state, command, character, HighmountainAppearance::FemaleOptions,
            HighmountainAppearance::FemaleLabels, HighmountainAppearance::FemaleRequirements);
    }

    struct HighmountainSelection
    {
        unsigned gender;
        unsigned kind; // 0: geometry group, 1: replaceable material
        unsigned target;
        unsigned value;
        unsigned choices[3]; // {option, value} packed as two uint16s; 0xffffffff means unconditional
        char path[128];
    };

    std::vector<HighmountainSelection> ReadSelections(wchar_t const* name)
    {
        return [name]
        {
            std::vector<HighmountainSelection> result;
            FILE* file = CatalogFile(name);
            if (!file)
                return result;
            unsigned header[3] = {};
            if (std::fread(header, sizeof(header), 1, file) == 1 && header[0] == 0x314D4845
                && header[1] == 1 && header[2] <= 16384)
                for (unsigned i = 0; i < header[2]; ++i)
                {
                    HighmountainSelection record{};
                    if (std::fread(&record, sizeof(record), 1, file) != 1)
                        break;
                    bool valid = record.gender < 2 && record.kind <= 4
                        && (record.kind == 4 ? record.target && record.value < 52
                            : record.kind == 3 ? record.target < 9 && record.value >= 16
                            && std::memchr(record.path, 0, sizeof(record.path))
                            : record.kind == 2 ? record.target < 5200 && record.value >= 10000
                            && record.value < 30000 : record.kind ? record.target < 16 && record.path[0]
                            && std::memchr(record.path, 0, sizeof(record.path)) : record.target < 52
                            && record.value >= record.target * 100 && record.value < record.target * 100 + 100);
                    for (unsigned selector : record.choices)
                        valid = valid && (selector == 0xffffffff || (selector & 0xffff) < 32
                            && (selector >> 16) < 256);
                    if (valid)
                        result.push_back(record);
                }
            std::fclose(file);
            return result;
        }();
    }

    std::vector<HighmountainSelection> const& HighmountainSelections()
    {
        static auto const records = ReadSelections(L"EsteriaHighmountain.bin");
        return records;
    }

    std::vector<HighmountainSelection> const& EarthenSelections()
    {
        static auto const records = ReadSelections(L"EsteriaEarthen.bin");
        return records;
    }

    std::vector<HighmountainSelection> const& HaranirSelections()
    {
        static auto const records = ReadSelections(L"EsteriaHaranir.bin");
        return records;
    }

    std::vector<HighmountainSelection> const& VulperaSelections()
    {
        static auto const records = ReadSelections(L"EsteriaVulpera.bin");
        return records;
    }

    std::vector<HighmountainSelection> const& RetailSelections(unsigned race)
    {
        static auto const naga = ReadSelections(L"EsteriaNaga.bin");
        static auto const tuskarr = ReadSelections(L"EsteriaTuskarr.bin");
        static auto const vrykul = ReadSelections(L"EsteriaVrykul.bin");
        static auto const human = ReadSelections(L"EsteriaThinHuman.bin");
        switch (race)
        {
            case 54: return naga;
            case 55: return tuskarr;
            case 56:
            case 57: return vrykul;
            case 58:
            case 59: return human;
            case 20: return VulperaSelections();
            default: return HaranirSelections();
        }
    }

    wchar_t const* RetailTextureBank(unsigned race)
    {
        switch (race)
        {
            case 54: return L"EsteriaNagaTextures.bin";
            case 55: return L"EsteriaTuskarrTextures.bin";
            case 56:
            case 57: return L"EsteriaVrykulTextures.bin";
            case 58:
            case 59: return L"EsteriaThinHumanTextures.bin";
            case 20: return L"EsteriaVulperaTextures.bin";
            default: return L"EsteriaHaranirTextures.bin";
        }
    }

    char const* RetailCacheFamily(unsigned race)
    {
        switch (race)
        {
            case 54: return "Naga";
            case 55: return "Tuskarr";
            case 56:
            case 57: return "Vrykul";
            case 58:
            case 59: return "ThinHuman";
            case 20: return "Vulpera";
            default: return "Haranir";
        }
    }

#include "HaranirMaterials.inl"

    template<class Options>
    bool ExtendedGeometry(void* character, Options const& options,
        std::vector<HighmountainSelection> const& records)
    {
        unsigned gender = Field<unsigned>(character, 0x1C);
        auto const network = earthenNetworkAppearance.find(character);
        if (network != earthenNetworkAppearance.end())
            SetHighmountainFields(character, network->second);
        auto fields = HighmountainFields(character);
        if (!ValidateExtended(Field<unsigned>(character, 0x18), gender, fields))
        {
            fields = {};
            SetHighmountainFields(character, fields);
        }
        void* instance = Field<void*>(character, 0x38);
        if (!instance)
            return true;
        unsigned materials = 0;
        std::uint64_t helmetGroups = 0;
        if (Field<unsigned>(character, 0x18) == 20 || Field<unsigned>(character, 0x18) == 54)
            for (auto const& record : records)
                if (record.kind == 4 && record.gender == gender && record.value < 52
                    && record.target == Field<unsigned>(character, 0x428))
                    helmetGroups |= std::uint64_t{1} << record.value;
        std::uint64_t geometryGroups = 0;
        unsigned selectedGeosets[52] = {};
        Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(instance, 10000, 29999, 0);
        for (auto const& record : records)
        {
            if (record.gender != gender || record.kind >= 3)
                continue;
            bool selected = true;
            for (unsigned selector : record.choices)
            {
                if (selector == 0xffffffff)
                    continue;
                unsigned index = selector & 0xffff;
                if (index >= options.size())
                {
                    selected = false;
                    break;
                }
                auto const& option = options[index];
                selected = selected && (fields[option.field] / option.factor) % option.count == selector >> 16;
            }
            if (!selected)
                continue;
            if (record.kind == 2)
            {
                unsigned group = record.target / 100;
                unsigned source = group < 19 ? Field<unsigned>(character, 0x144 + group * 4)
                    : selectedGeosets[group];
                if (record.target == 0 || source == record.target)
                    Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(
                        instance, record.value, record.value, 1);
                continue;
            }
            if (!record.kind)
            {
                if (geometryGroups & (std::uint64_t{1} << record.target))
                    continue;
                geometryGroups |= std::uint64_t{1} << record.target;
                unsigned selectedValue = record.value;
                if (helmetGroups & (std::uint64_t{1} << record.target))
                    selectedValue = record.target * 100;
                unsigned race = Field<unsigned>(character, 0x18);
                if (record.target == 20 && (race == 48 || race == 49 || race == 50 || race == 51
                    || race == 56 || race == 57))
                    // Native equipment slot7 (Feet) maps to component visual slot6 at 0x428 + 6*4.
                    selectedValue = Field<unsigned>(character, 0x440) ? 2002
                        : (race == 50 || race == 51 ? record.value : 2001);
                selectedGeosets[record.target] = selectedValue;
                if (record.target < 19)
                    Field<unsigned>(character, 0x144 + record.target * 4) = selectedValue;
                else
                {
                    Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(
                        instance, record.target * 100, record.target * 100 + 99, 0);
                    Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(
                        instance, selectedValue, selectedValue, 1);
                }
            }
            else if (!(materials & (1u << record.target)))
            {
                void* texture = Native<void*(__cdecl*)(char const*, void*)>(0x004E8D30)(
                    record.path, reinterpret_cast<void*>(Address(0x00AC46D0)));
                if (texture)
                {
                    Native<void(__thiscall*)(void*, unsigned, void*)>(0x00825260)(instance, record.target, texture);
                    Native<void(__cdecl*)(void*)>(0x0047BF30)(texture);
                }
                materials |= 1u << record.target;
            }
        }
        // Some source-hidden groups have no customization selector. Apply their hide after all selections.
        for (unsigned group = 0; group < 52; ++group)
            if (helmetGroups & (std::uint64_t{1} << group))
            {
                if (group < 19)
                    Field<unsigned>(character, 0x144 + group * 4) = group * 100;
                Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(
                    instance, group * 100, group * 100 + 99, 0);
            }
        return true;
    }

    bool HighmountainGeometry(void* character)
    {
        unsigned race = Field<unsigned>(character, 0x18);
        if (!ExtendedRace(race))
            return false;
        if (race != 46 && Field<void*>(character, 0x38))
            CaptureEarthenOwner(character);
        if (CreatureAppearance::Uses(race))
        {
            SetHaranirMaterials(character);
            return ExtendedGeometry(character, CreatureAppearance::Options(race, Field<unsigned>(character, 0x1C)),
                RetailSelections(race));
        }
        if (race == 20)
        {
            SetHaranirMaterials(character);
            if (Field<unsigned>(character, 0x1C) == 0)
                return ExtendedGeometry(character, VulperaAppearance::MaleOptions, VulperaSelections());
            return ExtendedGeometry(character, VulperaAppearance::FemaleOptions, VulperaSelections());
        }
        if (race == 50 || race == 51)
        {
            SetHaranirMaterials(character);
            if (Field<unsigned>(character, 0x1C) == 0)
                return ExtendedGeometry(character, HaranirAppearance::MaleOptions, HaranirSelections());
            return ExtendedGeometry(character, HaranirAppearance::FemaleOptions, HaranirSelections());
        }
        if (race == 46)
        {
            if (Field<unsigned>(character, 0x1C) == 0)
                return ExtendedGeometry(character, HighmountainAppearance::MaleOptions, HighmountainSelections());
            return ExtendedGeometry(character, HighmountainAppearance::FemaleOptions, HighmountainSelections());
        }
        if (Field<unsigned>(character, 0x1C) == 0)
            return ExtendedGeometry(character, EarthenAppearance::MaleOptions, EarthenSelections());
        return ExtendedGeometry(character, EarthenAppearance::FemaleOptions, EarthenSelections());
    }
}

extern "C" __declspec(dllexport) void __cdecl EsteriaCreateExtra(void* packet)
{
    void* character = *reinterpret_cast<void**>(Address(0x00B6B1A0));
    if (!packet || !character || !ExtendedRace(Field<unsigned>(character, 0x18))
        || Field<unsigned>(character, 0x18) == 20 || CreatureAppearance::Uses(Field<unsigned>(character, 0x18)))
        return;
    unsigned size = Field<unsigned>(packet, 0x10);
    unsigned base = Field<unsigned>(packet, 8);
    if (!size || size < base || size - base > Field<unsigned>(packet, 0x0C))
        return;
    auto* bytes = Field<unsigned char*>(packet, 4);
    auto fields = HighmountainFields(character);
    unsigned race = Field<unsigned>(character, 0x18);
    bytes[size - base - 1] = race == 50 || race == 51 ? 0 : fields[5];
    if (race == 50 || race == 51)
    {
        auto const append = Native<void(__thiscall*)(void*, unsigned)>(0x0047AFE0);
        for (unsigned i = 5; i < fields.size(); ++i)
            append(packet, fields[i]);
        for (unsigned i = 0; i < 4; ++i)
            append(packet, (0x31435248 >> (i * 8)) & 255);
    }
}

extern "C" __declspec(dllexport) void __cdecl EsteriaEnumExtra(void* packet)
{
    highmountainRoster.clear();
    cosmeticWingRoster.clear();
    if (!packet)
        return;
    unsigned length = Field<unsigned>(packet, 0x10);
    unsigned base = Field<unsigned>(packet, 8);
    if (length < base || length - base < 8 || length - base > Field<unsigned>(packet, 0x0C))
        return;
    auto* bytes = Field<unsigned char*>(packet, 4);
    unsigned size = length - base;
    if (!bytes)
        return;
    for (unsigned tail = 0; tail < 3 && size >= 8; ++tail)
    {
        unsigned magic = Field<unsigned>(bytes, size - 4);
        unsigned stride = magic == 0x31455848 ? 9 : magic == 0x32455848 ? 16 : magic == 0x31475743 ? 12 : 0;
        if (!stride)
            break;
        unsigned count = Field<unsigned>(bytes, size - 8);
        if (count > 100 || count > (size - 8) / stride)
            break;
        unsigned start = size - 8 - count * stride;
        for (unsigned i = 0; i < count; ++i)
        {
            auto guid = Field<std::uint64_t>(bytes, start + i * stride);
            if (stride == 12)
                cosmeticWingRoster[guid] = Field<unsigned>(bytes, start + i * stride + 8);
            else
                highmountainRoster[guid] = stride == 9
                    ? bytes[start + i * stride + 8] : Field<std::uint64_t>(bytes, start + i * stride + 8);
        }
        size = start;
        Field<unsigned>(packet, 0x10) = base + size;
    }
}

extern "C" __declspec(dllexport) void __cdecl EsteriaSelectExtra(void* character)
{
    if (!character)
        return;
    unsigned count = *reinterpret_cast<unsigned*>(Address(0x00B6B23C));
    auto* rows = *reinterpret_cast<unsigned char**>(Address(0x00B6B240));
    if (!rows || count > 100)
        return;
    for (unsigned i = 0; i < count; ++i)
    {
        auto* row = rows + i * 0x198;
        if (Field<void*>(row, 0x188) != character)
            continue;
        auto wing = cosmeticWingRoster.find(Field<std::uint64_t>(row, 0));
        cosmeticWingSelections[character] = wing == cosmeticWingRoster.end() ? 0 : wing->second;
        UpdateCosmeticWing(character);
        unsigned race = row[0x178];
        if (!ExtendedRace(race))
            return;
        auto it = highmountainRoster.find(Field<std::uint64_t>(row, 0));
        highmountainExtra[character] = race == 20 || CreatureAppearance::Uses(race)
            || it == highmountainRoster.end() ? 0 : it->second;
        if (race == 20 || race == 48 || race == 49 || race == 50 || race == 51 || CreatureAppearance::Uses(race))
        {
            // The preview's first base-section validation precedes the stock setters that establish
            // resolver context. Seed the authenticated roster identity/bytes before that validation.
            Field<unsigned>(character, 0x18) = race;
            Field<unsigned>(character, 0x1C) = row[0x17A];
            CaptureEarthenAppearance(character, row + 0x17B, highmountainExtra[character]);
            auto const appearance = earthenNetworkAppearance.find(character);
            if (appearance != earthenNetworkAppearance.end())
                SetHighmountainFields(character, appearance->second);
            highmountainContext = character;
        }
        return;
    }
}

extern "C" __declspec(dllexport) void __cdecl EsteriaUnitExtra(void* unit)
{
    if (!unit || (Field<unsigned>(unit, 0x14) != 3 && Field<unsigned>(unit, 0x14) != 4))
        return;
    void* character = Field<void*>(unit, 0xB4C);
    void* fields = Field<void*>(unit, 0xD0); // Native UnitFields starts after the six ObjectFields.
    if (!character || !fields || !ExtendedRace(Field<unsigned>(character, 0x18)))
        return;
    unsigned race = Field<unsigned>(character, 0x18);
    highmountainExtra[character] = race == 20 || CreatureAppearance::Uses(race) ? 0 : race == 50 || race == 51
        ? UnitAppearanceExtra(unit) : Field<unsigned>(fields, 0x8D * 4) & 255;
    // Stock player initialization clamps packed choices against sparse ordinary DBC counts.
    // Preserve the authenticated player bytes before the native compositor and accessory selectors run.
    if (Field<unsigned>(unit, 0x14) == 4)
    {
        auto* playerData = Field<unsigned char*>(unit, 0x1008);
        if (playerData)
            CaptureEarthenAppearance(character, playerData + 0x14, highmountainExtra[character]);
    }
    HighmountainGeometry(character);
}

extern "C" __declspec(dllexport) void __cdecl EsteriaRegisterExtra()
{
    // UNIT_FIELD_PADDING has no stock old-value cache slot. Registering it makes the client copy
    // to the lookup's out-of-range fallback, corrupting adjacent objects. Read it after unit updates.
}

extern "C" __declspec(dllexport) void __cdecl EsteriaForgetCharacter(void* character)
{
    ForgetCosmeticWing(character);
    cosmeticWingSelections.erase(character);
    haranirImages.erase(character);
    earthenNetworkAppearance.erase(character);
    highmountainExtra.erase(character);
    if (highmountainContext == character)
        highmountainContext = nullptr;
}

extern "C" __declspec(dllexport) void __cdecl EsteriaAppearanceContext(void* character)
{
    highmountainContext = character;
}

extern "C" __declspec(dllexport) void __cdecl EsteriaSectionArguments(unsigned* arguments)
{
    if (!arguments || !ExtendedRace(arguments[1]) || arguments[2] > 1 || !highmountainContext
        || Field<unsigned>(highmountainContext, 0x18) != arguments[1]
        || Field<unsigned>(highmountainContext, 0x1C) != arguments[2])
        return;
    auto fields = HighmountainFields(highmountainContext);
    unsigned gender = arguments[2];
    if (CreatureAppearance::Uses(arguments[1]))
        return;
    if (arguments[1] == 20 || arguments[1] == 50 || arguments[1] == 51)
    {
        arguments[4] = 0;
        arguments[5] = 0;
        return;
    }
    if (arguments[1] != 46)
    {
        arguments[4] = arguments[3] == 1 ? fields[1] % 10 : 0;
        arguments[5] = arguments[3] == 3 ? fields[3] % 14 : arguments[3] == 2 ? 0 : fields[0] % 14;
        return;
    }
    // Resolve actual logical choices before the native compositor indexes CharSections.
    unsigned skin = fields[0] % 9;
    unsigned face = fields[1] % (gender ? 4 : 5);
    unsigned paint = gender ? (fields[1] / 4) % 4 : fields[3] / 64;
    unsigned paintColor = gender ? fields[2] / 81 : fields[5] % 3;
    if (arguments[3] == 0 || arguments[3] == 1 || arguments[3] == 4)
    {
        arguments[4] = arguments[3] == 1 ? face : 0;
        arguments[5] = skin + 9 * (paint + 4 * paintColor);
    }
    else
    {
        arguments[4] = 0;
        arguments[5] = 0;
    }
}

extern "C" __declspec(dllexport) bool __cdecl EsteriaDirectSection(
    void* character, unsigned operation, unsigned const* arguments)
{
    if (!character || !ExtendedRace(Field<unsigned>(character, 0x18)) || !arguments || operation > 2)
        return false;
    highmountainContext = character;
    unsigned kind = operation == 0 ? 0 : operation == 1 ? 3 : arguments[0];
    unsigned slot = operation == 0 ? 1 : operation == 1 ? 0 : arguments[1];
    if (kind > 4 || slot > 2)
        return true;
    unsigned style = operation == 2 ? arguments[2] : 0;
    unsigned color = operation == 2 ? arguments[3] : Field<unsigned>(character, 0x28);
    char const* path = HaranirLayerPath(character, kind, slot);
    if (!path)
    {
        auto* table = *reinterpret_cast<void**>(Address(0x00B6B864));
        auto* row = Native<unsigned*(__cdecl*)(void*, unsigned, unsigned, unsigned, unsigned, unsigned, void*)>(
            0x004F3BA0)(table, Field<unsigned>(character, 0x18), Field<unsigned>(character, 0x1C),
                kind, style, color, nullptr);
        if (!row)
            return true;
        path = reinterpret_cast<char const*>(row[4 + slot]);
    }
    if (!path)
        return true;
    if (operation < 2)
    {
        if (Field<unsigned>(character, 0x18) == 20 || CreatureAppearance::Uses(Field<unsigned>(character, 0x18)))
        {
            SetHaranirMaterials(character);
            return true;
        }
        void* instance = Field<void*>(character, 0x38);
        if (instance && path[0])
        {
            void* texture = Native<void*(__cdecl*)(char const*, void*)>(0x004E8D30)(
                path, reinterpret_cast<void*>(Address(0x00AC46D0)));
            if (texture)
            {
                Native<void(__thiscall*)(void*, unsigned, void*)>(0x00825260)(
                    instance, operation == 0 ? 8 : 6, texture);
                Native<void(__cdecl*)(void*)>(0x0047BF30)(texture);
            }
        }
        return true;
    }
    // The stock layer setter validates, then bypasses the resolver and reindexes encoded bytes.
    // Keep its cache/refcount/dirty-bit lifecycle, with the resolved row as the only material source.
    void*& layer = Field<void*>(character, 0x194 + (kind * 3 + slot) * 4);
    if (layer)
        Native<void(__cdecl*)(void*)>(0x004F31A0)(layer);
    layer = nullptr;
    unsigned race = Field<unsigned>(character, 0x18);
    layer = path[0] ? (race == 20 || race == 50 || race == 51 || CreatureAppearance::Uses(race) ? HaranirLoadLayer(path)
        : Native<void*(__cdecl*)(char const*)>(0x004F3930)(path)) : nullptr;
    if (arguments[4] < 32)
        Field<unsigned>(character, 0x0C) |= 1u << arguments[4];
    void* pending = Field<void*>(character, 0x52C);
    if (pending)
    {
        Field<unsigned>(pending, 0) &= ~1u;
        Field<void*>(character, 0x52C) = nullptr;
    }
    Field<unsigned>(character, 8) &= ~8u;
    return true;
}

extern "C" __declspec(dllexport) unsigned __cdecl EsteriaSectionCount(unsigned const* arguments)
{
    // Race46 stores encoded bytes. Its material getters normalize every access into the sparse source table.
    if (!arguments || !ExtendedRace(arguments[1]) || arguments[2] > 1 || arguments[3] > 4)
        return 0xffffffff;
    if (CreatureAppearance::Uses(arguments[1]))
    {
        if (!CreatureAppearance::GenderAllowed(arguments[1], arguments[2]))
            return 0;
        auto const& options = CreatureAppearance::Options(arguments[1], arguments[2]);
        return arguments[3] == 2 || arguments[3] == 3 ? options[3].count : options[0].count;
    }
    if (arguments[1] == 20)
    {
        auto const& capacities = arguments[2] ? VulperaAppearance::FemaleCapacities
            : VulperaAppearance::MaleCapacities;
        return arguments[3] == 2 || arguments[3] == 3 ? capacities[3] : capacities[0];
    }
    if (arguments[1] == 50 || arguments[1] == 51)
    {
        auto const& capacities = arguments[2] ? HaranirAppearance::FemaleCapacities
            : HaranirAppearance::MaleCapacities;
        return arguments[3] == 2 || arguments[3] == 3 ? capacities[3] : capacities[0];
    }
    if (arguments[1] != 46)
    {
        auto const& capacities = arguments[2] ? EarthenAppearance::FemaleCapacities
            : EarthenAppearance::MaleCapacities;
        return arguments[3] == 2 || arguments[3] == 3 ? capacities[3] : capacities[0];
    }
    auto const& capacities = arguments[2] ? HighmountainAppearance::FemaleCapacities
        : HighmountainAppearance::MaleCapacities;
    return arguments[3] == 2 || arguments[3] == 3 ? capacities[3] : capacities[0];
}
