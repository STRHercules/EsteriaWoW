from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = Path(r"G:\3.3.5a - Dev\Data")
ARCHIVES = (DATA / "patch-Z.MPQ", DATA / "enUS" / "patch-enUS-Z.MPQ")
ENTRY = r"Interface\GlueXML\AccountLogin.lua"

sys.path.insert(0, str(ROOT / "tools"))
from cars_mount_pack import DLL_DEFAULT, Storm


def read_entry(storm: Storm, archive_path: Path) -> bytes:
    archive = storm.open_archive(archive_path)
    try:
        return storm.read(archive, ENTRY)
    finally:
        storm.dll.SFileCloseArchive(archive)


def assert_persistence_contract(source: str) -> None:
    assert 'pcall(GetCVar, "accountName")' in source
    assert 'pcall(SetCVar, "accountName", saved)' in source
    assert 'return fields[1] or "", fields[2] or "", fields[3] or "0", fields[4] or ""' in source
    assert 'local accountName, password, autoLogin, sceneID = LoginScenePicker_GetSavedData()' in source
    apply_start = source.index('apply:SetScript("OnClick"')
    apply_end = source.index("local cancel =", apply_start)
    apply_handler = source[apply_start:apply_end]
    assert "LOGIN_SCENE_PICKER_COMMITTED = LOGIN_SCENE_PICKER_PENDING;" in apply_handler
    assert "LoginScenePicker_SaveSession();" in apply_handler
    assert 'LoginScenePicker_Apply(LOGIN_SCENE_PICKER_COMMITTED)' in source
    login_start = source.index("function AccountLogin_Login()")
    login_end = source.index("\nfunction AccountLogin_CheckAutoLogin()", login_start)
    login_handler = source[login_start:login_end]
    assert login_handler.index("SetSavedAccountName(savedData)") < login_handler.index("DefaultServerLogin")
    assert login_handler.index('pcall(SetCVar, "accountName", savedData)') < login_handler.index("DefaultServerLogin")
    on_hide_start = source.index("local LoginScenePickerOriginalOnHide = AccountLogin_OnHide;")
    on_hide_end = source.index("local LoginScenePickerOriginalOnKeyDown", on_hide_start)
    on_hide_handler = source[on_hide_start:on_hide_end]
    assert "LoginScenePickerOriginalOnHide(self);" in on_hide_handler
    assert "LoginScenePicker_SaveSession();" not in on_hide_handler, (
        "OnHide must not overwrite an explicit login save with transient/cleared UI state"
    )
    assert "local LoginScenePickerOriginalLogin = AccountLogin_Login;" not in source


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    payloads = [read_entry(storm, path) for path in ARCHIVES]
    assert payloads[0] == payloads[1], "root and locale login scripts differ"
    assert_persistence_contract(payloads[0].decode("utf-8"))
    print("login-persistence contract: PASS")


if __name__ == "__main__":
    main()
