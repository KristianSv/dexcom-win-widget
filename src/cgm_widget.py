#!/usr/bin/env python3
"""
CGM Widget - A Windows taskbar widget for monitoring Dexcom G7 glucose data
"""

import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Optional
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

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


class CGMWidget:
    """Main CGM Widget class for monitoring glucose levels"""
    
    def __init__(self):
        self.dexcom = None
        self.current_reading = None
        self.last_update = None
        self.update_interval = 60  # seconds
        self.running = False
        self.icon = None
        self.config_file = "../assets/cgm_config.json"
        self.config = self.load_config()
        
        # Set default unit preference to mmol/L
        if 'unit_preference' not in self.config:
            self.config['unit_preference'] = 'mmol/L'
            self.save_config()
        
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
        """Setup Dexcom connection with user credentials"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Get credentials from config or user input
        username = self.config.get('username')
        password = self.config.get('password')
        region = self.config.get('region', 'us')
        
        if not username:
            username = simpledialog.askstring("Dexcom Setup", "Enter your Dexcom username/email:")
            if not username:
                return False
            self.config['username'] = username
        
        if not password:
            password = simpledialog.askstring("Dexcom Setup", "Enter your Dexcom password:", show='*')
            if not password:
                return False
            self.config['password'] = password
        
        # Ask for region if not set
        if 'region' not in self.config:
            region_choice = messagebox.askyesnocancel(
                "Region Selection", 
                "Are you in the United States?\n\nYes = US\nNo = Outside US\nCancel = Japan"
            )
            if region_choice is True:
                region = 'us'
            elif region_choice is False:
                region = 'ous'
            else:
                region = 'jp'
            self.config['region'] = region
        
        try:
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
                messagebox.showinfo("Success", f"Connected successfully!\nCurrent glucose: {test_reading.value} mg/dL")
                self.save_config()
                root.destroy()
                return True
            else:
                messagebox.showwarning("Warning", "Connected but no recent glucose reading available.")
                self.save_config()
                root.destroy()
                return True
                
        except DexcomError as e:
            messagebox.showerror("Dexcom Error", f"Failed to connect to Dexcom:\n{e}")
            # Clear saved credentials on error
            self.config.pop('password', None)
            root.destroy()
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
            root.destroy()
            return False
    
    def get_glucose_reading(self):
        """Get current glucose reading from Dexcom"""
        if not self.dexcom:
            return None
            
        try:
            reading = self.dexcom.get_current_glucose_reading()
            if reading:
                self.current_reading = reading
                self.last_update = datetime.now()
                print(f"Glucose: {reading.value} mg/dL ({reading.mmol_l} mmol/L) {reading.trend_arrow} - {reading.trend_description}")
            return reading
        except DexcomError as e:
            print(f"Dexcom error: {e}")
            return None
        except Exception as e:
            print(f"Error getting glucose reading: {e}")
            return None
    
    def get_display_glucose_value(self, reading):
        """Get glucose value in the configured unit"""
        if not reading:
            return None, ""
        
        unit_pref = self.config.get('unit_preference', 'mmol/L')
        if unit_pref == 'mmol/L':
            return reading.mmol_l, "mmol/L"
        else:
            return reading.mg_dl, "mg/dL"
    
    def get_glucose_color_ranges(self):
        """Get color ranges based on unit preference"""
        unit_pref = self.config.get('unit_preference', 'mmol/L')
        if unit_pref == 'mmol/L':
            return {
                'low': 3.9,    # < 3.9 mmol/L (70 mg/dL)
                'high': 10.0   # > 10.0 mmol/L (180 mg/dL)
            }
        else:
            return {
                'low': 70,     # < 70 mg/dL
                'high': 180    # > 180 mg/dL
            }
    
    def create_icon_image(self, glucose_value: Optional[float] = None, trend_arrow: str = "?") -> Image.Image:
        """Create system tray icon with glucose value"""
        # Create a 64x64 image
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background circle
        if glucose_value is not None:
            # Color based on glucose level using configured ranges
            ranges = self.get_glucose_color_ranges()
            if glucose_value < ranges['low']:  # Low
                bg_color = (255, 100, 100, 255)  # Red
            elif glucose_value > ranges['high']:  # High
                bg_color = (255, 165, 0, 255)   # Orange
            else:  # Normal
                bg_color = (100, 255, 100, 255)  # Green
        else:
            bg_color = (128, 128, 128, 255)  # Gray for no data
        
        draw.ellipse([2, 2, 62, 62], fill=bg_color)
        
        # Text
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        if glucose_value is not None:
            # Format glucose value based on unit
            unit_pref = self.config.get('unit_preference', 'mmol/L')
            if unit_pref == 'mmol/L':
                text = f"{glucose_value:.1f}"
            else:
                text = str(int(glucose_value))
            
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (64 - text_width) // 2
            y = (64 - text_height) // 2 - 5
            
            draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)
            
            # Add trend arrow
            arrow_y = y + text_height + 2
            arrow_bbox = draw.textbbox((0, 0), trend_arrow, font=font)
            arrow_width = arrow_bbox[2] - arrow_bbox[0]
            arrow_x = (64 - arrow_width) // 2
            draw.text((arrow_x, arrow_y), trend_arrow, fill=(0, 0, 0, 255), font=font)
        else:
            text = "?"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (64 - text_width) // 2
            y = (64 - text_height) // 2
            draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)
        
        return img
    
    def update_icon(self):
        """Update the system tray icon"""
        if self.current_reading:
            glucose_value, unit = self.get_display_glucose_value(self.current_reading)
            trend_arrow = self.current_reading.trend_arrow
            
            # Create tooltip text with both units for reference
            tooltip = f"Glucose: {glucose_value} {unit}"
            if unit == "mmol/L":
                tooltip += f" ({self.current_reading.mg_dl} mg/dL)"
            else:
                tooltip += f" ({self.current_reading.mmol_l} mmol/L)"
            tooltip += f"\nTrend: {self.current_reading.trend_description} {trend_arrow}"
            tooltip += f"\nUpdated: {self.last_update.strftime('%H:%M:%S')}"
        else:
            glucose_value = None
            trend_arrow = "?"
            tooltip = "No glucose data available"
        
        # Update icon
        icon_image = self.create_icon_image(glucose_value, trend_arrow)
        if self.icon:
            self.icon.icon = icon_image
            self.icon.title = tooltip
    
    def show_details(self, icon, item):
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
        
        # Show in a simple dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("CGM Widget - Glucose Details", details)
        root.destroy()
    
    def reconfigure(self, icon, item):
        """Reconfigure Dexcom connection"""
        # Clear saved credentials
        self.config.pop('username', None)
        self.config.pop('password', None)
        self.config.pop('region', None)
        
        if self.setup_dexcom_connection():
            messagebox.showinfo("Success", "Reconfiguration successful!")
        
    def quit_app(self, icon, item):
        """Quit the application"""
        self.running = False
        icon.stop()
    
    def update_loop(self):
        """Background loop to update glucose readings"""
        while self.running:
            self.get_glucose_reading()
            self.update_icon()
            time.sleep(self.update_interval)
    
    def run(self):
        """Run the CGM widget"""
        # Setup Dexcom connection
        if not self.setup_dexcom_connection():
            print("Failed to setup Dexcom connection. Exiting.")
            return
        
        # Get initial reading
        self.get_glucose_reading()
        
        # Create system tray icon
        icon_image = self.create_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show Details", self.show_details),
            pystray.MenuItem("Reconfigure", self.reconfigure),
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.icon = pystray.Icon("CGM Widget", icon_image, "CGM Widget", menu)
        
        # Start background update thread
        self.running = True
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()
        
        # Update icon initially
        self.update_icon()
        
        print("CGM Widget started. Check your system tray.")
        
        # Run the icon (this blocks)
        self.icon.run()


def main():
    """Main entry point"""
    print("Starting CGM Widget...")
    widget = CGMWidget()
    widget.run()


if __name__ == "__main__":
    main()