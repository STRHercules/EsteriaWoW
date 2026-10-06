#include <windows.h>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <initializer_list>
#include <cstdlib>
#include <array>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include "../src/server/shared/HaranirAppearance.h"
#include "../src/server/shared/VulperaAppearance.h"
#include "../src/server/shared/CreatureAppearance.h"

namespace
{
    using Resolve = void(__cdecl*)(unsigned*);
    Resolve resolve;
    unsigned row[10]{};
    unsigned lastKind, lastStyle, lastColor, lastSlot, loads, releases;
    unsigned texture, oldLayer, newLayer;
    unsigned registrations;
    bool earthenHair, earthenBelt;
    unsigned vulperaEarrings = 3500;
    unsigned earthenFootMask = 255;
    bool nagaBodyVisible = false;
    char path[] = "custom\\highmountain\\fixture.blp";
    char const haranirPrefix[] = "Interface\\AddOns\\EsteriaAppearanceCache\\Haranir\\";
    std::unordered_set<void*> generatedTextures;
    std::unordered_set<void*> generatedLayers;
    std::unordered_map<void*, std::string> generatedLayerPaths;
    std::array<void*, 16> boundTextures{};
    unsigned decodedTextures;

    void* __stdcall Allocate(unsigned size, char const*, unsigned, unsigned)
    {
        return std::calloc(1, size);
    }

    void* __fastcall TextureConstructor(void* value, void*)
    {
        generatedTextures.insert(value);
        return value;
    }

    void* __cdecl AddReference(void* value, char const*)
    {
        ++*reinterpret_cast<unsigned*>(static_cast<unsigned char*>(value) + 4);
        return value;
    }

    unsigned __cdecl Decode(void* value, unsigned char const* data)
    {
        assert(generatedTextures.contains(value));
        assert(*reinterpret_cast<unsigned const*>(data) == 0x32504C42);
        assert(*reinterpret_cast<unsigned const*>(data + 20) == 1172);
        ++decodedTextures;
        return 1;
    }

    __declspec(naked) unsigned DecodeThunk()
    {
        __asm
        {
            push dword ptr [esp + 4]
            push eax
            call Decode
            add esp, 8
            ret
        }
    }
    bool HaranirPath(char const* name)
    {
        // Generated materials must take the client's filesystem branch, including in Glue.
        return name[0] && name[1] == ':' && (std::strstr(name, haranirPrefix)
            || std::strstr(name, "Interface\\AddOns\\EsteriaAppearanceCache\\Vulpera\\")
            || std::strstr(name, "Interface\\AddOns\\EsteriaAppearanceCache\\Naga\\")
            || std::strstr(name, "Interface\\AddOns\\EsteriaAppearanceCache\\Tuskarr\\")
            || std::strstr(name, "Interface\\AddOns\\EsteriaAppearanceCache\\Vrykul\\")
            || std::strstr(name, "Interface\\AddOns\\EsteriaAppearanceCache\\ThinHuman\\"));
    }

    void __fastcall AppendByte(void* packet, void*, unsigned byte)
    {
        auto* words = static_cast<unsigned*>(packet);
        assert(words[4] >= words[2] && words[4] - words[2] < words[3]);
        reinterpret_cast<unsigned char*>(words[1])[words[4] - words[2]] = static_cast<unsigned char>(byte);
        ++words[4];
    }

    std::uintptr_t Address(std::uintptr_t preferred)
    {
        return reinterpret_cast<std::uintptr_t>(GetModuleHandleW(nullptr)) + preferred - 0x00400000;
    }

    void* Page(std::uintptr_t preferred)
    {
        auto address = Address(preferred) & ~std::uintptr_t{65535};
        void* result = VirtualAlloc(reinterpret_cast<void*>(address), 65536,
            MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        if (result != reinterpret_cast<void*>(address))
            std::fprintf(stderr, "Mock page %p unavailable: %lu\n", reinterpret_cast<void*>(address), GetLastError());
        assert(result == reinterpret_cast<void*>(address));
        return result;
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

    unsigned* __cdecl Section(void*, unsigned race, unsigned gender, unsigned kind,
        unsigned style, unsigned color, void*)
    {
        unsigned args[] = {0, race, gender, kind, style, color, 0};
        resolve(args);
        lastKind = args[3];
        lastStyle = args[4];
        lastColor = args[5];
        // The real sparse fixture has only hairstyle zero. The reported hairstyle-one crash must normalize.
        assert(lastKind <= 4);
        assert(lastStyle < 5);
        assert(lastColor < 108);
        if (lastKind == 3)
            assert(lastStyle == 0 && lastColor == 0);
        return row;
    }

    void* __cdecl Texture(char const* name, void*)
    {
        assert(!std::strcmp(name, path) || !std::strncmp(name, "custom\\earthen\\", 15)
            || !std::strncmp(name, "custom\\naga\\sirus\\", 18)
            || HaranirPath(name));
        ++loads;
        return &texture;
    }

    void __fastcall Bind(void*, void*, unsigned slot, void* value)
    {
        assert(value == &texture || generatedTextures.contains(value));
        assert(slot < boundTextures.size());
        boundTextures[slot] = value;
        lastSlot = slot;
    }

    void __cdecl ReleaseTexture(void* value)
    {
        if (generatedTextures.erase(value))
            std::free(value);
        else
            assert(value == &texture);
    }

    void* __cdecl Layer(char const* name)
    {
        assert(!std::strcmp(name, path) || HaranirPath(name));
        ++loads;
        if (HaranirPath(name))
        {
            void* value = std::calloc(1, 0xb4);
            generatedLayers.insert(value);
            generatedLayerPaths[value] = name;
            return value;
        }
        return &newLayer;
    }

    void __cdecl ReleaseLayer(void* value)
    {
        if (generatedLayers.erase(value))
        {
            generatedLayerPaths.erase(value);
            std::free(*reinterpret_cast<void**>(static_cast<unsigned char*>(value) + 0xac));
            std::free(value);
        }
        else
            assert(value == &oldLayer || value == &newLayer);
        ++releases;
    }

    void __cdecl Register(unsigned, unsigned, unsigned, void*, void*, unsigned, unsigned)
    {
        ++registrations;
    }

    void __fastcall Visibility(void*, void*, unsigned first, unsigned last, int enabled)
    {
        if (first <= 10000 && last >= 10000)
            nagaBodyVisible = enabled != 0;
        if (first >= 3500 && last < 3600)
            vulperaEarrings = enabled ? first : 3500;
        for (unsigned i = 0; i < 8; ++i)
            if (first <= 2001 + i && last >= 2001 + i)
                earthenFootMask = enabled ? earthenFootMask | (1u << i) : earthenFootMask & ~(1u << i);
        if (first == last && enabled)
        {
            earthenHair = earthenHair || first == 4011;
            earthenBelt = earthenBelt || first == 4105;
        }
    }
}

int main(int argc, char** argv)
{
    assert(argc == 2);
    auto module = LoadLibraryA(argv[1]);
    assert(module);
    resolve = reinterpret_cast<Resolve>(GetProcAddress(module, "EsteriaSectionArguments"));
    auto direct = reinterpret_cast<bool(__cdecl*)(void*, unsigned, unsigned const*)>(
        GetProcAddress(module, "EsteriaDirectSection"));
    assert(resolve && direct);
    // Install mock engine calls only in this harness's own address space; WoW is never loaded or modified.
    void* getPage = Page(0x004F3BA0);
    void* texturePage = Page(0x004E8D30);
    void* releasePage = Page(0x0047BF30);
    void* bindPage = Page(0x00825260);
    void* dataPage = Page(0x00B6B864);
    Hook(0x004F3BA0, reinterpret_cast<void*>(&Section));
    Hook(0x004E8D30, reinterpret_cast<void*>(&Texture));
    Hook(0x00825260, reinterpret_cast<void*>(&Bind));
    Hook(0x0047BF30, reinterpret_cast<void*>(&ReleaseTexture));
    Hook(0x004F3930, reinterpret_cast<void*>(&Layer));
    Hook(0x004F31A0, reinterpret_cast<void*>(&ReleaseLayer));
    row[4] = row[5] = row[6] = static_cast<unsigned>(reinterpret_cast<std::uintptr_t>(path));
    unsigned char character[0x600]{};
    *reinterpret_cast<unsigned*>(character + 0x18) = 46;
    *reinterpret_cast<unsigned*>(character + 0x28) = 233;
    *reinterpret_cast<unsigned*>(character + 0x2C) = 219;
    *reinterpret_cast<unsigned*>(character + 0x24) = 128;
    *reinterpret_cast<void**>(character + 0x38) = &texture;
    unsigned hair[] = {1, 0};
    assert(direct(character, 1, hair));
    assert(lastKind == 3 && lastStyle == 0 && lastColor == 0 && lastSlot == 6);
    unsigned head[] = {0};
    assert(direct(character, 0, head));
    assert(lastKind == 0 && lastColor == 26 && lastSlot == 8);
    unsigned layer[] = {1, 0, 219, 233, 9, 0};
    *reinterpret_cast<void**>(character + 0x1A0) = &oldLayer;
    unsigned pending = 1;
    *reinterpret_cast<void**>(character + 0x52C) = &pending;
    assert(direct(character, 2, layer));
    assert(lastKind == 1 && lastStyle == 4 && lastColor == 26);
    assert(*reinterpret_cast<void**>(character + 0x1A0) == &newLayer);
    assert(releases == 1 && loads == 3 && pending == 0);
    assert(*reinterpret_cast<unsigned*>(character + 0x0C) & (1u << 9));
    *reinterpret_cast<unsigned*>(character + 0x18) = 47;
    assert(!direct(character, 1, hair) && loads == 3);
    auto registerExtra = reinterpret_cast<void(__cdecl*)()>(GetProcAddress(module, "EsteriaRegisterExtra"));
    auto unitExtra = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaUnitExtra"));
    auto setContext = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaAppearanceContext"));
    auto forget = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaForgetCharacter"));
    auto geometry = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaGeometry"));
    assert(geometry);
    assert(registerExtra && unitExtra && setContext && forget);
    void* registerPage = Page(0x004D5BA0);
    Hook(0x004D5BA0, reinterpret_cast<void*>(&Register));
    registerExtra();
    assert(registrations == 0); // The stock cache has no padding slot; registration corrupts neighboring units.
    unsigned char unit[0x1010]{};
    unsigned fields[0x8E]{};
    unsigned char component[0x600]{};
    *reinterpret_cast<unsigned*>(unit + 0x14) = 3;
    *reinterpret_cast<void**>(unit + 0xB4C) = component;
    *reinterpret_cast<void**>(unit + 0xD0) = fields;
    *reinterpret_cast<unsigned*>(component + 0x18) = 46;
    for (unsigned color = 0; color < 3; ++color)
    {
        fields[0x8D] = color;
        unitExtra(unit);
        setContext(component);
        unsigned arguments[] = {0, 46, 0, 0, 0, 0};
        resolve(arguments);
        assert(arguments[5] == 36 * color); // Network changes retain the independent sixth appearance byte.
    }
    forget(component);
    unsigned arguments[] = {0, 46, 0, 0, 77, 88};
    resolve(arguments);
    assert(arguments[4] == 77 && arguments[5] == 88); // Freed context cannot affect later resolutions.
    setContext(component);
    resolve(arguments);
    assert(arguments[5] == 0); // Reusing the address cannot retain the previous sixth byte.
    forget(component);
    // Actual Earthen regression: the server/network bytes remain encoded, but stock initialization
    // replaces the component with ordinary skin/face/hair/color values before the update callback.
    unsigned char playerData[0x20]{};
    *reinterpret_cast<unsigned*>(unit + 0x14) = 4;
    *reinterpret_cast<void**>(unit + 0x1008) = playerData;
    *reinterpret_cast<unsigned*>(component + 0x18) = 48;
    unsigned char encoded[] = {40, 79, 153, 68, 90};
    std::memcpy(playerData + 0x14, encoded, 5);
    fields[0x8D] = 43;
    unsigned const offsets[] = {0x28, 0x2C, 0x34, 0x24, 0x30};
    for (unsigned race : {48u, 49u})
    {
        *reinterpret_cast<unsigned*>(component + 0x18) = race;
        for (unsigned offset : offsets)
            *reinterpret_cast<unsigned*>(component + offset) = 0;
        unitExtra(unit); // No instance: restore fields without invoking the mocked compositor.
        for (unsigned i = 0; i < 5; ++i)
            assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == encoded[i]);
        // The shared stock sanitizer runs after unit updates and before the final render selection.
        for (unsigned offset : offsets)
            *reinterpret_cast<unsigned*>(component + offset) = 0;
        geometry(component);
        for (unsigned i = 0; i < 5; ++i)
            assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == encoded[i]);
    }
    forget(component);
    playerData[0x14] = 255; // Invalid authenticated data must never become a model field.
    *reinterpret_cast<unsigned*>(component + 0x28) = 0;
    unitExtra(unit);
    assert(*reinterpret_cast<unsigned*>(component + 0x28) == 0);
    *reinterpret_cast<unsigned*>(component + 0x18) = 46;
    *reinterpret_cast<unsigned*>(unit + 0x14) = 3;
    forget(component);
    // Initial unit updates precede model-component creation. Resolve the owner at the shared final
    // geometry callback instead of depending on an earlier update callback capturing this component.
    void* connectionPage = Page(0x00C79CE0);
    unsigned char connection[0x2ED4]{};
    unsigned char manager[0xB0]{};
    *reinterpret_cast<void**>(Address(0x00C79CE0)) = connection;
    *reinterpret_cast<void**>(connection + 0x2ED0) = manager;
    *reinterpret_cast<void**>(manager + 0xAC) = unit;
    *reinterpret_cast<unsigned*>(unit + 0x14) = 4;
    *reinterpret_cast<unsigned*>(component + 0x18) = 48;
    *reinterpret_cast<void**>(component + 0x38) = &texture;
    std::memcpy(playerData + 0x14, encoded, 5);
    Hook(0x0082C7C0, reinterpret_cast<void*>(&Visibility));
    geometry(component);
    for (unsigned i = 0; i < 5; ++i)
        assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == encoded[i]);
    assert(earthenHair && earthenBelt);
    assert(earthenFootMask == 1); // One authored foot mesh, never eight overlapping alternate shapes.
    *reinterpret_cast<unsigned*>(component + 0x440) = 10141; // Recruit's Boots, from the live character.
    geometry(component);
    assert(earthenFootMask == 2); // Rounded boot foot replaces toes.
    *reinterpret_cast<unsigned*>(component + 0x440) = 0;
    geometry(component);
    assert(earthenFootMask == 1); // Removing boots restores bare toes, without resetting customization.
    for (unsigned i = 0; i < 5; ++i)
        assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == encoded[i]);
    forget(component);
    VirtualFree(connectionPage, 0, MEM_RELEASE);
    // Character Select creates a blank component before its first sparse base-section validation.
    auto enumExtra = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaEnumExtra"));
    auto selectExtra = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaSelectExtra"));
    assert(enumExtra && selectExtra);
    unsigned char roster[0x198]{};
    unsigned char preview[0x600]{};
    std::uint64_t guid = 518;
    std::memcpy(roster, &guid, sizeof(guid));
    roster[0x178] = 48;
    std::memcpy(roster + 0x17B, encoded, 5);
    *reinterpret_cast<void**>(roster + 0x188) = preview;
    *reinterpret_cast<unsigned*>(Address(0x00B6B23C)) = 1;
    *reinterpret_cast<void**>(Address(0x00B6B240)) = roster;
    unsigned char trailer[17]{};
    std::memcpy(trailer, &guid, sizeof(guid));
    trailer[8] = 43;
    *reinterpret_cast<unsigned*>(trailer + 9) = 1;
    *reinterpret_cast<unsigned*>(trailer + 13) = 0x31455848;
    unsigned packet[] = {0, reinterpret_cast<unsigned>(trailer), 0, sizeof(trailer), sizeof(trailer)};
    enumExtra(packet);
    selectExtra(preview);
    unsigned firstSection[] = {0, 48, 0, 0, 0, 40};
    resolve(firstSection);
    assert(firstSection[4] == 0 && firstSection[5] == 12);
    assert(*reinterpret_cast<unsigned*>(preview + 0x18) == 48);
    for (unsigned i = 0; i < 5; ++i)
        assert(*reinterpret_cast<unsigned*>(preview + offsets[i]) == encoded[i]);
    forget(preview);
    // Mixed legacy/Haranir roster tails and late stock initialization preserve all extension bytes.
    unsigned char mixed[42]{};
    std::memcpy(mixed + 1, &guid, sizeof(guid));
    mixed[9] = 43;
    *reinterpret_cast<unsigned*>(mixed + 10) = 1;
    *reinterpret_cast<unsigned*>(mixed + 14) = 0x31455848;
    std::uint64_t haranirGuid = 519;
    std::memcpy(mixed + 18, &haranirGuid, sizeof(haranirGuid));
    std::array<std::uint8_t, 13> wide{};
    for (unsigned i = 0; i < wide.size(); ++i)
        wide[i] = static_cast<std::uint8_t>(HaranirAppearance::MaleCapacities[i] - 1);
    auto extra = HaranirAppearance::Extra(wide);
    std::memcpy(mixed + 26, &extra, sizeof(extra));
    *reinterpret_cast<unsigned*>(mixed + 34) = 1;
    *reinterpret_cast<unsigned*>(mixed + 38) = 0x32455848;
    unsigned widePacket[] = {0, reinterpret_cast<unsigned>(mixed), 0, sizeof(mixed), sizeof(mixed)};
    enumExtra(widePacket);
    assert(widePacket[4] == 1);
    std::memcpy(roster, &haranirGuid, sizeof(haranirGuid));
    roster[0x178] = 50;
    std::memcpy(roster + 0x17B, wide.data(), 5);
    selectExtra(preview);
    for (unsigned i = 0; i < 5; ++i)
        assert(*reinterpret_cast<unsigned*>(preview + offsets[i]) == wide[i]);
    forget(preview);
    unsigned objectFields[6]{};
    objectFields[5] = static_cast<unsigned>(extra >> 32);
    *reinterpret_cast<void**>(unit + 8) = objectFields;
    fields[0x8D] = static_cast<unsigned>(extra);
    *reinterpret_cast<unsigned*>(component + 0x18) = 50;
    *reinterpret_cast<void**>(component + 0x38) = nullptr;
    std::memcpy(playerData + 0x14, wide.data(), 5);
    unitExtra(unit);
    for (unsigned i = 0; i < 5; ++i)
        assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == wide[i]);
    // CMSG_CHAR_CREATE appends exactly the uint64 plus its version signature using the native byte writer.
    Hook(0x0047AFE0, reinterpret_cast<void*>(&AppendByte));
    auto createExtra = reinterpret_cast<void(__cdecl*)(void*)>(GetProcAddress(module, "EsteriaCreateExtra"));
    assert(createExtra);
    *reinterpret_cast<void**>(Address(0x00B6B1A0)) = component;
    unsigned char createBytes[32]{};
    unsigned createPacket[] = {0, reinterpret_cast<unsigned>(createBytes), 0, sizeof(createBytes), 1};
    createExtra(createPacket);
    assert(createPacket[4] == 13 && createBytes[0] == 0);
    assert(!std::memcmp(createBytes + 1, &extra, 8));
    assert(*reinterpret_cast<unsigned*>(createBytes + 9) == 0x31435248);
    *reinterpret_cast<void**>(Address(0x00B6B1A0)) = nullptr;
    // Both genders generate the compositor's indexed body/face fragments from the complete catalog.
    void* haranirConnectionPage = Page(0x00C79CE0);
    void* allocationPage = Page(0x0076E540);
    void* decoderPage = Page(0x004B7BD0);
    Hook(0x0076E540, reinterpret_cast<void*>(&Allocate));
    Hook(0x004B8770, reinterpret_cast<void*>(&TextureConstructor));
    Hook(0x0047BF50, reinterpret_cast<void*>(&AddReference));
    Hook(0x004B7BD0, reinterpret_cast<void*>(&DecodeThunk));
    *reinterpret_cast<void**>(component + 0x38) = &texture;
    unsigned haranirBody[] = {0, 0, 0, 0, 9, 0};
    assert(direct(component, 2, haranirBody));
    auto* loaded = *reinterpret_cast<unsigned char**>(component + 0x194);
    assert(loaded && *reinterpret_cast<void**>(loaded + 0xac));
    assert(!(*reinterpret_cast<unsigned*>(loaded + 0xb0) & 0x100000));
    geometry(component);
    assert(decodedTextures == 7);
    forget(component);
    for (unsigned i = 0; i < wide.size(); ++i)
        wide[i] = static_cast<std::uint8_t>(HaranirAppearance::FemaleCapacities[i] - 1);
    extra = HaranirAppearance::Extra(wide);
    fields[0x8D] = static_cast<unsigned>(extra);
    objectFields[5] = static_cast<unsigned>(extra >> 32);
    *reinterpret_cast<unsigned*>(component + 0x18) = 51;
    *reinterpret_cast<unsigned*>(component + 0x1C) = 1;
    std::memcpy(playerData + 0x14, wide.data(), 5);
    unitExtra(unit);
    for (unsigned i = 0; i < 5; ++i)
        assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == wide[i]);
    assert(direct(component, 2, haranirBody));
    forget(component);
    assert(generatedTextures.empty());
    ReleaseLayer(*reinterpret_cast<void**>(component + 0x194));
    *reinterpret_cast<void**>(component + 0x194) = nullptr;
    // Vulpera retains the five stock bytes: no creation trailer and no stale padding dependency.
    for (unsigned gender = 0; gender < 2; ++gender)
    {
        *reinterpret_cast<unsigned*>(component + 0x18) = 20;
        *reinterpret_cast<unsigned*>(component + 0x1C) = gender;
        *reinterpret_cast<unsigned*>(component + 0x20) = 2;
        std::array<std::uint8_t, 5> appearance = {6, 7, 3, 38, 0};
        assert(VulperaAppearance::ValidateClass(gender, 2, appearance));
        std::memcpy(playerData + 0x14, appearance.data(), 5);
        unsigned priorDecodes = decodedTextures;
        unitExtra(unit);
        for (unsigned i = 0; i < appearance.size(); ++i)
            assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == appearance[i]);
        assert(direct(component, 2, haranirBody));
        loaded = *reinterpret_cast<unsigned char**>(component + 0x194);
        assert(loaded && *reinterpret_cast<void**>(loaded + 0xac));
        geometry(component);
        assert(decodedTextures == priorDecodes + 2); // Source eyes and complete independent skinExtra square.
        for (unsigned slot : {5u, 8u})
        {
            assert(generatedTextures.contains(boundTextures[slot]));
            std::string prefix = "\\Vulpera\\" + std::to_string(gender)
                + (slot == 5 ? "-3-" : "-4-");
            assert(std::strstr(static_cast<char*>(boundTextures[slot]) + 0x6c, prefix.c_str()));
        }
        for (unsigned slot = 0; slot < 2; ++slot)
        {
            unsigned faceArguments[] = {1, slot, 0, 0, slot ? 8u : 9u, 0};
            assert(direct(component, 2, faceArguments));
            void* faceLayer = *reinterpret_cast<void**>(component + 0x1a0 + slot * 4);
            assert(faceLayer && generatedLayers.contains(faceLayer));
            assert(generatedLayerPaths[faceLayer].ends_with(slot ? "-upper.blp" : "-lower.blp"));
            auto* pixels = *reinterpret_cast<unsigned char**>(static_cast<unsigned char*>(faceLayer) + 0xac);
            assert(pixels && *reinterpret_cast<unsigned*>(pixels + 12) == 256);
            assert(*reinterpret_cast<unsigned*>(pixels + 16) == (slot ? 64 : 128));
            // These are authored tail fur pixels in Wrath's face destinations, not blank face placeholders.
            unsigned offset = *reinterpret_cast<unsigned*>(pixels + 20);
            unsigned palette = 148 + pixels[offset + (slot ? 60 : 16) * 256 + 3] * 4;
            assert(pixels[palette] || pixels[palette + 1] || pixels[palette + 2]);
            ReleaseLayer(faceLayer);
            *reinterpret_cast<void**>(component + 0x1a0 + slot * 4) = nullptr;
        }
        unsigned extraSkinArguments[] = {0};
        assert(direct(component, 0, extraSkinArguments)); // Reuses owned decoded textures, no filename reload.
        assert(decodedTextures == priorDecodes + 2);
        if (gender == 0)
        {
            assert(vulperaEarrings == 3504);
            *reinterpret_cast<unsigned*>(component + 0x428) = 23151; // Retail visibility285 hides earrings.
            geometry(component);
            assert(vulperaEarrings == 3500);
            *reinterpret_cast<unsigned*>(component + 0x428) = 0;
            geometry(component);
            assert(vulperaEarrings == 3504);
        }
        *reinterpret_cast<void**>(Address(0x00B6B1A0)) = component;
        createPacket[4] = 1;
        createExtra(createPacket);
        assert(createPacket[4] == 1);
        *reinterpret_cast<void**>(Address(0x00B6B1A0)) = nullptr;
        forget(component);
        assert(generatedTextures.empty());
        ReleaseLayer(*reinterpret_cast<void**>(component + 0x194));
        *reinterpret_cast<void**>(component + 0x194) = nullptr;
    }
    for (unsigned race : {54u, 55u, 56u, 57u, 58u, 59u})
    {
        for (unsigned gender = 0; gender < (race == 54 ? 2u : 1u); ++gender)
        {
            *reinterpret_cast<unsigned*>(component + 0x18) = race;
            *reinterpret_cast<unsigned*>(component + 0x1C) = gender;
            std::array<std::uint8_t, 5> appearance{};
            auto const& choices = CreatureAppearance::Options(race, gender);
            for (unsigned i = 0; i < appearance.size(); ++i)
                appearance[i] = static_cast<std::uint8_t>(choices[i].count - 1);
            assert(CreatureAppearance::Validate(race, gender, appearance));
            assert(!CreatureAppearance::GenderAllowed(race, 2));
            std::memcpy(playerData + 0x14, appearance.data(), appearance.size());
            fields[0x8D] = 255; // These profiles never interpret padding as an extra appearance byte.
            unsigned priorDecodes = decodedTextures;
            unsigned priorLoads = loads;
            boundTextures.fill(nullptr);
            unitExtra(unit);
            for (unsigned i = 0; i < appearance.size(); ++i)
                assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == appearance[i]);
            assert(direct(component, 2, haranirBody));
            assert(*reinterpret_cast<void**>(component + 0x194));
            geometry(component);
            if (race == 54)
            {
                assert(loads >= priorLoads + 2);
                assert(boundTextures[8] == &texture);
                assert(boundTextures[6] == &texture);
                assert(*reinterpret_cast<unsigned*>(component + 0x18C) == 1800);
                *reinterpret_cast<unsigned*>(component + 0x428) = 32028; // Giantstalker's Helmet.
                geometry(component);
                assert(*reinterpret_cast<unsigned*>(component + 0x144) == 0); // Hide crests, not the base body.
                assert(*reinterpret_cast<unsigned*>(component + 0x150) == 300);
                assert(nagaBodyVisible);
                *reinterpret_cast<unsigned*>(component + 0x428) = 0;
                geometry(component);
                assert(*reinterpret_cast<unsigned*>(component + 0x144) == 5);
                assert(*reinterpret_cast<unsigned*>(component + 0x150) != 300);
                assert(nagaBodyVisible);
            }
            else
            {
                assert(decodedTextures > priorDecodes);
                assert(generatedTextures.contains(boundTextures[6]));
            }
            if (race == 56 || race == 57)
            {
                assert(*reinterpret_cast<unsigned*>(component + 0x18C) == 1801); // Base waist is not a hole.
                *reinterpret_cast<unsigned*>(component + 0x440) = 10141; // Reported Recruit's Boots.
                geometry(component);
                assert(earthenFootMask == 2);
                *reinterpret_cast<unsigned*>(component + 0x440) = 0;
                geometry(component);
                assert(earthenFootMask == 1);
                for (unsigned i = 0; i < appearance.size(); ++i)
                    assert(*reinterpret_cast<unsigned*>(component + offsets[i]) == appearance[i]);
            }
            *reinterpret_cast<void**>(Address(0x00B6B1A0)) = component;
            createPacket[4] = 1;
            createExtra(createPacket);
            assert(createPacket[4] == 1);
            *reinterpret_cast<void**>(Address(0x00B6B1A0)) = nullptr;
            forget(component);
            assert(generatedTextures.empty());
            ReleaseLayer(*reinterpret_cast<void**>(component + 0x194));
            *reinterpret_cast<void**>(component + 0x194) = nullptr;
        }
    }
    VirtualFree(haranirConnectionPage, 0, MEM_RELEASE);
    VirtualFree(allocationPage, 0, MEM_RELEASE);
    VirtualFree(decoderPage, 0, MEM_RELEASE);
    auto* guarded = static_cast<unsigned char*>(VirtualAlloc(nullptr, 8192, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
    assert(guarded);
    DWORD protection = 0;
    assert(VirtualProtect(guarded + 4096, 4096, PAGE_NOACCESS, &protection));
    auto* item = guarded + 4096 - 32;
    *reinterpret_cast<unsigned*>(item + 0x14) = 1;
    unitExtra(item); // The shared update hook must not read Unit fields from an item.
    VirtualFree(guarded, 0, MEM_RELEASE);
    void* pages[] = {getPage, texturePage, releasePage, bindPage, dataPage, registerPage};
    for (void* page : pages)
        VirtualFree(page, 0, MEM_RELEASE);
    std::puts("Highmountain materials/lifetime: PASS "
        "(getters, stock race, uncached padding, live sixth byte, teardown)");
    FreeLibrary(module);
}
