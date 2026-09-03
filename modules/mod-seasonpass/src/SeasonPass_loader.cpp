#include "SeasonPass.h"
#include "progression_events.h"

void AddSC_SeasonPass();
void AddSC_SeasonPassSeason();

// Name wird von AzerothCore aus dem Modulordner generiert: mod-seasonpass
void Addmod_seasonpassScripts()
{
    Progression::SetHandler(&SeasonPass::HandleDungeonEvent);
    AddSC_SeasonPass();
    AddSC_SeasonPassSeason();
}
