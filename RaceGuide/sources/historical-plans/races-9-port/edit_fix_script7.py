import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")

start = text.index("        if not args.skip_stage:")
end = text.index("        if args.dry_run:")
new = '''        if not args.skip_stage:
            pattern = re.compile(r"_[A-Za-z]{2}[MF](\\d\\d)?\\.(m2|skin|mdx)$", re.IGNORECASE)
            shipped: dict[str, str] = {}
            sources: dict[str, list[str]] = {}
            stems = set()
            for name in list_names(storm, ours, HEAD.lower()):
                tail = name[len(HEAD):]
                shipped.setdefault(tail.lower(), name)
                match = pattern.search(tail)
                if not match:
                    continue
                stem = tail[: match.start()]
                stems.add(stem)
                if tail.lower().endswith(".m2"):
                    sources.setdefault(stem.lower(), []).append(tail)
            print(f"head component stems our client already ships: {len(stems)}")

            def borrow(tail_stem: str, suffix: str) -> tuple[bytes | None, str | None]:
                """Any code/sex of the same stem, model and skin from one source."""
                for source in sources.get(tail_stem.lower(), ()):
                    model = read(storm, ours, f"{HEAD}{source}")
                    skin = read(storm, ours, f"{HEAD}{source[:-3]}00.skin")
                    if model[1] is None or skin[1] is None:
                        continue
                    if suffix.endswith(".skin"):
                        return skin[1], source
                    return model[1], source
                return None, None

            wanted: dict[str, str] = {}
            for stem in sorted(stems):
                for code in STAGE_CODES:
                    for sex in ("M", "F"):
                        for suffix in (".m2", "00.skin"):
                            key = f"{HEAD}{stem}_{code}{sex}{suffix}"
                            wanted.setdefault(key.lower(), key)

            total = 0
            borrowed = []
            missing = []
            for key in sorted(wanted.values()):
                _source, blob = read(storm, donor, key)
                note = None
                if blob is None:
                    tail = key[len(HEAD):]
                    stem, _sep, rest = tail.rpartition("_")
                    for fallback in FALLBACK_CODES:
                        _source, blob = read(storm, ours, f"{HEAD}{stem}_{fallback}{rest[2:]}")
                        if blob is not None:
                            note = f"{stem}_{fallback}{rest[2:]}"
                            break
                if blob is None:
                    tail_stem, _sep, suffix = key[len(HEAD):].rpartition("_")
                    blob, source = borrow(tail_stem, suffix)
                    note = f"{source} (any code/sex)" if source else None
                if blob is None:
                    missing.append(key)
                    continue
                entries[key] = blob
                total += len(blob)
                if note:
                    borrowed.append((key, note))
            staged = len(entries) - (1 if CHRRACES in entries else 0)
            print(f"   staging {staged} files, {total / 1048576:.1f} MB; "
                  f"{len(borrowed)} borrowed, {len(missing)} unavailable")
            for key, note in borrowed[:6]:
                print(f"      ~ {key[len(HEAD):]} <- {note}")
            for key in missing[:10]:
                print(f"      ! {key[len(HEAD):]}")

'''
path.write_text(text[:start] + new + text[end:], encoding="utf-8")
print("rewritten")
