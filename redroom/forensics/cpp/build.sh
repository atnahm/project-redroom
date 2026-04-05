#!/bin/bash

# Build script for Redroom C++ forensics modules on Linux/macOS
# Requirements: GCC/Clang, CMake 3.16+, OpenCV dev libraries

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  Redroom C++ Forensics Build Script - Linux/macOS  ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check for CMake
if ! command -v cmake &> /dev/null; then
    echo "❌ CMake not found"
    echo "Install with: sudo apt-get install cmake (Ubuntu/Debian)"
    echo "           : brew install cmake (macOS)"
    exit 1
fi

echo "✓ CMake found: $(cmake --version | head -1)"

# Check for OpenCV
echo ""
echo "Detecting OpenCV..."
if [ -d "/usr/local/include/opencv4" ]; then
    echo "✓ OpenCV 4.x found at /usr/local/include/opencv4"
    OPENCV_DIR="/usr/local"
elif [ -d "/usr/include/opencv4" ]; then
    echo "✓ OpenCV 4.x found at /usr/include/opencv4"
    OPENCV_DIR="/usr"
elif pkg-config --exists opencv4; then
    echo "✓ OpenCV found via pkg-config"
    OPENCV_DIR=$(pkg-config --variable=libdir opencv4)
else
    echo "⚠️  OpenCV not found - continuing with system defaults"
    OPENCV_DIR=""
fi

# Detect compiler
if command -v clang++ &> /dev/null; then
    COMPILER="clang++"
    echo "✓ Using Clang compiler"
elif command -v g++ &> /dev/null; then
    COMPILER="g++"
    echo "✓ Using GCC compiler"
else
    echo "❌ No C++ compiler found"
    exit 1
fi

# Create and enter build directory
echo ""
echo "Creating build directory..."
mkdir -p build
cd build

# Run CMake
echo ""
echo "Running CMake configuration..."
if [ -n "$OPENCV_DIR" ]; then
    cmake -DCMAKE_CXX_COMPILER=$COMPILER \
          -DCMAKE_BUILD_TYPE=Release \
          -DOpenCV_DIR="$OPENCV_DIR/lib/cmake/opencv4" \
          .. || {
        echo "❌ CMake configuration failed"
        exit 1
    }
else
    cmake -DCMAKE_CXX_COMPILER=$COMPILER \
          -DCMAKE_BUILD_TYPE=Release \
          .. || {
        echo "❌ CMake configuration failed (try: sudo apt-get install libopencv-dev)"
        exit 1
    }
fi

# Build
echo ""
echo "Building libraries (parallel with $(nproc) cores)..."
cmake --build . --config Release --parallel $(nproc)

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build complete!"
else
    echo "❌ Build failed"
    exit 1
fi

# List compiled libraries
echo ""
echo "Compiled libraries:"
[ -f "libprnu_extractor.so" ] && echo "  ✓ libprnu_extractor.so"
[ -f "libprnu_extractor.so.1" ] && echo "  ✓ libprnu_extractor.so.1"
[ -f "libbispectral_analyzer.so" ] && echo "  ✓ libbispectral_analyzer.so"
[ -f "libbispectral_analyzer.so.1" ] && echo "  ✓ libbispectral_analyzer.so.1"
[ -f "libprnu_extractor.dylib" ] && echo "  ✓ libprnu_extractor.dylib (macOS)"
[ -f "libbispectral_analyzer.dylib" ] && echo "  ✓ libbispectral_analyzer.dylib (macOS)"

echo ""
echo "Next steps:"
echo "  1. Test with: python ctypes_bridge.py"
echo "  2. Run integration tests: python ../../test_integration.py"
echo ""
echo "Troubleshooting:"
echo "  If OpenCV not found:"
echo "    Ubuntu/Debian: sudo apt-get install libopencv-dev opencv-data"
echo "    macOS:         brew install opencv"
echo "    From source:   https://github.com/opencv/opencv/releases"
echo ""
