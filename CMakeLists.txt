cmake_minimum_required(VERSION 3.15)
project(KAPESIT VERSION 1.0.0 LANGUAGES CXX ASM)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -fPIC -fopenmp -mavx2 -mfma")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -Wall -Wextra")

# Find required packages
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(NumPy REQUIRED)

# Include directories
include_directories(
    ${Python3_INCLUDE_DIRS}
    ${NumPy_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/kapesit
)

# Source files
set(CPP_SOURCES
    cpp/fastops.cpp
    cpp/quantum_sim.cpp
    cpp/parallel_ops.cpp
    cpp/numerical_ops.cpp
)

set(ASM_SOURCES
    cpp/assembly_ops.asm
)

# Build shared libraries
add_library(fastops SHARED ${CPP_SOURCES})
add_library(quantum SHARED ${CPP_SOURCES})
add_library(parallel SHARED ${CPP_SOURCES})
add_library(numerical SHARED ${CPP_SOURCES})
add_library(assembly SHARED ${ASM_SOURCES})

# Set output names
set_target_properties(fastops PROPERTIES OUTPUT_NAME "libfastops")
set_target_properties(quantum PROPERTIES OUTPUT_NAME "libquantum")
set_target_properties(parallel PROPERTIES OUTPUT_NAME "libparallel")
set_target_properties(numerical PROPERTIES OUTPUT_NAME "libnumerical")
set_target_properties(assembly PROPERTIES OUTPUT_NAME "libassembly")

# Install targets
install(TARGETS fastops quantum parallel numerical assembly
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

# Python package installation
install(DIRECTORY kapesit/
    DESTINATION ${Python3_SITE_PACKAGES}/kapesit
    FILES_MATCHING PATTERN "*.py"
)

# Tests
enable_testing()
add_subdirectory(tests) 