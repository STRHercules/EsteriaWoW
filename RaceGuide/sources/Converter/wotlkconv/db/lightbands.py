"""LightIntBand and LightFloatBand, rebuilt from LightData.

3.3.5a keeps a sky's day cycle in two tables addressed by arithmetic on the
LightParams id: eighteen colour bands at ``id * 18 - 17 + n`` and six float
bands at ``id * 6 - 5 + n``, each up to sixteen (time, value) keys.  Legion
folded both into LightData -- one row per param per time of day, one column
per band -- and the old tables are gone, so a converted LightParams names
skies 3.3.5a cannot find.

The columns were matched to the bands against a clean 3.3.5a client, over the
615 params whose key times are unchanged since Wrath: each colour band has
exactly one column whose values agree, the fog distance, fog multiplier and
cloud density float bands likewise.  The other three float bands have no
column any more; 3.3.5a's own tables hold one value in nearly every key (1.0,
0.95 and 1.0), which is written instead.
"""

from __future__ import annotations

from collections import defaultdict

from .dbc import DbcBuilder

#: LightIntBand band n <- LightData column.
INT_BANDS = (
    "DirectColor", "AmbientColor", "SkyTopColor", "SkyMiddleColor",
    "SkyBand1Color", "SkyBand2Color", "SkySmogColor", "SkyFogColor",
    "ShadowOpacity", "SunColor", "CloudSunColor", "CloudLayer1AmbientColor",
    "CloudEmissiveColor", "CloudLayer2AmbientColor", "OceanCloseColor",
    "OceanFarColor", "RiverCloseColor", "RiverFarColor",
)
#: LightFloatBand band n <- LightData column, or the constant 3.3.5a uses.
FLOAT_BANDS = ("FogEnd", "FogScaler", 1.0, "CloudDensity", 0.95, 1.0)
MAX_KEYS = 16
#: ID, Num, Time[16], Data[16]
FIELD_COUNT = 2 + 2 * MAX_KEYS


def build_light_bands(light_data_rows, param_ids) -> tuple[bytes, bytes, dict]:
    """``(LightIntBand.dbc, LightFloatBand.dbc, counts)`` for every param."""
    by_param: dict[int, list[dict]] = defaultdict(list)
    for row in light_data_rows:
        by_param[int(row.get("LightParamID") or 0)].append(row)
    ints = DbcBuilder(FIELD_COUNT)
    floats = DbcBuilder(FIELD_COUNT)
    truncated = 0
    params = sorted(set(param_ids) | {p for p in by_param if p})
    for param in params:
        rows = sorted(by_param.get(param, ()), key=lambda r: int(r.get("Time") or 0))
        if len(rows) > MAX_KEYS:
            truncated += 1
            rows = rows[:MAX_KEYS]
        times = [int(r.get("Time") or 0) for r in rows]
        for band, column in enumerate(INT_BANDS):
            values = {0: ("uint", param * len(INT_BANDS) - (len(INT_BANDS) - 1) + band),
                      1: ("uint", len(rows))}
            for k, row in enumerate(rows):
                values[2 + k] = ("uint", times[k])
                # 3.3.5a stores 0x00RRGGBB; retail may set the top byte.
                values[2 + MAX_KEYS + k] = ("uint", int(row.get(column) or 0) & 0xFFFFFF)
            ints.add(values)
        for band, source in enumerate(FLOAT_BANDS):
            values = {0: ("uint", param * len(FLOAT_BANDS) - (len(FLOAT_BANDS) - 1) + band),
                      1: ("uint", len(rows))}
            for k, row in enumerate(rows):
                values[2 + k] = ("uint", times[k])
                value = source if isinstance(source, float) else float(row.get(source) or 0.0)
                values[2 + MAX_KEYS + k] = ("float", value)
            floats.add(values)
    counts = {"params": len(params), "keys_truncated": truncated,
              "int_rows": len(ints.records), "float_rows": len(floats.records)}
    return ints.serialize(), floats.serialize(), counts
