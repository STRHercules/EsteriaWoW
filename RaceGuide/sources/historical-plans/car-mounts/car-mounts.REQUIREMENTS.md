# Unique car mounts requirements

## Goal

Extract the four supplied car MPQs, convert their chopper replacements into four additive WotLK mount definitions, build `PATCH-X.MPQ`, stage the matching server records, and restart the existing Docker realm without deleting persistent volumes.

## Source interpretation

`How To Install.txt` is source metadata only. Its one-patch and chopper-piggyback instructions are superseded by this request for four independent additions.

## Required outputs

- Complete extraction under `R:\Users\Zach\Downloads\WoW Cars 3.3.5 900 1 2026-07-17T00-39Z KALsNGcJL(1)\WoW Cars 3.3.5\Extracted\Patch-B`, `Patch-F`, `Patch-L`, and `Patch-S`.
- Real `R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\PATCH-X.MPQ`.
- Existing `3.3.5a - Dev\Data\patch-z.mpq` Battlemon folder preserved unchanged.
- A module SQL correction for the existing car definitions.

## Data contract

- Preserve existing unique spell IDs `200101..200104`, item IDs `900137..900140`, creature IDs `3460604..3460607`, display IDs `94229..94232`, model IDs `4892..4895`, and item display IDs `134239..134242`.
- Add collision-free vehicle IDs `900301..900304` and vehicle-seat IDs `900401..900404`.
- Each car gets unique model/skin/texture/icon paths; shared WAV/effect assets may be stored once when byte-identical.
- Client DBC additions use WXL continuation files under `DBFilesClient/` and a root `wxl-dbc.manifest`.
- Server SQL updates `creature_template.VehicleId`, corrects `.m2` model paths, and inserts matching `vehicle_dbc`/`vehicleseat_dbc` rows without editing the already-applied migration.

## Deployment boundary

Build the database-import/worldserver images as required by the repository workflow, run the importer, recreate `ac-worldserver`, and verify readiness, health, restart count, migration state, and matching rows. Do not run `docker compose down -v`.

Static archive/database verification does not constitute live WoW icon, learn, riding, or relog smoke testing.
