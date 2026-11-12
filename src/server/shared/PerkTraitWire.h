#ifndef CHARACTER_PERK_TRAIT_WIRE_H
#define CHARACTER_PERK_TRAIT_WIRE_H

#include <cstddef>
#include <cstdint>

// Shared verbatim between the client (Engine/Source/Retail/PerkTraitWire.h) and the server
// (src/server/shared/PerkTraitWire.h). Do not let the copies drift.
//
// Paths of Fate: the starting traits picked on the creator's FATE step. Trait ids are the contract: never reorder
// or reuse one, only append (the catalog is Esteria_Fate_Trait_Catalog.json in wowdecomp).
//
// Framing: an optional footer on CMSG_CHAR_CREATE only, appended after every other footer, so it is the last thing
// in the packet and the server strips it first. No footer means Unmarked (no traits).
//   v1  version(u8)=1 trait(u8) 'PFT1'                                   one of the eight original backgrounds
//   v2  version(u8)=2 count(u8) count x id(u16) length(u16) 'PFT2'       ids ascending and unique, never 0;
//                                                                        length = 2 + 2 * count, the bytes before it
// Integers are little-endian. This only frames the list; whether the build is allowed is PerkTraitRules.h's job.
namespace CharacterPerkTrait
{
    inline constexpr uint8_t Version = 1;
    inline constexpr size_t PayloadSize = 2; // version, trait id
    inline constexpr uint32_t FooterMagic = 0x31544650; // "PFT1"
    inline constexpr size_t FooterSize = PayloadSize + 4;

    inline constexpr uint8_t Version2 = 2;
    inline constexpr uint32_t FooterMagic2 = 0x32544650; // "PFT2"
    inline constexpr size_t MaxTraits = 8;
    inline constexpr size_t MaxFooter2Size = 2 + 2 * MaxTraits + 6;

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
        Count = 9, // the v1 backgrounds; later ids only exist in v2
    };

    struct Selection
    {
        uint8_t count = 0;
        uint16_t ids[MaxTraits] = {};
    };

    // v1: every original background can be picked.
    constexpr bool Selectable(uint8_t trait)
    {
        return trait < Count;
    }

    // Ascending, unique, no 0, at most MaxTraits.
    constexpr bool Canonical(Selection const& selection)
    {
        if (selection.count > MaxTraits)
            return false;
        for (size_t i = 0; i < selection.count; ++i)
            if (!selection.ids[i] || (i && selection.ids[i] <= selection.ids[i - 1]))
                return false;
        return true;
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

    // Writes the whole v2 footer; `out` holds MaxFooter2Size bytes. Returns the bytes written, 0 when the selection
    // is not canonical.
    inline size_t WriteFooter2(uint8_t* out, Selection const& selection)
    {
        if (!Canonical(selection))
            return 0;
        size_t at = 0;
        out[at++] = Version2;
        out[at++] = selection.count;
        for (size_t i = 0; i < selection.count; ++i)
        {
            out[at++] = uint8_t(selection.ids[i]);
            out[at++] = uint8_t(selection.ids[i] >> 8);
        }
        uint16_t const length = uint16_t(at);
        out[at++] = uint8_t(length);
        out[at++] = uint8_t(length >> 8);
        for (uint32_t shift = 0; shift < 32; shift += 8)
            out[at++] = uint8_t(FooterMagic2 >> shift);
        return at;
    }

    inline uint32_t Magic(uint8_t const* at)
    {
        return uint32_t(at[0]) | uint32_t(at[1]) << 8 | uint32_t(at[2]) << 16 | uint32_t(at[3]) << 24;
    }

    // Strip an optional footer (either version) from the end of the packet. Absent footer: present stays false, true
    // is returned. A footer that is present but malformed, or two trait footers in a row, returns false.
    // ByteBuffer::resize resets its read cursor, so explicitly preserve it.
    template <class Packet>
    bool ReadTail(Packet& packet, bool& present, Selection& selection)
    {
        size_t const read = packet.rpos();
        if (read > packet.size())
            return false;
        size_t const remaining = packet.size() - read;
        if (remaining < 4)
            return true;
        uint8_t const* end = packet.contents() + packet.size();
        uint32_t const magic = Magic(end - 4);
        size_t footer = 0;
        Selection parsed;
        if (magic == FooterMagic)
        {
            uint8_t trait = Unmarked;
            if (remaining < FooterSize || !ReadPayload(end - FooterSize, PayloadSize, trait))
                return false;
            footer = FooterSize;
            if (trait != Unmarked)
            {
                parsed.count = 1;
                parsed.ids[0] = trait;
            }
        }
        else if (magic == FooterMagic2)
        {
            if (remaining < 6)
                return false;
            size_t const length = size_t(end[-6]) | size_t(end[-5]) << 8;
            if (length < 2 || length > 2 + 2 * MaxTraits || remaining < length + 6)
                return false;
            uint8_t const* payload = end - 6 - length;
            if (payload[0] != Version2 || payload[1] > MaxTraits || length != size_t(2 + 2 * payload[1]))
                return false;
            parsed.count = payload[1];
            for (size_t i = 0; i < parsed.count; ++i)
                parsed.ids[i] = uint16_t(payload[2 + 2 * i] | payload[3 + 2 * i] << 8);
            if (!Canonical(parsed))
                return false;
            footer = length + 6;
        }
        else
            return true;

        // A second trait footer under this one is ambiguous: refuse it rather than pick one.
        if (remaining - footer >= 4)
        {
            uint32_t const under = Magic(end - footer - 4);
            if (under == FooterMagic || under == FooterMagic2)
                return false;
        }
        packet.resize(packet.size() - footer);
        packet.rpos(read);
        selection = parsed;
        present = true;
        return true;
    }
}

#endif
