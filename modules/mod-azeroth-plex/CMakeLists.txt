AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/mod_azeroth_plex.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/mod_azeroth_plex_loader.cpp")

CU_SET_PATH("CMAKE_CONFIG_OUTPUT_DIR" "${CMAKE_CURRENT_LIST_DIR}/conf")

CU_ADD_HOOK(AFTER_WORLDSERVER_CMAKE "${CMAKE_CURRENT_LIST_DIR}/conf/mod_azeroth_plex.conf.dist")
