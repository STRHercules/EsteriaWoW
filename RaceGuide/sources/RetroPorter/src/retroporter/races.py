from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RaceSpec:
    slug: str
    retail_client_file_string: str
    retail_name: str
    asset_roots: tuple[str, ...]
    core_model_file_ids: tuple[int, ...]
    required_file_ids: tuple[int, ...] = ()
    retail_race_ids: tuple[int, ...] = ()
    ready_for_assets: bool = True


RACES: dict[str, RaceSpec] = {
    "vulpera": RaceSpec(
        slug="vulpera",
        retail_client_file_string="Vulpera",
        retail_name="Vulpera",
        asset_roots=("character\\vulpera\\",),
        core_model_file_ids=(1890761, 1890759),
        retail_race_ids=(35,),
    ),
    "maghar": RaceSpec(
        slug="maghar",
        retail_client_file_string="MagharOrc",
        retail_name="Mag'har Orc",
        asset_roots=("character\\orc\\",),
        core_model_file_ids=(917116, 949470, 1968587),
    ),
    "highmountain": RaceSpec(
        slug="highmountain",
        retail_client_file_string="HighmountainTauren",
        retail_name="Highmountain Tauren",
        asset_roots=("character\\highmountaintauren\\",),
        core_model_file_ids=(1630218, 1630402),
    ),
    "mechagnome": RaceSpec(
        slug="mechagnome",
        retail_client_file_string="Mechagnome",
        retail_name="Mechagnome",
        asset_roots=(
            "character\\mechagnome\\",
            "character\\gnome\\",
            "item\\objectcomponents\\collections\\collections_mechagnome_",
        ),
        core_model_file_ids=(2564806, 2622502, 2628212, 2628213),
        required_file_ids=(2628215, 2628216),
    ),
    "earthen": RaceSpec(
        slug="earthen",
        retail_client_file_string="EarthenDwarf",
        retail_name="Earthen",
        asset_roots=(
            "character\\earthendwarf\\",
            "item\\objectcomponents\\collections\\earthenextras_",
        ),
        core_model_file_ids=(5548259, 5548261, 5792407, 5792408),
        required_file_ids=(5688294,),
        retail_race_ids=(84, 85),
    ),
    "haranir": RaceSpec(
        slug="haranir",
        retail_client_file_string="Harronir",
        retail_name="Haranir",
        asset_roots=(
            "character\\harronir\\",
            "character\\haranir\\",
            "models\\item\\unk_exp11_6255031_hr_f\\",
            "models\\item\\unk_exp11_6255032_hr_m\\",
        ),
        core_model_file_ids=(5422147, 5422149, 6255031, 6255032),
        retail_race_ids=(86, 91),
    ),
    "skyborne": RaceSpec(
        slug="skyborne",
        retail_client_file_string="Skyborne",
        retail_name="Skyborne",
        asset_roots=(
            "character\\bloodelf\\",
            "models\\creature\\unk_exp00_7478487\\",
            "models\\creature\\unk_exp00_7478494\\",
            "models\\unknown\\unk_exp00_7845092\\",
            "models\\unknown\\unk_exp00_7845093\\",
            "item\\objectcomponents\\collections\\demonhuntergeosets_be_",
        ),
        core_model_file_ids=(7478487, 7478494, 7845092, 7845093, 2763972, 2763973),
        retail_race_ids=(95, 96),
        ready_for_assets=True,
    ),
}
