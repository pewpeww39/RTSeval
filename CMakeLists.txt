cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(RTSeval_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()
add_executable(RTSeval
  RTSeval.c
)
pico_enable_stdio_usb(RTSeval 1)①
pico_enable_stdio_uart(RTSeval 1)②
pico_add_extra_outputs(RTSeval)
target_link_libraries(RTSeval pico_stdlib)
