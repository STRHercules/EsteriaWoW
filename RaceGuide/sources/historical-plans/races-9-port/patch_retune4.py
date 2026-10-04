import pathlib

path = pathlib.Path(".agents/plans/races-9-port/retune_vulpera_helm_calibration.py")
text = path.read_text(encoding="utf-8")

text = text.replace('HEAD = "Item\\\\ObjectComponents\\\\Head\\\\"',
                    'HEAD = "Item\\\\ObjectComponents\\\\Head\\\\"\n'
                    'ITEM_DISPLAY_INFO = "DBFilesClient\\\\ItemDisplayInfo.dbc"')
text = text.replace('''BASE_STEM = "Helm_Leather_B_06"''',
                    '''BASE_STEM = "Helm_Leather_B_06"
# every calibration item gets the same helmet geoset-vis pair, so only the fit differs
VIS_ID = 285
DISPLAY_IDS = (64503, 64429, 65195, 65160, 64427, 61210, 62159)''')

old = '''    storm = Storm(DLL_DEFAULT)
    handles = open_archives(storm, ORDER)
    entries: dict[str, bytes] = {}
    try:'''
new = '''    storm = Storm(DLL_DEFAULT)
    handles = open_archives(storm, ORDER)
    entries: dict[str, bytes] = {}
    try:
        _source, display_payload = read(storm, handles, ITEM_DISPLAY_INFO)
        display = Wdbc(display_payload)
        for row in display.rows:
            if row[0] in DISPLAY_IDS:
                row[13] = VIS_ID
                row[14] = VIS_ID
        entries[ITEM_DISPLAY_INFO] = (
            struct.pack("<4s4I", b"WDBC", len(display.rows), display.fields,
                        display.record_size, len(display.strings))
            + b"".join(struct.pack(f"<{display.fields}I",
                                   *(value & 0xFFFFFFFF for value in row))
                       for row in display.rows)
            + display.strings)
        print(f"{ITEM_DISPLAY_INFO}: {len(DISPLAY_IDS)} rows normalised to vis {VIS_ID}")'''
assert old in text
text = text.replace(old, new)
text = text.replace('from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402',
                    'from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402')
path.write_text(text, encoding="utf-8")
print("patched")
