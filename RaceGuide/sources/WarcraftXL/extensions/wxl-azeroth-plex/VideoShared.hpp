#pragma once

#include <windows.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace wxl_video_shared
{
    constexpr wchar_t kMappingName[] = L"Local\\WXLVideoCinemaFrames-v1";
    constexpr wchar_t kControlMappingName[] = L"Local\\WXLVideoCinemaControl-v1";
    constexpr uint32_t kMagic = 0x46565857u; // "WXVF"
    constexpr uint32_t kVersion = 2;
    constexpr uint32_t kWidth = 640;
    constexpr uint32_t kHeight = 360;
    constexpr uint32_t kStride = kWidth * 4;
    constexpr uint32_t kFrameBytes = kStride * kHeight;
    constexpr uint32_t kControlMagic = 0x43565857u; // "WXVC"
    constexpr uint32_t kControlVersion = 1;

    enum class Command : LONG
    {
        None = 0,
        Show = 1,
        Play = 2,
        Pause = 3,
        Stop = 4,
        Hide = 5,
    };

#pragma pack(push, 1)
    struct FrameHeader
    {
        uint32_t magic;
        uint32_t version;
        uint32_t headerBytes;
        uint32_t width;
        uint32_t height;
        uint32_t stride;
        uint32_t frameBytes;
        volatile LONG activeIndex;
        volatile LONG sequence;
        volatile LONG slotSequence[2];
        volatile LONG hostPid;
        volatile LONG ready;
        uint32_t reserved[3];
    };
#pragma pack(pop)

    static_assert(sizeof(FrameHeader) == 64, "shared video header ABI changed");

    struct ControlBlock
    {
        uint32_t magic;
        uint32_t version;
        uint32_t structBytes;
        volatile LONG commandSequence;
        volatile LONG command;
        volatile LONG volumeSequence;
        volatile LONG volumePercent;
        uint32_t reserved[4];
    };

    static_assert(sizeof(ControlBlock) == 44, "shared video control ABI changed");

    constexpr wchar_t kUiMappingName[] = L"Local\\WXLVideoCinemaUi-v1";
    constexpr uint32_t kUiMagic = 0x55565857u; // "WXVU"
    constexpr uint32_t kUiVersion = 3;
    constexpr size_t kUiTextBytes = 256;
    constexpr size_t kUiErrorBytes = 192;
    constexpr size_t kUiStatusBytes = 192;
    constexpr size_t kUiGuidBytes = 256;
    constexpr size_t kUiThumbBytes = 256;
    // ponytail: fixed list caps keep the cross-process ABI bounded; paginate when larger libraries matter.
    constexpr size_t kUiMaxServers = 8;
    constexpr size_t kUiMaxSections = 32;
    constexpr size_t kUiMaxItems = 64;
    constexpr size_t kUiMaxStreams = 32;
    constexpr size_t kUiMaxPartyMembers = 32;
    constexpr size_t kUiMaxPartyQueue = 32;
    constexpr size_t kUiMaxPublicRooms = 16;
    constexpr size_t kUiMaxMarkers = 4;

    enum class UiView : LONG
    {
        Login,
        Servers,
        Home,
        Library,
        Search,
        Details,
        Player,
        Party,
        Queue,
        Settings,
    };

    enum class UiCommand : LONG
    {
        None,
        StartLogin,
        SelectServer,
        SelectSection,
        SelectItem,
        Search,
        Play,
        Pause,
        Stop,
        Seek,
        SelectAudio,
        SelectSubtitle,
        SignOut,
        SetView,
        OpenWatchlist,
        NavigateBack,
        NextPage,
        PreviousPage,
        OpenHomeSection,
        SetPlaybackSpeed,
        SkipMarker,
        PlayNextEpisode,
        CancelAutoplay,
        CreateParty,
        CreatePublicParty,
        JoinParty,
        LeaveParty,
        RefreshPublicRooms,
        JoinPublicRoom,
        SetPartyPermissionMode,
        SetPartyQueueMode,
        SetPartySyncAudio,
        SetPartySyncSubtitles,
        StartReadyCheck,
        SetReadyState,
        AddCurrentToQueue,
        RemoveQueueItem,
        MoveQueueItem,
        PlayQueueItem,
        RespondControlRequest,
        SetDisconnectPolicy,
        ShareCinemaSettings,
    };

    struct UiServerSnapshot
    {
        char name[128]{};
        char uri[192]{};
    };

    struct UiSectionSnapshot
    {
        char key[64]{};
        char title[128]{};
        char type[32]{};
    };

    struct UiItemSnapshot
    {
        char ratingKey[64]{};
        char guid[kUiGuidBytes]{};
        char title[128]{};
        char type[32]{};
        char grandparentTitle[128]{};
        char thumb[kUiThumbBytes]{};
        LONG viewOffsetMs = 0;
        LONG durationMs = 0;
        LONG viewed = 0;
    };

    struct UiStreamSnapshot
    {
        LONG id = 0;
        LONG streamType = 0;
        char language[64]{};
        char title[128]{};
    };

    struct UiMarkerSnapshot
    {
        char type[32]{};
        LONG startMs = 0;
        LONG endMs = 0;
    };

    struct UiPartyMemberSnapshot
    {
        char id[128]{};
        char name[64]{};
        LONG role = 0;
        LONG connected = 0;
        LONG ready = 0;
    };

    struct UiPartyQueueSnapshot
    {
        char title[128]{};
        char type[32]{};
        LONG resolved = 0;
        uint64_t order = 0;
    };

    struct UiPublicRoomSnapshot
    {
        char code[16]{};
        char title[128]{};
        char hostName[64]{};
        LONG memberCount = 0;
    };

    struct UiCinemaSnapshot
    {
        char presetName[64]{};
        float width = 8.0f;
        float heightOffset = 0.5f;
        float rotationDegrees = 0.0f;
        float pinnedX = 0.64f;
        float pinnedY = 0.04f;
        float pinnedWidth = 0.32f;
        float depthOffset = -0.010f;
        float audioRange = 60.0f;
        LONG pinned = 0;
        LONG depthOcclusion = 1;
        LONG distanceAudio = 1;
        LONG aspectRatioMode = 0;
        LONG fitMode = 0;
        LONG frameStyle = 0;
        LONG ambientLighting = 0;
    };

    // ponytail: one latest-command slot is enough for the 16 ms panel tick; add a queue if bursts matter.
    struct UiCommandPacket
    {
        LONG command = 0;
        LONG index = -1;
        LONG value = 0;
        char text[kUiTextBytes]{};
    };

    struct UiSnapshot
    {
        uint32_t structBytes = sizeof(UiSnapshot);
        UiView view = UiView::Login;
        uint32_t serverCount = 0;
        uint32_t sectionCount = 0;
        uint32_t itemCount = 0;
        uint32_t streamCount = 0;
        uint32_t watchlistCount = 0;
        uint32_t watchlistLoaded = 0;
        uint32_t browseDepth = 0;
        uint32_t browseRoot = 0;
        uint32_t pageOffset = 0;
        uint32_t pageSize = 0;
        uint32_t pageTotalSize = 0;
        uint32_t playbackPositionMs = 0;
        uint32_t playbackDurationMs = 0;
        uint32_t playbackPaused = 0;
        uint32_t markerCount = 0;
        uint32_t partyMemberCount = 0;
        uint32_t partyQueueCount = 0;
        uint32_t publicRoomCount = 0;
        uint32_t partyConnectionState = 0;
        uint32_t partyRole = 0;
        uint32_t partyPermissionMode = 0;
        uint32_t partyQueueMode = 0;
        uint32_t partySyncAudio = 0;
        uint32_t partySyncSubtitles = 0;
        uint32_t partyDisconnectPolicy = 0;
        uint32_t partyPublicRoomsEnabled = 0;
        uint32_t partyReadyCheckActive = 0;
        uint32_t partyReconnectCount = 0;
        uint32_t nextEpisodeAvailable = 0;
        uint32_t autoplayRemainingMs = 0;
        uint32_t playbackSpeedPermille = 1000;
        float videoAspectRatio = 16.0f / 9.0f;
        int64_t partyReadyStartAtMs = 0;
        int64_t partyRelayRttMs = 0;
        int64_t partyClockOffsetMs = 0;
        int64_t partyDriftMs = 0;
        uint64_t partyRoomEpoch = 0;
        uint64_t partySequence = 0;
        UiItemSnapshot item{};
        UiItemSnapshot playingItem{};
        UiItemSnapshot nextEpisode{};
        UiCinemaSnapshot sharedCinema{};
        char error[kUiErrorBytes]{};
        char status[kUiStatusBytes]{};
        char watchlistError[kUiErrorBytes]{};
        char browseTitle[128]{};
        char partyRoomCode[16]{};
        char partyHostName[64]{};
        char partyError[kUiErrorBytes]{};
        char partyCorrection[32]{};
        char partyMediaMatch[64]{};
        char controlRequest[64]{};
        char controlRequestId[128]{};
        UiServerSnapshot servers[kUiMaxServers]{};
        UiSectionSnapshot sections[kUiMaxSections]{};
        UiItemSnapshot items[kUiMaxItems]{};
        UiStreamSnapshot streams[kUiMaxStreams]{};
        UiMarkerSnapshot markers[kUiMaxMarkers]{};
        UiPartyMemberSnapshot partyMembers[kUiMaxPartyMembers]{};
        UiPartyQueueSnapshot partyQueue[kUiMaxPartyQueue]{};
        UiPublicRoomSnapshot publicRooms[kUiMaxPublicRooms]{};
    };

    struct UiBridge
    {
        uint32_t magic = kUiMagic;
        uint32_t version = kUiVersion;
        uint32_t structBytes = sizeof(UiBridge);
        volatile LONG commandSequence = 0;
        UiCommandPacket command{};
        volatile LONG activeIndex = 0;
        volatile LONG sequence = 0;
        volatile LONG slotSequence[2]{};
        UiSnapshot slots[2]{};
    };

    static_assert(sizeof(UiCommandPacket) == 268, "UI command ABI changed");
    static_assert(sizeof(UiSnapshot) > 0, "UI snapshot ABI changed");

    inline void ClampPinnedLayout(float& left, float& top, float& width)
    {
        width = std::clamp(width, 0.15f, 0.80f);
        left = std::clamp(left, 0.0f, 1.0f - width);
        const float height = width * 9.0f / 16.0f;
        top = std::clamp(top, 0.0f, std::max(0.0f, 1.0f - height));
    }

    inline bool ReadUiSnapshot(const UiBridge* bridge, UiSnapshot& result)
    {
        if (!bridge || bridge->magic != kUiMagic || bridge->version != kUiVersion ||
            bridge->structBytes != sizeof(UiBridge))
            return false;

        for (int attempt = 0; attempt != 2; ++attempt)
        {
            const LONG sequence = bridge->sequence;
            MemoryBarrier();
            const LONG active = bridge->activeIndex;
            if (sequence <= 0 || active < 0 || active > 1)
                return false;

            const LONG slotSequence = bridge->slotSequence[active];
            if (slotSequence != sequence)
                continue;
            MemoryBarrier();
            std::memcpy(&result, &bridge->slots[active], sizeof(result));
            MemoryBarrier();
            result.error[kUiErrorBytes - 1] = '\0';
            result.status[kUiStatusBytes - 1] = '\0';
            result.watchlistError[kUiErrorBytes - 1] = '\0';
            result.browseTitle[sizeof(result.browseTitle) - 1] = '\0';
            result.item.ratingKey[sizeof(result.item.ratingKey) - 1] = '\0';
            result.item.guid[sizeof(result.item.guid) - 1] = '\0';
            result.item.title[sizeof(result.item.title) - 1] = '\0';
            result.item.type[sizeof(result.item.type) - 1] = '\0';
            result.item.grandparentTitle[sizeof(result.item.grandparentTitle) - 1] = '\0';
            result.item.thumb[sizeof(result.item.thumb) - 1] = '\0';
            for (auto& server : result.servers)
            {
                server.name[sizeof(server.name) - 1] = '\0';
                server.uri[sizeof(server.uri) - 1] = '\0';
            }
            for (auto& section : result.sections)
            {
                section.key[sizeof(section.key) - 1] = '\0';
                section.title[sizeof(section.title) - 1] = '\0';
                section.type[sizeof(section.type) - 1] = '\0';
            }
            for (auto& item : result.items)
            {
                item.ratingKey[sizeof(item.ratingKey) - 1] = '\0';
                item.guid[sizeof(item.guid) - 1] = '\0';
                item.title[sizeof(item.title) - 1] = '\0';
                item.type[sizeof(item.type) - 1] = '\0';
                item.grandparentTitle[sizeof(item.grandparentTitle) - 1] = '\0';
                item.thumb[sizeof(item.thumb) - 1] = '\0';
            }
            for (auto& stream : result.streams)
            {
                stream.language[sizeof(stream.language) - 1] = '\0';
                stream.title[sizeof(stream.title) - 1] = '\0';
            }
            if (bridge->slotSequence[active] == slotSequence &&
                bridge->sequence == sequence &&
                result.structBytes == sizeof(UiSnapshot))
                return true;
        }
        return false;
    }

    constexpr size_t kMappingBytes = sizeof(FrameHeader) + size_t(kFrameBytes) * 2u;

    inline uint8_t* Pixels(void* mapping, unsigned index)
    {
        return static_cast<uint8_t*>(mapping) + sizeof(FrameHeader) +
               size_t(index & 1u) * kFrameBytes;
    }

    inline const uint8_t* Pixels(const void* mapping, unsigned index)
    {
        return static_cast<const uint8_t*>(mapping) + sizeof(FrameHeader) +
               size_t(index & 1u) * kFrameBytes;
    }
}
