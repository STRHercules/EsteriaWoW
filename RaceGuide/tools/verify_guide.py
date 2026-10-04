"""Verify the handoff's frozen files and authored references without builds or live mutations."""

import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main():
    errors = []
    docs = sorted(ROOT.glob("*.md")) + sorted((ROOT / "reference").glob("*.md"))
    links = 0
    for doc in docs:
        raw = doc.read_bytes()
        text = raw.decode("utf-8")
        if b"\r" in raw or not raw.endswith(b"\n"):
            errors.append(f"Expected UTF-8/LF/trailing newline: {doc.name}")
        if any(line.rstrip() != line for line in text.splitlines()):
            errors.append(f"Trailing whitespace: {doc.name}")
        if text.count("~~~") % 2:
            errors.append(f"Unclosed code fence: {doc.name}")
        # Strip code so examples and parser representations cannot become false links.
        prose = re.sub(r"(?ms)^(?:~~~|```).*?^(?:~~~|```)[ \t]*$", "", text)
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", prose):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target = unquote(target.strip("<>").split("#", 1)[0])
            if not (doc.parent / target).exists():
                errors.append(f"Broken link in {doc.name}: {target}")
            links += 1

    manifest = json.loads((ROOT / "evidence/snapshot-manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = ROOT / item["snapshot"]
        if not path.is_file() or sha(path) != item["sha256"]:
            errors.append(f"Snapshot hash mismatch: {item['snapshot']}")
    current = json.loads((ROOT / "evidence/current-state.json").read_text(encoding="utf-8"))
    for item in current["glue"]:
        if "snapshot" in item and sha(ROOT / item["snapshot"]) != item["sha256"]:
            errors.append(f"Extracted Glue hash mismatch: {item['entry']}")
    for path in (ROOT / "tools").glob("*.py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            errors.append(str(error))
    conversations = json.loads((ROOT / "evidence/conversations.json").read_text(encoding="utf-8"))
    if len(conversations) != 6 or not all(c["all_pages_read"] for c in conversations):
        errors.append("The six supplied chats were not fully read")
    result = {"status": "failed" if errors else "passed", "documents_checked": len(docs),
              "local_links_checked": links, "snapshot_files_checked": len(manifest["files"]),
              "glue_records_checked": len(current["glue"]), "errors": errors}
    (ROOT / "evidence/guide-verification.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
