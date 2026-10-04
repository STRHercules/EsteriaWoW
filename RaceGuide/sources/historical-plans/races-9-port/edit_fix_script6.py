import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")

start = text.index("        if not args.skip_stage:")
end = text.index("        if args.dry_run:")
new = '''        if not args.skip_stage:
            pattern = re.compile(r"_[A-Za-z]{2}[MF](\\d\\d)?\\.(m2|skin|mdx)$", re.IGNORECASE)
            shipped: dict[str, str] = {}
            stems = set()
            for name in list_names(storm, ours, HEAD.lower()):
                tail = name[len(HEAD):]
                shipped.setdefault(tail.lower(), name)
                match = pattern.search(tail)
                if match:
                    stems.add(tail[: match.start()])
            print(f"head component stems our client already ships: {len(stems)}")

            def borrow(stem: str, suffix: str) -> bytes | None:
                """Any code/sex of the same stem, so the helm renders instead of cubing."""
                wanted_kind = "skin" if suffix.endswith(".skin") else "m2"
                for candidate in shipped.values():
                    tail = candidate[len(HEAD):]
                    if not tail.lower().startswith(stem.lower() + "_"):
                        continue
                    if (".skin" in tail.lower()) != (wanted_kind == "skin"):
                        continue
                    _source, blob = read(storm, ours, candidate)
                    if blob is not None:
                        return blob
                return None

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
                if blob is None:
                    tail = key[len(HEAD):]
                    stem, _sep, rest = tail.rpartition("_")
                    for fallback in FALLBACK_CODES:
                        _source, blob = read(storm, ours, f"{HEAD}{stem}_{fallback}{rest[2:]}")
                        if blob is not None:
                            borrowed.append((key, f"{stem}_{fallback}{rest[2:]}"))
                            break
                if blob is None:
                    blob = borrow(*key[len(HEAD):].rpartition("_")[::2])
                    if blob is not None:
                        borrowed.append((key, "any code/sex"))
                if blob is None:
                    missing.append(key)
                    continue
                entries[key] = blob
                total += len(blob)
            staged = len(entries) - (1 if CHRRACES in entries else 0)
            print(f"   staging {staged} files, {total / 1048576:.1f} MB; "
                  f"{len(borrowed)} borrowed, {len(missing)} unavailable")
            for key, source_key in borrowed[:5]:
                print(f"      ~ {key[len(HEAD):]} <- {source_key}")
            for key in missing[:10]:
                print(f"      ! {key[len(HEAD):]}")

'''
path.write_text(text[:start] + new + text[end:], encoding="utf-8")
print("rewritten")
