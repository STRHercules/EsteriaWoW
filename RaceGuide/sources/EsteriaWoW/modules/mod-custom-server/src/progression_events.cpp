#include "progression_events.h"

#if __has_include("MP_loader.cpp")
void AddSC_mod_custom_server_attunement_plus();
#endif

namespace
{
    Progression::Handler g_handler = nullptr;
}

namespace Progression
{
    void SetHandler(Handler handler)
    {
        g_handler = handler;
    }

    void Publish(DungeonEvent const& event)
    {
        if (!g_handler)
            return;
        g_handler(event);
    }
}

void Addmod_custom_serverScripts()
{
#if __has_include("MP_loader.cpp")
    AddSC_mod_custom_server_attunement_plus();
#endif
}
