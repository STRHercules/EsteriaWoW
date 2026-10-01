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
#include "../src/server/shared/HighmountainAppearance.h"

namespace
{
    bool HighmountainGeometry(void* character);
    bool HighmountainCycle(void* state, char const* command);
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
    void* character = *reinterpret_cast<void**>(Address(0x00B6B1A0));
    if (!character)
        return 0;
    if (HighmountainCycle(state, command))
        return std::strcmp(command, "EA_GET") == 0 ? 3 : 0;
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
    if (std::strcmp(command, "EA_CYCLE") != 0 || getTop(state) != 3 || !isNumber(state, 3))
        return 0;
    double delta = number(state, 3);
    if (delta != 1 && delta != -1)
        return 0;
    unsigned const next = (value + option.count + static_cast<int>(delta)) % option.count;
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
        case 52: return 13;
        case 53: return 10;
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
    std::unordered_map<void*, std::uint8_t> highmountainExtra;
    std::unordered_map<std::uint64_t, std::uint8_t> highmountainRoster;
    thread_local void* highmountainContext = nullptr;
    constexpr unsigned appearanceOffsets[] = {0x28, 0x2C, 0x34, 0x24, 0x30};

    std::array<std::uint8_t, 6> HighmountainFields(void* character)
    {
        std::array<std::uint8_t, 6> result{};
        for (unsigned i = 0; i < 5; ++i)
            result[i] = static_cast<std::uint8_t>(Field<unsigned>(character, appearanceOffsets[i]));
        auto it = highmountainExtra.find(character);
        result[5] = it == highmountainExtra.end() ? 0 : it->second;
        return result;
    }

    void SetHighmountainFields(void* character, std::array<std::uint8_t, 6> const& values)
    {
        for (unsigned i = 0; i < 5; ++i)
            Field<unsigned>(character, appearanceOffsets[i]) = values[i];
        highmountainExtra[character] = values[5];
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
            return true;
        }
        unsigned index = static_cast<unsigned>(requested) - 1;
        auto fields = HighmountainFields(character);
        if (std::strcmp(command, "EA_RANDOM") == 0)
        {
            static std::mt19937 random(GetTickCount());
            fields = {};
            for (unsigned i = 0; i < options.size(); ++i)
            {
                auto const& descriptor = options[i];
                unsigned first = std::uniform_int_distribution<unsigned>(0, descriptor.count - 1)(random);
                for (unsigned attempt = 0; attempt < descriptor.count; ++attempt)
                {
                    auto candidate = fields;
                    unsigned value = (first + attempt) % descriptor.count;
                    candidate[descriptor.field] += static_cast<std::uint8_t>(value * descriptor.factor);
                    if (HighmountainAppearance::Validate(Field<unsigned>(character, 0x1C), candidate))
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
            pushNumber(state, option.count);
            pushString(state, labels[index]);
            return true;
        }
        if (std::strcmp(command, "EA_CYCLE") != 0)
            return true;
        double direction = number(state, 3);
        if (direction != 1 && direction != -1)
            return true;
        for (unsigned step = 1; step <= option.count; ++step)
        {
            unsigned next = static_cast<unsigned>((static_cast<int>(value) + static_cast<int>(option.count) * 2
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
                    if (rule.option != index && dependent == rule.value && !(rule.mask & (1u << prerequisite)))
                        candidate[selected.field] -= static_cast<std::uint8_t>(dependent * selected.factor);
                }
            if (!HighmountainAppearance::Validate(Field<unsigned>(character, 0x1C), candidate))
                continue;
            SetHighmountainFields(character, candidate);
            Refresh(character);
            break;
        }
        return true;
    }

    bool HighmountainCycle(void* state, char const* command)
    {
        void* character = *reinterpret_cast<void**>(Address(0x00B6B1A0));
        if (!character || Field<unsigned>(character, 0x18) != 46)
            return false;
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

    std::vector<HighmountainSelection> const& HighmountainSelections()
    {
        static auto const records = []
        {
            std::vector<HighmountainSelection> result;
            FILE* file = CatalogFile(L"EsteriaHighmountain.bin");
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
                    bool valid = record.gender < 2 && record.kind < 3
                        && (record.kind == 2 ? record.target < 5200 && record.value >= 10000
                            && record.value < 30000 : record.kind ? record.target < 16 && record.path[0]
                            && std::memchr(record.path, 0, sizeof(record.path)) : record.target < 52
                            && record.value >= record.target * 100 && record.value < record.target * 100 + 100);
                    for (unsigned selector : record.choices)
                        valid = valid && (selector == 0xffffffff || (selector & 0xffff) < 23
                            && (selector >> 16) < 32);
                    if (valid)
                        result.push_back(record);
                }
            std::fclose(file);
            return result;
        }();
        return records;
    }

    bool HighmountainGeometry(void* character)
    {
        if (Field<unsigned>(character, 0x18) != 46)
            return false;
        unsigned gender = Field<unsigned>(character, 0x1C);
        auto fields = HighmountainFields(character);
        if (!HighmountainAppearance::Validate(gender, fields))
        {
            fields = {};
            SetHighmountainFields(character, fields);
        }
        void* instance = Field<void*>(character, 0x38);
        if (!instance)
            return true;
        unsigned materials = 0;
        std::uint64_t geometryGroups = 0;
        unsigned selectedGeosets[52] = {};
        Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(instance, 10000, 29999, 0);
        for (auto const& record : HighmountainSelections())
        {
            if (record.gender != gender)
                continue;
            bool selected = true;
            for (unsigned selector : record.choices)
            {
                if (selector == 0xffffffff)
                    continue;
                unsigned index = selector & 0xffff;
                auto const& option = gender ? HighmountainAppearance::FemaleOptions[index]
                    : HighmountainAppearance::MaleOptions[index];
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
                selectedGeosets[record.target] = record.value;
                if (record.target < 19)
                    Field<unsigned>(character, 0x144 + record.target * 4) = record.value;
                else
                {
                    Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(
                        instance, record.target * 100, record.target * 100 + 99, 0);
                    Native<void(__thiscall*)(void*, unsigned, unsigned, int)>(0x0082C7C0)(
                        instance, record.value, record.value, 1);
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
        return true;
    }
}

extern "C" __declspec(dllexport) void __cdecl EsteriaCreateExtra(void* packet)
{
    void* character = *reinterpret_cast<void**>(Address(0x00B6B1A0));
    if (!packet || !character || Field<unsigned>(character, 0x18) != 46)
        return;
    unsigned size = Field<unsigned>(packet, 0x10);
    unsigned base = Field<unsigned>(packet, 8);
    if (!size || size < base || size - base > Field<unsigned>(packet, 0x0C))
        return;
    auto* bytes = Field<unsigned char*>(packet, 4);
    bytes[size - base - 1] = HighmountainFields(character)[5];
}

extern "C" __declspec(dllexport) void __cdecl EsteriaEnumExtra(void* packet)
{
    highmountainRoster.clear();
    if (!packet)
        return;
    unsigned length = Field<unsigned>(packet, 0x10);
    unsigned base = Field<unsigned>(packet, 8);
    if (length < base || length - base < 8 || length - base > Field<unsigned>(packet, 0x0C))
        return;
    auto* bytes = Field<unsigned char*>(packet, 4);
    unsigned size = length - base;
    if (Field<unsigned>(bytes, size - 4) != 0x31455848)
        return;
    unsigned count = Field<unsigned>(bytes, size - 8);
    if (count > 100 || count > (size - 8) / 9)
        return;
    unsigned start = size - 8 - count * 9;
    for (unsigned i = 0; i < count; ++i)
        highmountainRoster[Field<std::uint64_t>(bytes, start + i * 9)] = bytes[start + i * 9 + 8];
    Field<unsigned>(packet, 0x10) = base + start;
}

extern "C" __declspec(dllexport) void __cdecl EsteriaSelectExtra(void* character)
{
    if (!character || Field<unsigned>(character, 0x18) != 46)
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
        auto it = highmountainRoster.find(Field<std::uint64_t>(row, 0));
        highmountainExtra[character] = it == highmountainRoster.end() ? 0 : it->second;
        return;
    }
}

extern "C" __declspec(dllexport) void __cdecl EsteriaUnitExtra(void* unit)
{
    if (!unit || (Field<unsigned>(unit, 0x14) != 3 && Field<unsigned>(unit, 0x14) != 4))
        return;
    void* character = Field<void*>(unit, 0xB4C);
    void* fields = Field<void*>(unit, 0xD0); // Native UnitFields starts after the six ObjectFields.
    if (!character || !fields || Field<unsigned>(character, 0x18) != 46)
        return;
    highmountainExtra[character] = static_cast<std::uint8_t>(Field<unsigned>(fields, 0x8D * 4));
    HighmountainGeometry(character);
}

extern "C" __declspec(dllexport) void __cdecl EsteriaRegisterExtra()
{
    // UNIT_FIELD_PADDING has no stock old-value cache slot. Registering it makes the client copy
    // to the lookup's out-of-range fallback, corrupting adjacent objects. Read it after unit updates.
}

extern "C" __declspec(dllexport) void __cdecl EsteriaForgetCharacter(void* character)
{
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
    if (!arguments || arguments[1] != 46 || arguments[2] > 1 || !highmountainContext
        || Field<unsigned>(highmountainContext, 0x18) != 46
        || Field<unsigned>(highmountainContext, 0x1C) != arguments[2])
        return;
    auto fields = HighmountainFields(highmountainContext);
    unsigned gender = arguments[2];
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
    if (!character || Field<unsigned>(character, 0x18) != 46 || !arguments || operation > 2)
        return false;
    highmountainContext = character;
    unsigned kind = operation == 0 ? 0 : operation == 1 ? 3 : arguments[0];
    unsigned slot = operation == 0 ? 1 : operation == 1 ? 0 : arguments[1];
    if (kind > 4 || slot > 2)
        return true;
    unsigned style = operation == 2 ? arguments[2] : 0;
    unsigned color = operation == 2 ? arguments[3] : Field<unsigned>(character, 0x28);
    auto* table = *reinterpret_cast<void**>(Address(0x00B6B864));
    auto* row = Native<unsigned*(__cdecl*)(void*, unsigned, unsigned, unsigned, unsigned, unsigned, void*)>(
        0x004F3BA0)(table, 46, Field<unsigned>(character, 0x1C), kind, style, color, nullptr);
    if (!row)
        return true;
    char const* path = reinterpret_cast<char const*>(row[4 + slot]);
    if (!path)
        return true;
    if (operation < 2)
    {
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
    layer = path[0] ? Native<void*(__cdecl*)(char const*)>(0x004F3930)(path) : nullptr;
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
    if (!arguments || arguments[1] != 46 || arguments[2] > 1 || arguments[3] > 4)
        return 0xffffffff;
    auto const& capacities = arguments[2] ? HighmountainAppearance::FemaleCapacities
        : HighmountainAppearance::MaleCapacities;
    return arguments[3] == 2 || arguments[3] == 3 ? capacities[3] : capacities[0];
}
