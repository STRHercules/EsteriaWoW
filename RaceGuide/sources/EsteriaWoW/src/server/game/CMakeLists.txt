#
# This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
#
# This file is free software; as a special exception the author gives
# unlimited permission to copy and/or distribute it, with or without
# modifications, as long as this notice is preserved.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY, to the extent permitted by law; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#

CU_RUN_HOOK(BEFORE_GAME_LIBRARY)

set(ELUNA_EXCLUDE_DIRS)
if (ELUNA)
  list(APPEND ELUNA_EXCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}/LuaEngine/methods/CMangos
    ${CMAKE_CURRENT_SOURCE_DIR}/LuaEngine/methods/Mangos
    ${CMAKE_CURRENT_SOURCE_DIR}/LuaEngine/methods/TrinityCore
    ${CMAKE_CURRENT_SOURCE_DIR}/LuaEngine/methods/VMangos)
else()
  list(APPEND ELUNA_EXCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/LuaEngine)
endif()

CollectSourceFiles(
  ${CMAKE_CURRENT_SOURCE_DIR}
  PRIVATE_SOURCES
  # Exclude
  ${CMAKE_CURRENT_SOURCE_DIR}/PrecompiledHeaders
  ${ELUNA_EXCLUDE_DIRS})

if (USE_COREPCH)
  set(PRIVATE_PCH_HEADER PrecompiledHeaders/gamePCH.h)
endif ()

# Group sources
GroupSources(${CMAKE_CURRENT_SOURCE_DIR})

add_library(game-interface INTERFACE)

CollectIncludeDirectories(
  ${CMAKE_CURRENT_SOURCE_DIR}
  PUBLIC_INCLUDES
  # Exclude
  ${CMAKE_CURRENT_SOURCE_DIR}/PrecompiledHeaders
  ${ELUNA_EXCLUDE_DIRS})

target_include_directories(game-interface
  INTERFACE
    ${PUBLIC_INCLUDES})

target_link_libraries(game-interface
  INTERFACE
    shared)

add_library(game STATIC
  ${PRIVATE_SOURCES})

add_dependencies(game revision.h)

target_include_directories(game
  PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR})

target_link_libraries(game
  PRIVATE
    acore-core-interface
  PUBLIC
    game-interface
    libsidecar)

set_target_properties(game
  PROPERTIES
    FOLDER
      "server")

# Generate precompiled header
if (USE_COREPCH)
  add_cxx_pch(game ${PRIVATE_PCH_HEADER})
endif ()

CU_RUN_HOOK(AFTER_GAME_LIBRARY)

if (ELUNA)
  if (WIN32)
    if (MSVC)
      add_custom_command(TARGET game POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/bin/$(ConfigurationName)/lua_scripts/extensions/
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/LuaEngine/extensions ${CMAKE_BINARY_DIR}/bin/$(ConfigurationName)/lua_scripts/extensions/)
    elseif (MINGW)
      add_custom_command(TARGET game POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/bin/lua_scripts/extensions/
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/LuaEngine/extensions ${CMAKE_BINARY_DIR}/bin/lua_scripts/extensions/)
    endif()
  endif()

  if (UNIX)
    install(DIRECTORY LuaEngine/extensions DESTINATION bin/lua_scripts/)
  elseif (WIN32)
    install(DIRECTORY LuaEngine/extensions DESTINATION "${CMAKE_INSTALL_PREFIX}/lua_scripts/")
  endif()

  add_subdirectory(LuaEngine)
endif()
