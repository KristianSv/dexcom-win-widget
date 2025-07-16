#!/usr/bin/env python3
"""
Build script for CGM Simple Widget executable
"""

import os
import sys
import subprocess
import shutil

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    
    # Remove build and dist directories
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  Removed {dir_name}/")
            except PermissionError:
                print(f"  Warning: Could not remove {dir_name}/ (files may be in use)")
    
    # Remove spec file
    spec_file = 'cgm_simple_widget.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  Removed {spec_file}")

def create_icon():
    """Create a simple icon file"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a 64x64 icon
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a glucose meter icon
        # Background circle
        draw.ellipse([4, 4, 60, 60], fill=(70, 130, 180, 255), outline=(50, 100, 150, 255), width=2)
        
        # Draw "CGM" text
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        text = "CGM"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (64 - text_width) // 2
        y = (64 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Save as ICO file
        img.save('cgm_icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        print("  Created cgm_icon.ico")
        return True
        
    except ImportError:
        print("  Pillow not available, skipping icon creation")
        return False

def build_executable():
    """Build the executable with PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command with optimizations
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Single file executable
        '--windowed',                   # No console window
        '--optimize=2',                 # Optimize bytecode
        '--strip',                      # Strip debug symbols
        '--clean',                      # Clean cache
        '--name=CGM_Simple_Widget',     # Custom name
    ]
    
    # Add icon if it exists
    if os.path.exists('cgm_icon.ico'):
        cmd.extend(['--icon=cgm_icon.ico'])
    
    # Add the main script
    cmd.append('cgm_simple_widget.py')
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Build failed: {e}")
        print(f"  Error output: {e.stderr}")
        return False

def main():
    """Main build process"""
    print("CGM Simple Widget - Build Script")
    print("=" * 40)
    
    # Clean previous builds
    clean_build()
    
    # Create icon
    create_icon()
    
    # Build executable
    if build_executable():
        print("\n✓ Build completed successfully!")
        print(f"✓ Executable location: {os.path.abspath('dist/CGM_Simple_Widget.exe')}")
        print(f"✓ File size: {os.path.getsize('dist/CGM_Simple_Widget.exe') / (1024*1024):.1f} MB")
        
        print("\nTo run the executable:")
        print("  Double-click: dist/CGM_Simple_Widget.exe")
        print("  Or from command line: dist\\CGM_Simple_Widget.exe")
        
    else:
        print("\n✗ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()