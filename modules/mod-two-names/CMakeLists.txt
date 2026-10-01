# AzerothCore module: mod-two-names
cmake_minimum_required(VERSION 3.16)

include("${CMAKE_CURRENT_LIST_DIR}/mod-two-names.cmake")

set(MOD_TWO_NAMES_ROOT ${CMAKE_CURRENT_SOURCE_DIR})

add_library(mod-two-names INTERFACE)

target_sources(mod-two-names INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/mod_two_names.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/two_names_loader.cpp
)

target_include_directories(mod-two-names INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(mod-two-names INTERFACE
    game
)
