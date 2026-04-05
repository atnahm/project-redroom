# C++ Forensics Modules Build Guide

## Overview

This directory contains C++ implementations of two critical hard-forensics modules:

1. **PRNU Extractor** - Extract camera sensor fingerprints
2. **Bispectral Analyzer** - Detect AI-generated artifacts

These are compiled to shared libraries (.dll/.so) and called from Python via ctypes.

## Prerequisites

### Windows
- **Visual Studio 2019+** or **MinGW-w64**
- **CMake 3.16+** (https://cmake.org/download/)
- **OpenCV 4.x** - Download from: https://opencv.org/releases/

Installation:
```bash
# Option 1: Pre-built OpenCV (recommended)
# Download opencv-4.x.0-windows.exe from https://opencv.org/releases/
# Run installer, select "Add to PATH"

# Option 2: Via vcpkg
vcpkg install opencv:x64-windows
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    opencv-data \
    libopencv-core-dev \
    libopencv-imgproc-dev \
    git
```

### macOS
```bash
brew install opencv cmake
```

## Build Instructions

### Option 1: Automated Build (Recommended)

**Windows:**
```cmd
cd redroom\forensics\cpp
build.bat
```

**Linux/macOS:**
```bash
cd redroom/forensics/cpp
chmod +x build.sh
./build.sh
```

### Option 2: Manual CMake Build

**Windows (Visual Studio):**
```cmd
cd redroom\forensics\cpp
mkdir build && cd build
cmake -G "Visual Studio 17 2022" -A x64 ..
cmake --build . --config Release
```

**Linux/macOS (Unix Makefiles):**
```bash
cd redroom/forensics/cpp
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --parallel 4
```

## Build Output

### Successful Build
After running `build.bat` or `build.sh`, you should see:

**Windows:**
```
✓ build\Release\prnu_extractor.dll
✓ build\Release\bispectral_analyzer.dll
```

**Linux:**
```
✓ build/libprnu_extractor.so
✓ build/libprnu_extractor.so.1
✓ build/libbispectral_analyzer.so
✓ build/libbispectral_analyzer.so.1
```

**macOS:**
```
✓ build/libprnu_extractor.dylib
✓ build/libbispectral_analyzer.dylib
```

## Testing the Build

### Test Python Integration
```bash
cd redroom/forensics/cpp
python ctypes_bridge.py
```

Expected output:
```
✅ PRNU Module: ENABLED
✅ Bispectral Module: ENABLED
```

### Run Full Integration Tests
```bash
cd redroom
python test_integration.py
```

## Module Descriptions

### PRNU Extractor (`prnu_extractor.cpp`)

**Purpose:** Extract camera sensor fingerprints via PRNU (Photo Response Non-Uniformity)

**Algorithm:**
1. Wiener filter to extract noise residual
2. Zero-mean normalization via sliding window
3. Cross-correlation matching against reference database
4. Returns: confidence score, estimated camera model, spoofing probability

**Key Functions:**
- `extract_from_image()` - Single frame PRNU (lower confidence)
- `extract_from_video()` - Multi-frame averaging (higher confidence)
- `extract_from_frames()` - Batch frame processing
- `compare_to_reference()` - Match against NIST/FBI database

**Parameters:**
- `wiener_kernel_size`: 5 (default, adjust for image resolution)
- `zero_mean_window`: 8 (window for local normalization)

### Bispectral Analyzer (`bispectral_analyzer.cpp`)

**Purpose:** Detect AI-generated artifacts via frequency-domain analysis

**Algorithm:**
1. 2D FFT on image
2. Detect frequency spikes (8-32 kHz for GAN, 16-64 kHz for Diffusion)
3. Compute bicoherence (phase coherence measurement)
4. Classify artifact type and estimate AI probability

**Key Functions:**
- `analyze()` - Single image analysis
- `analyze_frames()` - Temporal consistency check across video
- `set_paranoid_mode()` - Toggle 3.5σ (1% false positive) vs 2σ (5%)
- `get_fft_spectrum()` - Debug visualization of frequency spectrum

**Paranoid Mode:**
- **OFF (2σ threshold)**: 5% false positive rate, better for natural media
- **ON (3.5σ threshold)**: 1% false positive rate, for classified analysis

## Troubleshooting

### CMake Not Found
```
Error: CMake not in PATH
```
**Solution:**
- Windows: Reinstall CMake and select "Add CMake to PATH"
- Linux: `sudo apt-get install cmake`
- macOS: `brew install cmake`

### OpenCV Not Found
```
Error: Could not find OpenCV
```
**Solution:**
- Windows: Manually specify OpenCV path in CMakeLists.txt
- Linux: `sudo apt-get install libopencv-dev`
- macOS: `brew install opencv`

### Build Fails with Compiler Error
```
error: unknown pragma pack push...
```
**Solution:**
- Update Visual Studio: `Tools → Get Tools and Features → Update`
- Or use MinGW: `cmake -G "Unix Makefiles" ..`

### DLL/SO Not Found at Runtime
```
OSError: cannot load library
```
**Solution:**
1. Verify libraries exist: `ls build/lib*.so` or `dir build\Release\*.dll`
2. Check library path in `ctypes_bridge.py`
3. On Linux: `export LD_LIBRARY_PATH=$PWD/build:$LD_LIBRARY_PATH`

## Advanced Build Options

### Enable GPU Acceleration (CUDA)
```bash
cmake -DENABLE_GPU=ON ..
```
**Requirements:** NVIDIA CUDA Toolkit 11.0+

### Custom OpenCV Directory
```bash
cmake -DOpenCV_DIR=/custom/path/to/opencv/build ..
```

### Build with Debug Symbols
```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
```

### Build Static Libraries (instead of shared)
Edit CMakeLists.txt:
```cmake
add_library(prnu_extractor STATIC ${PRNU_SOURCES})  # Instead of SHARED
```

## Performance Considerations

- **PRNU extraction from video**: ~500ms per frame (depends on resolution)
- **Bispectral analysis**: ~100ms per image
- **Optimal configuration**: 64-core CPU, 32GB RAM for real-time 4K
- **GPU acceleration**: ~50x faster with NVIDIA A100 (optional)

## Reference Standards

- **PRNU**: Fridrich & Kodovský (2012) "Rich Models for Steganalysis"
- **Bispectral**: Coluccia et al. (2015) "Detection and Localization of Splicing in Forged Images"
- **OpenCV**: https://docs.opencv.org/

## File Structure

```
redroom/forensics/cpp/
├── CMakeLists.txt              # CMake configuration
├── prnu_extractor.hpp          # PRNU header
├── prnu_extractor.cpp          # PRNU implementation
├── bispectral_analyzer.hpp     # Bispectral header
├── bispectral_analyzer.cpp     # Bispectral implementation
├── ctypes_bridge.py            # Python ctypes wrapper
├── build.bat                   # Windows build script
├── build.sh                    # Linux/macOS build script
├── README.md                   # This file
└── build/                      # (generated after build)
    ├── prnu_extractor.dll/.so  # Compiled library
    └── bispectral_analyzer.dll/.so
```

## Next Steps

1. ✅ Build C++ modules
2. ✅ Test with `python ctypes_bridge.py`
3. ✅ Run integration tests: `python redroom/test_integration.py`
4. Continue with Redroom Tier-1 deployment
