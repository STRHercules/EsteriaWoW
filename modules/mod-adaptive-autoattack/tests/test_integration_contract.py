from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "data/sql/db-world/2026_09_14_00_adaptive_autoattack.sql"
ADAPTIVE = ROOT / "src/AdaptiveAutoAttack.cpp"
HOOKS = ROOT / "src/AttackHooks.cpp"
LOADER = ROOT / "src/loader.cpp"


def test_enable_setting_is_cached_and_sql_is_guarded():
    adaptive = ADAPTIVE.read_text(encoding="utf-8")
    hooks = HOOKS.read_text(encoding="utf-8")
    loader = LOADER.read_text(encoding="utf-8")
    sql = SQL.read_text(encoding="utf-8")

    assert "bool AdaptiveAutoAttackEnabled()" in adaptive
    assert adaptive.count('sConfigMgr->GetOption<bool>("AdaptiveAutoAttack.Enable", true)') == 1
    assert "AdaptiveAutoAttackEnabled()" in hooks
    assert "AdaptiveAutoAttackEnabled()" in loader
    assert "START TRANSACTION" in sql
    assert "DECLARE EXIT HANDLER FOR SQLEXCEPTION" in sql
    assert "SIGNAL SQLSTATE" in sql
    assert "FROM `updates`" in sql


if __name__ == "__main__":
    test_enable_setting_is_cached_and_sql_is_guarded()
    print("adaptive autoattack integration contract: PASS")
