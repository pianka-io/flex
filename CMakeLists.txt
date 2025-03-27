cmake_minimum_required(VERSION 3.10)
project(flexlib LANGUAGES C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(Python3_ROOT_DIR "C:/Python313-32")
set(Python3_INCLUDE_DIR "C:/Python313-32/include")
set(Python3_LIBRARY_RELEASE "C:/Python313-32/libs/python313.lib")
set(Python3_LIBRARY_DEBUG "C:/Python313-32/libs/python313_d.lib")

find_package(Python3 3.13 REQUIRED COMPONENTS Development)

if(NOT Python3_FOUND)
    message(FATAL_ERROR "Python3 not found! Make sure Python3-32 is installed correctly.")
endif()

add_library(flexlib SHARED
    library.c
    api/api.c
    diablo/controls.c
    diablo/diablo.c
    diablo/drawing.c
    diablo/hooks.c
    diablo/window.c
    utilities/list.c
    utilities/log.c
)

target_include_directories(flexlib PRIVATE ${Python3_INCLUDE_DIR})
target_link_directories(flexlib PRIVATE "C:/Python313-32/libs")

target_link_libraries(flexlib PRIVATE
    "$<$<CONFIG:Debug>:${Python3_LIBRARY_DEBUG}>"
    "$<$<CONFIG:Release>:${Python3_LIBRARY_RELEASE}>"
)

set_target_properties(flexlib PROPERTIES
    PREFIX ""
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

add_custom_target(copy_files ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    "${CMAKE_SOURCE_DIR}/resources"
    "${CMAKE_BINARY_DIR}/resources"
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    "${CMAKE_SOURCE_DIR}/scripts"
    "${CMAKE_BINARY_DIR}/scripts"
)

add_dependencies(flexlib copy_files)
