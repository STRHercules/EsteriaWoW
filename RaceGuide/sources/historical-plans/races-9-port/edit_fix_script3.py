import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")

start = text.index("        if not args.skip_stage:")
end = text.index("        if args.dry_run:")
new = '''        if not args.skip_stage:
            pattern = re.compile(r"_[A-Za-z]{2}[MF](\\d\\d)?\\.(m2|skin|mdx)$", re.IGNORECASE)
            stems = set()
            for name in list_names(storm, ours, HEAD.lower()):
                tail = name[len(HEAD):]
                match = pattern.search(tail)
                if match:
                    stems.add(tail[: match.start()])
            print(f"head component stems our client already ships: {len(stems)}")

            wanted: dict[str, str] = {}
            for stem in sorted(stems):
                for code in STAGE_CODES:
                    for sex in ("M", "F"):
                        for suffix in (".m2", "00.skin"):
                            key = f"{HEAD}{stem}_{code}{sex}{suffix}"
                            wanted.setdefault(key.lower(), key)
            total = 0
            missing = []
            for key in sorted(wanted.values()):
                _source, blob = read(storm, donor, key)
                if blob is None:
                    missing.append(key)
                    continue
                entries[key] = blob
                total += len(blob)
            staged = len(entries) - (1 if CHRRACES in entries else 0)
            print(f"   staging {staged} files, {total / 1048576:.1f} MB; "
                  f"absent from donor: {len(missing)}")
            for key in missing[:10]:
                print(f"      ! {key[len(HEAD):]}")

'''
text = text[:start] + new + text[end:]
path.write_text(text, encoding="utf-8")
print("rewritten")
