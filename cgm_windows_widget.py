#!/usr/bin/env python3
"""
CGM Windows Widget - A true Windows taskbar widget using Windows API
"""

import sys
import time
import threading
from datetime import datetime
from typing import Optional
import json
import os
import ctypes
from ctypes import wintypes
import tkinter as tk

try:
    from pydexcom import Dexcom, Region
    from pydexcom.errors import DexcomError
except ImportError:
    print("pydexcom not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

# Windows API constants
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
WS_EX_NOACTIVATE = 0x08000000
WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000

GWL_EXSTYLE = -20
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_FRAMECHANGED = 0x0020

HWND_TOPMOST = -1

# Load Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class CGMWindowsWidget:
    """True Windows taskbar widget using Windows API"""
    
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
        
        # Initialize the widget window
        self.root = None
        self.glucose_label = None
        self.hwnd = None
        
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
                return "#FF4444"  # Red
            elif glucose_value > 10.0:  # High
                return "#FF8800"  # Orange
            else:  # Normal
                return "#44FF44"  # Green
        else:
            if glucose_value < 70:  # Low
                return "#FF4444"  # Red
            elif glucose_value > 180:  # High
                return "#FF8800"  # Orange
            else:  # Normal
                return "#44FF44"  # Green
    
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
    
    def make_widget_style(self):
        """Apply Windows API styling to make it a true widget"""
        if not self.hwnd:
            return
            
        try:
            # Get current extended style
            current_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
            
            # Set new extended style for widget behavior
            new_style = current_style | WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_NOACTIVATE
            user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, new_style)
            
            # Apply the changes
            user32.SetWindowPos(
                self.hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
            )
            
            print("✓ Applied Windows widget styling")
            
        except Exception as e:
            print(f"Warning: Could not apply widget styling: {e}")
    
    def create_widget_window(self):
        """Create the Windows widget window"""
        self.root = tk.Tk()
        
        # Configure window
        self.root.title("CGM")
        self.root.geometry("120x40")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(False, False)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Position at top-right of screen (like Windows widgets)
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        x = screen_width - 140  # 120 width + 20 margin
        y = 20  # Top margin
        self.root.geometry(f"120x40+{x}+{y}")
        
        # Get window handle after it's created
        self.root.update()
        self.hwnd = user32.GetParent(self.root.winfo_id())
        if not self.hwnd:
            self.hwnd = user32.FindWindowW(None, "CGM")
        
        # Apply Windows widget styling
        self.make_widget_style()
        
        # Create glucose display
        self.glucose_label = tk.Label(
            self.root,
            text="--.-",
            font=("Segoe UI", 11, "bold"),
            bg='#1e1e1e',
            fg='#ffffff',
            justify='center'
        )
        self.glucose_label.pack(expand=True, fill='both')
        
        # Bind events
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<Button-3>", self.show_context_menu)
        self.glucose_label.bind("<Button-1>", self.on_click)
        self.glucose_label.bind("<Button-3>", self.show_context_menu)
        
        # Make window draggable
        self.glucose_label.bind("<ButtonPress-1>", self.start_drag)
        self.glucose_label.bind("<B1-Motion>", self.on_drag)
        
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        return self.root
    
    def start_drag(self, event):
        """Start dragging the widget"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_drag(self, event):
        """Handle dragging the widget"""
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
    
    def on_click(self, event):
        """Handle click on widget"""
        if event.num == 1:  # Left click
            self.show_details()
    
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
    
    def show_details(self):
        """Show detailed glucose information"""
        if self.current_reading:
            glucose_value, unit = self.get_display_glucose_value(self.current_reading)
            
            details = f"""CGM Widget - Glucose Details

Primary: {glucose_value} {unit}
Alternative: {self.current_reading.mg_dl} mg/dL | {self.current_reading.mmol_l} mmol/L
Trend: {self.current_reading.trend_description} {self.current_reading.trend_arrow}
Time: {self.current_reading.datetime.strftime('%H:%M:%S')}
Last Update: {self.last_update.strftime('%H:%M:%S')}

Status: {'Recent' if (datetime.now() - self.current_reading.datetime).seconds < 600 else 'Outdated'}"""
        else:
            details = "CGM Widget - No Data\n\nNo glucose data available.\nPlease check your Dexcom connection."
        
        # Show details in a message box
        import tkinter.messagebox as msgbox
        msgbox.showinfo("CGM Widget", details)
    
    def refresh_now(self):
        """Force immediate refresh of glucose data"""
        print("Manual refresh requested...")
        self.get_glucose_reading()
        self.update_display()
    
    def quit_app(self):
        """Quit the application"""
        print("Shutting down CGM Windows Widget...")
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def update_display(self):
        """Update the widget display"""
        if not self.root or not self.glucose_label:
            return
            
        if self.current_reading:
            glucose_value, unit = self.get_display_glucose_value(self.current_reading)
            trend_arrow = self.current_reading.trend_arrow
            
            # Format display text
            if unit == "mmol/L":
                display_text = f"{glucose_value:.1f} {trend_arrow}"
            else:
                display_text = f"{int(glucose_value)} {trend_arrow}"
            
            # Update color based on glucose level
            color = self.get_glucose_color(glucose_value)
            
            self.glucose_label.config(text=display_text, fg=color)
            
            # Update tooltip
            tooltip_text = f"Glucose: {glucose_value} {unit}\nTrend: {self.current_reading.trend_description}\nUpdated: {self.last_update.strftime('%H:%M:%S')}"
            
        else:
            self.glucose_label.config(text="--.- ?", fg='#808080')
    
    def update_loop(self):
        """Background loop to update glucose readings"""
        while self.running:
            self.get_glucose_reading()
            if self.root:
                self.root.after(0, self.update_display)  # Thread-safe GUI update
            time.sleep(self.update_interval)
    
    def run(self):
        """Run the CGM Windows widget"""
        # Setup Dexcom connection
        if not self.setup_dexcom_connection():
            print("Failed to setup Dexcom connection.")
            print("Please run 'python cgm_widget_cli.py' first to configure your credentials.")
            return
        
        # Get initial reading
        print("Getting initial glucose reading...")
        self.get_glucose_reading()
        
        # Create widget window
        print("Creating Windows widget...")
        self.create_widget_window()
        
        # Start background update thread
        self.running = True
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()
        
        # Update display initially
        self.update_display()
        
        print(f"✓ CGM Windows Widget started successfully!")
        print(f"✓ Widget appears at top-right of screen")
        print(f"✓ Updates every {self.update_interval} seconds")
        print(f"✓ Left-click for details, right-click for menu")
        print(f"✓ Drag to move, right-click and Exit to quit")
        
        try:
            # Run the GUI main loop
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nReceived Ctrl+C, shutting down...")
        finally:
            self.running = False


def main():
    """Main entry point"""
    print("Starting CGM Windows Widget...")
    print("This creates a true Windows widget using the Windows API.")
    widget = CGMWindowsWidget()
    widget.run()


if __name__ == "__main__":
    main()