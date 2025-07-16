@echo off
echo CGM Simple Widget - Quick Build Script
echo =====================================
echo.

echo Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

echo.
echo Building executable...
python -m PyInstaller --onefile --windowed --name=CGM_Simple_Widget cgm_simple_widget.py

echo.
if exist dist\CGM_Simple_Widget.exe (
    echo ✓ Build successful!
    echo ✓ Executable created: dist\CGM_Simple_Widget.exe
    echo.
    echo You can now double-click dist\CGM_Simple_Widget.exe to run the widget.
) else (
    echo ✗ Build failed!
    echo Please check the error messages above.
)

echo.
pause