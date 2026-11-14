#!/bin/sh
# Phase 1 server install on Live (ac-worldserver / acore_world). Run from Git Bash on the host.
# Backs up first; adds only files and rows that do not exist yet; restarts ac-worldserver at the end.
set -e
export MSYS_NO_PATHCONV=1
W=G:/CoAMapsPort
S=$W/stage/server
OUT=$W/extract-out
B=G:/housing-build/live-backup-coamaps-$(date +%Y%m%d-%H%M%S)
DATA=/azerothcore/env/dist/data
FLY=R:/Users/Zach/Documents/GitHub/EsteriaWoW/modules/mod-fly-anywhere/data/patch/server/AreaTable.dbc
mkdir -p $B
docker exec ac-database bash -o pipefail -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --single-transaction --quick --routines --triggers --set-gtid-purged=OFF acore_world | gzip -1' > $B/acore_world.sql.gz
for t in Map AreaTrigger WorldSafeLocs LiquidType; do docker cp ac-worldserver:$DATA/dbc/$t.dbc $B/$t.dbc; done
cp $FLY $B/AreaTable.dbc
echo "backup: $B"

for t in Map AreaTrigger WorldSafeLocs LiquidType; do docker cp $S/dbc/$t.dbc ac-worldserver:$DATA/dbc/$t.dbc; done
cp $S/dbc/AreaTable.dbc $FLY

# terrain data: only files the volume lacks (vmap .vmo files are per model and shared with Esteria's own maps)
for d in maps vmaps mmaps; do
  docker exec ac-worldserver ls $DATA/$d | sort > $W/have-$d.txt
  ls $OUT/$d | sort | comm -23 - $W/have-$d.txt > $W/new-$d.txt
  tar -C $OUT/$d -cf - -T $W/new-$d.txt | docker exec -i -u root ac-worldserver tar -C $DATA/$d -xf -
  echo "$d: copied $(wc -l < $W/new-$d.txt) new files"
done

docker exec -i ac-database mysql -uroot -ppassword --default-character-set=utf8mb4 acore_world < $S/sql/coa_maps_world.sql 2>&1 | grep -v Warning || true
echo "sql applied; restarting ac-worldserver"
docker restart ac-worldserver
