/*
 * AzerothPlex media protocol -- shared shape with the AzerothPlex helper in the client.
 *
 * Every message is a 3-byte header (uint8 type, uint16 payload length, little-endian) followed by
 * that many payload bytes. Video/audio payloads are opaque to the server: they carry the client's
 * own 12-byte frame header plus the encoded access unit, and the server only moves the bytes.
 *
 * Everything is a fixed-size little-endian struct, so both ends memcpy and never parse. Keep this
 * file in step with host/AzerothPlexProtocol.hpp in the AzerothPlex repository.
 */

#ifndef MOD_AZEROTH_PLEX_PROTOCOL_H
#define MOD_AZEROTH_PLEX_PROTOCOL_H

#include <cstdint>

namespace azerothplex
{
    constexpr uint32_t kProtocolVersion = 1;
    constexpr uint16_t kMaxPayloadBytes = 60 * 1024;
    constexpr uint16_t kMaxNameBytes = 32;
    constexpr uint16_t kMaxTextBytes = 96;
    constexpr uint16_t kMaxBroadcastersPerUpdate = 16;
    constexpr uint32_t kNoBroadcaster = 0;

    enum class Message : uint8_t
    {
        None = 0,
        Hello = 1,
        Welcome = 2,
        Reject = 3,
        Pose = 4,
        Start = 5,
        Stop = 6,
        Watch = 7,
        State = 8,
        Watching = 9,
        Ping = 10,
        Pong = 11,
        Video = 20,
        Audio = 21,
    };

    /// Why the server refused a connection or a request. The client turns it into its own words.
    enum class RejectCode : uint16_t
    {
        None = 0,
        BadProtocol,
        UnknownCharacter,
        NotInWorld,
        AddressMismatch,
        ServerDisabled,
        TooManyConnections,
        NoSuchBroadcast,
        BroadcastsFull,
        ViewersFull,
    };

#pragma pack(push, 1)
    struct Header
    {
        uint8_t type;
        uint16_t length;
    };

    /// The screen placement the client renders a broadcast at, in the broadcaster's own world.
    struct Pose
    {
        int32_t mapId;
        float centerX;
        float centerY;
        float centerZ;
        float rightX;
        float rightY;
        float rightZ;
        float width;
        float aspect;
        float depthOffset;
        float audioRange;
        uint8_t visible;
        uint8_t depthOcclusion;
        uint8_t distanceAudio;
        uint8_t broadcasting;
    };

    struct Hello
    {
        uint32_t version;
        uint32_t flags;
        uint64_t guid;
        char name[kMaxNameBytes];
    };

    struct Welcome
    {
        uint32_t sessionId;
        uint32_t tickMs;
        uint32_t bitrate;
        uint16_t fps;
        uint16_t width;
        uint16_t height;
        uint16_t rangeYards;
        uint16_t maxViewers;
        uint16_t reserved;
    };

    struct Reject
    {
        uint16_t code;
        char text[kMaxTextBytes];
    };

    struct Watch
    {
        uint32_t broadcasterId;
    };

    struct Watching
    {
        uint32_t broadcasterId;
    };

    struct Broadcaster
    {
        uint32_t sessionId;
        float distance;
        uint16_t viewers;
        uint8_t watching;
        uint8_t reserved;
        char name[kMaxNameBytes];
        Pose pose;
    };

    struct State
    {
        uint32_t mapId;
        uint16_t count;
        uint16_t reserved;
        // Followed by count Broadcaster records.
    };
#pragma pack(pop)

    static_assert(sizeof(Header) == 3, "protocol header changed");
    static_assert(sizeof(Pose) == 48, "pose changed");
    static_assert(sizeof(Hello) == 48, "hello changed");
    static_assert(sizeof(Welcome) == 24, "welcome changed");
    static_assert(sizeof(Reject) == 98, "reject changed");
    static_assert(sizeof(Broadcaster) == 92, "broadcaster changed");
    static_assert(sizeof(State) == 8, "state changed");
}

#endif
