AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/EsteriaCasino.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/CasinoBoardGames.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/CasinoPoker.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/CasinoLottery.cpp")
AC_ADD_SCRIPT("${CMAKE_CURRENT_LIST_DIR}/src/loader.cpp")

set_property(GLOBAL APPEND PROPERTY ACORE_MODULE_TEST_SOURCES
  "${CMAKE_CURRENT_LIST_DIR}/tests/casino_test.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/tests/board_games_test.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/tests/holdem_test.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/tests/lottery_test.cpp")
set_property(GLOBAL APPEND PROPERTY ACORE_MODULE_TEST_INCLUDES
  "${CMAKE_CURRENT_LIST_DIR}/src")
