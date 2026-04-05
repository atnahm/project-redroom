cmake_minimum_required(VERSION 3.16)
project(redroom_forensics)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenCV REQUIRED)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${OpenCV_INCLUDE_DIRS}
)

# Source files for PRNU extractor
set(PRNU_SOURCES
    prnu_extractor.cpp
)

# Source files for Bispectral analyzer
set(BISPECTRAL_SOURCES
    bispectral_analyzer.cpp
)

# Build shared libraries (for ctypes loading from Python)

# PRNU Extractor Library
add_library(prnu_extractor SHARED ${PRNU_SOURCES})
target_link_libraries(prnu_extractor ${OpenCV_LIBS})
set_target_properties(prnu_extractor PROPERTIES
    VERSION 1.0
    SOVERSION 1
    PUBLIC_HEADER "prnu_extractor.hpp"
)

# Bispectral Analyzer Library
add_library(bispectral_analyzer SHARED ${BISPECTRAL_SOURCES})
target_link_libraries(bispectral_analyzer ${OpenCV_LIBS})
set_target_properties(bispectral_analyzer PROPERTIES
    VERSION 1.0
    SOVERSION 1
    PUBLIC_HEADER "bispectral_analyzer.hpp"
)

# Installation
install(TARGETS prnu_extractor bispectral_analyzer
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    PUBLIC_HEADER DESTINATION include/redroom/forensics/cpp
)

# Build options
option(BUILD_TESTS "Build test executables" OFF)
option(ENABLE_GPU "Enable GPU acceleration (CUDA)" OFF)

# GPU support (optional)
if(ENABLE_GPU)
    find_package(CUDA REQUIRED)
    message(STATUS "CUDA support enabled")
endif()

# Compiler flags for optimization
if(MSVC)
    target_compile_options(prnu_extractor PRIVATE /O2 /W4)
    target_compile_options(bispectral_analyzer PRIVATE /O2 /W4)
else()
    target_compile_options(prnu_extractor PRIVATE -O3 -Wall -Wextra)
    target_compile_options(bispectral_analyzer PRIVATE -O3 -Wall -Wextra)
endif()

# Print build configuration
message(STATUS "=== Redroom Forensics Build Configuration ===")
message(STATUS "OpenCV found: ${OpenCV_FOUND}")
message(STATUS "OpenCV version: ${OpenCV_VERSION}")
message(STATUS "OpenCV libraries: ${OpenCV_LIBS}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "GPU support: ${ENABLE_GPU}")
