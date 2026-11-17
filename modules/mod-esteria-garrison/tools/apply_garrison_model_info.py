from pathlib import Path

IDS = [
    68101, 68102, 68103, 68104, 68105, 68106, 68107, 68108, 68109, 68110, 68111, 68112,
    68120, 68121, 68122, 68123, 68124, 68125, 68126, 68127, 68128, 68129, 68130, 68131,
    68132, 68133, 68134, 68135, 68136, 68137, 68138, 68139, 68140, 68141, 68142, 68143,
    68144, 68145, 68146, 68147, 68148, 68149, 68150, 68151, 68152, 68153, 68154, 68155,
    68156, 68157, 68158, 68159, 68160, 68161, 68162, 68163, 68164, 68165, 68166, 68167,
    68301, 68302, 68303, 68304, 68305, 68306,
]

sql_path = Path(__file__).resolve().parents[1] / "sql" / "world" / "garrison_creature_model_info.sql"
lines = [
    "-- Auto: bounding stubs for garrison CreatureDisplayInfo 681xx/683xx",
    "DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN 68100 AND 68400;",
]
for i in IDS:
    lines.append(
        "INSERT INTO `creature_model_info` "
        "(`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`, `VerifiedBuild`) "
        f"VALUES ({i}, 0.5, 1.5, 2, 0, 0);"
    )
sql_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", sql_path, "rows", len(IDS))
