from __future__ import annotations

from .base import StageContext, StageResult


MANUAL_STAGE_GUIDANCE = {
    "discover": "Implement/enable an online CDN or local CASC Retail DB2 discovery adapter and emit normalized discovery JSON.",
    "extract": "Implement/enable targeted FileDataID extraction and populate sources/retail/races/<race>/ without copying a full client.",
    "inventory": "Generate a deterministic dependency inventory for the cached race source assets.",
    "convert-model": "Configure M2Mod/FixTXID/MultiConverter adapter steps for the installed tool versions.",
    "convert-textures": "Normalize/copy required BLP texture dependencies into converted output.",
    "build-customization": "Flatten Retail customization choices into the WotLK normalization model.",
    "generate-dbc": "Generate verified WotLK DBC record inputs from normalized race data.",
    "generate-acore-sql": "Render AzerothCore playercreateinfo* SQL from verified mappings.",
    "generate-glue": "Generate patchable GlueXML metadata/fragments for the selected character creator.",
    "validate": "Add deep asset/DBC/SQL/Glue validation before enabling packaging.",
    "package": "Enable derived-file packaging only after validation is implemented.",
}


def run_scaffold_stage(name: str, context: StageContext) -> StageResult:
    guidance = MANUAL_STAGE_GUIDANCE[name]
    return StageResult(name, "blocked", guidance)
