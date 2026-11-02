#ifndef CHARACTER_START_ZONE_WIRE_H
#define CHARACTER_START_ZONE_WIRE_H

#include <cstddef>
#include <cstdint>

// Shared verbatim between the client (Engine/Source/Retail/StartZoneWire.h) and the server
// (src/server/shared/StartZoneWire.h). Do not let the copies drift.
//
// The starting zone picked on the creator's last page. Ids are the contract: never reorder or reuse one, only append.
//
// Framing: an optional footer of payload + 'SZN1' on CMSG_CHAR_CREATE only, appended just before the Paths of Fate
// footer, so the server strips it right after that one. No footer means the race's own starting zone.
namespace CharacterStartZone
{
    inline constexpr uint8_t Version = 1;
    inline constexpr size_t PayloadSize = 2; // version, zone id
    inline constexpr uint32_t FooterMagic = 0x314E5A53; // "SZN1"
    inline constexpr size_t FooterSize = PayloadSize + 4;

    enum Zone : uint8_t
    {
        RaceDefault = 0,
        Northshire = 1,      // Human
        ColdridgeValley = 2, // Dwarf, Gnome
        Shadowglen = 3,      // Night Elf
        AmmenVale = 4,       // Draenei
        ValleyOfTrials = 5,  // Orc, Troll
        CampNarache = 6,     // Tauren
        Deathknell = 7,      // Undead
        SunstriderIsle = 8,  // Blood Elf
        Count = 9,
    };

    constexpr bool Selectable(uint8_t zone)
    {
        return zone < Count;
    }

    // The race whose playercreateinfo position is the zone's start.
    // Races: 1 Human, 3 Dwarf, 4 Night Elf, 2 Orc, 6 Tauren, 5 Undead, 10 Blood Elf, 11 Draenei.
    constexpr uint8_t Race(uint8_t zone)
    {
        constexpr uint8_t races[Count] = { 0, 1, 3, 4, 11, 2, 6, 5, 10 };
        return races[zone];
    }

    inline void WritePayload(uint8_t* out, uint8_t zone)
    {
        out[0] = Version;
        out[1] = zone;
    }

    inline bool ReadPayload(uint8_t const* in, size_t size, uint8_t& zone)
    {
        if (!in || size != PayloadSize || in[0] != Version || !Selectable(in[1]))
            return false;
        zone = in[1];
        return true;
    }

    // Strip an optional footer from the end of the packet. Absent footer: present stays false, true is returned.
    // A footer that is present but malformed returns false.
    template <class Packet>
    bool ReadTail(Packet& packet, bool& present, uint8_t& zone)
    {
        size_t const read = packet.rpos();
        if (read > packet.size())
            return false;
        size_t const remaining = packet.size() - read;
        if (remaining < FooterSize)
            return true;
        uint8_t const* tail = packet.contents() + packet.size() - FooterSize;
        uint32_t const magic = uint32_t(tail[PayloadSize]) | uint32_t(tail[PayloadSize + 1]) << 8
            | uint32_t(tail[PayloadSize + 2]) << 16 | uint32_t(tail[PayloadSize + 3]) << 24;
        if (magic != FooterMagic)
            return true;
        if (!ReadPayload(tail, PayloadSize, zone))
            return false;
        packet.resize(packet.size() - FooterSize);
        packet.rpos(read);
        present = true;
        return true;
    }
}

#endif
