#!/usr/bin/env python3
"""
Test script for CGM Widget - Uses mock data for development/testing
"""

import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Optional
import tkinter as tk
from tkinter import messagebox
import json
import os
import random

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("pystray and Pillow not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


class MockGlucoseReading:
    """Mock glucose reading for testing"""
    
    def __init__(self, value: int, trend: str = "Flat"):
        self.value = value
        self.mg_dl = value
        self.mmol_l = round(value * 0.0555, 1)
        self.trend_direction = trend
        self.datetime = datetime.now()
        
        # Trend mappings
        trend_arrows = {
            "DoubleUp": "↑↑",
            "SingleUp": "↑", 
            "FortyFiveUp": "↗",
            "Flat": "→",
            "FortyFiveDown": "↘",
            "SingleDown": "↓",
            "DoubleDown": "↓↓"
        }
        
        trend_descriptions = {
            "DoubleUp": "rising quickly",
            "SingleUp": "rising",
            "FortyFiveUp": "rising slightly", 
            "Flat": "steady",
            "FortyFiveDown": "falling slightly",
            "SingleDown": "falling",
            "DoubleDown": "falling quickly"
        }
        
        self.trend_arrow = trend_arrows.get(trend, "?")
        self.trend_description = trend_descriptions.get(trend, "unknown")


class MockDexcom:
    """Mock Dexcom class for testing"""
    
    def __init__(self, username, password, region=None):
        self.username = username
        self.password = password
        self.region = region
        self.base_glucose = 120  # Starting glucose level
        self.trend_direction = "Flat"
        
    def get_current_glucose_reading(self):
        """Generate mock glucose reading with realistic variation"""
        # Simulate glucose variation
        variation = random.randint(-10, 10)
        self.base_glucose = max(50, min(400, self.base_glucose + variation))
        
        # Occasionally change trend
        if random.random() < 0.1:  # 10% chance to change trend
            trends = ["DoubleUp", "SingleUp", "FortyFiveUp", "Flat", 
                     "FortyFiveDown", "SingleDown", "DoubleDown"]
            self.trend_direction = random.choice(trends)
        
        return MockGlucoseReading(self.base_glucose, self.trend_direction)


class TestCGMWidget:
    """Test version of CGM Widget with mock data"""
    
    def __init__(self):
        self.dexcom = None
        self.current_reading = None
        self.last_update = None
        self.update_interval = 10  # Faster updates for testing
        self.running = False
        self.icon = None
        self.config = {'unit_preference': 'mmol/L'}  # Default to mmol/L for testing
        
    def setup_mock_connection(self):
        """Setup mock Dexcom connection"""
        print("Setting up mock Dexcom connection...")
        
        # Create mock connection
        self.dexcom = MockDexcom("test@example.com", "password", "us")
        
        # Get initial reading
        test_reading = self.dexcom.get_current_glucose_reading()
        print(f"Mock connection established. Initial glucose: {test_reading.value} mg/dL")
        
        return True
    
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
        """Get mock glucose reading"""
        if not self.dexcom:
            return None
            
        try:
            reading = self.dexcom.get_current_glucose_reading()
            if reading:
                self.current_reading = reading
                self.last_update = datetime.now()
                glucose_value, unit = self.get_display_glucose_value(reading)
                print(f"Mock Glucose: {glucose_value} {unit} ({reading.mg_dl} mg/dL | {reading.mmol_l} mmol/L) {reading.trend_arrow} - {reading.trend_description}")
            return reading
        except Exception as e:
            print(f"Error getting mock glucose reading: {e}")
            return None
    
    def create_icon_image(self, glucose_value: Optional[int] = None, trend_arrow: str = "?") -> Image.Image:
        """Create system tray icon with glucose value"""
        # Create a 64x64 image
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background circle
        if glucose_value:
            # Color based on glucose level
            if glucose_value < 70:  # Low
                bg_color = (255, 100, 100, 255)  # Red
            elif glucose_value > 180:  # High
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
        
        if glucose_value:
            text = str(glucose_value)
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
            text = "TEST"
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
            glucose_value = self.current_reading.value
            trend_arrow = self.current_reading.trend_arrow
            
            tooltip = f"[TEST MODE] Glucose: {glucose_value} mg/dL ({self.current_reading.mmol_l} mmol/L)\n"
            tooltip += f"Trend: {self.current_reading.trend_description} {trend_arrow}\n"
            tooltip += f"Updated: {self.last_update.strftime('%H:%M:%S')}"
        else:
            glucose_value = None
            trend_arrow = "?"
            tooltip = "[TEST MODE] No glucose data available"
        
        # Update icon
        icon_image = self.create_icon_image(glucose_value, trend_arrow)
        if self.icon:
            self.icon.icon = icon_image
            self.icon.title = tooltip
    
    def show_details(self, icon, item):
        """Show detailed glucose information"""
        if self.current_reading:
            details = f"""[TEST MODE] Current Glucose Reading:
            
Value: {self.current_reading.value} mg/dL ({self.current_reading.mmol_l} mmol/L)
Trend: {self.current_reading.trend_description} {self.current_reading.trend_arrow}
Time: {self.current_reading.datetime.strftime('%Y-%m-%d %H:%M:%S')}
Last Update: {self.last_update.strftime('%H:%M:%S')}

Status: Mock Data - For Testing Only"""
        else:
            details = "[TEST MODE] No glucose data available."
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("CGM Widget - Test Mode", details)
        root.destroy()
    
    def simulate_glucose_scenarios(self, icon, item):
        """Simulate different glucose scenarios"""
        scenarios = [
            (65, "SingleDown"),   # Low glucose
            (85, "Flat"),         # Normal
            (120, "FortyFiveUp"), # Normal rising
            (200, "SingleUp"),    # High glucose
            (250, "DoubleUp"),    # Very high
        ]
        
        scenario = random.choice(scenarios)
        self.dexcom.base_glucose = scenario[0]
        self.dexcom.trend_direction = scenario[1]
        
        print(f"Simulating scenario: {scenario[0]} mg/dL, {scenario[1]}")
        
        # Force immediate update
        self.get_glucose_reading()
        self.update_icon()
    
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
        """Run the test CGM widget"""
        print("Starting CGM Widget in TEST MODE...")
        
        # Setup mock connection
        if not self.setup_mock_connection():
            print("Failed to setup mock connection. Exiting.")
            return
        
        # Get initial reading
        self.get_glucose_reading()
        
        # Create system tray icon
        icon_image = self.create_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show Details", self.show_details),
            pystray.MenuItem("Simulate Scenario", self.simulate_glucose_scenarios),
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.icon = pystray.Icon("CGM Widget Test", icon_image, "[TEST] CGM Widget", menu)
        
        # Start background update thread
        self.running = True
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()
        
        # Update icon initially
        self.update_icon()
        
        print("CGM Widget TEST MODE started. Check your system tray.")
        print("Right-click the icon to simulate different glucose scenarios.")
        
        # Run the icon (this blocks)
        self.icon.run()


def main():
    """Main entry point for test mode"""
    print("=" * 50)
    print("CGM Widget - TEST MODE")
    print("=" * 50)
    print("This version uses mock data for testing purposes.")
    print("No real Dexcom connection is required.")
    print("=" * 50)
    
    widget = TestCGMWidget()
    widget.run()


if __name__ == "__main__":
    main()