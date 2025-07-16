#!/usr/bin/env python3
"""
Setup script for CGM Widget
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def create_shortcut():
    """Create a desktop shortcut (Windows)"""
    if sys.platform != "win32":
        print("Shortcut creation is only supported on Windows")
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "CGM Widget.lnk")
        target = os.path.join(os.getcwd(), "cgm_widget.py")
        wDir = os.getcwd()
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print(f"✓ Desktop shortcut created: {path}")
    except ImportError:
        print("To create shortcuts, install: pip install winshell pywin32")
    except Exception as e:
        print(f"Failed to create shortcut: {e}")

def main():
    """Main setup function"""
    print("CGM Widget Setup")
    print("================")
    
    # Install requirements
    if not install_requirements():
        return
    
    # Ask about shortcut
    if sys.platform == "win32":
        response = input("\nCreate desktop shortcut? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            create_shortcut()
    
    print("\nSetup complete!")
    print("\nTo run the CGM Widget:")
    print("  python cgm_widget.py")
    print("\nThe widget will appear in your system tray.")
    print("Right-click the icon for options.")

if __name__ == "__main__":
    main()