// races-64-esteria: expand the customized Esteria 3.3.5a client to 64 race IDs.

#include "wxl/PluginApi.h"

#include <windows.h>

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>

namespace
{
    static_assert(sizeof(void*) == 4, "races-64-esteria must be built as a Win32 DLL");

    constexpr uintptr_t kPreferredImageBase = 0x00400000;

    constexpr uintptr_t kEsteriaFoundationSignatureVa = 0x00DFE000;
    constexpr uintptr_t kOriginalMemoryTableVa = 0x00DFE220;
    constexpr uintptr_t kOriginalRaceNameTableVa = 0x00DFE400;
    constexpr uintptr_t kRaceNamePatchVa = 0x004CDA43;
    constexpr uintptr_t kMemoryTableClearSizePatchVa = 0x004E1C34;
    constexpr uintptr_t kMemoryTableCleanupCountPatchVa = 0x004E1E9B;
    constexpr uintptr_t kRaceRestrictionExtendedBranchVa = 0x004DFAF0;
    constexpr uintptr_t kRaceRestrictionErrorVa = 0x004DFC32;
    constexpr uintptr_t kRaceRestrictionResultVa = 0x004DFC18;
    constexpr uintptr_t kCharacterLimitVa = 0x00464C4F;

    constexpr std::array<uintptr_t, 8> kMemoryTablePatchVas = {
        0x004E157D, 0x004E16A3, 0x004E15B5, 0x004E20EE,
        0x004E222A, 0x004E2127, 0x004E1E94, 0x004E1C3A,
    };

    constexpr char kEsteriaFoundationSignature[] = "ESTERIA_CLIENT_FOUNDATION_V3";
    constexpr uint32_t kOriginalClearSize = 0x100;
    constexpr uint32_t kOriginalCleanupCount = 22;
    constexpr uint8_t kExpectedCharacterLimit = 0x64;
    constexpr uint32_t kRaceCount = 64;
    constexpr uint32_t kSexCount = 2;
    constexpr uint32_t kExistingRaceNameCount = 32;
    constexpr uint32_t kFirstFallbackRace = 28;
    constexpr size_t kOriginalMemoryTableSize = 0x100;
    constexpr size_t kMemoryTableSize = kRaceCount * kSexCount * sizeof(uint32_t);
    constexpr size_t kRaceNameTableSize = kRaceCount * sizeof(uint32_t);
    constexpr size_t kDataSize = kMemoryTableSize + kRaceNameTableSize + sizeof(uint32_t);

    constexpr std::array<uint8_t, 6> kOriginalExtendedRaceBranch = {
        0x0F, 0x87, 0x3C, 0x01, 0x00, 0x00,
    };

    uint8_t* g_data = nullptr;
    uint8_t* g_thunk = nullptr;

    uintptr_t RuntimeAddress(uintptr_t preferredVa)
    {
        const auto imageBase = reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
        return imageBase + (preferredVa - kPreferredImageBase);
    }

    template <typename T>
    T Read(uintptr_t preferredVa)
    {
        T value{};
        std::memcpy(&value, reinterpret_cast<const void*>(RuntimeAddress(preferredVa)), sizeof(value));
        return value;
    }

    bool Matches(uintptr_t preferredVa, const void* expected, size_t size)
    {
        return std::memcmp(reinterpret_cast<const void*>(RuntimeAddress(preferredVa)), expected, size) == 0;
    }

    bool WriteMemory(void* destination, const void* source, size_t size)
    {
        DWORD previousProtection = 0;
        if (!VirtualProtect(destination, size, PAGE_EXECUTE_READWRITE, &previousProtection))
            return false;

        std::memcpy(destination, source, size);
        FlushInstructionCache(GetCurrentProcess(), destination, size);

        DWORD ignored = 0;
        return VirtualProtect(destination, size, previousProtection, &ignored) != FALSE;
    }

    bool FitsRelativeBranch(uintptr_t instructionEnd, uintptr_t target)
    {
        const int64_t displacement = static_cast<int64_t>(target) - static_cast<int64_t>(instructionEnd);
        return displacement >= std::numeric_limits<int32_t>::min()
            && displacement <= std::numeric_limits<int32_t>::max();
    }

    int32_t RelativeBranch(uintptr_t instructionEnd, uintptr_t target)
    {
        return static_cast<int32_t>(static_cast<int64_t>(target) - static_cast<int64_t>(instructionEnd));
    }

    struct Patch
    {
        uintptr_t address;
        size_t size;
        std::array<uint8_t, 6> replacement{};
        std::array<uint8_t, 6> original{};
    };

    template <typename T>
    Patch MakePatch(uintptr_t preferredVa, const T& replacement)
    {
        static_assert(sizeof(T) <= 6);
        Patch patch{ RuntimeAddress(preferredVa), sizeof(T) };
        std::memcpy(patch.replacement.data(), &replacement, sizeof(T));
        std::memcpy(patch.original.data(), reinterpret_cast<const void*>(patch.address), sizeof(T));
        return patch;
    }

    bool ApplyPatches(std::array<Patch, 12>& patches)
    {
        for (size_t applied = 0; applied < patches.size(); ++applied)
        {
            Patch& patch = patches[applied];
            if (!WriteMemory(reinterpret_cast<void*>(patch.address), patch.replacement.data(), patch.size))
            {
                // Include the current entry when protection restoration failed after its bytes changed.
                for (size_t rollback = applied + 1; rollback > 0; --rollback)
                {
                    Patch& previous = patches[rollback - 1];
                    WriteMemory(reinterpret_cast<void*>(previous.address), previous.original.data(),
                                previous.size);
                }
                return false;
            }
        }
        return true;
    }

    bool HasExpectedClientImage()
    {
        if (!Matches(kEsteriaFoundationSignatureVa, kEsteriaFoundationSignature,
                     sizeof(kEsteriaFoundationSignature))
            || Read<uint32_t>(kRaceNamePatchVa)
                != static_cast<uint32_t>(RuntimeAddress(kOriginalRaceNameTableVa))
            || Read<uint32_t>(kMemoryTableClearSizePatchVa) != kOriginalClearSize
            || Read<uint32_t>(kMemoryTableCleanupCountPatchVa) != kOriginalCleanupCount
            || Read<uint8_t>(kCharacterLimitVa) != kExpectedCharacterLimit
            || !Matches(kRaceRestrictionExtendedBranchVa, kOriginalExtendedRaceBranch.data(),
                        kOriginalExtendedRaceBranch.size()))
            return false;

        const uint32_t expectedMemoryTable = static_cast<uint32_t>(RuntimeAddress(kOriginalMemoryTableVa));
        for (const uintptr_t address : kMemoryTablePatchVas)
            if (Read<uint32_t>(address) != expectedMemoryTable)
                return false;

        return true;
    }

    bool AllocateTables()
    {
        g_data = static_cast<uint8_t*>(
            VirtualAlloc(nullptr, kDataSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
        if (!g_data) return false;

        std::memcpy(g_data, reinterpret_cast<const void*>(RuntimeAddress(kOriginalMemoryTableVa)),
                    kOriginalMemoryTableSize);

        auto* const raceNames = reinterpret_cast<uint32_t*>(g_data + kMemoryTableSize);
        auto* const dummy = reinterpret_cast<uint32_t*>(g_data + kMemoryTableSize + kRaceNameTableSize);
        std::memcpy(raceNames, reinterpret_cast<const void*>(RuntimeAddress(kOriginalRaceNameTableVa)),
                    kExistingRaceNameCount * sizeof(uint32_t));

        const uint32_t dummyAddress = static_cast<uint32_t>(reinterpret_cast<uintptr_t>(dummy));
        for (uint32_t race = kFirstFallbackRace; race < kRaceCount; ++race)
            raceNames[race] = dummyAddress;

        return true;
    }

    bool AllocateRestrictionThunk()
    {
        constexpr size_t kThunkSize = 25;
        g_thunk = static_cast<uint8_t*>(
            VirtualAlloc(nullptr, kThunkSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
        if (!g_thunk) return false;

        std::array<uint8_t, kThunkSize> thunk = {
            0x83, 0xFF, 0x0C,                         // cmp edi, 12
            0x0F, 0x82, 0, 0, 0, 0,                  // jb  stock error
            0x83, 0xFF, 0x3F,                         // cmp edi, 63
            0x0F, 0x87, 0, 0, 0, 0,                  // ja  stock error
            0xD9, 0xEE,                               // fldz
            0xE9, 0, 0, 0, 0,                        // jmp common Lua-result path
        };

        const uintptr_t thunkAddress = reinterpret_cast<uintptr_t>(g_thunk);
        const uintptr_t errorAddress = RuntimeAddress(kRaceRestrictionErrorVa);
        const uintptr_t resultAddress = RuntimeAddress(kRaceRestrictionResultVa);
        if (!FitsRelativeBranch(thunkAddress + 9, errorAddress)
            || !FitsRelativeBranch(thunkAddress + 18, errorAddress)
            || !FitsRelativeBranch(thunkAddress + 25, resultAddress)
            || !FitsRelativeBranch(RuntimeAddress(kRaceRestrictionExtendedBranchVa) + 6, thunkAddress))
            return false;

        const int32_t lowerError = RelativeBranch(thunkAddress + 9, errorAddress);
        const int32_t upperError = RelativeBranch(thunkAddress + 18, errorAddress);
        const int32_t result = RelativeBranch(thunkAddress + 25, resultAddress);
        std::memcpy(thunk.data() + 5, &lowerError, sizeof(lowerError));
        std::memcpy(thunk.data() + 14, &upperError, sizeof(upperError));
        std::memcpy(thunk.data() + 21, &result, sizeof(result));
        std::memcpy(g_thunk, thunk.data(), thunk.size());

        DWORD previousProtection = 0;
        return VirtualProtect(g_thunk, kThunkSize, PAGE_EXECUTE_READ, &previousProtection) != FALSE;
    }

    void ReleaseAllocations()
    {
        if (g_thunk) VirtualFree(g_thunk, 0, MEM_RELEASE);
        if (g_data) VirtualFree(g_data, 0, MEM_RELEASE);
        g_thunk = nullptr;
        g_data = nullptr;
    }

    bool Install()
    {
        if (g_data && g_thunk)
            return true;
        if (g_data || g_thunk)
        {
            ReleaseAllocations();
            return false;
        }

        if (!HasExpectedClientImage() || !AllocateTables() || !AllocateRestrictionThunk())
        {
            ReleaseAllocations();
            return false;
        }

        const uint32_t memoryTable = static_cast<uint32_t>(reinterpret_cast<uintptr_t>(g_data));
        const uint32_t raceNameTable = memoryTable + static_cast<uint32_t>(kMemoryTableSize);
        const uint32_t clearSize = static_cast<uint32_t>(kMemoryTableSize);
        const uint32_t cleanupCount = kRaceCount;

        std::array<uint8_t, 6> extendedRaceBranch = { 0x0F, 0x87, 0, 0, 0, 0 };
        const int32_t branch = RelativeBranch(RuntimeAddress(kRaceRestrictionExtendedBranchVa) + 6,
                                               reinterpret_cast<uintptr_t>(g_thunk));
        std::memcpy(extendedRaceBranch.data() + 2, &branch, sizeof(branch));

        std::array<Patch, 12> patches{};
        size_t index = 0;
        for (const uintptr_t address : kMemoryTablePatchVas)
            patches[index++] = MakePatch(address, memoryTable);
        patches[index++] = MakePatch(kMemoryTableClearSizePatchVa, clearSize);
        patches[index++] = MakePatch(kMemoryTableCleanupCountPatchVa, cleanupCount);
        patches[index++] = MakePatch(kRaceNamePatchVa, raceNameTable);
        patches[index++] = MakePatch(kRaceRestrictionExtendedBranchVa, extendedRaceBranch);

        if (!ApplyPatches(patches))
        {
            // Keep allocations alive if rollback could not restore a pointer or branch safely.
            return false;
        }

        return true;
    }
}

extern "C" const WXL_PluginInfo* __cdecl WXL_Query()
{
    static const WXL_PluginInfo info = {
        sizeof(WXL_PluginInfo),
        WXL_API_VERSION,
        "races-64-esteria",
        1,
        WXL_CLIENT_BUILD,
    };
    return &info;
}

extern "C" int __cdecl WXL_Load(const WXL_Api* api)
{
    if (!api || !api->Log) return 0;

    if (!Install())
    {
        api->Log(WXL_LOG_ERROR, "races-64-esteria",
                 "could not install the Esteria 64-race runtime patch; signature or memory image differs");
        return 0;
    }

    api->Log(WXL_LOG_INFO, "races-64-esteria", "Esteria 64-race support installed");
    return 1;
}
