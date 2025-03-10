cmake_minimum_required(VERSION 3.10)
project(flexlib LANGUAGES C)

# flexlib
add_library(flexlib SHARED library.c api.c log.c diablo/diablo.c)

set_target_properties(flexlib PROPERTIES PREFIX "")
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(CMAKE_SYSTEM_PROCESSOR x86)
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -masm=intel")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -m32 -masm=intel")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -m32")

target_link_libraries(flexlib PRIVATE msvcrt)

# Plugin: pickup-gold
add_library(pickup-gold SHARED plugins/pickup-gold.c)

set_target_properties(pickup-gold PROPERTIES
    PREFIX ""
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/plugins"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/plugins"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/plugins"
)

target_link_libraries(pickup-gold PRIVATE flexlib msvcrt)
add_dependencies(pickup-gold flexlib)
