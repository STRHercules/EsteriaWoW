"""Generate reference indexes from the captured evidence, without accessing a client or database."""

from collections import Counter
import json
from pathlib import Path
import textwrap
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reference"


def read(name):
    return json.loads((ROOT / "evidence" / name).read_text(encoding="utf-8"))


def write(name, lines):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def link(path, label=None):
    return f"[{label or Path(path).name}]({quote('../' + path, safe='/')})"


def main():
    manifest = read("snapshot-manifest.json")
    current = read("current-state.json")
    lines = ["# Complete Python tool and library index", "", "Generated from source ASTs; no listed script was executed.",
             "Historical scripts retain original paths and may mutate archives or databases.",
             "Use the maintained entry points in [the recipes](../03-RECIPES.md) for deployment.", "",
             "Exact parser declarations and imports: [tool-index.json](../evidence/tool-index.json).", ""]
    seen = set()
    for entry in sorted(read("tool-index.json"), key=lambda e: e["snapshot"]):
        path = entry["snapshot"]
        if path in seen:
            continue
        seen.add(path)
        lines += [f"## {path.removeprefix('sources/')}", "", link(path, "Source"), ""]
        summary = (entry.get("summary") or "Library, test, or historical helper; inspect its source before use.")
        lines += textwrap.wrap(" ".join(summary.split()), width=110, break_long_words=False) + [""]
        if entry.get("arguments"):
            short = [a for a in entry["arguments"] if len(a) <= 120]
            if short:
                lines += ["Parser declarations:", "", "```python", *short, "```", ""]
            if len(short) != len(entry["arguments"]):
                lines += ["Long declarations for this entry are preserved in the linked tool-index.json.", ""]
    write("ALL_TOOLS.md", lines)

    lines = ["# Exact customization option catalog", "", "Read from each saved integration codec.",
             "A one-choice field is a constant and does not add a changing creator control.",
             "Skyborne/Mechagnome descriptors reside in the shared binary catalog and have their own recipe.", ""]
    for race, sexes in current["codecs"].items():
        lines += [f"## {race}", ""]
        for sex, profile in sexes.items():
            varying = sum(o["choices"] > 1 for o in profile["controls"])
            lines += [f"### {sex}: {varying} changing controls, {len(profile['controls'])} authored fields", "",
                      "| Control | Choices |", "| --- | ---: |"]
            lines += [f"| {o['label']} | {o['choices']} |" for o in profile["controls"]]
            lines += [""]
    write("CUSTOMIZATION_OPTIONS.md", lines)

    lines = ["# Current client race rows", "", "Decoded from the effective ChrRaces.dbc, including legacy/NPC rows.",
             "A DBC row or database start does not mean that race is visible in the creator.", "",
             "| ID | Name | File string | Prefix | Male / female display | Team field |",
             "| ---: | --- | --- | --- | --- | ---: |"]
    lines += [f"| {r['id']} | {r['name']} | {r['file_string']} | {r['prefix']} | "
              f"{r['male_display']} / {r['female_display']} | {r['team_id']} |" for r in current["race_rows"]]
    write("RACE_ROWS.md", lines)

    lines = ["# Installed client artifacts", "", "SHA-256 values refer to the client at capture time.",
             "Large archives are size-inventoried only; this list is not an MPQ payload verification report.", ""]
    for item in read("client-artifacts.json")["artifacts"]:
        lines += [f"## {Path(item['path']).name}", "", f"Location: `{item['path']}`", "",
                  f"Bytes: {item['bytes']:,}", "", f"SHA-256: `{item['sha256']}`", ""]
        if "header_u32" in item:
            lines += [f"Header DWORDs: `{item['header_u32']}`", ""]
    write("CLIENT_ARTIFACTS.md", lines)

    lines = ["# Core files changed since the initial AC import", "",
             "Baseline a29b5dc is this repository's AC import, not a verified current upstream commit.",
             "This includes inherited playerbot changes, Eluna integration and Esteria changes.",
             "Current dirty source is included; it is not proof that the running image contains every change.", "",
             "Exact diff: [server-since-core-import.patch](../evidence/server-since-core-import.patch).", ""]
    for line in (ROOT / "evidence/core-changed-files.tsv").read_text(encoding="utf-8").splitlines():
        additions, deletions, path = line.split("\t", 2)
        snapshot = "sources/EsteriaWoW/" + path
        source = link(snapshot, path) if (ROOT / snapshot).is_file() else f"`{path}` (deleted)"
        lines += [f"- {source}", f"  Added {additions} lines; removed {deletions}."]
    write("CORE_FILES.md", lines)

    lines = ["# Source-installed module inventory", "", "Presence and source-file counts are verified.",
             "Activation still depends on compiled inclusion, configuration, SQL, and feature-specific live tests.", "",
             "| Module | Text/source files | Reference |", "| --- | ---: | --- |"]
    for module in read("modules.json"):
        name = module["name"]
        path = f"sources/EsteriaWoW/modules/{name}/README.md"
        reference = link(path, "README") if (ROOT / path).is_file() else f"EsteriaWoW `modules/{name}/`"
        lines += [f"| {name} | {module['source_files']} | {reference} |"]
    write("MODULES.md", lines)

    lines = ["# Source package provenance", "", f"Server HEAD: `{manifest['server_head']}`", "",
             f"Captured files: {len(manifest['files']):,}", "",
             f"Captured file bytes: {sum(f['bytes'] for f in manifest['files']):,}", "",
             "Original paths, hashes and destinations: [snapshot-manifest.json](../evidence/snapshot-manifest.json).",
             "The Compose SOAP credential is replaced with an environment variable in the shareable copy.",
             "Original-source and snapshot hashes are recorded separately for that file.", "",
             "## Sources no longer available", ""]
    lines += [f"- `{p}`" for p in manifest["missing_sources"]]
    lines += ["", "## Snapshot families", ""]
    counts = Counter(f["snapshot"].split("/")[1] for f in manifest["files"])
    lines += [f"- {name}: {count} files." for name, count in sorted(counts.items())]
    write("SOURCE_PROVENANCE.md", lines)
    print(json.dumps({"unique_python_entries": len(seen), "race_rows": len(current["race_rows"]),
                      "dbc_differences": [{"name": d["name"], "server_records": d.get("server_records"),
                        "same_rows": d.get("same_record_multiset"), "same_strings": d.get("string_pools_equal"),
                        "changed_id_count": len(d.get('semantic_changes', [])),
                        "changed_id_sample": [c['id'] for c in d.get('semantic_changes', [])][:8]}
                        for d in current['dbc'] if d.get('byte_equal_to_server') is False]}, indent=2))


if __name__ == "__main__":
    main()
