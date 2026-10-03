#include <windows.h>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "../src/server/shared/HighmountainAppearance.h"
#include "../src/server/shared/EarthenAppearance.h"
#include "../src/server/shared/HaranirAppearance.h"
#include "../src/server/shared/VulperaAppearance.h"

int main(int argc, char** argv)
{
    assert(argc == 2);
    assert(HighmountainAppearance::Validate(0, {}));
    assert(HighmountainAppearance::Validate(1, {}));
    assert(!HighmountainAppearance::Validate(2, {}));
    assert(!HighmountainAppearance::Validate(0, {255, 255, 255, 255, 255, 255}));
    assert(EarthenAppearance::Validate(0, {195, 79, 164, 195, 164, 49}));
    assert(EarthenAppearance::Validate(1, {195, 79, 164, 195, 164, 31}));
    assert(!EarthenAppearance::Validate(1, {195, 79, 164, 195, 164, 32}));
    for (unsigned gender = 0; gender < 2; ++gender)
    {
        auto const& capacities = gender ? VulperaAppearance::FemaleCapacities : VulperaAppearance::MaleCapacities;
        std::array<std::uint8_t, 5> fields{};
        for (unsigned i = 0; i < fields.size(); ++i)
            fields[i] = static_cast<std::uint8_t>(capacities[i] - 1);
        fields = VulperaAppearance::Normalize(gender, 1, fields);
        assert(VulperaAppearance::Validate(gender, fields));
        fields[4] = 3;
        assert(!VulperaAppearance::Validate(gender, fields));
        for (unsigned characterClass : {1u, 6u})
        {
            fields = VulperaAppearance::Normalize(gender, characterClass, fields);
            assert(VulperaAppearance::ValidateClass(gender, characterClass, fields));
        }
    }
    for (unsigned gender = 0; gender < 2; ++gender)
    {
        auto const& capacities = gender ? HaranirAppearance::FemaleCapacities : HaranirAppearance::MaleCapacities;
        std::array<std::uint8_t, 13> fields{};
        for (unsigned i = 0; i < fields.size(); ++i)
            fields[i] = static_cast<std::uint8_t>(capacities[i] - 1);
        assert(HaranirAppearance::Validate(gender, fields));
        auto extra = HaranirAppearance::Extra(fields);
        assert(HaranirAppearance::Fields(fields[0], fields[1], fields[2], fields[3], fields[4], extra) == fields);
        assert(extra >> 32); // The old one-byte transport must not silently truncate the new state.
        fields[12] = 1;
        assert(!HaranirAppearance::Validate(gender, fields));
    }
    HMODULE module = LoadLibraryA(argv[1]);
    assert(module);
    auto source = reinterpret_cast<std::uint32_t(__cdecl*)(void const*, void const*)>(
        GetProcAddress(module, "EsteriaWideSource"));
    auto draw = reinterpret_cast<std::uint32_t(__cdecl*)(void const*, void*)>(
        GetProcAddress(module, "EsteriaDrawStart"));
    assert(source && draw);
    std::uint16_t section[24] = {};
    std::uint32_t skin[12] = {};
    unsigned char model[0x174] = {};
    unsigned char instance[0x30] = {};
    unsigned char context[0x64] = {};
    *reinterpret_cast<void**>(model + 0x170) = skin;
    *reinterpret_cast<void**>(instance + 0x2C) = model;
    *reinterpret_cast<void**>(context + 0x60) = instance;
    skin[3] = 200000;
    for (std::uint32_t level = 0; level < 4; ++level)
        for (std::uint32_t low = 0; low < 65536; low += 127)
        {
            section[1] = static_cast<std::uint16_t>(level);
            section[4] = static_cast<std::uint16_t>(low);
            section[5] = 300;
            std::uint32_t wide = (level << 16) | low;
            auto expected = wide <= 200000 && 300 <= 200000 - wide ? wide : low;
            assert(draw(section, context) == expected);
            assert(source(section, skin) == expected);
        }
    section[1] = 5;
    assert(source(section, nullptr) == section[4]);
    assert(source(nullptr, skin) == 0);
    auto geometry = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaGeometry"));
    assert(geometry);
    unsigned char highmountain[0x200] = {};
    *reinterpret_cast<unsigned*>(highmountain + 0x18) = 46;
    geometry(highmountain); // Safe without an instance; validates the six-byte default.
    auto setContext = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaAppearanceContext"));
    auto resolve = reinterpret_cast<void(__cdecl*)(unsigned*)>(GetProcAddress(module, "EsteriaSectionArguments"));
    auto sectionCount = reinterpret_cast<unsigned(__cdecl*)(unsigned const*)>(
        GetProcAddress(module, "EsteriaSectionCount"));
    auto directSection = reinterpret_cast<bool(__cdecl*)(void*, unsigned, unsigned const*)>(
        GetProcAddress(module, "EsteriaDirectSection"));
    assert(setContext && resolve && sectionCount && directSection);
    setContext(highmountain);
    unsigned sectionArguments[] = {0, 46, 0, 3, 1, 0, 0};
    resolve(sectionArguments);
    assert(sectionArguments[4] == 0 && sectionArguments[5] == 0);
    assert(sectionCount(sectionArguments) == 256);
    sectionArguments[3] = 0;
    assert(sectionCount(sectionArguments) == 234);
    sectionArguments[3] = 3;
    sectionArguments[2] = 1;
    assert(sectionCount(sectionArguments) == 175);
    sectionArguments[2] = 0;
    sectionArguments[1] = 47;
    sectionArguments[4] = 77;
    resolve(sectionArguments);
    assert(sectionArguments[4] == 77 && sectionCount(sectionArguments) == 0xffffffff);
    *reinterpret_cast<unsigned*>(highmountain + 0x18) = 47;
    assert(!directSection(highmountain, 1, sectionArguments));
    *reinterpret_cast<unsigned*>(highmountain + 0x18) = 46;
    unsigned char character[0x200] = {};
    *reinterpret_cast<unsigned*>(character + 0x18) = 53;
    *reinterpret_cast<unsigned*>(character + 0x1C) = 0;
    *reinterpret_cast<unsigned*>(character + 0x34) = 54;
    *reinterpret_cast<unsigned*>(character + 0x2C) = 123;
    geometry(character);
    assert(*reinterpret_cast<unsigned*>(character + 0x160) == 704);
    assert(*reinterpret_cast<unsigned*>(character + 0x148) >= 100);
    assert(*reinterpret_cast<unsigned*>(character + 0x184) == 1600);
    *reinterpret_cast<unsigned*>(character + 0x30) = 31;
    geometry(character);
    assert(*reinterpret_cast<unsigned*>(character + 0x184) == 4306);
    *reinterpret_cast<unsigned*>(character + 0x34) = 20;
    geometry(character);
    assert(*reinterpret_cast<unsigned*>(character + 0x184) == 1600);
    auto restore = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaSkin"));
    assert(restore);
    std::strcpy(reinterpret_cast<char*>(model) + 0x3C, "custom\\skyborne\\expanded\\male\\7478487.m2");
    restore(model);
    assert(skin[1] > 19000 && skin[3] == 185073 && skin[11] == 75);
    std::strcpy(reinterpret_cast<char*>(model) + 0x3C, "custom\\vulpera\\native\\male\\vulperamale.m2");
    restore(model);
    assert(skin[1] == 22163 && skin[3] > 65535 && skin[11] == 75);
    auto skillRace = reinterpret_cast<unsigned(__cdecl*)(unsigned)>(GetProcAddress(module, "EsteriaSkillRace"));
    assert(skillRace);
    for (unsigned race = 1; race < 64; ++race)
        assert(skillRace(race) == (race == 45 ? 2 : race == 46 ? 6 : race == 47 ? 7 : race == 48 ? 3
            : race == 49 ? 2 : race == 50 ? 4 : race == 51 ? 8 : race == 52 ? 13 : race == 53 ? 10
            : race == 54 ? 10 : race == 55 ? 3 : race == 56 || race == 58 ? 1
            : race == 57 || race == 59 ? 2 : race));
    for (unsigned race : {48u, 49u})
    {
        unsigned char earthen[0x200] = {};
        *reinterpret_cast<unsigned*>(earthen + 0x18) = race;
        *reinterpret_cast<unsigned*>(earthen + 0x28) = 195;
        *reinterpret_cast<unsigned*>(earthen + 0x2C) = 79;
        *reinterpret_cast<unsigned*>(earthen + 0x24) = 195;
        geometry(earthen);
        setContext(earthen);
        unsigned arguments[] = {0, race, 0, 1, 255, 255, 0};
        resolve(arguments);
        assert(arguments[4] == 9 && arguments[5] == 13);
        arguments[3] = 3;
        resolve(arguments);
        assert(arguments[4] == 0 && arguments[5] == 13 && sectionCount(arguments) == 196);
        arguments[1] = 46; // A stale context must not alter a different race's material arguments.
        arguments[4] = 123;
        resolve(arguments);
        assert(arguments[4] == 123);
    }
    *reinterpret_cast<unsigned*>(character + 0x18) = 47;
    *reinterpret_cast<unsigned*>(character + 0x34) = 49;
    *reinterpret_cast<unsigned*>(character + 0x30) = 10;
    geometry(character);
    assert(*reinterpret_cast<unsigned*>(character + 0x150) == 304);
    assert(*reinterpret_cast<unsigned*>(character + 0x158) == 502);
    assert(*reinterpret_cast<unsigned*>(character + 0x160) == 704);
    assert(*reinterpret_cast<unsigned*>(character + 0x184) == 1603);
    assert(*reinterpret_cast<unsigned*>(character + 0x188) == 1700);
    *reinterpret_cast<unsigned*>(character + 0x24) = 98;
    geometry(character);
    assert(*reinterpret_cast<unsigned*>(character + 0x188) == 1701);
    *reinterpret_cast<unsigned*>(character + 0x24) = 203;
    geometry(character);
    assert(*reinterpret_cast<unsigned*>(character + 0x188) == 1702);
    *reinterpret_cast<unsigned*>(character + 0x24) = 230;
    geometry(character);
    assert(*reinterpret_cast<unsigned*>(character + 0x188) == 1705);
    auto enumExtra = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaEnumExtra"));
    assert(enumExtra);
    unsigned char roster[32] = {};
    unsigned char packet[24] = {};
    *reinterpret_cast<void**>(packet + 4) = roster;
    *reinterpret_cast<unsigned*>(packet + 12) = sizeof(roster);
    *reinterpret_cast<unsigned*>(packet + 16) = 18;
    *reinterpret_cast<std::uint64_t*>(roster + 1) = 123;
    roster[9] = 81;
    *reinterpret_cast<unsigned*>(roster + 10) = 1;
    *reinterpret_cast<unsigned*>(roster + 14) = 0x31455848;
    enumExtra(packet);
    assert(*reinterpret_cast<unsigned*>(packet + 16) == 1);
    *reinterpret_cast<unsigned*>(packet + 16) = 18;
    *reinterpret_cast<unsigned*>(roster + 10) = 101;
    enumExtra(packet);
    assert(*reinterpret_cast<unsigned*>(packet + 16) == 18);
    std::puts("Native appearance helpers: PASS (no WXL loaded)");
    FreeLibrary(module);
}
