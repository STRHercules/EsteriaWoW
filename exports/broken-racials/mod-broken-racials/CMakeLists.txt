# Broken racials (Salvager, Krokul Cunning, Fel-Scarred, Echo of the Naaru).
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/BrokenRacialEffects.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/BrokenRacialEffects.h")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/broken_racials.cpp")

AC_ADD_SCRIPT_LOADER("BrokenRacials" "${CMAKE_CURRENT_LIST_DIR}/src/loader.h")
