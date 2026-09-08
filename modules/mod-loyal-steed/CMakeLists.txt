# Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license

# Reuse the installed mod-improved-bank module; the repository copy is identical
# and would register duplicate scripts when both modules are compiled.

# mod-loyal-steed
add_definitions(-DHAVE_MOD_IMPROVED_BANK)
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/MountEvolved.cpp")
AC_ADD_SCRIPT_LOADER("mod_mount_evolved" "${CMAKE_CURRENT_LIST_DIR}/src/MP_loader.cpp")
