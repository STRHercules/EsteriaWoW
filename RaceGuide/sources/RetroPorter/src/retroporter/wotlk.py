from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from .config import Config


DB2_TABLES = (
    "ChrRaces",
    "ChrModel",
    "ChrRaceXChrModel",
    "ChrCustomizationOption",
    "ChrCustomizationChoice",
    "ChrCustomizationReq",
    "ChrCustomizationReqChoice",
    "ChrCustomizationVisReq",
    "ChrCustomizationElement",
    "ChrCustomizationGeoset",
    "ChrCustomizationMaterial",
    "ChrCustomizationSkinnedModel",
    "ChrCustomizationDisplayInfo",
    "ChrCustomizationBoneSet",
    "ChrCustomizationCondModel",
    "ChrCustItemGeoModify",
    "ChrCustGeoComponentLink",
    "ChrCustomizationConversion",
    "ChrModelMaterial",
    "ChrModelTextureLayer",
    "CharComponentTextureLayouts",
    "CharComponentTextureSections",
    "ComponentTextureFileData",
    "ModelFileData",
    "TextureFileData",
    "CreatureDisplayInfo",
    "CreatureModelData",
)


def converter_command() -> list[str]:
    return [sys.executable, "-m", "wotlkconv"]


def run_converter(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*converter_command(), *args],
        check=check,
        text=True,
    )


def extraction_dir(config: Config, race_slug: str) -> Path:
    return config.work_root / race_slug / "retail-db2"


def output_dir(config: Config, race_slug: str) -> Path:
    return config.work_root / race_slug / "output"


def extract_db2(
    config: Config,
    race_slug: str,
    *,
    source_root: Path | None = None,
    source_product: str | None = None,
) -> Path:
    out = extraction_dir(config, race_slug)
    args = [
        "casc",
        "extract",
        "--casc",
        str(source_root or config.retail_root),
        "--casc-product",
        source_product or config.product,
        "--casc-keys",
        str(config.keys),
        "--listfile",
        str(config.listfile),
    ]
    for table in DB2_TABLES:
        args.extend(["--include", f"dbfilesclient/{table.lower()}.db2"])
    args.extend(["-o", str(out), "--overwrite"])
    run_converter(args)
    return out


def load_db2(config: Config, race_slug: str, table_name: str):
    try:
        from wotlkconv.db.db2 import parse_db2
        from wotlkconv.db.dbd import DbdIndex
    except ImportError as exc:  # pragma: no cover - environment guard
        raise RuntimeError(
            "wotlkconv is not installed. Install Bar3b0n3s/Converter first."
        ) from exc

    path = extraction_dir(config, race_slug) / "dbfilesclient" / f"{table_name.lower()}.db2"
    definitions = DbdIndex(config.dbd_dir)
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run extract-db2 first.")
    return parse_db2(path.read_bytes(), str(path), definitions, table_name)
