# AzerothCore includes this file when configuring modules.
# Check both declarations and call sites: removing `override` alone makes the
# module compile without ever running its name validation.
if("${MODULE_MOD-TWO-NAMES}" STREQUAL "disabled")
    return()
endif()

set(_two_names_hook_files
    "src/server/game/Scripting/ScriptDefines/MiscScript.h"
    "src/server/game/Scripting/ScriptMgr.h"
    "src/server/game/Scripting/ScriptDefines/MiscScript.cpp"
    "src/server/game/Globals/ObjectMgr.cpp"
)

foreach(_two_names_file IN LISTS _two_names_hook_files)
    set(_two_names_path "${CMAKE_SOURCE_DIR}/${_two_names_file}")
    if(NOT EXISTS "${_two_names_path}")
        message(FATAL_ERROR
            "mod-two-names: cannot find ${_two_names_file}. "
            "Install this module inside an AzerothCore source checkout.")
    endif()

    file(READ "${_two_names_path}" _two_names_source)
    foreach(_two_names_hook CanNormalizePlayerName OnCheckPlayerName)
        if(NOT _two_names_source MATCHES "${_two_names_hook}[ \t\r\n]*\\(")
            message(FATAL_ERROR
                "mod-two-names requires the name hooks missing from ${_two_names_file}.\n"
                "From your AzerothCore source directory run:\n"
                "  git apply --ignore-space-change --check modules/mod-two-names/patches/azerothcore-name-hooks.patch\n"
                "  git apply --ignore-space-change modules/mod-two-names/patches/azerothcore-name-hooks.patch\n"
                "Then re-run CMake and rebuild game, modules and worldserver.\n"
                "Do not remove override from the module: the hooks must be called by the core.\n"
                "If the patch conflicts, see patches/README.md; do not force it.")
        endif()
    endforeach()
endforeach()

unset(_two_names_hook_files)
unset(_two_names_file)
unset(_two_names_path)
unset(_two_names_source)
unset(_two_names_hook)
