from pathlib import Path


SOURCE = Path(
    "modules/mod-custom-server/data/sql/db-world/updates/"
    "u_custom_server_2026_09_10_01_race_scope_corrective.sql"
)


def test_race_scope_uses_class_cross_join_alias():
    text = SOURCE.read_text(encoding="utf-8")
    assert "expected.ClassID" not in text
    assert text.count("classes.ClassID") >= 5


if __name__ == "__main__":
    test_race_scope_uses_class_cross_join_alias()
    print("race scope SQL alias contract: PASS")
