cmake_minimum_required(VERSION 3.10)
project(flexlib LANGUAGES C)

add_library(flexlib SHARED library.c log.c diablo.c)

set_target_properties(flexlib PROPERTIES PREFIX "")
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(CMAKE_SYSTEM_PROCESSOR x86)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -m32")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -m32")

target_link_libraries(flexlib PRIVATE msvcrt)
