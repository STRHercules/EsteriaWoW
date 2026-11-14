/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license: https://github.com/azerothcore/azerothcore-wotlk/blob/master/LICENSE-AGPL3
 * Copyright (C) 2021+ WarheadCore <https://github.com/WarheadCore>
 */

// From SC
void AddSC_Transmog();
void AddSC_transmog_commandscript();
void AddSC_transmog_client();
void AddSC_esteria_cosmetics();

// Add all
void Addmod_transmogScripts()
{
    AddSC_Transmog();
    AddSC_transmog_commandscript();
    AddSC_transmog_client();
    AddSC_esteria_cosmetics();
}
