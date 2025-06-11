import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Scrollbar, Text
from PIL import Image, ImageTk
import os
import shutil
import subprocess
import threading
import webbrowser
import time
from tkinter import filedialog, messagebox, Toplevel
from console import Console
from file_manager import FileManager
from transient_simulation import run_simulation_and_generate_html
from graphs_generator import run_simulation_and_generate_graphs
import psutil
from whiteboard import Whiteboard
import json
import tkinter.filedialog as filedialog
from tkinter import filedialog, messagebox
import cv2
import sys
from dashboard import Dashboard

class AiravataSoftware:
    def __init__(self, root):
        self.root = root
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.icons_dir = os.path.join(self.script_dir, "Icons")
        self.whamo_path = os.path.join(self.script_dir, "WHAMO.exe")
        self.visualization_dir = os.path.join(self.script_dir, "visualization")
        self.assets_dir = os.path.join(self.visualization_dir, "attached_assets_parsed")
        self.app_path = os.path.join(self.script_dir, "JayShreeRam", "app.py")
        
        self.setup_ui()
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)

    def get_icon_path(self, icon_filename):
        """Get the full path to an icon file"""
        return os.path.join(self.icons_dir, icon_filename)

    def load_and_resize_icon(self, icon_filename, size=(32, 32)):
        """Load and resize an icon using relative path"""
        try:
            icon_path = self.get_icon_path(icon_filename)
            if not os.path.exists(icon_path):
                print(f"Warning: Icon not found at {icon_path}")
                # Return a default/placeholder icon or None
                return None
            
            img = Image.open(icon_path)
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading icon {icon_filename}: {e}")
            return None

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            self.root.attributes("-fullscreen", False)
            self.root.geometry("1000x700")

    def setup_ui(self):
        self.root.title("Airavata 2.0")
        self.root.geometry("1000x700")
        self.current_theme = 'dark'
        self.root.config(bg="#333")
        self.file_saved = False
        self.file_open = False
        self.elements = []
        self.simulation = None
        self.file_manager = FileManager()
        
        if not self.file_manager:
            print("File manager is not initialized.")
            return
            
        self.whiteboard = Whiteboard(root)
        self.current_file_name = None
        self.highlighted_element = None
        self.simulation_properties = {
            "simulation_time": 10.0,
            "time_step": 0.01,
            "gravity": 9.81,
            "fluid_density": 1000.0
        }
        
        # Create UI components
        self.create_file_label()
        self.create_toolbar()
        self.create_console()
        self.create_whiteboard()
        self.set_app_icon()
        self.create_simulation_property_labels()
        # Apply dark theme as default
        self.apply_dark_theme(show_message=False)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg="#55cee0", pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Load Icons using relative paths
        self.new_icon = self.load_and_resize_icon("new_icon.png")
        self.open_icon = self.load_and_resize_icon("open_icon.png")
        self.save_icon = self.load_and_resize_icon("save_icon.png")
        self.close_icon = self.load_and_resize_icon("close_icon.png")
        self.info_icon = self.load_and_resize_icon("info_icon.png")
        self.export_icon = self.load_and_resize_icon("export_icon.png")
        self.theme_icon = self.load_and_resize_icon("theme_icon.png")
        self.performance_icon = self.load_and_resize_icon("performance_icon.png")
        self.clear_screen_icon = self.load_and_resize_icon("clear_screen_icon.png")
        self.reset_icon = self.load_and_resize_icon("reset_icon.png")
        self.simulation_toolbar_icon = self.load_and_resize_icon("S2.png")
        self.simulation_menu_icon = self.load_and_resize_icon("S1.png")
        self.view_graph_icon = self.load_and_resize_icon("view_graph_icon.png")
        self.Hide_label_icon = self.load_and_resize_icon("Hide_label_icon.png")
        self.Show_label_icon = self.load_and_resize_icon("Show_label_icon.png")
        self.Run_icon = self.load_and_resize_icon("Run_icon.png")
        self.INP_request = self.load_and_resize_icon("INP_request.png")
        self.Final_output_request = self.load_and_resize_icon("Final_output_request.png")
        self.Back_to_dashboard = self.load_and_resize_icon("Back_to_dashboard.png")

        # Add all other buttons first (left side)
        if self.new_icon:
            self.add_toolbar_button(toolbar, self.new_icon, "New File", self.create_new_file)
        if self.open_icon:
            self.add_toolbar_button(toolbar, self.open_icon, "Open File", self.open_file)
        if self.save_icon:
            self.add_toolbar_button(toolbar, self.save_icon, "Save File", self.save_file)
        if self.close_icon:
            self.add_toolbar_button(toolbar, self.close_icon, "Terminate File", self.terminate_file)
        if self.info_icon:
            self.add_toolbar_button(toolbar, self.info_icon, "File Info", self.show_file_info)
        if self.export_icon:
            self.add_toolbar_button(toolbar, self.export_icon, "Export Excel", self.export_to_excel)
        if self.theme_icon:
            self.add_toolbar_button(toolbar, self.theme_icon, "Toggle Theme", self.toggle_theme)
        if self.performance_icon:
            self.add_toolbar_button(toolbar, self.performance_icon, "Monitor Performance", self.monitor_performance)
        if self.clear_screen_icon:
            self.add_toolbar_button(toolbar, self.clear_screen_icon, "Clear Screen", self.clear_screen)
        if self.reset_icon:
            self.add_toolbar_button(toolbar, self.reset_icon, "Reset Element Sizes", self.reset_element_sizes)
        if self.INP_request:
            self.add_toolbar_button(toolbar, self.INP_request, "Select INP file", self.INP_out)
        if self.Final_output_request:
            self.add_toolbar_button(toolbar, self.Final_output_request, "Final output", self.final_out)

        # Add the "Simulation" toolbar button
        if self.simulation_toolbar_icon:
            self.add_toolbar_button(toolbar, self.simulation_toolbar_icon, "Simulation", self.show_dropdown)

        # Add the "Back to Dashboard" button LAST (rightmost)
        if self.Back_to_dashboard:
            # Create a separator frame to push the button to the right
            separator = tk.Frame(toolbar, bg="#55cee0", width=20)
            separator.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            # Add the button with RIGHT packing
            btn = tk.Button(
                toolbar,
                image=self.Back_to_dashboard,
                relief=tk.RAISED,
                bd=3,
                command=self.back_to_dashboard,
                highlightthickness=0,
                activebackground="#d9d9d9"
            )
            btn.pack(side=tk.RIGHT, padx=2, pady=2)
            btn.config(
                relief=tk.RAISED,
                bd=3,
                highlightbackground="#c0c0c0",
                highlightcolor="#f0f0f0"
            )
    
    def back_to_dashboard(self):
        """Return to the dashboard screen from the main application."""
        try:
            # Clear the current application
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Reset window state to match dashboard's preferred size
            self.root.state('zoomed')
            self.root.geometry("1200x800")  # Set to dashboard's preferred size
            
            # Recreate the dashboard
            from dashboard import Dashboard
            Dashboard(self.root, lambda: show_main_application(self.root))
            
            # Don't try to log to console after destroying it
            return
            
        except Exception as e:
            # Show error message directly since console is gone
            messagebox.showerror("Error", f"Failed to return to dashboard: {str(e)}")

    def INP_out(self):
        """Runs WHAMO.exe with an .INP file and generates output files in the same directory."""

        def run_whamo_interactive(inp_file_path):
            try:
                if not os.path.exists(self.whamo_path):
                    self.console.log("WHAMO executable not found.", level="error")
                    messagebox.showerror("Error", "WHAMO.exe not found. Please verify the path.")
                    return

                filename_only = os.path.splitext(os.path.basename(inp_file_path))[0]
                folder = os.path.dirname(inp_file_path)

                # Output filenames WITH extensions
                out_name = f"{filename_only}_OUT.OUT"
                plt_name = f"{filename_only}_PLT.PLT"
                tab_name = f"{filename_only}_SHEET.TAB"

                out_path = os.path.join(folder, out_name)
                plt_path = os.path.join(folder, plt_name)
                tab_path = os.path.join(folder, tab_name)

                if all(os.path.exists(p) for p in [out_path, plt_path, tab_path]):
                    result = messagebox.askyesno(
                        "Output files exist",
                        f"Output files for '{filename_only}' already exist.\nDo you want to overwrite and run WHAMO again?"
                    )
                    if not result:
                        self.console.log("User chose not to overwrite existing output files.", level="info")
                        return
                    else:
                        # Delete existing output files before running WHAMO again
                        for f in [out_path, plt_path, tab_path]:
                            try:
                                os.remove(f)
                                self.console.log(f"Deleted existing file: {f}", level="info")
                            except Exception as e:
                                self.console.log(f"Failed to delete {f}: {str(e)}", level="warning")

                # Provide the filenames with extensions as WHAMO expects full names
                whamo_input = f"{filename_only}\r\n{out_name}\r\n{plt_name}\r\n{tab_name}\r\n"

                self.console.log(f"Running WHAMO on: {inp_file_path}", level="info")

                process = subprocess.Popen(
                    [self.whamo_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    universal_newlines=True
                )

                stdout, stderr = process.communicate(input=whamo_input)

                if process.returncode != 0:
                    self.console.log("WHAMO failed to run.", level="error")
                    self.console.log(stderr, level="error")
                    messagebox.showerror("WHAMO Error", f"WHAMO failed:\n{stderr}")
                    return

                self.console.log("WHAMO ran successfully.", level="success")
                self.console.log(stdout, level="info")

                if os.path.exists(out_path):
                    messagebox.showinfo("WHAMO Finished", f".OUT file generated:\n{out_path}")
                else:
                    messagebox.showwarning("WHAMO Finished", "WHAMO ran, but .OUT file was not found.")

            except Exception as e:
                self.console.log(f"Error running WHAMO: {str(e)}", level="error")
                messagebox.showerror("Error", f"Failed to run WHAMO: {str(e)}")

        try:
            self.console.log("Select a .INP file to run WHAMO...", level="info")

            inp_file = filedialog.askopenfilename(
                title="Select .INP File",
                filetypes=[("INP Files", "*.inp"), ("All Files", "*.*")]
            )

            if not inp_file:
                self.console.log("File selection cancelled.", level="warning")
                return

            if not os.path.exists(inp_file):
                self.console.log("Selected file does not exist.", level="error")
                messagebox.showerror("Error", "The selected .INP file does not exist.")
                return

            thread = threading.Thread(target=run_whamo_interactive, args=(inp_file,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.console.log(f"Error selecting INP file: {str(e)}", level="error")
            messagebox.showerror("Error", f"Failed to select .INP file: {str(e)}")

    def final_out(self):
        """Launches the hydraulic system visualization in Streamlit after selecting a file"""
        try:
            # Show a message indicating visualization is being prepared
            self.console.log("Opening file selection for hydraulic system visualization...", level="info")
            
            # Open a file dialog to select the .OUT file
            file_path = filedialog.askopenfilename(
                title="Select Hydraulic System File (.OUT)",
                filetypes=[("OUT Files", ".out"), ("Text Files", ".txt"), ("All Files", ".")]
            )
            
            # Check if a file was selected
            if not file_path:
                self.console.log("File selection cancelled.", level="warning")
                return
                
            # Check if the selected file is valid
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "Selected file does not exist.")
                self.console.log(f"Selected file does not exist: {file_path}", level="error")
                return
            
            # Create directories if they don't exist
            if not os.path.exists(self.visualization_dir):
                os.makedirs(self.visualization_dir)
                
            if not os.path.exists(self.assets_dir):
                os.makedirs(self.assets_dir)
            
            # Copy the selected file to the visualization directory
            viz_file = os.path.join(self.assets_dir, "complete_data.txt")
            shutil.copy(file_path, viz_file)
            
            # Verify app.py exists
            if not os.path.exists(self.app_path):
                messagebox.showerror("Error", f"Visualization file not found: {self.app_path}\nPlease make sure app.py exists in the visualization directory.")
                self.console.log(f"Visualization file not found: {self.app_path}", level="error")
                return
            
            # Show processing message
            processing_window = Toplevel(self.root)
            processing_window.title("Processing")
            processing_window.geometry("300x100")
            processing_window.transient(self.root)
            processing_window.grab_set()
            
            # Center the processing window
            processing_window.update_idletasks()
            width = processing_window.winfo_width()
            height = processing_window.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            processing_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Add a message and progress indicator
            tk.Label(processing_window, text="Launching visualization...", font=("Segoe UI", 12)).pack(pady=10)
            progress_bar = tk.Label(processing_window, text="Please wait...", font=("Segoe UI", 10))
            progress_bar.pack(pady=5)
            
            # Function to update the processing window with progress
            def update_progress(msg):
                progress_bar.config(text=msg)
                processing_window.update()
            
            # Launch the Streamlit application in a separate process
            def run_streamlit():
                try:
                    update_progress("Starting Streamlit server...")
                    
                    # Debug output to console - helps troubleshoot
                    self.console.log(f"Launching Streamlit with: {self.app_path}", level="info")
                    
                    # Construct the command with proper quoting
                    command = f'python -m streamlit run "{self.app_path}" --server.port 5000'
                    
                    # Run the command
                    process = subprocess.Popen(command, shell=True)
                    
                    update_progress("Server started, opening browser...")
                    self.console.log("Visualization is now running at http://localhost:5000", level="success")
                    
                    # Open the browser automatically
                    time.sleep(3)  # Give Streamlit time to start
                    webbrowser.open("http://localhost:5000")
                    
                    # Close the processing window
                    processing_window.destroy()
                    
                    # Show a success message
                    messagebox.showinfo("Visualization Started", "The hydraulic system visualization has been launched in your web browser.")
                
                except Exception as e:
                    processing_window.destroy()
                    self.console.log(f"Error in thread: {str(e)}", level="error")
                    messagebox.showerror("Error", f"Failed to launch visualization: {str(e)}")
            
            # Run the Streamlit app in a separate thread
            thread = threading.Thread(target=run_streamlit)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.console.log(f"Error launching visualization: {str(e)}", level="error")
            messagebox.showerror("Error", f"Failed to launch visualization: {str(e)}")
            if 'processing_window' in locals() and processing_window.winfo_exists():
                processing_window.destroy()

    def show_dropdown(self, event=None):
        """Show the dropdown menu when the button is clicked."""
        self.dropdown_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def hide_tooltip(self, event=None):
        """Hide the tooltip and reset button relief."""
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            self.tooltip = None
        self.dropdown_button.config(relief=tk.FLAT)  # Reset the button relief when tooltip is hidden

        # Bind the dropdown menu to reset the button relief when it is closed
        self.dropdown_menu.bind("<Leave>", lambda event: self.dropdown_button.config(relief=tk.FLAT))

    def simulation_action(self):
        """Action for Simulation option."""
        self.open_property_box_simulation("Simulation Properties")

    def open_property_box_simulation(self, title):
        """Open a property box with the specified title."""
        property_box = Toplevel(self.root)
        property_box.title(title)
        property_box.geometry("500x450")  # Adjusted size for added properties
        property_box.config(bg="#f5f5f5")  # Set background color

        # Create a frame for better organization
        frame = tk.Frame(property_box, bg="#f5f5f5")
        frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create labels and entry fields for simulation properties
        labels = ["Simulation Time:", "Time Step:", "Gravity:", "Fluid Density:"]
        self.entries = []

        for label_text in labels:
            label = tk.Label(frame, text=label_text, bg="#f5f5f5", font=("Segoe UI", 12))
            label.pack(pady=(5, 0), anchor="w")  # Add padding and align to the left

            entry = tk.Entry(frame, font=("Segoe UI", 12), borderwidth=2, relief="groove")
            entry.pack(pady=5, fill=tk.X)  # Add padding and make it expand horizontally
            self.entries.append(entry)

        # Load and display the saved simulation properties
        self.simulation_time_entry, self.time_step_entry, self.gravity_entry, self.fluid_density_entry = self.entries
        self.simulation_time_entry.delete(0, tk.END)
        self.simulation_time_entry.insert(0, str(self.simulation_properties['simulation_time']))

        self.time_step_entry.delete(0, tk.END)
        self.time_step_entry.insert(0, str(self.simulation_properties['time_step']))

        self.gravity_entry.delete(0, tk.END)
        self.gravity_entry.insert(0, str(self.simulation_properties['gravity']))

        self.fluid_density_entry.delete(0, tk.END)
        self.fluid_density_entry.insert(0, str(self.simulation_properties['fluid_density']))

        # Save and Cancel buttons with improved styling
        button_frame = tk.Frame(property_box, bg="#f5f5f5")
        button_frame.pack(pady=10)

        save_button = tk.Button(button_frame, text="Save", command=lambda: self.save_simulation_properties(
            self.simulation_time_entry.get(), self.time_step_entry.get(), self.gravity_entry.get(), self.fluid_density_entry.get(), property_box),
            bg="#4CAF50", fg="white", font=("Segoe UI", 12), relief="raised", padx=10)
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=property_box.destroy,
                                bg="#f44336", fg="white", font=("Segoe UI", 12), relief="raised", padx=10)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def save_simulation_properties(self, simulation_time, time_step, gravity, fluid_density, property_box):
        """Save simulation properties."""
        try:
            # Convert values to float and store them (or handle validation if needed)
            self.simulation_properties = {
                "simulation_time": float(simulation_time),
                "time_step": float(time_step),
                "gravity": float(gravity),
                "fluid_density": float(fluid_density),
            }
            # Close the property box after saving
            property_box.destroy()
            self.console.log("Simulation properties saved.", level="success")
        except ValueError:
            self.console.log("Invalid input. Please enter valid numbers.", level="error")

    def view_graph_action(self):
        """Action for View Graph option."""
        if not self.current_file_name:
            self.console.log("No file is currently open. Please open a file first.", level="error")
            messagebox.showerror("Error", "No file is currently open. Please open a file first.")
            return

        run_simulation_and_generate_graphs(self.root, self.current_file_name)

    def Hide_label_action(self):
        """Hides the labels of all elements on the whiteboard."""
        for element in self.whiteboard.elements:
            if hasattr(element, "label_id") and element.label_id is not None:
                self.whiteboard.canvas.itemconfig(element.label_id, state="hidden")
        self.console.log("Labels hidden successfully.", level="info")

    def Show_label_action(self):
        """Shows the labels of all elements on the whiteboard again."""
        for element in self.whiteboard.elements:
            if hasattr(element, "label_id") and element.label_id is not None:
                self.whiteboard.canvas.itemconfig(element.label_id, state="zoomed")
        self.console.log("Labels shown successfully.", level="info")

    def Run_icon_action(self):
        """Run the simulation based on the current file."""
        if not self.current_file_name:
            self.console.log("No file is currently open. Please open a file first.", level="error")
            messagebox.showerror("Error", "No file is currently open. Please open a file first.")
            return

        run_simulation_and_generate_html(self.root, self.current_file_name)

    def open_property_box(self, title):
        """Open a property box with the specified title """
        property_box = Toplevel(self.root)
        property_box.title(title)
        property_box.geometry("300x200")  # Set size of the property box
        label = tk.Label(property_box, text=f"{title} - (Content to be added later)", padx=10, pady=10)
        label.pack(expand=True)

    def create_file_label(self):
        """Label to display the current file's name."""
        self.file_label = tk.Label(self.root, text="No file opened", bg="#f5f5f5", anchor="w", font=("Segoe UI", 10))
        self.file_label.pack(fill=tk.X)

    def update_file_label(self):
        """Update the file label to show the current file name."""
        if self.current_file_name:
            self.file_label.config(text=f"Current File: {os.path.basename(self.current_file_name)}")
        else:
            self.file_label.config(text="No file opened")

    def create_console(self):
        self.console_frame = tk.Frame(self.root, bg="#f5f5f5", bd=2, relief="sunken")
        self.console_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.console = Console(self.console_frame)
        self.console.frame.pack(fill=tk.X)

    def create_whiteboard(self):
        self.whiteboard_frame = tk.Frame(self.root)
        self.whiteboard_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.whiteboard = Whiteboard(self.whiteboard_frame)
        self.whiteboard.pack(fill=tk.BOTH, expand=True)

        # Initially disable the whiteboard
        self.whiteboard_disabled = False

    def reset_element_sizes(self):
        """Reset the size of all elements on the whiteboard."""
        # Iterate over all elements in the whiteboard
        for element in self.whiteboard.elements:
            # Reset the icon, label, and port sizes to their default values
            element.reset_size()

    def enable_whiteboard(self):
        """Enable the whiteboard interactions."""
        self.whiteboard_disabled = False

    def disable_whiteboard(self):
        """Disable the whiteboard interactions."""
        self.whiteboard_disabled = True

    def add_toolbar_button(self, toolbar, icon, tooltip, command):
        # Initial button creation with full 3D appearance
        button = tk.Button(
            toolbar,
            image=icon,
            relief=tk.RAISED,  # Start in raised state for 3D
            bd=3,  # Border for depth
            command=command,
            highlightthickness=0,
            activebackground="#d9d9d9"  # Slightly darker active background
        )
        button.pack(side=tk.LEFT, padx=2, pady=2)

        # Immediately set consistent appearance
        button.config(
            relief=tk.RAISED,
            bd=3,
            highlightbackground="#c0c0c0",  # Shadow for 3D effect
            highlightcolor="#f0f0f0"  # Subtle highlight for lighting
        )

        # Hover effects for a dynamic 3D look
        def on_enter(event):
            button.config(
                relief=tk.RAISED,
                bd=4,  # Thicker border for hover
                highlightbackground="#a0a0a0"  # Pronounced shadow
            )

        def on_leave(event):
            button.config(
                relief=tk.RAISED,
                bd=3,  # Reset border thickness
                highlightbackground="#c0c0c0"  # Reset shadow
            )

        # Simulate button press effect
        def on_click(event):
            button.config(
                relief=tk.SUNKEN,  # Pressed appearance
                bd=2,  # Slightly thinner border for pressed state
                highlightbackground="#808080"  # Stronger shadow
            )

        def on_release(event):
            button.config(
                relief=tk.RAISED,
                bd=4,  # Return to hover border
            )

        # Bind hover and click events
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<ButtonPress-1>", on_click)
        button.bind("<ButtonRelease-1>", on_release)

        # Tooltip functionality
        button.bind("<Enter>", lambda event, text=tooltip: self.show_tooltip(event, text))
        button.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event, text):
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 20
        self.tooltip = Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_attributes("-alpha", 0.9)  # Make it semi-transparent
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=text, bg="lightyellow", font=("Segoe UI", 10), relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            self.tooltip = None

    def create_new_file(self):
        if self.file_open:
            messagebox.showwarning("Warning", "Close the current file before creating a new one.")
        else:
            file_name = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
            if file_name:
                # Create a new, empty file
                with open(file_name, 'w') as new_file:
                    new_file.write("{}")  # Optionally initialize with default JSON content (empty JSON object)
                self.file_manager = FileManager(os.path.dirname(file_name))
                self.file_saved = False
                self.file_open = True
                self.current_file_name = file_name  # Set the current file name
                self.whiteboard.is_file_open = True  # Enable the whiteboard
                self.whiteboard.clear()  # Clear the whiteboard
                self.update_file_label()  # Update the file label
                self.console.log("New file created successfully.",level="success")

    def open_file(self):
        """Open a file and load its content onto the canvas."""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            messagebox.showinfo("No File Selected", "No file was selected.")
            return

        try:
            # Load elements from the selected file
            with open(file_path, 'r') as file:
                elements_data = json.load(file)

            if not isinstance(elements_data, dict) or 'elements' not in elements_data:
                raise ValueError("Invalid file structure. Expected a dictionary with an 'elements' key.")

            # Clear existing elements before loading new one
            self.whiteboard.clear()

            # Load elements into the canvas
            self.whiteboard.load_elements(elements_data['elements'])

            # Check and load simulation properties
            if 'simulation_properties' in elements_data['elements']:
                self.simulation_properties = elements_data['elements']['simulation_properties']
                self.update_simulation_properties_ui()  # Update UI with loaded properties
            else:
                # Default values if simulation properties are missing
                self.simulation_properties = {
                    "simulation_time": 10.0,
                    "time_step": 0.01,
                    "gravity": 9.81,
                    "fluid_density": 1000.0,
                }
                self.update_simulation_properties_ui()  # Update UI with default properties

            # Update file state
            self.current_file_name = file_path
            self.file_open = True  # Set the file open flag
            self.whiteboard.is_file_open = True  # Enable the whiteboard
            self.file_manager.file_path = file_path  # Update the file manager
            self.update_file_label()  # Update the file label
            self.console.log(f"Successfully loaded file: {os.path.basename(file_path)}", level="success")

            messagebox.showinfo("File Loaded", f"Successfully loaded file: {os.path.basename(file_path)}")

        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("File Error", f"Failed to load the file. Error: {e}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

    def update_simulation_properties_ui(self):
        """Update the UI elements with the current simulation properties."""
        self.simulation_time_label.config(text=f"Simulation Time [s]: {self.simulation_properties.get('simulation_time', 10.0)}")
        self.time_step_label.config(text=f"Time Step dt [s]: {self.simulation_properties.get('time_step', 0.01)}")
        self.gravity_label.config(text=f"Gravity [m/s^2]: {self.simulation_properties.get('gravity', 9.81)}")
        self.fluid_density_label.config(text=f"Fluid ρ [kg/m^3]: {self.simulation_properties.get('fluid_density', 1000.0)}")

    def create_simulation_property_labels(self):
        """Create labels to display simulation properties."""
        self.simulation_time_label = tk.Label(self.root, text=f"Simulation Time [s]: {self.simulation_properties.get('simulation_time', 10.0)}")
        self.simulation_time_label.pack(padx=10, pady=5)

        self.time_step_label = tk.Label(self.root, text=f"Time Step dt [s]: {self.simulation_properties.get('time_step', 0.01)}")
        self.time_step_label.pack(padx=10, pady=5)

        self.gravity_label = tk.Label(self.root, text=f"Gravity [m/s^2]: {self.simulation_properties.get('gravity', 9.81)}")
        self.gravity_label.pack(padx=10, pady=5)

        self.fluid_density_label = tk.Label(self.root, text=f"Fluid ρ [kg/m^3]: {self.simulation_properties.get('fluid_density', 1000.0)}")
        self.fluid_density_label.pack(padx=10, pady=5)

    def save_file(self):
        if not self.file_open:
            # If no file is open, show an error message
            self.console.log("No file is currently open. Please open a file first.", level="error")
            messagebox.showerror("No File Open", "No file is currently open. Please open a file first.")
            return

        # Collect simulation properties from UI if they are editable
        if hasattr(self, 'simulation_time_var'):
            self.simulation_properties = {
                "simulation_time": self.simulation_time_var.get(),
                "time_step": self.time_step_var.get(),
                "gravity": self.gravity_var.get(),
                "fluid_density": self.fluid_density_var.get()
            }

        if self.current_file_name:
            # Save both elements and simulation properties to the file
            data_to_save = {
                "elements": [element.to_data() for element in self.whiteboard.elements],
                "simulation_properties": self.simulation_properties,  # Save simulation properties
            }
            self.file_manager.save_elements(self.current_file_name, data_to_save)
            self.console.log(
                f"File saved successfully: {os.path.basename(self.current_file_name)}",
                level="success",
            )
        else:
            file_path = filedialog.asksaveasfilename(
                title="Save File",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
            )

            if file_path:
                self.file_manager.file_path = file_path
                self.current_file_name = file_path
                data_to_save = {
                    "elements": [element.to_data() for element in self.whiteboard.elements],
                    "simulation_properties": self.simulation_properties,  # Save simulation properties
                }
                self.file_manager.save_elements(file_path, data_to_save)
                self.console.log(
                    f"File saved successfully: {os.path.basename(file_path)}",
                    level="success",
                )
            else:
                self.console.log("No file selected for saving.", level="error")

    def terminate_file(self):
        """Terminate the current file."""
        if self.file_open:
            self.file_manager.close_file()  # Clear file-related data
            self.simulation = None
            self.file_saved = False
            self.file_open = False
            self.whiteboard.is_file_open = False  # Disable the whiteboard
            self.whiteboard.clear()  # Clear the whiteboard
            self.current_file_name = None  # Reset the current file name
            self.update_file_label()  # Update the file label
            self.console.log("File terminated successfully.",level="success")
        else:
            self.root.quit()

    def clear_screen(self):
        self.whiteboard.clear()
        # Clear the console if you want to
        #self.console.clear()

    def show_file_info(self):
        info_window = Toplevel(self.root)
        info_window.title("File Information")

        # Set size of the window
        width, height = 400, 300
        x = (info_window.winfo_screenwidth() // 2) - (width // 2)
        y = (info_window.winfo_screenheight() // 2) - (height // 2)
        info_window.geometry(f"{width}x{height}+{x}+{y}")  # Center the window on the screen
        info_window.resizable(True, True)  # Allow resizing of the window

        # Ensure the dialog is modal and focused
        info_window.transient(self.root)  # Associate with the main window
        info_window.grab_set()  # Prevent interaction with other windows until this one is closed
        info_window.focus_set()  # Automatically focus on the info window

        # Add a frame to hold the content, using grid for better control
        frame = tk.Frame(info_window, padx=10, pady=10)
        frame.grid(row=0, column=0, sticky="nsew")

        # Allow the frame to expand and fill the available space
        info_window.grid_rowconfigure(0, weight=1)
        info_window.grid_columnconfigure(0, weight=1)

        # Create a canvas for scrolling and allow it to expand
        canvas = tk.Canvas(frame)
        canvas.grid(row=0, column=0, sticky="nsew")

        # Create a vertical scrollbar and link it to the canvas
        scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Create the Text widget inside the canvas and insert the information
        text_area = Text(canvas, wrap=tk.WORD, font=("Segoe UI", 10))
        info_text = """
        ❖ Problem Statement ID : SIH1693
        ❖ Problem Statement Title: Developing a 
        Robust Hydraulic Transient Analysis Model.
        ❖ Theme : Smart Automation
        ❖ Team ID : 36652
        ❖ Team Name : AIRAVATA
        """
        text_area.insert(tk.END, info_text)
        text_area.config(state=tk.DISABLED)  # Make the text area read-only

        # Create a window on the canvas for the Text widget
        canvas.create_window((0, 0), window=text_area, anchor="nw")

        # Configure the canvas to update its scroll region with content
        canvas.config(yscrollcommand=scrollbar.set)

        # Ensure the Text widget resizes with the window (both horizontally and vertically)
        def on_resize(event):
            # Update the canvas scroll region and text widget size
            canvas.config(scrollregion=canvas.bbox("all"))
            
            # Resize the Text widget to match the canvas width
            text_area.config(width=(event.width // 6), height=(event.height // 20))  # Dynamically resize

        # Bind the resize event of the frame to adjust text widget size
        frame.bind("<Configure>", on_resize)

        # Ensure the canvas and text widget update properly for resizing
        text_area.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def set_app_icon(self):
        """Set the custom app icon at the top-left of the window."""
        try:
            app_icon = Image.open(self.get_icon_path("letter-a.png"))
            app_icon = app_icon.resize((32, 32), Image.Resampling.LANCZOS)
            self.root.iconphoto(True, ImageTk.PhotoImage(app_icon))
        except Exception as e:
            print(f"Could not set app icon: {e}")





    def export_to_excel(self):
        if self.simulation:
            data = self.simulation.method_of_characteristics()
            output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
            if output_path:
                self.file_manager.export_to_excel(data, output_path)
                self.console.log("Exported project to Excel successfully.",level="success")
        else:
            messagebox.showwarning("Warning", "No project data to export.")

    def toggle_theme(self):
        if self.current_theme == 'light':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self, show_message=True):
        """Applies the dark theme to the application."""
        self.root.config(bg="#333")
        self.console.frame.config(bg="#333")
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(fg="#f5f5f5", bg="#333")
            elif isinstance(widget, tk.Button):
                widget.config(fg="#f5f5f5", bg="#333")
        self.current_theme = 'dark'
        if show_message:
            messagebox.showinfo("Theme", "Switched to Dark mode.")


    def apply_light_theme(self):
        self.root.config(bg="#f5f5f5")
        self.console.frame.config(bg="#f5f5f5")
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(fg="#000000", bg="#f5f5f5")
            elif isinstance(widget, tk.Button):
                widget.config(fg="#000000", bg="#f5f5f5")
        self.current_theme = 'light'
        messagebox.showinfo("Theme", "Switched to Light mode.")

    def on_element_click(self, event):
        """Handles left-click events to select or highlight an element."""
        item = self.canvas.find_closest(event.x, event.y)
        item_type = self.canvas.type(item)

    def highlight_element(self, element):
        if self.highlighted_element:
            self.whiteboard.remove_highlight(self.highlighted_element)

        self.highlighted_element = element
        self.whiteboard.highlight_element(element)
        self.console.log(f"Element {element.label} highlighted.",level="info")

    def monitor_performance(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        net_info = psutil.net_io_counters()
        battery = psutil.sensors_battery()
        battery_status = "Charging" if battery and battery.power_plugged else "Not Charging"
        battery_percentage = battery.percent if battery else "N/A"
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_usage = ", ".join([f"GPU {gpu.id}: {gpu.memoryUtil * 100:.2f}% used" for gpu in gpus])
        except ImportError:
            gpu_usage = "GPU monitoring not available"
        
        processes = [(p.info['pid'], p.info['name'], p.info['cpu_percent']) for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent'])]
        processes = sorted(processes, key=lambda x: x[2], reverse=True)[:5]
        process_info = "\n".join([f"PID: {pid}, Name: {name}, CPU Usage: {cpu}%" for pid, name, cpu in processes])

        messagebox.showinfo("Performance Monitoring", 
                            f"CPU Usage: {cpu_usage}%\n"
                            f"Memory Usage: {memory_info.percent}%\n"
                            f"Disk Usage: {disk_info.percent}%\n"
                            f"Network - Sent: {net_info.bytes_sent} bytes, Received: {net_info.bytes_recv} bytes\n"
                            f"Battery Status: {battery_status} ({battery_percentage}%)\n"
                            f"GPU Usage: {gpu_usage}\n"
                            f"Top 5 Processes by CPU Usage:\n{process_info}")

        self.console.log(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_info.percent}%",level="info")



# Update the splash screen function to use relative paths as well
def show_video_splash_screen(root, on_splash_close):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "Icons", "splash_video.mp4")
    
    if not os.path.exists(video_path):
        print(f"Warning: Splash video not found at {video_path}")
        # Skip splash screen if video not found
        on_splash_close(None)
        return
    
    splash = Toplevel(root)
    splash.title("Airavata Loading")
    splash.geometry("800x600")
    splash.overrideredirect(True)
    
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    splash.geometry(f"800x600+{x}+{y}")

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get video dimensions
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate scaling factors
    splash_width = 800
    splash_height = 600

    # Calculate the scaling factor to fit the splash screen
    scale_x = splash_width / original_width
    scale_y = splash_height / original_height
    scale = max(scale_x, scale_y)

    def update_frame():
        ret, frame = cap.read()
        if ret:
            # Resize frame to fill the splash screen
            frame = cv2.resize(frame, (int(original_width * scale), int(original_height * scale)))

            # Crop the frame if it exceeds the splash screen dimensions
            height, width, _ = frame.shape
            start_x = max(0, (width - splash_width) // 2)
            start_y = max(0, (height - splash_height) // 2)
            frame = frame[start_y:start_y + splash_height, start_x:start_x + splash_width]

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame)
            frame_photo = ImageTk.PhotoImage(frame_image)
            splash_label.config(image=frame_photo)
            splash_label.image = frame_photo
            splash_label.after(10, update_frame)
        else:
            on_splash_close(splash)

    splash_label = tk.Label(splash)
    splash_label.pack(fill=tk.BOTH, expand=True)

    root.withdraw()
    update_frame()

    splash.after(5000, lambda: on_splash_close(splash))


# Show the main dashboard after the splash screen
def show_dashboard_screen(root):
    """Show the dashboard screen with proper callback to main app"""
    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create new dashboard instance with callback
    from dashboard import Dashboard
    dashboard = Dashboard(root, lambda: show_main_application(root))
    return dashboard

# Function that will be triggered when the splash screen is closed
def on_splash_close(splash):
    splash.destroy()  # Close splash screen
    root.deiconify()  # Show the main window
    root.geometry("1200x800")  # Set consistent size for dashboard
    root.state('zoomed')
    show_dashboard_screen(root)  # Show the dashboard after splash screen

# Function to show the main application when the button is clicked on the dashboard
def show_main_application(root):
    """Show the main application from dashboard"""
    # Clear the dashboard screen
    for widget in root.winfo_children():
        widget.destroy()
    
    # Set window size before creating main app
    root.geometry("1000x700")  # Match AiravataSoftware's preferred size
    root.state('zoomed')
    
    # Initialize the main application
    app = AiravataSoftware(root)
    return app

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    root.state("zoomed")
    root.withdraw()

    # Start the splash screen
    show_video_splash_screen(root, on_splash_close)
    
    root.mainloop()
