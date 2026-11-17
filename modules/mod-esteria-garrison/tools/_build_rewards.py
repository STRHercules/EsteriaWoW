import json
import struct
import subprocess
import urllib.request
from pathlib import Path

root = Path(r"g:\risServer")
db2 = next((root / r"EsteriaWoW\modules\mod-esteria-garrison\tools\_reward_dl").glob("*21676*.db2"))
data = db2.read_bytes()
base = 48
rows = [struct.unpack_from("<11I", data, base + i * 44) for i in range(658)]

mysql = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
proc = subprocess.run(
    [mysql, "--host=127.0.0.1", "-uacore", "-pacore", "-D", "acore_world", "--batch", "--raw",
     "-e", "SELECT id FROM db2_garr_mission WHERE garr_follower_type_id=1"],
    capture_output=True, text=True, check=False)
missions = set()
for line in proc.stdout.splitlines()[1:]:
    if line.strip().isdigit():
        missions.add(int(line))
print("missions", len(missions))

by_mission = {}
items = set()
currencies = set()
for row in rows:
    mission = row[1]
    if mission not in missions:
        continue
    xp, item, qty, currency, value = row[2], row[3], row[4], row[5], row[6]
    entry = None
    if item:
        entry = ["item", 0, qty or 1, ""]
        items.add(item)
        entry.append(item)
    elif currency and value:
        entry = ["currency", 0, value, ""]
        currencies.add(currency)
        entry.append(currency)
    elif value:
        gold = value // 10000
        if gold < 1:
            gold = 1
        entry = ["gold", 0, gold, "%d Gold" % gold]
    elif xp:
        entry = ["xp", 1001982, xp, "%d XP" % xp]
    if entry:
        by_mission.setdefault(mission, []).append(entry)

print("rewarded", len(by_mission), "items", len(items), "currencies", sorted(currencies))

def tooltip(kind, ident):
    url = "https://nether.wowhead.com/tooltip/%s/%d" % (kind, ident)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8", "replace"))
    return payload.get("icon") or "", payload.get("name") or ""

icons = {}
for item in sorted(items):
    try:
        icon, name = tooltip("item", item)
        icons[("item", item)] = (icon.lower(), name)
        print("item", item, icon, name)
    except Exception as error:
        print("item fail", item, error)
for currency in sorted(currencies):
    try:
        icon, name = tooltip("currency", currency)
        icons[("currency", currency)] = (icon.lower(), name)
        print("currency", currency, icon, name)
    except Exception as error:
        print("currency fail", currency, error)

wanted = set()
for _key, (icon, _name) in icons.items():
    if icon:
        wanted.add("interface/icons/%s.blp" % icon)

found = {}
listfile = root / r"_ref\community-listfile.csv"
with listfile.open("r", encoding="utf-8", errors="replace") as handle:
    for line in handle:
        line = line.strip()
        if ";" not in line:
            continue
        fdid, path = line.split(";", 1)
        path = path.lower()
        if path in wanted and path not in found:
            found[path] = int(fdid)
print("icons found", len(found), "of", len(wanted))

cache = root / r"Esteria - Client\Data\Retail\Cache\Retail\wow-88d5e8ef05ec5a8446cdec93d142d7c6\decoded\2\strict"

def checksum(blob):
    value = 14695981039346656037
    for byte in blob:
        value ^= byte
        value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value

def ensure(fdid):
    dest = cache / ("id-%d.bin" % fdid)
    if dest.exists():
        return True
    url = "https://wago.tools/api/casc/%d?download" % fdid
    request = urllib.request.Request(url, headers={"User-Agent": "esteria"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    if payload[:4] != b"BLP2":
        print("bad blp", fdid)
        return False
    header = struct.pack("<IIQ", 0x31434457, len(payload), checksum(payload))
    dest.write_bytes(header + payload)
    print("cached", fdid, len(payload))
    return True

ensure(1001982)
for path, fdid in found.items():
    if not ensure(fdid):
        found[path] = 0

for mission, entries in by_mission.items():
    for entry in entries:
        if entry[0] == "item":
            item = entry.pop()
            icon, name = icons.get(("item", item), ("", ""))
            entry[1] = found.get("interface/icons/%s.blp" % icon, 0) if icon else 0
            entry[3] = name or ("Item %d" % item)
        elif entry[0] == "currency":
            currency = entry.pop()
            icon, name = icons.get(("currency", currency), ("", ""))
            entry[1] = found.get("interface/icons/%s.blp" % icon, 0) if icon else 0
            entry[3] = name or ("Currency %d" % currency)

lines = ["MISSION_REWARD = {"]
for mission in sorted(by_mission):
    parts = []
    for kind, icon, amount, name in by_mission[mission]:
        if kind != "gold" and not icon:
            continue
        safe = name.replace("\\", "\\\\").replace('"', '\\"')
        parts.append('{"%s",%d,%d,"%s"}' % (kind, icon, amount, safe))
    if parts:
        lines.append(" [%d]={%s}," % (mission, ",".join(parts)))
lines.append("}")
out = root / r"Esteria - Client\Interface\AddOns\EsteriaGarrison\_mission_rewards.lua"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out, "lines", len(lines))
