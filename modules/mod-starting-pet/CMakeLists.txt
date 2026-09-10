# Add script files
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/StartingPet.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/StartingPetSC.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/StartingPet.h")

# Add scripts to script loader
AC_ADD_SCRIPT_LOADER("StartingPet" "${CMAKE_CURRENT_LIST_DIR}/src/loader.h")

# Add config file
AC_ADD_CONFIG_FILE("${CMAKE_CURRENT_LIST_DIR}/conf/mod_startingpet.conf.dist")
