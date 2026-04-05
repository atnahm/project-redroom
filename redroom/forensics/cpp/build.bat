@echo off
REM Build script for Redroom C++ forensics modules on Windows
REM Requirements: Visual Studio 2019+ (or Git Bash with MinGW), CMake 3.16+, OpenCV

setlocal enabledelayedexpansion

REM Add CMake to PATH if installed
if exist "C:\Program Files\CMake\bin\cmake.exe" (
    set "PATH=C:\Program Files\CMake\bin;!PATH!"
)

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  Redroom C++ Forensics Build Script - Windows      ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Check for CMake
where cmake >nul 2>nul
if errorlevel 1 (
    echo ❌ CMake not found. Install from: https://cmake.org/download/
    exit /b 1
)

echo ✓ CMake found
cmake --version

REM Check for Visual Studio
echo.
echo Detecting Visual Studio...
if exist "C:\Program Files\Microsoft Visual Studio\2022" (
    set VS_PATH=C:\Program Files\Microsoft Visual Studio\2022
    echo ✓ Visual Studio 2022 found
) else if exist "C:\Program Files\Microsoft Visual Studio\2019" (
    set VS_PATH=C:\Program Files\Microsoft Visual Studio\2019
    echo ✓ Visual Studio 2019 found
) else (
    echo ⚠️  Visual Studio not found (optional - can use MinGW)
)

REM Create build directory
echo.
echo Creating build directory...
if not exist "build" mkdir build
cd build

REM Run CMake
echo.
echo Running CMake...
cmake -G "Visual Studio 17 2022" -A x64 .. ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DOpenCV_DIR="C:\opencv\build" ^
    || (
        echo ❌ CMake configuration failed
        exit /b 1
    )

REM Build
echo.
echo Building libraries...
cmake --build . --config Release --parallel 4
if errorlevel 1 (
    echo ❌ Build failed
    exit /b 1
)

echo.
echo ✅ Build complete!
echo.
echo Compiled libraries:
if exist "Release\prnu_extractor.dll" (
    echo  ✓ Release\prnu_extractor.dll
)
if exist "Release\bispectral_analyzer.dll" (
    echo  ✓ Release\bispectral_analyzer.dll
)

echo.
echo Next steps:
echo  1. Verify libraries are created in build\Release\
echo  2. Test with: python ctypes_bridge.py
echo  3. Run integration tests: python ..\..\test_integration.py

cd ..
endlocal
