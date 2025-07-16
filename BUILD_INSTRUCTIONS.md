# CGM Simple Widget - Build Instructions

This document explains how to build the CGM Simple Widget into a standalone executable that can be double-clicked to run.

## Overview

The CGM Simple Widget has been successfully converted into a standalone Windows executable using PyInstaller. The executable includes all dependencies and can run on any Windows system without requiring Python to be installed.

## Prerequisites

- Python 3.8 or higher
- All dependencies from `requirements.txt` installed
- PyInstaller installed (`pip install pyinstaller`)

## Quick Build

The simplest way to build the executable:

```bash
python -m PyInstaller --onefile --windowed cgm_simple_widget.py
```

This creates `dist/cgm_simple_widget.exe` - a single executable file.

## Advanced Build (Recommended)

For a more professional build with custom name and icon:

```bash
python -m PyInstaller --onefile --windowed --name=CGM_Simple_Widget --icon=cgm_icon.ico cgm_simple_widget.py
```

## Build Script

Use the provided `build_executable.py` script for automated building:

```bash
python build_executable.py
```

This script:
- Cleans previous build artifacts
- Creates a custom icon file
- Builds the executable with optimizations
- Provides build status and file information

## Build Options Explained

- `--onefile`: Creates a single executable file (vs. a directory with multiple files)
- `--windowed`: No console window appears (GUI-only application)
- `--name=CGM_Simple_Widget`: Custom name for the executable
- `--icon=cgm_icon.ico`: Custom icon for the executable
- `--optimize=2`: Optimize Python bytecode (optional)
- `--clean`: Clean PyInstaller cache before building

## Output

The build process creates:
- `dist/cgm_simple_widget.exe` (or `CGM_Simple_Widget.exe` with custom name)
- `build/` directory (temporary build files)
- `.spec` file (PyInstaller configuration)

## File Size

The executable is approximately 25-30 MB, which includes:
- Python runtime
- All required libraries (pydexcom, tkinter, etc.)
- SSL certificates for HTTPS connections
- Tcl/Tk GUI framework

## Distribution

The executable is completely self-contained and can be:
- Copied to any Windows system
- Run without installing Python or dependencies
- Placed anywhere on the system
- Added to the Start Menu or Desktop

## Configuration

The executable will:
1. Look for `cgm_config.json` in the same directory
2. If not found, prompt for Dexcom credentials on first run
3. Save configuration for future runs

## Troubleshooting

### Build Issues

**Permission Error**: If you get "Access is denied" errors:
- Close any running instances of the executable
- Run the build command again

**Missing Dependencies**: If the build fails due to missing modules:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

**Icon Issues**: If icon creation fails:
- The build will continue without an icon
- Install Pillow: `pip install Pillow`

### Runtime Issues

**Antivirus Warnings**: Some antivirus software may flag the executable:
- This is common with PyInstaller executables
- Add an exception for the file if needed

**Slow Startup**: First run may be slower as the executable extracts:
- Subsequent runs will be faster
- This is normal PyInstaller behavior

## Manual Build Steps

If you prefer to build manually:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Create Icon** (optional):
   ```python
   # Run the icon creation part of build_executable.py
   python -c "from build_executable import create_icon; create_icon()"
   ```

3. **Build Executable**:
   ```bash
   python -m PyInstaller --onefile --windowed cgm_simple_widget.py
   ```

4. **Test the Executable**:
   ```bash
   dist\cgm_simple_widget.exe
   ```

## Updating the Executable

When you make changes to the source code:

1. Make your changes to `cgm_simple_widget.py`
2. Test the changes: `python cgm_simple_widget.py`
3. Rebuild the executable: `python build_executable.py`
4. Test the new executable: `dist\CGM_Simple_Widget.exe`

## Deployment

For easy deployment, you can:

1. **Create a ZIP file** with the executable and a README
2. **Create an installer** using tools like Inno Setup or NSIS
3. **Distribute directly** - just share the `.exe` file

## Security Considerations

- The executable contains your Python code in compiled form
- Configuration files (with credentials) are stored in plain text
- The executable runs with the same permissions as the user
- Network connections are made to Dexcom servers over HTTPS

## Performance

- **Startup time**: 2-5 seconds (first run may be slower)
- **Memory usage**: ~50-100 MB
- **CPU usage**: Minimal (updates every 60 seconds)
- **Network usage**: Minimal (small API calls to Dexcom)

## Success Indicators

A successful build should:
- ✅ Complete without errors
- ✅ Create `dist/cgm_simple_widget.exe`
- ✅ Executable runs when double-clicked
- ✅ Shows credential setup dialogs if no config exists
- ✅ Displays glucose widget after successful setup

## Next Steps

After building successfully:
1. Test the executable on your system
2. Copy to desired location (Desktop, Start Menu, etc.)
3. Run and verify all functionality works
4. Share with others or deploy as needed

The CGM Simple Widget is now ready for standalone use!