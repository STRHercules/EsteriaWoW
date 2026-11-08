"""A neighborhood map's plots from retail NeighborhoodPlot, as data/plots.tsv holds Founder's Point's.

    python neighborhood_plots.py <NeighborhoodPlot.csv> <NeighborhoodMapID> <out tsv>

NeighborhoodPlot.csv is a wago.tools export (https://wago.tools/db2/NeighborhoodPlot/csv). Same rules as wowdecomp
docs/housing/tools/phase3/make_plots.py: a HousePosition (Field_12_0_0_63534_004) more than 55 yd from its cornerstone
is unfinished retail data, so that house stands 32 yd out along the cornerstone's facing instead. Razorwind Shores
(map 2) has 53 such plots in 12.0.
"""
import csv
import math
import sys

FAR_HOUSE = 55


def main(src, neighborhood, out):
    rows = sorted((r for r in csv.DictReader(open(src, encoding="utf-8")) if r["NeighborhoodMapID"] == neighborhood),
                  key=lambda r: int(r["PlotIndex"]))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["plot", "house_x", "house_y", "house_z", "house_yaw", "corner_x", "corner_y", "corner_z", "corner_o",
                    "exit_x", "exit_y", "exit_z"])
        for r in rows:
            v = lambda name, n: [float(r[f"{name}_{i}"]) for i in range(n)]  # noqa: E731
            house, yaw = v("Field_12_0_0_63534_004", 3), v("Field_12_0_0_63534_005", 3)[2]
            corner, facing = v("CornerstonePosition", 3), v("CornerstoneRotation", 3)[2]
            if math.hypot(house[0] - corner[0], house[1] - corner[1]) > FAR_HOUSE:
                house = [corner[0] + 32 * math.cos(facing), corner[1] + 32 * math.sin(facing), corner[2]]
                yaw = facing + math.pi
            w.writerow([r["PlotIndex"], *[round(x, 3) for x in house], round(yaw, 4), *[round(x, 3) for x in corner],
                        round(facing, 4), *[round(x, 3) for x in v("TeleportPosition", 3)]])
    print(f"{len(rows)} plots -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
