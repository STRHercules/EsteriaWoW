from pathlib import Path
d = Path(r".agents\plans\freeborn-client\final")
lua = (d / "CharacterCreate.lua").read_text(encoding="utf-8").splitlines()
xml = (d / "CharacterCreate.xml").read_text(encoding="utf-8")
print("deployed lua lines:", len(lua))
for n, line in enumerate(lua, 1):
    if any(k in line for k in ("if not CharacterFreeborn_Init", ">>> freeborn-third-team", "<<< freeborn-third-team",
                               "string.sub(name, 1, firstLength)", "CharacterFreeborn_IsSelected", "CreateCharacter(CharacterFreeborn_CreateName")):
        print(f"  L{n}: {line.strip()[:96]}")
print("--- deployed button element ---")
i = xml.index('<CheckButton name="CharacterCreateFreebornButton"')
print(xml[i-32:i+430])
