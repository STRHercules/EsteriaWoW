#include <windows.h>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>

namespace
{
    using Resolve = void(__cdecl*)(unsigned*);
    Resolve resolve;
    unsigned row[10]{};
    unsigned lastKind, lastStyle, lastColor, lastSlot, loads, releases;
    unsigned texture, oldLayer, newLayer;
    unsigned registrations;
    char path[] = "custom\\highmountain\\fixture.blp";

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
        assert(!std::strcmp(name, path));
        ++loads;
        return &texture;
    }

    void __fastcall Bind(void*, void*, unsigned slot, void* value)
    {
        assert(value == &texture);
        lastSlot = slot;
    }

    void __cdecl ReleaseTexture(void* value)
    {
        assert(value == &texture);
    }

    void* __cdecl Layer(char const* name)
    {
        assert(!std::strcmp(name, path));
        ++loads;
        return &newLayer;
    }

    void __cdecl ReleaseLayer(void* value)
    {
        assert(value == &oldLayer || value == &newLayer);
        ++releases;
    }

    void __cdecl Register(unsigned, unsigned, unsigned, void*, void*, unsigned, unsigned)
    {
        ++registrations;
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
    assert(registerExtra && unitExtra && setContext && forget);
    void* registerPage = Page(0x004D5BA0);
    Hook(0x004D5BA0, reinterpret_cast<void*>(&Register));
    registerExtra();
    assert(registrations == 0); // The stock cache has no padding slot; registration corrupts neighboring units.
    unsigned char unit[0xB50]{};
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
