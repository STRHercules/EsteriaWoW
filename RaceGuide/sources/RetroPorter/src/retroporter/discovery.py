from __future__ import annotations

from typing import Any

from .config import Config
from .races import RaceSpec
from .wotlk import load_db2


ELEMENT_LINKS = {
    "ChrCustomizationGeosetID": "ChrCustomizationGeoset",
    "ChrCustomizationSkinnedModelID": "ChrCustomizationSkinnedModel",
    "ChrCustomizationMaterialID": "ChrCustomizationMaterial",
    "ChrCustomizationBoneSetID": "ChrCustomizationBoneSet",
    "ChrCustomizationCondModelID": "ChrCustomizationCondModel",
    "ChrCustomizationDisplayInfoID": "ChrCustomizationDisplayInfo",
    "ChrCustItemGeoModifyID": "ChrCustItemGeoModify",
    "ChrCustGeoComponentLinkID": "ChrCustGeoComponentLink",
}


def _id(row_id: int, row: dict[str, Any]) -> int:
    return int(row.get("ID", row_id))


def rows_by_id(table, ids: set[int]) -> list[dict[str, Any]]:
    return [
        {"_row_id": row_id, **row}
        for row_id, row in table
        if _id(row_id, row) in ids
    ]


def collect_file_data_ids(value: Any, key: str = "") -> set[int]:
    found: set[int] = set()
    if isinstance(value, dict):
        for child_key, child in value.items():
            found.update(collect_file_data_ids(child, str(child_key)))
    elif isinstance(value, (list, tuple)):
        for child in value:
            found.update(collect_file_data_ids(child, key))
    elif isinstance(value, int) and value > 0 and "filedataid" in key.lower():
        found.add(value)
    return found


def discover_race(config: Config, spec: RaceSpec) -> dict[str, Any]:
    races = load_db2(config, spec.slug, "ChrRaces")
    if spec.retail_race_ids:
        wanted_race_ids = set(spec.retail_race_ids)
        matches = [
            (row_id, row)
            for row_id, row in races
            if _id(row_id, row) in wanted_race_ids
        ]
    else:
        matches = [
            (row_id, row)
            for row_id, row in races
            if (
                spec.retail_client_file_string
                and row.get("ClientFileString") == spec.retail_client_file_string
            )
            or row.get("Name_lang") == spec.retail_name
        ]
    if not matches:
        raise RuntimeError("Expected at least one race row, found none")
    if spec.retail_race_ids and len(matches) != len(spec.retail_race_ids):
        raise RuntimeError(
            f"Expected {len(spec.retail_race_ids)} configured race rows, found {len(matches)}"
        )
    if not spec.retail_race_ids and len(matches) != 1:
        raise RuntimeError(f"Expected one race row, found {len(matches)}")

    race_ids = {_id(row_id, row) for row_id, row in matches}
    race_row_id, race_row = matches[0]
    race_id = _id(race_row_id, race_row)

    links = load_db2(config, spec.slug, "ChrRaceXChrModel")
    model_links = [
        {"_row_id": row_id, **row}
        for row_id, row in links
        if row.get("ChrRacesID") in race_ids or row.get("RaceID") in race_ids
    ]
    model_ids = {int(row["ChrModelID"]) for row in model_links}
    model_rows = rows_by_id(load_db2(config, spec.slug, "ChrModel"), model_ids)
    display_ids = {int(row["DisplayID"]) for row in model_rows if row.get("DisplayID")}

    options = load_db2(config, spec.slug, "ChrCustomizationOption")
    option_rows = [
        {"_row_id": row_id, **row}
        for row_id, row in options
        if row.get("ChrModelID") in model_ids
    ]
    option_ids = {_id(row["_row_id"], row) for row in option_rows}

    choices = load_db2(config, spec.slug, "ChrCustomizationChoice")
    choice_rows = [
        {"_row_id": row_id, **row}
        for row_id, row in choices
        if row.get("ChrCustomizationOptionID") in option_ids
    ]
    choice_ids = {_id(row["_row_id"], row) for row in choice_rows}

    req_ids = {int(row["ChrCustomizationReqID"]) for row in choice_rows if row.get("ChrCustomizationReqID")}
    req_rows = rows_by_id(load_db2(config, spec.slug, "ChrCustomizationReq"), req_ids)
    req_choice_table = load_db2(config, spec.slug, "ChrCustomizationReqChoice")
    req_choice_rows = [
        {"_row_id": row_id, **row}
        for row_id, row in req_choice_table
        if row.get("ChrCustomizationReqID") in req_ids
    ]
    vis_req_ids = {int(row["ChrCustomizationVisReqID"]) for row in choice_rows if row.get("ChrCustomizationVisReqID")}
    vis_req_rows = rows_by_id(load_db2(config, spec.slug, "ChrCustomizationVisReq"), vis_req_ids) if vis_req_ids else []

    elements = load_db2(config, spec.slug, "ChrCustomizationElement")
    element_rows = [
        {"_row_id": row_id, **row}
        for row_id, row in elements
        if row.get("ChrCustomizationChoiceID") in choice_ids
        or row.get("RelatedChrCustomizationChoiceID") in choice_ids
    ]

    linked: dict[str, list[dict[str, Any]]] = {}
    for column, table_name in ELEMENT_LINKS.items():
        ids = {int(row[column]) for row in element_rows if row.get(column)}
        if ids:
            linked[table_name] = rows_by_id(load_db2(config, spec.slug, table_name), ids)

    display_rows: list[dict[str, Any]] = []
    creature_models: list[dict[str, Any]] = []
    try:
        displays = load_db2(config, spec.slug, "CreatureDisplayInfo")
    except FileNotFoundError:
        displays = None
    if displays is not None:
        display_rows = rows_by_id(displays, display_ids)
        creature_model_ids = {
            int(row["ModelID"]) for row in display_rows if row.get("ModelID")
        }
        if creature_model_ids:
            creature_models = rows_by_id(
                load_db2(config, spec.slug, "CreatureModelData"), creature_model_ids
            )

    material_resource_ids = {
        int(row["MaterialResourcesID"])
        for row in linked.get("ChrCustomizationMaterial", [])
        if row.get("MaterialResourcesID")
    }
    texture_rows: list[dict[str, Any]] = []
    if material_resource_ids:
        texture_table = load_db2(config, spec.slug, "TextureFileData")
        texture_rows = [
            {"_row_id": row_id, **row}
            for row_id, row in texture_table
            if row.get("MaterialResourcesID") in material_resource_ids
        ]

    result = {
        "race_id": race_id,
        "race_ids": sorted(race_ids),
        "race": {"_row_id": race_row_id, **race_row},
        "races": [{"_row_id": row_id, **row} for row_id, row in matches],
        "model_links": model_links,
        "models": model_rows,
        "display_rows": display_rows,
        "creature_model_rows": creature_models,
        "options": option_rows,
        "choices": choice_rows,
        "requirements": req_rows,
        "requirement_choices": req_choice_rows,
        "visibility_requirements": vis_req_rows,
        "elements": element_rows,
        "linked": linked,
        "texture_files": texture_rows,
    }
    result["file_data_ids"] = sorted(collect_file_data_ids(result))

    from wotlkconv.listfile import Listfile

    listfile = Listfile.load(config.listfile)
    result["file_assets"] = [
        {"file_data_id": file_id, "path": listfile.path_for(file_id)}
        for file_id in result["file_data_ids"]
    ]
    return result
