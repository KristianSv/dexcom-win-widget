#!/usr/bin/env python3
"""
CGM Widget CLI - Command line version for initial testing
"""

import sys
import time
import threading
from datetime import datetime
from typing import Optional
import json
import os
import getpass

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


class CGMWidgetCLI:
    """Command-line version of CGM Widget for testing"""
    
    def __init__(self):
        self.dexcom = None
        self.current_reading = None
        self.last_update = None
        self.update_interval = 60  # seconds
        self.running = False
        self.icon = None
        self.config_file = "cgm_config.json"
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
        """Setup Dexcom connection with command-line prompts"""
        print("\n=== Dexcom Setup ===")
        
        # Get credentials from config or user input
        username = self.config.get('username')
        password = self.config.get('password')
        region = self.config.get('region', 'us')
        
        if not username:
            username = input("Enter your Dexcom username/email: ").strip()
            if not username:
                print("Username is required.")
                return False
            self.config['username'] = username
        else:
            print(f"Using saved username: {username}")
        
        if not password:
            password = getpass.getpass("Enter your Dexcom password: ")
            if not password:
                print("Password is required.")
                return False
            self.config['password'] = password
        else:
            print("Using saved password.")
        
        # Ask for region if not set
        if 'region' not in self.config:
            print("\nSelect your region:")
            print("1. United States (us)")
            print("2. Outside United States (ous)")
            print("3. Japan (jp)")
            
            choice = input("Enter choice (1-3): ").strip()
            if choice == '1':
                region = 'us'
            elif choice == '2':
                region = 'ous'
            elif choice == '3':
                region = 'jp'
            else:
                print("Invalid choice, defaulting to US")
                region = 'us'
            
            self.config['region'] = region
        else:
            print(f"Using saved region: {region}")
        
        try:
            print(f"\nConnecting to Dexcom ({region})...")
            
            # Convert region string to Region enum
            region_enum = Region(region)
            self.dexcom = Dexcom(
                username=username,
                password=password,
                region=region_enum
            )
            
            # Test the connection
            print("Testing connection...")
            test_reading = self.dexcom.get_current_glucose_reading()
            if test_reading:
                print(f"✓ Connected successfully!")
                print(f"Current glucose: {test_reading.value} mg/dL ({test_reading.mmol_l} mmol/L)")
                print(f"Trend: {test_reading.trend_description} {test_reading.trend_arrow}")
                self.save_config()
                return True
            else:
                print("⚠ Connected but no recent glucose reading available.")
                print("This might be normal if your sensor hasn't transmitted recently.")
                self.save_config()
                return True
                
        except DexcomError as e:
            print(f"✗ Failed to connect to Dexcom: {e}")
            print("\nTroubleshooting tips:")
            print("1. Verify your credentials at https://uam1.dexcom.com (US) or https://uam2.dexcom.com (Outside US)")
            print("2. Ensure you have Dexcom Share enabled with at least one follower")
            print("3. Make sure you're using your main account credentials (not follower credentials)")
            print("4. Try using your account ID instead of username")
            
            # Clear saved credentials on error
            self.config.pop('password', None)
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
            else:
                print("No recent glucose reading available")
            return reading
        except DexcomError as e:
            print(f"Dexcom error: {e}")
            return None
        except Exception as e:
            print(f"Error getting glucose reading: {e}")
            return None
    
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
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
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
            
            print(f"\n=== Current Glucose Reading ===")
            print(f"Primary: {glucose_value} {unit}")
            print(f"Alternative: {self.current_reading.mg_dl} mg/dL | {self.current_reading.mmol_l} mmol/L")
            print(f"Trend: {self.current_reading.trend_description} {self.current_reading.trend_arrow}")
            print(f"Time: {self.current_reading.datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last Update: {self.last_update.strftime('%H:%M:%S')}")
            print(f"Status: {'Recent' if (datetime.now() - self.current_reading.datetime).seconds < 600 else 'Outdated'}")
        else:
            print("\nNo glucose data available. Please check your Dexcom connection.")
    
    def quit_app(self, icon, item):
        """Quit the application"""
        print("\nShutting down CGM Widget...")
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
        print("\nGetting initial glucose reading...")
        self.get_glucose_reading()
        
        # Create system tray icon
        icon_image = self.create_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show Details", self.show_details),
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.icon = pystray.Icon("CGM Widget", icon_image, "CGM Widget", menu)
        
        # Start background update thread
        self.running = True
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()
        
        # Update icon initially
        self.update_icon()
        
        print(f"\n✓ CGM Widget started successfully!")
        print(f"✓ Check your system tray for the glucose icon")
        print(f"✓ Updates every {self.update_interval} seconds")
        print(f"✓ Right-click the icon for options")
        print(f"✓ Press Ctrl+C to quit")
        
        try:
            # Run the icon (this blocks)
            self.icon.run()
        except KeyboardInterrupt:
            print("\nReceived Ctrl+C, shutting down...")
            self.running = False


def main():
    """Main entry point"""
    print("Starting CGM Widget (CLI Version)...")
    print("This version uses command-line prompts for setup.")
    widget = CGMWidgetCLI()
    widget.run()


if __name__ == "__main__":
    main()