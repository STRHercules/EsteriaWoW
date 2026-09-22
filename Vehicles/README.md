# Car mount seat locations

`Vehicle.dbc` and `VehicleSeat.dbc` are complete WotLK WDBC files: the verified
client/server baseline plus the four car rows from the current `PATCH-X.MPQ`.

## Second-seat lookup

| Car | `Vehicle.dbc` row | Change | `VehicleSeat.dbc` row | Current offsets |
|---|---:|---|---:|---|
| Bentley | `900301` | `SeatID_2 = 900401` | `900401` | `X=0.0, Y=0.0, Z=0.0` |
| Ferrari | `900302` | `SeatID_2 = 900402` | `900402` | `X=0.0, Y=0.0, Z=0.0` |
| Skyline | `900303` | `SeatID_2 = 900403` | `900403` | `X=0.0, Y=0.0, Z=0.0` |
| Lamborghini | `900304` | `SeatID_2 = 900404` | `900404` | `X=0.0, Y=0.0, Z=0.0` |

For each matching `VehicleSeat.dbc` row, edit only these three fields:

```text
AttachmentOffsetX
AttachmentOffsetY
AttachmentOffsetZ
```

They are fields 3, 4, and 5 when counted from zero, or columns 4, 5, and 6
when the ID is column 1. They are also byte offsets `0x0C`, `0x10`, and
`0x14` inside the 232-byte row. The values are local vehicle coordinates:
X forward/back, Y left/right, and Z up/down.

Leave `ID`, `AttachmentID` (`14`), animation fields, and `SeatID_2` unchanged.
Use small adjustments such as `0.1` to `0.25` and test in-game.

After editing, keep the client WXL continuation and server SQL synchronized.
The server mirrors are in
`modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_09_00_cars_unique.sql`.

Source baseline: `BinaryWork/patch-enUS-3-inspect-20260906/DBFilesClient/`.
Car rows: `3.3.5a - Dev/Data/PATCH-X.MPQ`, entries
`DBFilesClient/Vehicle.dbc1-cars` and `DBFilesClient/VehicleSeat.dbc1-cars`.
