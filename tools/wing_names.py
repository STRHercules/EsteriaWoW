"""Player-facing names for the Sirus wing models.

The donor names are author-side file names -- ``dreadqueen_3846335_wings``, ``tb_ogre_armor_01_wings``
-- and ship straight into the spellbook if they are humanised naively.  These rules turn a model
path into the name a player should see.
"""

from __future__ import annotations

import re

#: Whole model stems, lowercased, that no rule gets right on its own.
OVERRIDES = {
    "wings2": "Alas Wings II",
    "wings3": "Alas Wings III",
    "wings4": "Alas Wings IV",
    "wings5": "Alas Wings V",
    "crocsunmount_wings": "Crocosaur Wings",
    "demon_dpsbody_wings": "Demon Wings",
    "demon_dpsbodybelf_wings": "Blood Elf Demon Wings",
    "flyingsprite_custom_wings_dark_wings": "Flying Sprite Wings (Dark)",
    "vesper_wings": "Vesper Wings",
    "kyrianfemale_wings1_wings": "Kyrian Wings (Light)",
    "kyrianfemale_tex2_3033077_wings": "Kyrian Wings (Pale)",
    "voidtouchedwolfbat_wings_rightmirror": "Void-Touched Wolf Bat Wings (Mirrored)",
}

#: word -> replacement, applied to the humanised words (case-insensitive).
WORDS = {
    "amalgamofrage": "Amalgamofrage",
    "boneabomination": "Bone Abomination",
    "bwonsamdispirit": "Bwonsamdi Spirit",
    "deathelementalmount": "Death Elemental",
    "dpsbody": "",
    "dpsbodybelf": "Blood Elf",
    "dreadqueen": "Dread Queen",
    "eredarboss": "Eredar",
    "felbatmountforsaken": "Forsaken Fel Bat",
    "flyingspriteboss": "Sprite Sovereign",
    "flyingspriteevil": "Vile Sprite",
    "flyingsprite": "Flying Sprite",
    "gargoyle2": "Gargoyle",
    "hakkarshadowlands": "Hakkar",
    "illidandark2": "Illidan",
    "jailerrevendreth": "Jailer",
    "kaelthasshadowlands": "Kael'thas",
    "kyrianfemale": "Kyrian",
    "kyrianmaw": "Maw Kyrian",
    "lightforgedmechsuit": "Lightforged Mech",
    "mogufemale": "Mogu",
    "nerzhulshadowlands": "Ner'zhul",
    "obsidiandestroyer2": "Obsidian Destroyer",
    "peacockmount": "Peacock",
    "protoarchon": "Proto-Archon",
    "sarkarethtransformed": "Sarkareth",
    "soulbindernaazindhri": "Soulbinder Naazindhri",
    "succubus2": "Succubus",
    "thaurissan2": "Thaurissan",
    "thelastarchitect": "The Last Architect",
    "unboundfireelementallord": "Unbound Fire Elemental Lord",
    "valkier2": "Val'kyr",
    "voidgod": "Void God",
    "voidtouchedwolfbat": "Void-Touched Wolf Bat",
    "voidwraithraidboss": "Void Wraith",
    "voidwraithboss": "Void Wraith",
    "voidwraith": "Void Wraith",
    "tb": "",
    "ogre_armor": "Ogre Armor",
    "arbiter2": "Arbiter",
    "archon_wings_gray": "Archon Wings (Gray)",
}

#: words that describe the variant, moved into a trailing "(...)".
VARIANT = {
    "red": "Red", "red2": "Red II", "blue": "Blue", "white": "White", "green": "Green",
    "yellow": "Yellow", "pink": "Pink", "black": "Black", "purple": "Purple", "teal": "Teal",
    "orange": "Orange", "gray": "Gray", "grey": "Gray", "brown": "Brown", "cyan": "Cyan",
    "gold": "Gold", "bronze": "Bronze", "stone": "Stone", "dark": "Dark", "moon": "Moon",
    "sun": "Sun", "darkgreen": "Dark Green", "darkteal": "Dark Teal", "indigo": "Indigo",
    "tealindigo": "Teal Indigo", "blackbrown": "Black Brown", "fel": "Fel",
    "darkpurpleorange": "Dark Purple Orange", "darkpurpleorange2": "Dark Purple Orange II",
}

SMALL = {"of", "the", "and", "or", "a", "an", "in", "on"}

#: words the donor uses that would otherwise reach the player verbatim.
WORDS.update({
    "priest": "", "guardianspirit": "Guardian Spirit", "spiderdemon": "Spider Demon",
    "nhallish": "Nhallish", "warlockmorphwings": "Warlock Wings", "warlockmorph": "Warlock",
    "alasillidan": "Alas Illidan", "marcaancestral": "Ancestral Mark",
    "taunt_flag": "Taunt Flag", "s_": "", "a": "", "alysrazor": "Alysrazor",
    "batloa": "Bat Loa", "bloodqueen": "Blood Queen", "boneguardfel": "Boneguard Fel",
    "dragonsinestra": "Dragon Sinestra", "dreadlord2": "Dreadlord", "fx": "",
    "fel_overfiend": "Fel Overfiend", "kithix": "Kithix",
    "mantidgrandvizier": "Mantid Grand Vizier", "mantid_low03_wingednoshadow": "Mantid",
    "reanimatedmannorothskeleton": "Reanimated Mannoroth",
    "reanimatedmannoroth": "Reanimated Mannoroth", "wingederedar": "Winged Eredar",
})

VARIANT.update({
    "magenta": "Magenta", "brownskin": "Brown Skin", "darkskin": "Dark Skin",
    "redskin": "Red Skin", "whiteskin": "White Skin", "original": "Original",
    "yellw": "Yellow", "01blue": "Blue", "01pink": "Pink", "flyanim": "Flying",
    "boss": "Boss", "01": "I", "02": "II",
})


OVERRIDES.update({
    "overfiend_wings": "Fel Overfiend Wings",
    "overfiend_wings_blue": "Fel Overfiend Wings (Blue)",
    "overfiend_wings_green": "Fel Overfiend Wings (Green)",
    "overfiend_wings_purple": "Fel Overfiend Wings (Purple)",
    "overfiend_wings_teal": "Fel Overfiend Wings (Teal)",
    "overfiend_wings_white": "Fel Overfiend Wings (White)",
    "reanimatedmannorothskeleton_wings": "Mannoroth Skeleton Wings",
    "reanimatedmannorothskeleton_wings1": "Mannoroth Skeleton Wings II",
    "wingederedar_wings_boss": "Winged Eredar Lord Wings",
    "spell_warlockmorphwings": "Warlock Wings",
    "mantid_low03_wingednoshadow_wings": "Mantid Wings",
    "mantid_low03_wingednoshadow_wings_blue": "Mantid Wings (Blue)",
    "mantid_low03_wingednoshadow_wings_brown": "Mantid Wings (Brown)",
    "mantid_low03_wingednoshadow_wings_red": "Mantid Wings (Red)",
})

ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")


def number_family(models: list) -> dict:
    """Give one family's numbered variants I..N, so no two wings share a name.

    ``batloa_wings`` + ``batloa_wings1..3`` become ``Bat Loa Wings I..IV``.
    """
    groups = {}
    for model in models:
        stem = re.sub(r"\.(mdx|m2)$", "", model.replace("/", "\\").split("\\")[-1], flags=re.I).lower()
        index = 0
        if re.search(r"(?<=[a-z_])\d$", stem):
            index = int(stem[-1])
            stem = stem[:-1]
        groups.setdefault(stem, []).append((index, model))
    names = {}
    for members in groups.values():
        if len(members) == 1:
            continue
        for index, model in sorted(members):
            names[model] = index
    return names


#: Remaining cases where the author's numbering is the only thing telling two wings apart.
OVERRIDES.update({
    "dreadqueen_3846332_wings": "Dread Queen Wings I",
    "dreadqueen_3846333_wings": "Dread Queen Wings II",
    "dreadqueen_3846334_wings": "Dread Queen Wings III",
    "dreadqueen_3846335_wings": "Dread Queen Wings IV",
    "dreadqueen_3846336_wings": "Dread Queen Wings V",
    "dreadqueen_3846337_wings": "Dread Queen Wings VI",
    "skull_wings01": "Skull Wings I",
    "skull_wings02": "Skull Wings II",
    "skull_wings03": "Skull Wings III",
    "skull_wings04": "Skull Wings IV",
    "flyingspriteevil_wings_21_wings": "Vile Sprite Wings I",
    "flyingspriteevil_wings_22_wings": "Vile Sprite Wings II",
    "flyingspriteevil_wings_23_wings": "Vile Sprite Wings III",
    "flyingspriteevil_wings_24_wings": "Vile Sprite Wings IV",
    "xavius_wings_color_01": "Xavius Wings (Color I)",
    "xavius_wings_color_02": "Xavius Wings (Color II)",
    "xavius_wings_color_03": "Xavius Wings (Color III)",
    "xavius_wings_color_04": "Xavius Wings (Color IV)",
    "arbiter2_wings": "Arbiter Wings II",
    "tb_ogre_armor_01_wings": "Ogre Armor Wings I",
    "tb_ogre_armor_02_wings": "Ogre Armor Wings II",
    "voidwraithraidboss_wings": "Void Wraith Wings (Raid)",
    "obsidiandestroyer2_boss_wings": "Obsidian Destroyer Wings",
    "voidtouchedwolfbat_wings_right": "Void-Touched Wolf Bat Wings (Right)",
    "flyingsprite_wings_tealindigo_wings": "Flying Sprite Wings (Teal Indigo)",
})



def _words(stem: str) -> list:
    s = re.sub(r"\.(mdx|m2)$", "", stem, flags=re.I)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)
    return [w for w in re.split(r"[_\s]+", s) if w]


def clean_wing_name(model_path: str) -> str:
    """Turn a donor model path into a player-facing name."""
    stem = re.sub(r"\.(mdx|m2)$", "", model_path.replace("/", "\\").split("\\")[-1], flags=re.I)
    if stem.lower() in OVERRIDES:
        return OVERRIDES[stem.lower()]

    words = [w for w in _words(stem) if not re.fullmatch(r"\d{5,}", w)]
    lowered = [w.lower() for w in words]
    # drop the author's version tail: _01 / _02 / _v2 / _tex2
    variant_extra = []
    keep = []
    for i, (w, lw) in enumerate(zip(words, lowered)):
        if lw in ("v2", "tex2") or re.fullmatch(r"0\d", lw):
            continue
        if lw == "wings1":
            continue
        if lw in VARIANT:
            variant_extra.append(VARIANT[lw])
            continue
        keep.append((w, lw))

    # collapse a doubled "wings wings"
    names, seen_wings = [], False
    for w, lw in keep:
        mapped = WORDS.get(lw)
        if mapped is not None:
            if mapped:
                names.extend(mapped.split())
            continue
        if lw == "wings":
            if seen_wings:
                continue
            seen_wings = True
        names.append(w)

    pretty = []
    for i, w in enumerate(names):
        lw = w.lower()
        if lw in ("of", "the", "and", "or", "a", "an", "in", "on") and i:
            pretty.append(lw)
        elif w.isupper() and len(w) <= 3:
            pretty.append(w)
        else:
            pretty.append(w[:1].upper() + w[1:])
    name = " ".join(pretty)
    if "wings" not in name.lower():
        name += " Wings"
    if variant_extra:
        name += " (" + ", ".join(variant_extra) + ")"
    return name


def wing_name(model_path: str, number: int | None = None) -> str:
    """Clean name, with an optional family numeral appended."""
    name = clean_wing_name(model_path)
    if number:
        # ``batloa_wings2`` is the family's third wing, not a wing called "Wings2".
        name = re.sub(r"\d+$", "", name).strip()
        name += " " + ROMAN[min(number, len(ROMAN) - 1)]
    return name
