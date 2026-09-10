AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/mod_wxl_dbc.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/WxlDbcLoader.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/WxlDbcScan.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/WxlDbcRegistry.cpp")
AC_ADD_SCRIPT_LOADER("WxlDbc" "${CMAKE_CURRENT_LIST_DIR}/src/loader.h")

AC_ADD_CONFIG_FILE("${CMAKE_CURRENT_LIST_DIR}/conf/mod_wxl_dbc.conf.dist")
