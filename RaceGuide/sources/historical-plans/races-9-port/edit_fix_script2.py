import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")

old = text[text.index("        if not args.skip_stage:"):text.index("        if args.dry_run:")]
new = '''        if not args.skip_stage:
            payload = None
            source = None
            for name in OUR_ORDER:
                path = CLIENT / name
                if not path.is_file():
                    continue
                handle = H()
                if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
                    continue
                try:
                    payload = storm.read(handle, ITEM_DISPLAY_INFO)
                    source = name
                except Exception:
                    continue
                finally:
                    storm.dll.SFileCloseArchive(handle)
                if payload:
                    break
            display = Wdbc(payload)
            stems = set()
            for row in display.rows:
                for field in (1, 2):
                    stem = display.text(row[field])
                    if stem:
                        stems.add(stem[:-4] if stem.lower().endswith(".mdx") else stem)
            print(f"stems in {source} {ITEM_DISPLAY_INFO}: {len(stems)}")

            wanted: dict[str, str] = {}
            for stem in sorted(stems):
                for code in STAGE_CODES:
                    for sex in ("M", "F"):
                        for suffix in (f".m2", "00.skin"):
                            key = f"{HEAD}{stem}_{code}{sex}{suffix}"
                            wanted.setdefault(key.lower(), key)
            total = 0
            missing = []
            for key in sorted(wanted.values()):
                source_name, blob = read(storm, donor, key)
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
text = text.replace(old, new)

text = text.replace(
    'CHRRACES = "DBFilesClient\\\\ChrRaces.dbc"',
    'CHRRACES = "DBFilesClient\\\\ChrRaces.dbc"\nITEM_DISPLAY_INFO = "DBFilesClient\\\\ItemDisplayInfo.dbc"')
text = text.replace(
    'DERIVED = re.compile(r"_(Hu)([MF])(\\d\\d\\.skin|\\.m2|\\.mdx)$", re.IGNORECASE)\n', "")
path.write_text(text, encoding="utf-8")
print("rewritten")
