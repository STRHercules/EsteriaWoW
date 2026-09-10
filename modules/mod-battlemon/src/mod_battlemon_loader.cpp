/*
 * mod-battlemon — AzerothCore loader.
 *
 * Directory name "mod-battlemon" maps to Addmod_battlemonScripts().
 */

void AddSC_battlemon();

void AddSC_battlemon_sidecar();

void Addmod_battlemonScripts()
{
    AddSC_battlemon();
    AddSC_battlemon_sidecar();
}
