# CoA import pipeline

Batch scripts used to regenerate, package, stage and deploy the CoA port. Run from anywhere; they find the repo from
their own location. Work files, logs and database backups go to `G:/coa-build/codex-batch7-20261103/` (`out` in each
script); the CoA sources are `G:/CoAClient/Client` and `azerothcore-wotlk-coa`.

1. `run_pipeline.py` - catalog, SQL slices, creature slice, `G:/coa-build/batch7.MPQ`.
2. `append_affect_table.py` then `verify_mpq.py` - always both; the pipeline drops `EsteriaSpellAffect.dbc`.
3. `../coa_overwrite_audit.py --target-client "G:/3.3.5a - Dev" --world-spell-ids G:/coa-build/codex-batch7-20261103/world-spell-ids-before-coa.txt`
   must print `0 collision(s)`.
4. `verify_build.py` - copies `src/` and the module into `coa-lead` and builds worldserver.
5. `package_runtime.py esteria-coa:<new tag>` - wraps the built worldserver in a new image.
6. Isolated test: `backup_db.py`, `stage_databases.py`, `prepare_stage.py`, `apply_sql.py coa_b7_world`,
   `start_stage.py esteria-coa:<new tag>`, `check_stage.py` (port 8095, databases `coa_b7_*`).
   Remove the stage container (`docker rm -f coa-codex-stage`) before starting another.
7. Deploy: back up, `apply_sql.py acore_world`, copy the MPQ over the installed CoA patch with WoW closed, point
   `docker-compose.twoforms.yml` at the new tag, recreate only `ac-worldserver`.
