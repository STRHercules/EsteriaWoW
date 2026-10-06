#include <windows.h>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
#include <array>
#include <string>
#include <initializer_list>

namespace
{
    template<class T>
    T& Field(void* p, unsigned offset)
    {
        return *reinterpret_cast<T*>(static_cast<unsigned char*>(p) + offset);
    }

    std::uintptr_t Address(std::uintptr_t preferred)
    {
        return reinterpret_cast<std::uintptr_t>(GetModuleHandleW(nullptr)) + preferred - 0x00400000;
    }

    void Hook(std::uintptr_t preferred, void* function)
    {
        auto* code = reinterpret_cast<unsigned char*>(Address(preferred));
        code[0] = 0xE9;
        *reinterpret_cast<int*>(code + 1) = static_cast<int>(
            reinterpret_cast<std::uintptr_t>(function) - reinterpret_cast<std::uintptr_t>(code) - 5);
    }

    std::vector<void*> children;
    unsigned created, released, detached;
    float scale;
    bool attachmentAvailable = true;
    std::string modelPath;

    void* __fastcall Create(void* scene, void*, char const* path, unsigned flags)
    {
        assert(scene && !flags);
        modelPath = path;
        auto* child = new unsigned char[0x200]{};
        Field<unsigned>(child, 0) = 1;
        children.push_back(child);
        ++created;
        return child;
    }

    int __fastcall HasAttachment(void*, void*, unsigned attachment)
    {
        assert(attachment == 16);
        return attachmentAvailable;
    }

    void __fastcall Attach(void* child, void*, void* parent, unsigned attachment, void* transform, int force)
    {
        assert(attachment == 16 && !transform && !force);
        Field<void*>(child, 0x48) = parent;
        ++Field<unsigned>(child, 0);
    }

    void __fastcall Detach(void* child, void*)
    {
        assert(Field<void*>(child, 0x48) && Field<unsigned>(child, 0) == 2);
        Field<void*>(child, 0x48) = nullptr;
        --Field<unsigned>(child, 0);
        ++detached;
    }

    void __fastcall Release(void* child, void*)
    {
        assert(!Field<void*>(child, 0x48) && Field<unsigned>(child, 0) == 1);
        Field<unsigned>(child, 0) = 0;
        ++released;
    }

    void __fastcall Sequence(void*, void*, int bone, int animation, int variation,
        int time, float speed, int blend, int enabled)
    {
        assert(bone == -1 && animation == 0 && variation == -1 && time == 0
            && speed == 1 && blend == 1 && enabled == 1);
    }

    void __fastcall Placement(void*, void*, float const* origin, float facing, float value)
    {
        assert(!origin[0] && !origin[1] && !origin[2] && !facing);
        scale = value;
    }
}

int main(int argc, char** argv)
{
    assert(argc == 2);
    for (unsigned address : {0x00810000u, 0x00820000u, 0x00830000u, 0x00B60000u})
        assert(VirtualAlloc(reinterpret_cast<void*>(Address(address)), 65536,
            MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE) == reinterpret_cast<void*>(Address(address)));
    Hook(0x0081F8F0, reinterpret_cast<void*>(Create));
    Hook(0x008273D0, reinterpret_cast<void*>(HasAttachment));
    Hook(0x00831630, reinterpret_cast<void*>(Attach));
    Hook(0x008274F0, reinterpret_cast<void*>(Detach));
    Hook(0x00824ED0, reinterpret_cast<void*>(Release));
    Hook(0x00832AB0, reinterpret_cast<void*>(Sequence));
    Hook(0x008251D0, reinterpret_cast<void*>(Placement));

    // Use actual staged catalog records; do not substitute a fixture over the deployment catalog.
    std::string catalog = argv[1];
    catalog = catalog.substr(0, catalog.find_last_of("\\/")) + "\\EsteriaCosmeticWings.bin";
    FILE* file = nullptr;
    assert(!fopen_s(&file, catalog.c_str(), "rb"));
    struct Record
    {
        unsigned spell, attachment;
        float scale;
        char path[260];
    };
    unsigned header[3]{};
    Record definition{};
    assert(std::fread(header, sizeof(header), 1, file) == 1 && header[0] == 0x31475743
        && header[1] == 1 && header[2] > 0);
    assert(std::fread(&definition, sizeof(definition), 1, file) == 1);
    std::fclose(file);

    HMODULE module = LoadLibraryA(argv[1]);
    assert(module);
    using Invoke = void(__cdecl*)(void*);
    auto enumExtra = reinterpret_cast<Invoke>(GetProcAddress(module, "EsteriaEnumExtra"));
    auto selectExtra = reinterpret_cast<Invoke>(GetProcAddress(module, "EsteriaSelectExtra"));
    auto geometry = reinterpret_cast<Invoke>(GetProcAddress(module, "EsteriaGeometry"));
    auto forget = reinterpret_cast<Invoke>(GetProcAddress(module, "EsteriaForgetCharacter"));
    assert(enumExtra && selectExtra && geometry && forget);

    std::array<unsigned char, 128> bytes{};
    unsigned packet[6]{};
    Field<void*>(packet, 4) = bytes.data();
    Field<unsigned>(packet, 8) = 37; // Reader bases need not be zero.
    Field<unsigned>(packet, 12) = static_cast<unsigned>(bytes.size());
    unsigned cursor = 1;
    auto append = [&](auto value)
    {
        std::memcpy(bytes.data() + cursor, &value, sizeof(value));
        cursor += sizeof(value);
    };
    append(std::uint64_t{11}); append(std::uint8_t{81}); append(1u); append(0x31455848u);
    append(std::uint64_t{22}); append(std::uint64_t{0x123456789ABC}); append(1u); append(0x32455848u);
    append(std::uint64_t{11}); append(definition.spell);
    append(std::uint64_t{22}); append(12345u); // A non-wing spell must never spawn a preview attachment.
    append(2u); append(0x31475743u);
    Field<unsigned>(packet, 16) = 37 + cursor;
    enumExtra(packet);
    assert(Field<unsigned>(packet, 16) == 38); // All three trailers stripped, stock roster untouched.

    unsigned char rows[3 * 0x198]{};
    unsigned char first[0x200]{}, second[0x200]{}, creator[0x200]{};
    unsigned char parent[0x200]{}, replacement[0x200]{};
    unsigned scene{};
    for (void* value : {static_cast<void*>(parent), static_cast<void*>(replacement)})
    {
        Field<unsigned>(value, 0x10) = 1;
        Field<void*>(value, 0x28) = &scene;
    }
    Field<unsigned>(first, 0x18) = Field<unsigned>(second, 0x18) = Field<unsigned>(creator, 0x18) = 1;
    Field<void*>(first, 0x38) = parent;
    Field<void*>(second, 0x38) = replacement;
    Field<void*>(creator, 0x38) = replacement;
    Field<std::uint64_t>(rows, 0) = 11;
    Field<void*>(rows, 0x188) = first;
    rows[0x178] = 1;
    Field<std::uint64_t>(rows, 0x198) = 22;
    Field<void*>(rows, 0x198 + 0x188) = second;
    rows[0x198 + 0x178] = 1;
    *reinterpret_cast<void**>(Address(0x00B6B240)) = rows;
    *reinterpret_cast<unsigned*>(Address(0x00B6B23C)) = 2;
    selectExtra(first);
    assert(created == 1 && modelPath == definition.path && scale == definition.scale);
    geometry(first); geometry(first); selectExtra(first);
    assert(created == 1 && !released); // Repeated renders must not stack copies.
    selectExtra(second); geometry(second); geometry(creator);
    assert(created == 1); // Other characters and the creator inherit no wings.

    Field<void*>(first, 0x38) = replacement;
    geometry(first);
    assert(created == 2 && detached == 1 && released == 1); // Parent replaced by stock preview refresh.
    auto* child = children.back();
    Detach(child, nullptr); // Stock teardown may remove the parent-owned reference before our hook.
    geometry(first);
    assert(created == 3 && released == 2);
    forget(first); forget(first);
    assert(detached == 3 && released == 3); // Cleanup and address reuse are safe.
    geometry(first);
    assert(created == 3);

    selectExtra(first);
    assert(created == 4);
    Field<unsigned>(packet, 16) = 38;
    enumExtra(packet); // Fresh no-wing roster clears an earlier equipped aura.
    selectExtra(first);
    assert(released == 4 && detached == 4);
    geometry(first);
    assert(created == 4);

    // Invalid counts, truncated tails and null buffers cannot create wing state.
    cursor = 1;
    append(std::uint64_t{11}); append(definition.spell); append(101u); append(0x31475743u);
    Field<unsigned>(packet, 16) = 37 + cursor;
    enumExtra(packet);
    assert(Field<unsigned>(packet, 16) == 37 + cursor);
    selectExtra(first);
    assert(created == 4);
    cursor = 1;
    append(std::uint64_t{11}); append(definition.spell); append(1u); append(0x31475743u);
    Field<unsigned>(packet, 16) = 37 + cursor;
    enumExtra(packet);
    attachmentAvailable = false;
    selectExtra(first);
    assert(created == 4);
    attachmentAvailable = true;
    Field<unsigned>(replacement, 0x10) = 0;
    geometry(first);
    assert(created == 4); // Delayed parent loading retries without creating a dangling wing.
    Field<unsigned>(replacement, 0x10) = 1;
    geometry(first);
    assert(created == 5);
    forget(first);
    assert(released == 5 && detached == 5);
    Field<void*>(packet, 4) = nullptr;
    enumExtra(packet);
    enumExtra(nullptr);
    for (auto* value : children)
        delete[] static_cast<unsigned char*>(value);
    FreeLibrary(module);
    std::puts("Cosmetic wings: PASS (mixed trailers, isolation, repeats, parent refresh, removal, cleanup)");
}
