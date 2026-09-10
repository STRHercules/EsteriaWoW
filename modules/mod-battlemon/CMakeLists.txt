# mod-battlemon — AzerothCore module (WotLK 3.3.5 + playerbots).
# Sources are auto-collected from src/ by the core module system.
# src: BattlemonMgr.cpp, BattlemonScripts.cpp, mod_battlemon_loader.cpp
# (party / catch / dex / timed wilds)

AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src")

AC_ADD_CONFIG_FILE("${CMAKE_CURRENT_LIST_DIR}/conf/mod_battlemon.conf.dist")

AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src")

AC_ADD_CONFIG_FILE("${CMAKE_CURRENT_LIST_DIR}/conf/mod_battlemon.conf.dist")
