#!/usr/bin/env python3
"""
CGM Simple Widget - A minimal, working desktop widget for immediate use
"""

import sys
import time
import threading
from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

try:
    from pydexcom import Dexcom, Region
    from pydexcom.errors import DexcomError
except ImportError:
    print("pydexcom not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


class CGMSimpleWidget:
    """Minimal desktop widget for glucose monitoring"""
    
    def __init__(self):
        self.dexcom = None
        self.current_reading = None
        self.last_update = None
        self.update_interval = 60
        self.running = False
        self.config_file = "cgm_config.json"
        self.config = self.load_config()
        
        if 'unit_preference' not in self.config:
            self.config['unit_preference'] = 'mmol/L'
            self.save_config()
        
        self.root = None
        self.display_label = None
        
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
    
    def save_position(self, x, y):
        """Save widget position to config"""
        self.config['window_position'] = {'x': x, 'y': y}
        self.save_config()
    
    def get_saved_position(self):
        """Get saved widget position from config"""
        return self.config.get('window_position', None)
    
    def get_default_position(self):
        """Calculate default position (top-right corner)"""
        if self.root:
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            x = screen_width - 180
            y = 20
            return {'x': x, 'y': y}
        return {'x': 100, 'y': 100}  # Fallback if root not available
    
    def setup_dexcom_connection(self):
        """Setup Dexcom connection with user credentials"""
        # Create a temporary root window for dialogs
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide the main window
        
        # Get credentials from config or user input
        username = self.config.get('username')
        password = self.config.get('password')
        region = self.config.get('region', 'us')
        
        if not username:
            username = simpledialog.askstring("Dexcom Setup", "Enter your Dexcom username/email:")
            if not username:
                temp_root.destroy()
                return False
            self.config['username'] = username
        
        if not password:
            password = simpledialog.askstring("Dexcom Setup", "Enter your Dexcom password:", show='*')
            if not password:
                temp_root.destroy()
                return False
            self.config['password'] = password
        
        # Ask for region if not set
        if 'region' not in self.config:
            # Create a better region selection dialog
            region_dialog = tk.Toplevel(temp_root)
            region_dialog.title("Select Your Region")
            region_dialog.geometry("300x200")
            region_dialog.resizable(False, False)
            region_dialog.grab_set()  # Make it modal
            
            # Center the dialog
            region_dialog.transient(temp_root)
            
            selected_region = tk.StringVar(value='us')
            
            tk.Label(region_dialog, text="Select your Dexcom region:", font=("Arial", 12, "bold")).pack(pady=10)
            
            tk.Radiobutton(region_dialog, text="United States", variable=selected_region, value='us', font=("Arial", 10)).pack(pady=5)
            tk.Radiobutton(region_dialog, text="Outside United States", variable=selected_region, value='ous', font=("Arial", 10)).pack(pady=5)
            tk.Radiobutton(region_dialog, text="Japan", variable=selected_region, value='jp', font=("Arial", 10)).pack(pady=5)
            
            def on_ok():
                region_dialog.destroy()
            
            def on_cancel():
                selected_region.set('cancel')
                region_dialog.destroy()
            
            button_frame = tk.Frame(region_dialog)
            button_frame.pack(pady=20)
            
            tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
            
            # Wait for dialog to close
            region_dialog.wait_window()
            
            if selected_region.get() == 'cancel':
                temp_root.destroy()
                return False
            
            region = selected_region.get()
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
                temp_root.destroy()
                return True
            else:
                messagebox.showwarning("Warning", "Connected but no recent glucose reading available.")
                self.save_config()
                temp_root.destroy()
                return True
                
        except DexcomError as e:
            messagebox.showerror("Dexcom Error", f"Failed to connect to Dexcom:\n{e}")
            # Clear saved credentials on error
            self.config.pop('password', None)
            temp_root.destroy()
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
            temp_root.destroy()
            return False
    
    def get_glucose_reading(self):
        if not self.dexcom:
            return None
        try:
            reading = self.dexcom.get_current_glucose_reading()
            if reading:
                self.current_reading = reading
                self.last_update = datetime.now()
            return reading
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_display_text(self):
        if not self.current_reading:
            return "No Data", "#888888"
        
        unit_pref = self.config.get('unit_preference', 'mmol/L')
        if unit_pref == 'mmol/L':
            value = self.current_reading.mmol_l
            text = f"{value:.1f} mmol/L"
            # Color based on mmol/L ranges
            if value < 3.9:
                color = "#FF4444"  # Red
            elif value > 10.0:
                color = "#FF8800"  # Orange  
            else:
                color = "#44FF44"  # Green
        else:
            value = self.current_reading.mg_dl
            text = f"{value} mg/dL"
            # Color based on mg/dL ranges
            if value < 70:
                color = "#FF4444"  # Red
            elif value > 180:
                color = "#FF8800"  # Orange
            else:
                color = "#44FF44"  # Green
        
        trend = self.current_reading.trend_arrow
        return f"{text} {trend}", color
    
    def create_widget(self):
        self.root = tk.Tk()
        self.root.title("CGM")
        self.root.geometry("160x50")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Position widget - use saved position or default
        saved_pos = self.get_saved_position()
        if saved_pos:
            x, y = saved_pos['x'], saved_pos['y']
            print(f"Using saved position: {x}, {y}")
        else:
            default_pos = self.get_default_position()
            x, y = default_pos['x'], default_pos['y']
            print(f"Using default position: {x}, {y}")
            # Save the default position for next time
            self.save_position(x, y)
        
        self.root.geometry(f"160x50+{x}+{y}")
        
        # Main display
        self.display_label = tk.Label(
            self.root,
            text="Loading...",
            font=("Segoe UI", 11, "bold"),
            bg='#1a1a1a',
            fg='#ffffff',
            justify='center'
        )
        self.display_label.pack(expand=True, fill='both')
        
        # Events
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<Button-3>", self.on_right_click)
        self.display_label.bind("<Button-1>", self.on_click)
        self.display_label.bind("<Button-3>", self.on_right_click)
        
        # Dragging
        self.root.bind("<ButtonPress-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.display_label.bind("<ButtonPress-1>", self.start_drag)
        self.display_label.bind("<B1-Motion>", self.on_drag)
        
        self.drag_x = 0
        self.drag_y = 0
        
    def start_drag(self, event):
        self.drag_x = event.x_root - self.root.winfo_x()
        self.drag_y = event.y_root - self.root.winfo_y()
    
    def on_drag(self, event):
        x = event.x_root - self.drag_x
        y = event.y_root - self.drag_y
        self.root.geometry(f"+{x}+{y}")
        # Save position when dragging
        self.save_position(x, y)
    
    def on_click(self, event):
        self.show_details()
    
    def on_right_click(self, event):
        if not self.running or not self.root:
            return
            
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Details", command=self.show_details)
            menu.add_command(label="Refresh", command=self.refresh)
            menu.add_separator()
            
            # Unit toggle option
            current_unit = self.config.get('unit_preference', 'mmol/L')
            if current_unit == 'mmol/L':
                menu.add_command(label="Switch to mg/dL", command=self.switch_to_mgdl)
            else:
                menu.add_command(label="Switch to mmol/L", command=self.switch_to_mmoll)
            
            menu.add_separator()
            menu.add_command(label="Exit", command=self.quit_app)
            
            menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            # Widget has been destroyed, ignore
            pass
        finally:
            try:
                menu.grab_release()
            except (tk.TclError, UnboundLocalError):
                # Widget destroyed or menu not created, ignore
                pass
    
    def show_details(self):
        if self.current_reading:
            details = f"""CGM Widget

Glucose: {self.current_reading.mmol_l:.1f} mmol/L ({self.current_reading.mg_dl} mg/dL)
Trend: {self.current_reading.trend_description} {self.current_reading.trend_arrow}
Time: {self.current_reading.datetime.strftime('%H:%M:%S')}
Updated: {self.last_update.strftime('%H:%M:%S')}"""
        else:
            details = "CGM Widget\n\nNo glucose data available."
        
        messagebox.showinfo("CGM Widget", details)
    
    def refresh(self):
        print("Manual refresh...")
        self.get_glucose_reading()
        self.update_display()
    
    def switch_to_mgdl(self):
        """Switch display unit to mg/dL"""
        self.config['unit_preference'] = 'mg/dL'
        self.save_config()
        self.update_display()
        print("Switched to mg/dL")
    
    def switch_to_mmoll(self):
        """Switch display unit to mmol/L"""
        self.config['unit_preference'] = 'mmol/L'
        self.save_config()
        self.update_display()
        print("Switched to mmol/L")
    
    def quit_app(self):
        print("Shutting down...")
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def update_display(self):
        if self.root and self.display_label:
            text, color = self.get_display_text()
            self.display_label.config(text=text, fg=color)
    
    def update_loop(self):
        while self.running:
            self.get_glucose_reading()
            if self.root:
                self.root.after(0, self.update_display)
            
            # Sleep in smaller chunks to allow faster shutdown
            for _ in range(self.update_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def run(self):
        if not self.setup_dexcom_connection():
            print("Setup failed. Run cgm_widget_cli.py first.")
            return
        
        print("Creating widget...")
        self.create_widget()
        
        self.running = True
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()
        
        self.get_glucose_reading()
        self.update_display()
        
        print("✓ CGM Widget running!")
        print("✓ Drag to move, click for details, right-click for menu")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False


if __name__ == "__main__":
    print("CGM Simple Widget - Minimal glucose monitoring")
    widget = CGMSimpleWidget()
    widget.run()