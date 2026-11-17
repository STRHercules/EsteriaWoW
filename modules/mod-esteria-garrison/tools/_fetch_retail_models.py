"""Fetch retail modelviewer FileDataIDs for garrison NPCs/GOs."""
import json
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0"}

# esteria entry -> retail creature id (wowhead)
NPCS = {
    9601101: 77209,   # Baros Alexston
    9601102: 78466,   # Gazlowe
    9601103: 80551,   # Lieutenant Thorn
    9601104: 79740,   # Warmaster Zog
    9601105: 79970,   # Alliance quartermaster (placeholder id; resolve)
    9601106: 79774,   # Horde quartermaster
    9601107: 81103,   # Dungar Longdrink
    9601108: 86031,   # Flight master Horde
    9601109: 86677,   # Alliance guard
    9601110: 86678,   # Horde guard
    9601111: 80496,   # Sergeant Crowley?
    9601112: 79781,   # Horde sergeant
    9601120: 77368,   # Innkeeper Lunarfall
    9601121: 79828,   # Innkeeper Frostwall
    9601122: 86974,   # Stable master Alliance
    9601123: 86973,   # Stable master Horde
    9601166: 85484,   # Menagerie / beast keeper stand-in (Ken Loggin 77377)
    9601301: 77378,   # Shelly Hamby
    9601302: 79320,   # Qiana Moonshadow
    9601303: 79281,   # Rulkan
    9601304: 79715,   # Delvar Ironfist
    9601305: 82392,   # Admiral Taylor
    9601306: 80572,   # Fiona
    9601401: 84776,   # Olin Umberhide
    9601402: 79853,   # Mulverick
    9601403: 79315,   # Ka'la
    9601404: 80001,   # Lantresor
    9601405: 79921,   # Shadow Hunter Rala
    9601406: 85130,   # Benjamin Gibb
}

# building trainers / workers — named retail NPCs where known
EXTRAS = {
    9601126: 77792,   # Rachelle Black (blacksmith area / mining?)
    9601130: 77792,   # Rachelle Black blacksmith
    9601148: 77377,   # Ken Loggin lumber
    9601150: 86775,   # trading?
    9601156: 91582,   # mage tower?
}

GOS = {
    9602001: 237191,  # Garrison Cache guess
}


def get(kind: str, rid: int):
    url = f"https://wow.zamimg.com/modelviewer/live/meta/{kind}/{rid}.json"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    out = {}
    for entry, rid in {**NPCS, **EXTRAS}.items():
        try:
            meta = get("npc", rid)
            out[str(entry)] = {
                "retailId": rid,
                "kind": "npc",
                "model": meta.get("Model"),
                "scale": meta.get("Scale") or 1.0,
                "textures": meta.get("Textures") or {},
            }
            print(entry, rid, "OK", meta.get("Model"), meta.get("Textures"))
        except Exception as e:
            print(entry, rid, "FAIL", e)
            out[str(entry)] = {"retailId": rid, "kind": "npc", "error": str(e)}
    for entry, rid in GOS.items():
        try:
            meta = get("gameobject", rid)
            out[str(entry)] = {
                "retailId": rid,
                "kind": "go",
                "model": meta.get("Model"),
                "scale": meta.get("Scale") or 1.0,
                "textures": meta.get("Textures") or {},
                "raw": meta,
            }
            print("GO", entry, rid, "OK", meta)
        except Exception as e:
            print("GO", entry, rid, "FAIL", e)
            # try a few cache object ids
            for alt in (236916, 233028, 230749, 237191, 232343):
                try:
                    meta = get("gameobject", alt)
                    print("  alt GO", alt, meta)
                except Exception as e2:
                    print("  alt GO", alt, "FAIL", e2)

    path = Path(__file__).with_name("retail_model_meta.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
