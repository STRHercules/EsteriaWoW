"""Replicate the staging loop with diagnostics."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_item_component_prefixes as fix

storm = fix.Storm(fix.DLL_DEFAULT)
ours = fix.open_archives(storm, fix.CLIENT, fix.OUR_ORDER)
donor = fix.open_archives(storm, fix.DONOR, fix.DONOR_ORDER)

pattern = re.compile(r"_[A-Za-z]{2}[MF](\d\d)?\.(m2|skin|mdx)$", re.IGNORECASE)
stems = set()
for name in fix.list_names(storm, ours, fix.HEAD.lower()):
    tail = name[len(fix.HEAD):]
    match = pattern.search(tail)
    if match:
        stems.add(tail[: match.start()])
print("stems:", len(stems), sorted(stems)[:3])

wanted: dict[str, str] = {}
for stem in sorted(stems):
    for code in fix.STAGE_CODES:
        for sex in ("M", "F"):
            for suffix in (".m2", "00.skin"):
                key = f"{fix.HEAD}{stem}_{code}{sex}{suffix}"
                wanted.setdefault(key.lower(), key)

missing = []
for key in sorted(wanted.values()):
    _source, blob = fix.read(storm, donor, key)
    if blob is None:
        tail = key[len(fix.HEAD):]
        stem, _sep, rest = tail.rpartition("_")
        tried = []
        for fallback in fix.FALLBACK_CODES:
            borrowed_key = f"{fix.HEAD}{stem}_{fallback}{rest}"
            _src, blob = fix.read(storm, ours, borrowed_key)
            tried.append(f"{fallback}:{'ok' if blob else 'no'}")
        if blob is None:
            missing.append((key, tried, borrowed_key))
for entry in missing[:4]:
    print(entry[0][len(fix.HEAD):], "->", entry[1], "last:", entry[2][len(fix.HEAD):])
print("missing total:", len(missing))
for _name, handle in ours + donor:
    storm.dll.SFileCloseArchive(handle)
