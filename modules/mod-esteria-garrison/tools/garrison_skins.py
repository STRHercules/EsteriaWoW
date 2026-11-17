"""Body textures for garrison creatures.

Retail humanoids keep the body texture out of the M2 (texture type 1, "supplied by
display info"). The 3.3.5 display row has nowhere to put a FileDataID for type 1, so
the mesh draws white. The client already applies EsteriaMounts skin rows to whatever
display is on screen, and Data/HotS/MountSkins.csv is merged on top of that catalog.
This writes one type-1 row per garrison display: the bake texture of its
CreatureDisplayInfoExtra, or the display's own texture variation when it has no bake.
"""
import argparse
import csv
import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = Path(r"G:\garrison-build\ref")  # wago.tools DB2 CSVs, cached
DBC_SQL = HERE.parent / "sql" / "world" / "garrison_dbc_world.sql"
BUILD = "12.1.5.70783"  # the installed retail client's build (T:\World of Warcraft\.build.info), so rows match it
BEGIN, END = "# mod-esteria-garrison begin", "# mod-esteria-garrison end"


def wago(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as response:
        return response.read().decode("utf-8", "replace")


def garrison_displays():
    """The creature displays the garrison adds (build_client_dbc.py's server rows); Esteria's own are never touched."""
    text = DBC_SQL.read_text(encoding="utf-8")
    block = re.search(r"REPLACE INTO `creaturedisplayinfo_dbc` \([^)]*\) VALUES\n(.*?);\n", text, re.S)
    return {int(i) for i in re.findall(r"^\((\d+),", block.group(1), re.M)}


def load_rows(path, key):
    with path.open(encoding="utf-8") as handle:
        return {int(row[key]): row for row in csv.DictReader(handle)}


def batched(url, ids, column):
    rows = []
    ids = sorted(set(ids))
    for start in range(0, len(ids), 40):
        filt = "||".join(f"exact:{item}" for item in ids[start:start + 40])
        text = wago(f"{url}&filter[{column}]={filt}")
        rows.extend(csv.DictReader(text.splitlines()))
    return rows


def textures_for(materials):
    found = {}
    for row in batched("https://wago.tools/db2/TextureFileData/csv?build=" + BUILD, materials, "MaterialResourcesID"):
        material = int(row["MaterialResourcesID"])
        usage = int(row["UsageType"])
        file_id = int(row["FileDataID"])
        current = found.get(material)
        if current is None or (usage == 0 and current[0] != 0) or (current[0] != 0 and usage < current[0]):
            found[material] = (usage, file_id)
    return {material: file_id for material, (_, file_id) in found.items()}


def geosets_for(retail_ids):
    chosen = {}
    for row in batched("https://wago.tools/db2/CreatureDisplayInfoGeosetData/csv?build=" + BUILD, retail_ids, "CreatureDisplayInfoID"):
        display = int(row["CreatureDisplayInfoID"])
        index = int(row["GeosetIndex"])
        value = int(row["GeosetValue"])
        chosen.setdefault(display, {}).setdefault(index, value)
    return chosen


# One mesh per body region. Mesh 0 stays up on its own. The head is 3202 (3201 is a stub).
# Shins are group 5 and thighs group 13; leaving either at 0 drops the boots onto the ground.
ANATOMY = {4: 1, 5: 1, 7: 2, 13: 1, 18: 1, 20: 1, 22: 1, 23: 1, 32: 2, 33: 1}


def db2(name):
    path = REF / f"wago_{name}.csv"
    if not path.exists() or path.stat().st_size < 20:
        path.write_text(wago(f"https://wago.tools/db2/{name}/csv?build={BUILD}"), encoding="utf-8")
        print("fetched", name, path.stat().st_size)
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def customization(entries):
    """Per display extra: the hairstyle geoset and the hair/eye/skin-extra materials.

    entries are (extra id, race, sex). A display's own choices replace the race default
    for the same option, so each NPC keeps the braid or beard it was baked with.
    """
    entries = list(entries)
    link = {(int(row["ChrRacesID"]), int(row["Sex"])): int(row["ChrModelID"]) for row in db2("ChrRaceXChrModel")}
    layout_of = {int(row["ID"]): int(row["CharComponentTextureLayoutID"] or 0) for row in db2("ChrModel")}
    options_by_model = {}
    for row in db2("ChrCustomizationOption"):
        options_by_model.setdefault(int(row["ChrModelID"]), []).append(int(row["ID"]))
    best = {}
    for row in db2("ChrCustomizationChoice"):
        option = int(row["ChrCustomizationOptionID"])
        current = best.get(option)
        if current is None or int(row["OrderIndex"]) < int(current["OrderIndex"]):
            best[option] = row
    default_choice = {option: int(row["ID"]) for option, row in best.items()}
    elements = {}
    for row in db2("ChrCustomizationElement"):
        elements.setdefault(int(row["ChrCustomizationChoiceID"]), []).append(row)
    geoset_row = {int(row["ID"]): row for row in db2("ChrCustomizationGeoset")}
    materials = {int(row["ID"]): row for row in db2("ChrCustomizationMaterial")}
    # Hair color (target 10) paints texture type 6. Skip type 1: that slot is the body bake.
    slot_of = {}
    for row in db2("ChrModelTextureLayer"):
        for key in ("ChrModelTextureTargetID_0", "ChrModelTextureTargetID_1"):
            target = int(row[key] or 0)
            slot = int(row["TextureType"] or 0)
            if target and slot and slot != 1:
                slot_of.setdefault((int(row["CharComponentTextureLayoutsID"]), target), slot)
    picked = {}
    for extra_id, _race, _sex in entries:
        if extra_id:
            picked.setdefault(extra_id, [])
    for row in batched("https://wago.tools/db2/CreatureDisplayInfoOption/csv?build=" + BUILD, picked, "CreatureDisplayInfoExtraID"):
        picked.setdefault(int(row["CreatureDisplayInfoExtraID"]), []).append(
            (int(row["ChrCustomizationOptionID"]), int(row["ChrCustomizationChoiceID"])))
    looks = {}
    for extra_id, race, sex in entries:
        model = link.get((race, sex), 0)
        chosen = {option: default_choice[option] for option in options_by_model.get(model, []) if option in default_choice}
        for option, choice in picked.get(extra_id, []):
            chosen[option] = choice
        geosets, textures = {}, {}
        layout = layout_of.get(model, 0)
        for choice in chosen.values():
            for element in elements.get(choice, []):
                geoset_id = int(element["ChrCustomizationGeosetID"] or 0)
                row = geoset_row.get(geoset_id)
                if row:
                    geosets[int(row["GeosetType"])] = int(row["GeosetID"])
                material = materials.get(int(element["ChrCustomizationMaterialID"] or 0))
                if not material:
                    continue
                target = int(material["ChrModelTextureTargetID"] or 0)
                resource = int(material["MaterialResourcesID"] or 0)
                slot = slot_of.get((layout, target), 6 if target == 10 else 0)
                if slot and resource:
                    textures[slot] = resource
        looks[extra_id] = (geosets, textures)
    return looks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default=r"G:\3.3.5a - Dev")
    out = Path(ap.parse_args().client) / "Data" / "HotS" / "MountSkins.csv"
    REF.mkdir(parents=True, exist_ok=True)
    displays = garrison_displays()
    mapping = json.loads((HERE / "garrison_display_map.json").read_text(encoding="utf-8"))["creature_display"]
    retail_of = {int(local): int(retail) for retail, local in mapping.items()}
    info = {int(r["ID"]): r for r in db2("CreatureDisplayInfo")}
    extra = {int(r["ID"]): r for r in db2("CreatureDisplayInfoExtra")}

    wanted = {}
    skipped = []
    for local in sorted(displays):
        retail = retail_of.get(local)
        row = info.get(retail) if retail else None
        if not row:
            skipped.append(local)
            continue
        extra_id = int(row["ExtendedDisplayInfoID"] or 0)
        variation = int(row["TextureVariationFileDataID_0"] or 0)
        record = extra.get(extra_id) if extra_id else None
        # The square bake is a different packing. The model's UVs are the 2:1 race sheet,
        # which is the HD bake: face, chest and legs land on the matching islands there.
        material = int(record["HDBakeMaterialResourcesID"] or 0) if record else 0
        if not material and record:
            material = int(record["BakeMaterialResourcesID"] or 0)
        race = int(record["DisplayRaceID"] or 0) if record else 0
        sex = int(record["DisplaySexID"] or 0) if record else 0
        if material:
            wanted[local] = ("bake", material, retail, race, sex, extra_id)
        elif variation:
            wanted[local] = ("variation", variation, retail, race, sex, extra_id)
        else:
            skipped.append(local)

    looks = customization((extra_id, race, sex) for kind, _value, _retail, race, sex, extra_id in wanted.values() if kind == "bake")
    resources = [material for kind, material, _retail, _race, _sex, _extra in wanted.values() if kind == "bake"]
    for geoset_map, textures in looks.values():
        resources.extend(textures.values())
    baked = textures_for(resources)
    geosets = geosets_for(retail for _kind, _value, retail, _race, _sex, _extra in wanted.values())
    lines = ["# garrison creature looks: display;t;textureType;fileDataId  or  display;g;geosetGroup;geosetValue"]
    missing = []
    overflow = []
    geoset_rows = 0
    for local, (kind, value, retail, race, sex, extra_id) in sorted(wanted.items()):
        file_id = baked.get(value) if kind == "bake" else value
        if not file_id:
            missing.append(local)
            continue
        lines.append(f"{local};t;1;{file_id}")
        if kind != "bake":
            lines.append(f"{local};t;11;{file_id}")
        # Baking a character leaves every hairstyle and armor variant switched on, which piles
        # them up. The display's own choices name its braid, beard and tail; the remaining
        # groups are one body part each, and anything unmentioned is an extra outfit to hide.
        # Hair color is texture type 6, never the body sheet. A plain creature only gets the
        # groups its own display row names.
        if kind == "bake":
            hair_geosets, hair_textures = looks.get(extra_id, ({}, {}))
            for slot, resource in sorted(hair_textures.items()):
                hair_file = baked.get(resource)
                if hair_file and slot != 1:
                    lines.append(f"{local};t;{slot};{hair_file}")
            chosen = dict(ANATOMY)
            chosen.update(hair_geosets)
            if 0 not in chosen:
                chosen[0] = 0
            for group in range(61):
                chosen.setdefault(group, 0)
        else:
            chosen = geosets.get(retail, {})
        for index in sorted(chosen):
            geoset = chosen[index]
            if index >= 100 or geoset >= 100:
                overflow.append((local, index, geoset))
                continue
            lines.append(f"{local};g;{index};{geoset}")
            geoset_rows += 1

    # the client merges this loose file over its archive catalog: keep everyone else's rows, replace only our block
    old = out.read_text(encoding="utf-8") if out.exists() else ""
    old = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", old, flags=re.S).rstrip("\n")
    theirs = {int(l.split(";")[0]) for l in old.splitlines() if l and not l.startswith("#")}
    clash = theirs & {int(l.split(";")[0]) for l in lines[1:]}
    assert not clash, f"displays already skinned in {out}: {sorted(clash)[:10]}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text((old + "\n" if old else "") + "\n".join([BEGIN] + lines[1:] + [END]) + "\n", encoding="utf-8", newline="\n")
    print(f"displays {len(displays)}, skinned {sum(1 for line in lines if ';t;' in line)} texture rows, {geoset_rows} geoset rows")
    print(f"no texture: {len(skipped)} {skipped[:12]}")
    print(f"bake without a file: {len(missing)} {missing[:12]}")
    print(f"geoset out of range: {len(overflow)} {overflow[:8]}")
    print("wrote", out)


if __name__ == "__main__":
    main()
