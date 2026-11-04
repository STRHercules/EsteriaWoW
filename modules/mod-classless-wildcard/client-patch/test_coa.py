#!/usr/bin/env python3
"""lib/coa.py on tiny synthetic tables: strings move into the target's block,
visuals and icons follow the ids they were copied under, the contradicted slot
mask is cleared, nothing of the target's is overwritten, and an id the target
uses for something else is copied under a fresh one.

Run:  python test_coa.py
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import coa  # noqa: E402

B = "\\"
NONE = 0xFFFFFFFF


def table(fields, rows, strings):
    """rows: list of {col: int | str}; strings are added to the block."""
    block = bytearray(b"\0")
    recs = bytearray()
    for row in rows:
        rec = bytearray(fields * 4)
        for col, value in row.items():
            if isinstance(value, str):
                off = len(block)
                block += value.encode() + b"\0"
                value = off
            struct.pack_into("<I", rec, col * 4, value)
        recs += rec
    block += strings
    return b"WDBC" + struct.pack("<4I", len(rows), fields, fields * 4, len(block)) + bytes(recs) + bytes(block)


def cell(data, row, col):
    _m, n, f, size, _s = struct.unpack_from("<4s4I", data)
    return struct.unpack_from("<I", data, 20 + row * size + col * 4)[0]


def text(data, off):
    _m, n, f, size, _s = struct.unpack_from("<4s4I", data)
    block = data[20 + n * size:]
    return block[off:block.index(b"\0", off)].decode()


def check_spells():
    target = table(234, [{0: 1, 136: "Stock"}], b"")
    source = table(234, [{0: 7, 136: "Pad"},
                         {0: 500996, 136: "Brutal Swing", 153: "Rank 2", 131: 1000064, 70: 131072, 133: 52943}], b"")
    kept, _n = coa.append_spells(target, source, [500996], {500996})
    assert cell(kept, 1, 131) == 1000064 and cell(kept, 1, 133) == 52943, "unmapped ids are kept"
    out, added = coa.append_spells(target, source, [500996], {500996}, {1000064: 0}, {52943: 990001})
    assert added == 1
    assert cell(out, 0, 0) == 1 and text(out, cell(out, 0, 136)) == "Stock", "the target's own row is untouched"
    assert cell(out, 1, 0) == 500996
    assert text(out, cell(out, 1, 136)) == "Brutal Swing" and text(out, cell(out, 1, 153)) == "Rank 2"
    assert cell(out, 1, 131) == 0, "a visual left off is cleared"
    assert cell(out, 1, 133) == 990001, "a moved icon follows"
    assert cell(out, 1, 70) == 0, "contradicted slot mask cleared"
    try:
        coa.append_spells(out, source, [500996])
        raise AssertionError("an existing id was overwritten")
    except coa.CoAError:
        pass


def check_icons():
    orc = "Interface" + B + "Icons" + B + "Achievement_Character_Orc_Male"
    axe = "Interface" + B + "icons" + B + "5_axe_Border"
    other = "Interface" + B + "Icons" + B + "Something_Else"
    icons = table(2, [{0: 3289, 1: orc}], b"")
    out, new, moved = coa.append_icons(icons, {"3289": orc.lower(), "52943": axe})
    assert new == {52943: axe} and not moved, (new, moved)
    assert text(out, cell(out, 1, 1)) == axe
    out, new, moved = coa.append_icons(icons, {"3289": other}, 60000)
    assert moved == {3289: 60001} and new == {60001: other}, (new, moved)
    assert text(out, cell(out, 0, 1)) == orc, "ours untouched"


def tables(spec):
    fields = dict((n, coa.VISUAL_TABLES[n][0]) for n in coa.VISUAL_TABLES)
    fields["AnimationData"] = 8
    return {n: coa.Table(table(fields[n], spec.get(n, []), b""), fields[n], n) for n in fields}


def check_visuals():
    """A visual comes across with its kits, effect model and sound; a row the
    target has identically is reused; one that differs is copied under a new id
    with the reference moved; an animation this client lacks plays none."""
    hand, boom = "spells" + B + "hand.m2", "spells" + B + "boom.M2"
    src = tables({
        "SpellVisual": [{0: 900, 1: 0, 2: 901, 3: 902, 4: NONE, 5: NONE, 6: NONE}],
        "SpellVisualKit": [{0: 901, 1: NONE, 2: 58, 7: 950, 15: 970},
                           {0: 902, 1: NONE, 2: NONE, 4: 951}],
        "SpellVisualEffectName": [{0: 950, 1: "hand", 2: hand}, {0: 951, 1: "boom", 2: boom}],
        "SoundEntries": [{0: 970, 2: "swing", 3: "swing.ogg", 23: "sound" + B + "spells"}],
    })
    dst = tables({"AnimationData": [{0: 58}],
                  "SpellVisualEffectName": [{0: 951, 1: "boom", 2: "Spells" + B + "Boom.m2"}]})
    added, models, sounds, vmap = coa.visual_closure(src, dst, [900])
    assert {k: v for k, v in added.items() if v} == {"SpellVisual": 1, "SpellVisualKit": 2,
                                                     "SpellVisualEffectName": 1, "SoundEntries": 1}, added
    assert models == [hand], models
    assert sounds == ["sound" + B + "spells" + B + "swing.ogg"], sounds
    assert dst["SpellVisualKit"].cell(901, 7) == 950 and vmap == {900: 900}

    other = "spells" + B + "other.m2"
    dst = tables({"AnimationData": [{0: 58}], "SpellVisualEffectName": [{0: 950, 1: "other", 2: other}]})
    coa.visual_closure(src, dst, [900])
    names = dst["SpellVisualEffectName"]
    moved_to = dst["SpellVisualKit"].cell(901, 7)
    assert moved_to == 952, "the clashing effect name moved past both tables' ids (%d)" % moved_to
    assert names.text(names.cell(950, 2)) == other, "ours untouched"
    assert names.text(names.cell(952, 2)) == hand

    dst = tables({})
    coa.visual_closure(src, dst, [900])
    assert dst["SpellVisualKit"].cell(901, 2) == NONE, "an animation this client lacks plays none"


def check_gameobjects():
    source = coa.Table(table(19, [{0: 10, 1: "new.m2"}, {0: 11, 1: "shared.m2"}], b""), 19, "source")
    target = coa.Table(table(19, [{0: 10, 1: "existing.m2"}, {0: 11, 1: "shared.m2"}], b""), 19, "target")
    original = target.row(10)
    mapping, rows, models = coa.gameobject_displays(source, target, [10, 11])
    assert mapping[10] > 11 and mapping[11] == 11
    assert target.row(10) == original and len(rows) == 1
    assert target.text(target.cell(mapping[10], 1)) == "new.m2" and models == ["new.m2"]
    try:
        coa.gameobject_displays(source, target, [12])
    except coa.CoAError:
        pass
    else:
        raise AssertionError("missing object display was silently accepted")


def main():
    check_gameobjects()
    check_spells()
    check_icons()
    check_visuals()
    print("all checks passed")


if __name__ == "__main__":
    main()
