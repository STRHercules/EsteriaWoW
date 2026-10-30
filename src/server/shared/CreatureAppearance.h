// Generated from the selected race sources by tools/creature_race_pack.py.
#ifndef ACORE_CREATURE_APPEARANCE_H
#define ACORE_CREATURE_APPEARANCE_H

#include "KyrianAppearance.h"

#include <array>
#include <cstdint>

namespace CreatureAppearance
{
    struct Option
    {
        unsigned field;
        unsigned count;
        unsigned factor;
    };

    inline constexpr std::array<Option, 5> NagaMale = {{
        {0, 25, 1},
        {1, 1, 1},
        {2, 5, 1},
        {3, 15, 1},
        {4, 96, 1},
    }};

    inline constexpr std::array<Option, 5> NagaFemale = {{
        {0, 255, 1},
        {1, 1, 1},
        {2, 5, 1},
        {3, 80, 1},
        {4, 240, 1},
    }};

    inline constexpr std::array<Option, 5> TuskarrMale = {{
        {0, 7, 1},
        {1, 1, 1},
        {2, 7, 1},
        {3, 7, 1},
        {4, 7, 1},
    }};

    inline constexpr std::array<Option, 5> TuskarrFemale = {{
        {0, 7, 1},
        {1, 1, 1},
        {2, 1, 1},
        {3, 1, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> VrykulMale = {{
        {0, 6, 1},
        {1, 1, 1},
        {2, 6, 1},
        {3, 5, 1},
        {4, 6, 1},
    }};

    inline constexpr std::array<Option, 5> VrykulFemale = {{
        {0, 6, 1},
        {1, 1, 1},
        {2, 5, 1},
        {3, 5, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> ThinhumanMale = {{
        {0, 4, 1},
        {1, 2, 1},
        {2, 4, 1},
        {3, 4, 1},
        {4, 7, 1},
    }};

    inline constexpr std::array<Option, 5> SethrakMale = {{
        {0, 5, 1},
        {1, 1, 1},
        {2, 4, 1},
        {3, 4, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> SethrakFemale = {{
        {0, 1, 1},
        {1, 1, 1},
        {2, 1, 1},
        {3, 1, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> GnollMale = {{
        {0, 120, 1},
        {1, 54, 1},
        {2, 60, 1},
        {3, 48, 1},
        {4, 3, 1},
    }};

    inline constexpr std::array<Option, 5> SaberonMale = {{
        {0, 4, 1},
        {1, 10, 1},
        {2, 3, 1},
        {3, 3, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Drakkin_AllianceMale = {{
        {0, 7, 1},
        {1, 1, 1},
        {2, 5, 1},
        {3, 7, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Drakkin_AllianceFemale = {{
        {0, 16, 1},
        {1, 1, 1},
        {2, 1, 1},
        {3, 25, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Drakkin_HordeMale = {{
        {0, 16, 1},
        {1, 1, 1},
        {2, 1, 1},
        {3, 25, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Drakkin_HordeFemale = {{
        {0, 16, 1},
        {1, 1, 1},
        {2, 1, 1},
        {3, 25, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Drakonid_AllianceMale = {{
        {0, 17, 1},
        {1, 4, 1},
        {2, 6, 1},
        {3, 76, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Drakonid_HordeMale = {{
        {0, 17, 1},
        {1, 4, 1},
        {2, 6, 1},
        {3, 76, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Slime_Giant_AllianceMale = {{
        {0, 35, 1},
        {1, 2, 1},
        {2, 1, 1},
        {3, 1, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Slime_Giant_HordeMale = {{
        {0, 35, 1},
        {1, 2, 1},
        {2, 1, 1},
        {3, 1, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Centaur_AllianceMale = {{
        {0, 16, 1},
        {1, 1, 1},
        {2, 9, 1},
        {3, 1, 1},
        {4, 8, 1},
    }};

    inline constexpr std::array<Option, 5> Centaur_AllianceFemale = {{
        {0, 16, 1},
        {1, 1, 1},
        {2, 14, 1},
        {3, 1, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> Centaur_HordeMale = {{
        {0, 16, 1},
        {1, 1, 1},
        {2, 9, 1},
        {3, 1, 1},
        {4, 8, 1},
    }};

    inline constexpr std::array<Option, 5> Centaur_HordeFemale = {{
        {0, 16, 1},
        {1, 1, 1},
        {2, 14, 1},
        {3, 1, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> KyrianMale = {{
        {0, 19, 1},
        {1, 15, 1},
        {2, 160, 1},
        {3, 110, 1},
        {4, 96, 1}, // Values 80..95 mark independently packed new palettes.
    }};

    inline constexpr std::array<Option, 5> KyrianFemale = {{
        {0, 23, 1},
        {1, 20, 1},
        {2, 95, 1},
        {3, 55, 1},
        {4, 96, 1},
    }};

    inline constexpr std::array<Option, 5> VenthyrMale = {{
        {0, 14, 1},
        {1, 108, 1},
        {2, 8, 1},
        {3, 7, 1},
        {4, 32, 1},
    }};

    inline constexpr std::array<Option, 5> VenthyrFemale = {{
        {0, 6, 1},
        {1, 216, 1},
        {2, 6, 1},
        {3, 6, 1},
        {4, 40, 1},
    }};

    inline constexpr std::array<Option, 5> DarkfallenMale = {{
        {0, 5, 1},
        {1, 1, 1},
        {2, 21, 1},
        {3, 4, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 5> DarkfallenFemale = {{
        {0, 4, 1},
        {1, 1, 1},
        {2, 25, 1},
        {3, 5, 1},
        {4, 1, 1},
    }};

    inline constexpr std::array<Option, 15> GnollControls = {{
        {0, 10, 1},
        {1, 6, 1},
        {1, 3, 6},
        {1, 3, 18},
        {0, 3, 10},
        {2, 3, 1},
        {2, 4, 3},
        {2, 5, 12},
        {3, 2, 1},
        {3, 2, 2},
        {0, 4, 30},
        {3, 2, 4},
        {3, 3, 8},
        {3, 2, 24},
        {4, 3, 1},
    }};

    inline constexpr std::array<char const*, 15> GnollLabels = {
        "Fur Color",
        "Mane",
        "Beard",
        "Ears",
        "Eyes",
        "Outfit Color",
        "Chest Sling",
        "Cuffs",
        "Waist",
        "Loincloth",
        "Tail",
        "Leg Wraps",
        "Pauldrons",
        "Belt Strap",
        "Trousers",
    };

    inline constexpr std::array<Option, 5> DrakonidControls = {{
        {0, 17, 1},
        {1, 2, 1},
        {2, 6, 1},
        {1, 2, 2},
        {3, 76, 1},
    }};

    inline constexpr std::array<char const*, 5> DrakonidLabels = {
        "Skin Color",
        "Head",
        "Horns",
        "Tail",
        "Eye Color",
    };

    inline constexpr std::array<Option, 8> KyrianMaleControls = {{
        {0, 19, 1}, {2, 10, 1}, {3, 17, 1}, {2, 16, 10},
        {1, 3, 1}, {1, 5, 3}, {4, 4, 1}, {4, 4, 4},
    }};

    inline constexpr std::array<char const*, 8> KyrianMaleLabels = {
        "Body Palette",
        "Armor Palette",
        "Wing Palette",
        "Hair Palette",
        "Hair Style",
        "Headwear",
        "Outfit",
        "Shoulders",
    };

    inline constexpr std::array<Option, 8> KyrianFemaleControls = {{
        {0, 23, 1}, {2, 5, 1}, {3, 25, 1}, {2, 19, 5},
        {1, 4, 1}, {1, 5, 4}, {4, 4, 1}, {4, 4, 4},
    }};

    inline constexpr std::array<char const*, 8> KyrianFemaleLabels = {
        "Body Palette",
        "Armor Palette",
        "Wing Palette",
        "Hair Palette",
        "Hair Style",
        "Headwear",
        "Outfit",
        "Shoulders",
    };

    inline constexpr std::array<Option, 8> VenthyrMaleControls = {{
        {0, 14, 1},
        {2, 8, 1},
        {3, 7, 1},
        {1, 6, 1},
        {4, 8, 1},
        {4, 4, 8},
        {1, 6, 6},
        {1, 3, 36},
    }};

    inline constexpr std::array<char const*, 8> VenthyrMaleLabels = {
        "Skin / Body Palette",
        "Accessory Palette",
        "Hair Color",
        "Body / Outfit Style",
        "Hair Style",
        "Facial Hair",
        "Collar / Robe",
        "Headwear",
    };

    inline constexpr std::array<Option, 8> VenthyrFemaleControls = {{
        {0, 6, 1},
        {2, 6, 1},
        {3, 6, 1},
        {1, 4, 1},
        {4, 8, 1},
        {4, 5, 8},
        {1, 6, 4},
        {1, 9, 24},
    }};

    inline constexpr std::array<char const*, 8> VenthyrFemaleLabels = {
        "Skin / Body Palette",
        "Accessory Palette",
        "Hair Color",
        "Body / Outfit Style",
        "Hair Style",
        "Earrings",
        "Collar / Cape",
        "Headwear",
    };

    constexpr bool Uses(unsigned race)
    {
        return (((((((((((((((race >= 54 && race <= 59) || race == 62) || race == 63) || race == 64) || race == 66) || race == 67) || race == 69) || race == 70) || race == 71) || race == 72) || race == 73) || race == 74) || race == 43) || race == 44) || race == 75) || race == 76;
    }

    constexpr bool GenderAllowed(unsigned race, unsigned gender)
    {
        return Uses(race) && (gender == 0
            || ((race == 54 || race == 55 || race == 56 || race == 57 || race == 62 || race == 66 || race == 67 || race == 73 || race == 74 || race == 75 || race == 76 || race == 43 || race == 44) && gender == 1));
    }

    constexpr bool UsesPlayerVrykul(unsigned race, unsigned gender)
    {
        return (race == 56 || race == 57) && gender == 1;
    }

    constexpr bool UsesStockMaterials(unsigned race, unsigned gender)
    {
        return UsesPlayerVrykul(race, gender) || (race == 66 && gender == 1) || (race == 67 && gender < 2);
    }

    constexpr std::array<Option, 5> const& Options(unsigned race, unsigned gender)
    {
        switch (race)
        {
            case 54:
                return gender ? NagaFemale : NagaMale;
            case 55:
                return gender ? TuskarrFemale : TuskarrMale;
            case 56:
            case 57:
                return gender ? VrykulFemale : VrykulMale;
            case 58:
            case 59:
                return ThinhumanMale;
            case 62:
                return gender ? SethrakFemale : SethrakMale;
            case 63:
                return GnollMale;
            case 64:
                return SaberonMale;
            case 66:
                return gender ? Drakkin_AllianceFemale : Drakkin_AllianceMale;
            case 67:
                return gender ? Drakkin_HordeFemale : Drakkin_HordeMale;
            case 69:
                return Drakonid_AllianceMale;
            case 70:
                return Drakonid_HordeMale;
            case 71:
                return Slime_Giant_AllianceMale;
            case 72:
                return Slime_Giant_HordeMale;
            case 73:
                return gender ? Centaur_AllianceFemale : Centaur_AllianceMale;
            case 74:
                return gender ? Centaur_HordeFemale : Centaur_HordeMale;
            case 75:
                return gender ? KyrianFemale : KyrianMale;
            case 76:
                return gender ? VenthyrFemale : VenthyrMale;
            case 43:
            case 44:
                return gender ? DarkfallenFemale : DarkfallenMale;
            default:
                return NagaMale;
        }
    }

    constexpr bool Validate(unsigned race, unsigned gender, std::array<std::uint8_t, 5> const& fields)
    {
        if (!GenderAllowed(race, gender))
            return false;
        auto const& options = Options(race, gender);
        for (unsigned i = 0; i < fields.size(); ++i)
            if (fields[i] >= options[i].count)
                return false;
        return true;
    }
}

#endif
