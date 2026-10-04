import struct
import sys
from pathlib import Path


CLIENT_PATCH_ROOT = Path("modules/mod-classless-wildcard/client-patch")
sys.path.insert(0, str(CLIENT_PATCH_ROOT))
from lib import dbc  # noqa: E402


SOURCE = Path("modules/mod-custom-server/src/mod_attunement_plus.cpp")
CHASSIS_SQL = Path(
    "modules/mod-custom-server/data/sql/db-world/updates/"
    "u_custom_server_2026_09_17_classless_race_chassis.sql"
)
RESTORE_SQL = Path(
    "modules/mod-custom-server/data/sql/db-world/updates/"
    "u_custom_server_2026_09_17_classless_restore_actions.sql"
)
BROKEN_ALIGNMENT_SQL = Path(
    "modules/mod-custom-server/data/sql/db-world/updates/"
    "u_custom_server_2026_09_17_broken_race14_alignment.sql"
)


def test_classless_armor_filter_contract():
    text = SOURCE.read_text(encoding="utf-8")
    assert '#include "ClasslessMgr.h"' in text
    assert "sClasslessMgr->cfg.enabled" in text
    assert "sClasslessMgr->FindState(player)" in text


def test_classless_race_overlay_preserves_custom_actions():
    chassis = CHASSIS_SQL.read_text(encoding="utf-8")
    restore = RESTORE_SQL.read_text(encoding="utf-8")
    assert "DELETE FROM `playercreateinfo_action`" not in chassis
    assert "DELETE FROM `playercreateinfo_action`" in restore
    assert "WHERE `race` BETWEEN 15 AND 28" not in restore
    assert "AND `button` = 9" in restore
    assert "(15, 2, 9, 59752, 0)" not in restore
    assert "(16, 2, 3, 33697, 0)" in restore
    assert "(17, 2, 3, 28730, 0)" in restore
    assert "(21, 2, 3, 59542, 0)" in restore
    assert "(23, 2, 4, 2481, 0)" in restore
    assert "(28, 2, 3, 33697, 0)" in restore


def test_classless_client_keeps_esteria_broken_race14_creatable():
    raw = b"WDBC" + struct.pack("<4I", 1, 2, 2, 1) + bytes((14, 1)) + b"\0"
    patched, _ = dbc.single_class_combos(raw, 2)
    rows = [tuple(patched[offset:offset + 2]) for offset in range(20, len(patched) - 1, 2)]
    assert (14, 2) in rows


def test_server_alignment_uses_esteria_broken_model_pair():
    sql = BROKEN_ALIGNMENT_SQL.read_text(encoding="utf-8")
    assert "WHERE `ID` = 14" in sql
    assert "`MaleDisplayId` = 60002" in sql
    assert "`FemaleDisplayId` = 60003" in sql
    assert "`ClientPrefix` = 'Bk'" in sql


if __name__ == "__main__":
    test_classless_armor_filter_contract()
    test_classless_race_overlay_preserves_custom_actions()
    test_classless_client_keeps_esteria_broken_race14_creatable()
    test_server_alignment_uses_esteria_broken_model_pair()
    print("classless compatibility contract: PASS")
