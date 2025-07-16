#!/usr/bin/env python3
"""
CGM Taskbar Widget - A Windows taskbar widget that displays directly on the taskbar
"""

import sys
import time
import threading
from datetime import datetime
from typing import Optional
import json
import os
import getpass
import tkinter as tk
from tkinter import ttk

try:
    from pydexcom import Dexcom, Region
    from pydexcom.errors import DexcomError
except ImportError:
    print("pydexcom not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("pystray and Pillow not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


class CGMTaskbarWidget:
    """Taskbar widget that displays directly on the Windows taskbar"""
    
    def __init__(self):
        self.dexcom = None
        self.current_reading = None
        self.last_update = None
        self.update_interval = 60  # seconds
        self.running = False
        self.config_file = "cgm_config.json"
        self.config = self.load_config()
        
        # Set default unit preference to mmol/L
        if 'unit_preference' not in self.config:
            self.config['unit_preference'] = 'mmol/L'
            self.save_config()
        
        # Initialize the taskbar window
        self.root = None
        self.glucose_label = None
        self.trend_label = None
        self.time_label = None
        
    def load_config(self) -> dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_dexcom_connection(self):
        """Setup Dexcom connection using saved credentials"""
        username = self.config.get('username')
        password = self.config.get('password')
        region = self.config.get('region', 'us')
        
        if not username or not password:
            print("No saved credentials found. Please run cgm_widget_cli.py first to set up credentials.")
            return False
        
        try:
            print(f"Connecting to Dexcom using saved credentials...")
            
            # Convert region string to Region enum
            region_enum = Region(region)
            self.dexcom = Dexcom(
                username=username,
                password=password,
                region=region_enum
            )
            
            # Test the connection
            test_reading = self.dexcom.get_current_glucose_reading()
            if test_reading:
                print(f"✓ Connected successfully!")
                print(f"Current glucose: {test_reading.value} mg/dL ({test_reading.mmol_l} mmol/L)")
                return True
            else:
                print("⚠ Connected but no recent glucose reading available.")
                return True
                
        except DexcomError as e:
            print(f"✗ Failed to connect to Dexcom: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    
    def get_display_glucose_value(self, reading):
        """Get glucose value in the configured unit"""
        if not reading:
            return None, ""
        
        unit_pref = self.config.get('unit_preference', 'mmol/L')
        if unit_pref == 'mmol/L':
            return reading.mmol_l, "mmol/L"
        else:
            return reading.mg_dl, "mg/dL"
    
    def get_glucose_color(self, glucose_value):
        """Get color based on glucose level"""
        if glucose_value is None:
            return "#808080"  # Gray for no data
        
        unit_pref = self.config.get('unit_preference', 'mmol/L')
        if unit_pref == 'mmol/L':
            if glucose_value < 3.9:  # Low
                return "#FF6464"  # Red
            elif glucose_value > 10.0:  # High
                return "#FFA500"  # Orange
            else:  # Normal
                return "#64FF64"  # Green
        else:
            if glucose_value < 70:  # Low
                return "#FF6464"  # Red
            elif glucose_value > 180:  # High
                return "#FFA500"  # Orange
            else:  # Normal
                return "#64FF64"  # Green
    
    def get_glucose_reading(self):
        """Get current glucose reading from Dexcom"""
        if not self.dexcom:
            return None
            
        try:
            reading = self.dexcom.get_current_glucose_reading()
            if reading:
                self.current_reading = reading
                self.last_update = datetime.now()
                glucose_value, unit = self.get_display_glucose_value(reading)
                print(f"Glucose: {glucose_value} {unit} ({reading.mg_dl} mg/dL | {reading.mmol_l} mmol/L) {reading.trend_arrow} - {reading.trend_description}")
            return reading
        except DexcomError as e:
            print(f"Dexcom error: {e}")
            return None
        except Exception as e:
            print(f"Error getting glucose reading: {e}")
            return None
    
    def create_taskbar_window(self):
        """Create the taskbar widget window"""
        self.root = tk.Tk()
        
        # Configure window to appear on taskbar
        self.root.title("CGM Widget")
        self.root.geometry("200x80")
        
        # Make window stay on top and always visible
        self.root.attributes('-topmost', True)
        self.root.attributes('-toolwindow', True)  # Prevents it from appearing in Alt+Tab
        
        # Position window at bottom right of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 220  # 200 width + 20 margin
        y = screen_height - 120  # 80 height + 40 margin for taskbar
        self.root.geometry(f"200x80+{x}+{y}")
        
        # Configure window style
        self.root.configure(bg='#2d2d2d')
        self.root.resizable(False, False)
        
        # Remove window decorations but keep it in taskbar
        self.root.overrideredirect(False)
        
        # Create labels for glucose data
        self.glucose_label = tk.Label(
            self.root,
            text="--.-",
            font=("Arial", 16, "bold"),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        self.glucose_label.pack(pady=(5, 0))
        
        self.trend_label = tk.Label(
            self.root,
            text="? --",
            font=("Arial", 12),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        self.trend_label.pack()
        
        self.time_label = tk.Label(
            self.root,
            text="--:--",
            font=("Arial", 8),
            bg='#2d2d2d',
            fg='#cccccc'
        )
        self.time_label.pack(pady=(0, 5))
        
        # Bind right-click for context menu
        self.root.bind("<Button-3>", self.show_context_menu)
        self.glucose_label.bind("<Button-3>", self.show_context_menu)
        self.trend_label.bind("<Button-3>", self.show_context_menu)
        self.time_label.bind("<Button-3>", self.show_context_menu)
        
        # Bind double-click to show details
        self.root.bind("<Double-Button-1>", self.show_details)
        self.glucose_label.bind("<Double-Button-1>", self.show_details)
        
        return self.root
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Show Details", command=self.show_details)
        context_menu.add_command(label="Refresh Now", command=self.refresh_now)
        context_menu.add_separator()
        context_menu.add_command(label="Exit", command=self.quit_app)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_details(self, event=None):
        """Show detailed glucose information"""
        if self.current_reading:
            glucose_value, unit = self.get_display_glucose_value(self.current_reading)
            
            details = f"""Current Glucose Reading:
            
Primary: {glucose_value} {unit}
Alternative: {self.current_reading.mg_dl} mg/dL | {self.current_reading.mmol_l} mmol/L
Trend: {self.current_reading.trend_description} {self.current_reading.trend_arrow}
Time: {self.current_reading.datetime.strftime('%Y-%m-%d %H:%M:%S')}
Last Update: {self.last_update.strftime('%H:%M:%S')}

Status: {'Recent' if (datetime.now() - self.current_reading.datetime).seconds < 600 else 'Outdated'}"""
        else:
            details = "No glucose data available.\n\nPlease check your Dexcom connection."
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title("CGM Widget - Glucose Details")
        details_window.geometry("400x250")
        details_window.configure(bg='#2d2d2d')
        details_window.attributes('-topmost', True)
        
        text_widget = tk.Text(
            details_window,
            wrap=tk.WORD,
            bg='#2d2d2d',
            fg='#ffffff',
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, details)
        text_widget.config(state=tk.DISABLED)
    
    def refresh_now(self):
        """Force immediate refresh of glucose data"""
        print("Manual refresh requested...")
        self.get_glucose_reading()
        self.update_display()
    
    def quit_app(self):
        """Quit the application"""
        print("Shutting down CGM Taskbar Widget...")
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def update_display(self):
        """Update the taskbar widget display"""
        if not self.root:
            return
            
        if self.current_reading:
            glucose_value, unit = self.get_display_glucose_value(self.current_reading)
            trend_arrow = self.current_reading.trend_arrow
            
            # Update glucose value with color
            color = self.get_glucose_color(glucose_value)
            if unit == "mmol/L":
                glucose_text = f"{glucose_value:.1f} {unit}"
            else:
                glucose_text = f"{int(glucose_value)} {unit}"
            
            self.glucose_label.config(text=glucose_text, fg=color)
            self.trend_label.config(text=f"{trend_arrow} {self.current_reading.trend_description}")
            self.time_label.config(text=self.last_update.strftime('%H:%M:%S'))
            
            # Update window background color slightly based on glucose level
            if glucose_value is not None:
                if unit == "mmol/L":
                    if glucose_value < 3.9:  # Low
                        bg_color = '#3d2d2d'  # Slightly red tint
                    elif glucose_value > 10.0:  # High
                        bg_color = '#3d3d2d'  # Slightly orange tint
                    else:  # Normal
                        bg_color = '#2d3d2d'  # Slightly green tint
                else:
                    if glucose_value < 70:  # Low
                        bg_color = '#3d2d2d'  # Slightly red tint
                    elif glucose_value > 180:  # High
                        bg_color = '#3d3d2d'  # Slightly orange tint
                    else:  # Normal
                        bg_color = '#2d3d2d'  # Slightly green tint
                
                self.root.configure(bg=bg_color)
                self.glucose_label.configure(bg=bg_color)
                self.trend_label.configure(bg=bg_color)
                self.time_label.configure(bg=bg_color)
        else:
            self.glucose_label.config(text="--.-", fg='#808080')
            self.trend_label.config(text="? No Data")
            self.time_label.config(text="--:--")
    
    def update_loop(self):
        """Background loop to update glucose readings"""
        while self.running:
            self.get_glucose_reading()
            if self.root:
                self.root.after(0, self.update_display)  # Thread-safe GUI update
            time.sleep(self.update_interval)
    
    def run(self):
        """Run the CGM taskbar widget"""
        # Setup Dexcom connection
        if not self.setup_dexcom_connection():
            print("Failed to setup Dexcom connection.")
            print("Please run 'python cgm_widget_cli.py' first to configure your credentials.")
            return
        
        # Get initial reading
        print("Getting initial glucose reading...")
        self.get_glucose_reading()
        
        # Create taskbar window
        print("Creating taskbar widget...")
        self.create_taskbar_window()
        
        # Start background update thread
        self.running = True
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()
        
        # Update display initially
        self.update_display()
        
        print(f"✓ CGM Taskbar Widget started successfully!")
        print(f"✓ Widget appears at bottom-right of screen")
        print(f"✓ Updates every {self.update_interval} seconds")
        print(f"✓ Double-click for details, right-click for menu")
        print(f"✓ Close the window or use right-click menu to quit")
        
        try:
            # Run the GUI main loop
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nReceived Ctrl+C, shutting down...")
        finally:
            self.running = False


def main():
    """Main entry point"""
    print("Starting CGM Taskbar Widget...")
    print("This widget displays directly on your Windows taskbar.")
    widget = CGMTaskbarWidget()
    widget.run()


if __name__ == "__main__":
    main()