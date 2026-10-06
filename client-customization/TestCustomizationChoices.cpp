#include <windows.h>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include "../src/server/shared/VulperaAppearance.h"
#include "../src/server/shared/CreatureAppearance.h"

namespace
{
    struct Lua
    {
        char const* command;
        double option;
        double target;
        std::vector<double> numbers;
        std::string choices;
    };

    int __cdecl IsNumber(Lua*, int index) { return index != 1; }
    int __cdecl GetTop(Lua*) { return 3; }
    double __cdecl Number(Lua* lua, int index) { return index == 2 ? lua->option : lua->target; }
    char const* __cdecl String(Lua* lua, int, std::size_t*) { return lua->command; }
    void __cdecl PushNumber(Lua* lua, double value) { lua->numbers.push_back(value); }
    void __cdecl PushString(Lua* lua, char const* value) { lua->choices = value; }
    unsigned __cdecl Variations(void*, unsigned, unsigned, unsigned) { return 3; }
    unsigned __cdecl Colors(void*, unsigned, unsigned, unsigned, unsigned) { return 4; }
    unsigned __cdecl Flags(unsigned, unsigned) { return 7; }
    bool __cdecl Allowed(unsigned flags, unsigned required) { return flags == required; }
    unsigned const* __cdecl Section(void*, unsigned, unsigned, unsigned kind,
        unsigned variation, unsigned color, bool* textured)
    {
        static unsigned row[10] = {0, 0, 0, 0, 0, 0, 0, 7};
        if (textured)
            *textured = false;
        return variation == 1 || color == 1 || (kind == 2 && !textured) ? nullptr : row;
    }

    void __fastcall Setter3(void*, void*, unsigned, int) { }
    void __fastcall Setter4(void*, void*, unsigned, int, int) { }
    void __fastcall Setter5(void*, void*, unsigned, int, int, int) { }
    void __cdecl Refresh(void*, int) { }
    unsigned previewPlacements;
    void __fastcall PlacePreview(void* instance, void*, float const* position, float yaw, float scale)
    {
        auto* matrix = reinterpret_cast<float*>(static_cast<unsigned char*>(instance) + 0xB4);
        matrix[0] = matrix[5] = std::cos(yaw) * scale;
        matrix[1] = std::sin(yaw) * scale;
        matrix[4] = -matrix[1];
        matrix[10] = scale;
        for (unsigned i = 0; i < 3; ++i)
            matrix[12 + i] = position[i];
        ++previewPlacements;
    }

    std::uintptr_t Address(std::uintptr_t preferred)
    {
        return reinterpret_cast<std::uintptr_t>(GetModuleHandleW(nullptr)) + preferred - 0x00400000;
    }

    void* Page(std::uintptr_t preferred)
    {
        auto address = Address(preferred) & ~std::uintptr_t{65535};
        auto page = VirtualAlloc(reinterpret_cast<void*>(address), 65536,
            MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        assert(page == reinterpret_cast<void*>(address));
        return page;
    }

    void Hook(std::uintptr_t preferred, void* destination)
    {
        auto* code = reinterpret_cast<unsigned char*>(Address(preferred));
        code[0] = 0xE9;
        auto delta = static_cast<std::int32_t>(reinterpret_cast<std::uintptr_t>(destination)
            - reinterpret_cast<std::uintptr_t>(code) - 5);
        std::memcpy(code + 1, &delta, 4);
        FlushInstructionCache(GetCurrentProcess(), code, 5);
    }
}

int main(int argc, char** argv)
{
    assert(argc == 2 || argc == 3);
    auto module = LoadLibraryA(argv[1]);
    assert(module);
    auto cycle = reinterpret_cast<int(__cdecl*)(Lua*)>(GetProcAddress(module, "EsteriaCycle"));
    auto forget = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaForgetCharacter"));
    auto wheelBlocked = reinterpret_cast<bool(__cdecl*)()>(GetProcAddress(module, "EsteriaDropdownWheelBlocked"));
    assert(cycle && forget && wheelBlocked);
    std::array pages = {Page(0x004E0000), Page(0x004F0000), Page(0x00840000), Page(0x00B60000), Page(0x00820000)};
    Hook(0x008251D0, reinterpret_cast<void*>(&PlacePreview));
    Hook(0x0084DF20, reinterpret_cast<void*>(&IsNumber));
    Hook(0x0084DBD0, reinterpret_cast<void*>(&GetTop));
    Hook(0x0084E030, reinterpret_cast<void*>(&Number));
    Hook(0x0084E0E0, reinterpret_cast<void*>(&String));
    Hook(0x0084E2A0, reinterpret_cast<void*>(&PushNumber));
    Hook(0x0084E350, reinterpret_cast<void*>(&PushString));
    Hook(0x004F3AE0, reinterpret_cast<void*>(&Variations));
    Hook(0x004F3B10, reinterpret_cast<void*>(&Colors));
    Hook(0x004F3A40, reinterpret_cast<void*>(&Flags));
    Hook(0x004F39A0, reinterpret_cast<void*>(&Allowed));
    Hook(0x004F3BA0, reinterpret_cast<void*>(&Section));
    Hook(0x004EA2F0, reinterpret_cast<void*>(&Setter4));
    Hook(0x004EA6B0, reinterpret_cast<void*>(&Setter5));
    Hook(0x004EA490, reinterpret_cast<void*>(&Setter4));
    Hook(0x004EA3E0, reinterpret_cast<void*>(&Setter3));
    Hook(0x004EA590, reinterpret_cast<void*>(&Setter4));
    Hook(0x004E6AE0, reinterpret_cast<void*>(&Refresh));
    alignas(4) unsigned char character[0x200]{};
    *reinterpret_cast<void**>(Address(0x00B6B1A0)) = character;
    *reinterpret_cast<void**>(Address(0x00B6B864)) = character;
    unsigned features[128]{};
    features[2] = 3;
    *reinterpret_cast<unsigned**>(Address(0x00B6B860)) = features;
    *reinterpret_cast<unsigned*>(character + 0x18) = 1;
    alignas(4) unsigned char previewInstance[0x200]{};
    alignas(4) unsigned char previewModel[0x200]{};
    *reinterpret_cast<void**>(character + 0x38) = previewInstance;
    *reinterpret_cast<void**>(previewInstance + 0x2C) = previewModel;
    std::strcpy(reinterpret_cast<char*>(previewModel) + 0x3C, "custom\\vrykul\\native\\male\\vrykulmale.m2");
    auto* matrix = reinterpret_cast<float*>(previewInstance + 0xB4);
    matrix[0] = matrix[5] = std::cos(.7f);
    matrix[1] = std::sin(.7f);
    matrix[4] = -matrix[1];
    matrix[10] = 1;
    matrix[12] = 4;
    matrix[13] = 5;
    matrix[14] = 6;
    Lua preview{"EA_PREVIEW_SCALE", 0};
    assert(cycle(&preview) == 0 && previewPlacements == 0); // Other races and world units stay unchanged.
    *reinterpret_cast<unsigned*>(character + 0x18) = 56;
    assert(cycle(&preview) == 0 && previewPlacements == 1);
    assert(std::abs(std::hypot(matrix[0], matrix[1]) - .55f) < .0001f);
    assert(std::abs(std::atan2(matrix[1], matrix[0]) - .7f) < .0001f);
    assert(matrix[12] == 4 && matrix[13] == 5 && matrix[14] == 6);
    assert(cycle(&preview) == 0 && previewPlacements == 1); // No cumulative shrinking.
    unsigned char roster[0x198]{};
    *reinterpret_cast<void**>(roster + 0x188) = character;
    *reinterpret_cast<void**>(Address(0x00B6B240)) = roster;
    *reinterpret_cast<unsigned*>(Address(0x00B6B23C)) = 1;
    *reinterpret_cast<unsigned*>(character + 0x18) = 57;
    matrix[0] = matrix[5] = 1;
    matrix[1] = matrix[4] = 0;
    Lua selectPreview{"EA_PREVIEW_SCALE", 1};
    assert(cycle(&selectPreview) == 0 && previewPlacements == 2);
    assert(std::abs(matrix[0] - .55f) < .0001f);
    Lua invalidPreview{"EA_PREVIEW_SCALE", 2};
    assert(cycle(&invalidPreview) == 0 && previewPlacements == 2);
    *reinterpret_cast<void**>(character + 0x38) = nullptr;
    *reinterpret_cast<unsigned*>(character + 0x18) = 1;
    constexpr char const* stock[] = {"0,2,3,", "0,2,", "0,2,", "0,2,3,", "0,1,2,"};
    for (unsigned i = 1; i <= 5; ++i)
    {
        Lua get{"EA_STOCK_GET", static_cast<double>(i)};
        assert(cycle(&get) == 2 && get.numbers[0] == 0 && get.numbers[1] >= 3);
        Lua choices{"EA_STOCK_CHOICES", static_cast<double>(i)};
        assert(cycle(&choices) == 1 && choices.choices == stock[i - 1]);
    }
    for (unsigned race : {20u, 46u, 47u, 48u, 49u, 50u, 51u, 52u, 53u, 54u})
        for (unsigned gender = 0; gender < 2; ++gender)
        {
            forget(character);
            std::memset(character, 0, sizeof(character));
            *reinterpret_cast<unsigned*>(character + 0x18) = race;
            *reinterpret_cast<unsigned*>(character + 0x1C) = gender;
            *reinterpret_cast<unsigned*>(character + 0x20) = 1;
            for (unsigned i = 1; i <= 29; ++i)
            {
                Lua get{"EA_GET", static_cast<double>(i)};
                int result = cycle(&get);
                if (race == 47 || race == 52 || race == 53)
                {
                    if (!result)
                    {
                        assert(i > 10);
                        continue;
                    }
                    assert(result == 2);
                }
                else
                    assert(result == 3);
                assert(get.numbers.size() == 2);
                if (race == 54 && i <= 5)
                    assert(get.numbers[1] == CreatureAppearance::Options(race, gender)[i - 1].count);
                Lua choices{"EA_CHOICES", static_cast<double>(i)};
                auto before = std::array<unsigned char, sizeof(character)>{};
                std::memcpy(before.data(), character, sizeof(character));
                assert(cycle(&choices) == 1);
                assert(!std::memcmp(before.data(), character, sizeof(character)));
                if (get.numbers[1] > 1)
                {
                    if (choices.choices.find(std::to_string(static_cast<unsigned>(get.numbers[0])) + ",")
                        == std::string::npos)
                        std::fprintf(stderr, "race=%u gender=%u option=%u current=%g count=%g choices=%s\n",
                            race, gender, i, get.numbers[0], get.numbers[1], choices.choices.c_str());
                    assert(choices.choices.find(std::to_string(static_cast<unsigned>(get.numbers[0])) + ",")
                        != std::string::npos);
                    auto last = choices.choices.rfind(',', choices.choices.size() - 2);
                    unsigned target = std::stoul(choices.choices.substr(last == std::string::npos ? 0 : last + 1));
                    Lua set{"EA_SET", static_cast<double>(i), static_cast<double>(target)};
                    assert(cycle(&set) == 0);
                    Lua selected{"EA_GET", static_cast<double>(i)};
                    cycle(&selected);
                    assert(selected.numbers[0] == target);
                    std::memcpy(before.data(), character, sizeof(character));
                    Lua invalid{"EA_SET", static_cast<double>(i), get.numbers[1]};
                    cycle(&invalid);
                    assert(!std::memcmp(before.data(), character, sizeof(character)));
                    std::vector<std::vector<double>> baseline;
                    for (unsigned option = 1; option <= 29; ++option)
                    {
                        Lua state{"EA_GET", static_cast<double>(option)};
                        cycle(&state);
                        baseline.push_back(state.numbers);
                    }
                    Lua save{"EA_PREVIEW_SAVE", 1};
                    assert(cycle(&save) == 1 && save.numbers[0] == 1);
                    Lua hover{"EA_SET", static_cast<double>(i), std::stod(choices.choices)};
                    cycle(&hover);
                    Lua restore{"EA_PREVIEW_RESTORE", 1};
                    assert(cycle(&restore) == 1 && restore.numbers[0] == 1);
                    assert(!std::memcmp(before.data(), character, sizeof(character)));
                    for (unsigned option = 1; option <= 29; ++option)
                    {
                        Lua state{"EA_GET", static_cast<double>(option)};
                        cycle(&state);
                        assert(state.numbers == baseline[option - 1]);
                    }
                    ++*reinterpret_cast<unsigned*>(character + 0x20);
                    Lua switched{"EA_PREVIEW_RESTORE", 1};
                    assert(cycle(&switched) == 1 && switched.numbers[0] == 0);
                    --*reinterpret_cast<unsigned*>(character + 0x20);
                    Lua end{"EA_PREVIEW_END", 1};
                    cycle(&end);
                    Lua ended{"EA_PREVIEW_RESTORE", 1};
                    assert(cycle(&ended) == 1 && ended.numbers[0] == 0);
                }
            }
        }
    constexpr unsigned offsets[] = {0x28, 0x2C, 0x34, 0x24, 0x30};
    for (unsigned gender = 0; gender < 2; ++gender)
        for (unsigned characterClass : {1u, 6u})
        {
            forget(character);
            std::memset(character, 0, sizeof(character));
            *reinterpret_cast<unsigned*>(character + 0x18) = 20;
            *reinterpret_cast<unsigned*>(character + 0x1C) = gender;
            *reinterpret_cast<unsigned*>(character + 0x20) = characterClass;
            unsigned eyeOption = gender ? 7 : 6;
            Lua choices{"EA_CHOICES", static_cast<double>(eyeOption)};
            assert(cycle(&choices) == 1);
            assert(characterClass == 6 ? choices.choices == "14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,"
                : choices.choices == "0,1,2,3,4,5,6,7,8,9,10,11,12,13,"
                    "15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,");
            for (unsigned attempt = 0; attempt < 32; ++attempt)
            {
                Lua random{"EA_RANDOM", 1};
                cycle(&random);
                std::array<std::uint8_t, 5> fields{};
                for (unsigned i = 0; i < fields.size(); ++i)
                    fields[i] = static_cast<std::uint8_t>(*reinterpret_cast<unsigned*>(character + offsets[i]));
                assert(VulperaAppearance::ValidateClass(gender, characterClass, fields));
            }
            Lua stylePalette{"EA_SET", static_cast<double>(eyeOption), 15};
            cycle(&stylePalette);
            Lua eyeStyle{"EA_SET", 10, 2};
            cycle(&eyeStyle);
            Lua selectedStyle{"EA_GET", 10};
            assert(cycle(&selectedStyle) == 3 && selectedStyle.numbers[0] == 2 && selectedStyle.numbers[1] == 3);
            Lua restrictedEye{"EA_SET", static_cast<double>(eyeOption), characterClass == 6 ? 14.0 : 0.0};
            cycle(&restrictedEye);
            *reinterpret_cast<unsigned*>(character + 0x20) = characterClass == 6 ? 1 : 6;
            Lua changed{"EA_GET", static_cast<double>(eyeOption)};
            assert(cycle(&changed) == 3);
            assert(changed.numbers[0] == (characterClass == 6 ? 0 : 14));
        }
    *reinterpret_cast<unsigned*>(character + 0x18) = 1;
    Lua stockSave{"EA_PREVIEW_SAVE", 1};
    cycle(&stockSave);
    unsigned skin = *reinterpret_cast<unsigned*>(character + 0x28);
    *reinterpret_cast<unsigned*>(character + 0x28) = 1;
    Lua stockRestore{"EA_PREVIEW_RESTORE", 1};
    cycle(&stockRestore);
    assert(*reinterpret_cast<unsigned*>(character + 0x28) == skin);
    if (argc == 3)
    {
        // Exercise the patched v180 callback after Windows has resolved its new import and relocations.
        auto zoom = LoadLibraryA(argv[2]);
        assert(zoom);
        auto base = reinterpret_cast<std::uintptr_t>(zoom);
        auto callback = reinterpret_cast<void(__cdecl*)(void*, void*)>(base + 0x1A50);
        auto* target = reinterpret_cast<float*>(base + 0x1A958);
        // Simulate an active creator in the harness; do not depend on WoW's absolute scene pointer.
        std::array<unsigned char, 6> activeScene = {0xB8, 1, 0, 0, 0, 0xC3};
        auto* sceneCheck = reinterpret_cast<void*>(base + 0x1040);
        DWORD protection = 0, previous = 0;
        assert(VirtualProtect(sceneCheck, activeScene.size(), PAGE_EXECUTE_READWRITE, &protection));
        std::memcpy(sceneCheck, activeScene.data(), activeScene.size());
        assert(VirtualProtect(sceneCheck, activeScene.size(), protection, &previous));
        FlushInstructionCache(GetCurrentProcess(), sceneCheck, activeScene.size());
        unsigned event[] = {0x20A, 120u << 16};
        *target = 0;
        Lua block{"EA_WHEEL_BLOCK", 1};
        cycle(&block);
        assert(wheelBlocked());
        callback(nullptr, event);
        assert(*target == 0);
        Lua unblock{"EA_WHEEL_BLOCK", 0};
        cycle(&unblock);
        assert(!wheelBlocked());
        callback(nullptr, event);
        assert(*target > 0);
        float selectedZoom = *target;
        cycle(&block);
        callback(nullptr, event);
        assert(*target == selectedZoom);
        cycle(&unblock);
        FreeLibrary(zoom);
        std::puts("GlueZoom wheel guard: PASS (dropdown blocks zoom, closed dropdown resumes zoom)");
    }
    for (void* page : pages)
        VirtualFree(page, 0, MEM_RELEASE);
    FreeLibrary(module);
    std::puts("Customization choices: PASS (stock gaps, both genders, dependency filters, preview restoration)");
}
