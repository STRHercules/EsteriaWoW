#ifndef CHARACTER_PERK_TRAIT_WIRE_H
#define CHARACTER_PERK_TRAIT_WIRE_H

#include <cstddef>
#include <cstdint>

// Shared verbatim between the client (Engine/Source/Retail/PerkTraitWire.h) and the server
// (src/server/shared/PerkTraitWire.h). Do not let the copies drift.
//
// Paths of Fate: the background trait picked on the creator's FATE step. Trait ids are the contract: never reorder
// or reuse one, only append.
//
// Framing: an optional footer of payload + 'PFT1' on CMSG_CHAR_CREATE only, appended after every other footer, so it
// is the last thing in the packet and the server strips it first. No footer means Unmarked.
namespace CharacterPerkTrait
{
    inline constexpr uint8_t Version = 1;
    inline constexpr size_t PayloadSize = 2; // version, trait id
    inline constexpr uint32_t FooterMagic = 0x31544650; // "PFT1"
    inline constexpr size_t FooterSize = PayloadSize + 4;

    enum Trait : uint8_t
    {
        Unmarked = 0,
        Wanderer = 1,
        GlassCannon = 2,
        Ironbound = 3,
        ArtisanSoul = 4,
        CuriousMind = 5,
        FolkHero = 6,
        OutlawHeart = 7,
        FrugalSurvivor = 8,
        Count = 9,
    };

    // Every trait can be picked: all of them modify systems the game already has (quest reputation, looted gold).
    constexpr bool Selectable(uint8_t trait)
    {
        return trait < Count;
    }

    inline void WritePayload(uint8_t* out, uint8_t trait)
    {
        out[0] = Version;
        out[1] = trait;
    }

    // False for a wrong version or a trait that cannot be picked; `trait` is only written when the payload is good.
    inline bool ReadPayload(uint8_t const* in, size_t size, uint8_t& trait)
    {
        if (!in || size != PayloadSize || in[0] != Version || !Selectable(in[1]))
            return false;
        trait = in[1];
        return true;
    }

    // Strip an optional footer from the end of the packet. Absent footer: present stays false, true is returned.
    // A footer that is present but malformed returns false. ByteBuffer::resize resets its read cursor, so explicitly
    // preserve it.
    template <class Packet>
    bool ReadTail(Packet& packet, bool& present, uint8_t& trait)
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
        if (!ReadPayload(tail, PayloadSize, trait))
            return false;
        packet.resize(packet.size() - FooterSize);
        packet.rpos(read);
        present = true;
        return true;
    }
}

#endif
