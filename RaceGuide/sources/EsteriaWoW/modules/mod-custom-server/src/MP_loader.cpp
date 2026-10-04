/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license: https://github.com/azerothcore/azerothcore-wotlk/blob/master/LICENSE-AGPL3
 */

void AddSC_darkfallen_racials();
void AddSC_mod_attunement_plus();
void AddSC_instance_mode();

void AddSC_mod_custom_server_attunement_plus()
{
    AddSC_instance_mode();
    AddSC_mod_attunement_plus();
    AddSC_darkfallen_racials();
}
