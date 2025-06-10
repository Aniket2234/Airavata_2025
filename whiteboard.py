import tkinter as tk
from tkinter import simpledialog, messagebox
from element import InletReservoir, OutletReservoir, Valve, Manifold, SurgeTank, Turbine, Pipe
from file_manager import FileManager  # Assuming this manages file open/save
import os
import json  # Add this import statement
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk 


class Whiteboard(tk.Frame):
    def __init__(self, parent, project_folder=None):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.elements = []  # List to store all created elements

        # Background image attributes
        self.background_image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/White.jpg"
        self.bg_image_id = None
        self.bg_image = None
        # Bind Control + MouseWheel for zooming
        self.canvas.bind("<Control-MouseWheel>", self.scale_elements)

        # Set the background image
        if self.background_image_path:
            self.after(100, lambda: self.set_background_image(self.background_image_path))

        # Bind resize event for background image
        self.canvas.bind("<Configure>", self.resize_background)

        # Initialize other canvas-related attributes
        self.initialize_canvas(project_folder)

    def scale_elements(self, event):
        """Scale all elements if none is selected, or only the selected element."""
        scale_factor = 1.1 if event.delta > 0 else 0.9  # Zoom in or out based on scroll direction
        
        if self.selected_element:  # If an element is selected, scale it individually
            self.selected_element.scale(scale_factor)
        else:  # If no element is selected, scale all elements
            for element in self.elements:
                element.scale(scale_factor)



    def scale(self, scale_factor):
        """Scale the element size and adjust associated ports, label, and icon while keeping the icon fixed in place."""
        
        # Get the current bounding box of the icon
        current_bbox = self.canvas.bbox(self.icon_item)
        if current_bbox:
            # Calculate new dimensions based on scale_factor
            original_width = current_bbox[2] - current_bbox[0]
            original_height = current_bbox[3] - current_bbox[1]

            # Apply scale factor to both width and height
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            # Set minimum and maximum size limits
            min_size = 20  # Minimum size for the icon (both width and height)
            max_size = 300  # Maximum size for the icon (both width and height)

            # Ensure the new size is within the bounds
            new_width = max(min_size, min(new_width, max_size))
            new_height = max(min_size, min(new_height, max_size))

            # Resize the icon image proportionally
            img = Image.open(self.icon_path)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.icon = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self.icon_item, image=self.icon)

            # Keep the icon's center position fixed, without moving it
            self.canvas.coords(self.icon_item, self.x + new_width // 2, self.y + new_height // 2)

            # Adjust the label position to stay aligned with the resized icon
            font_size = max(8, int(12 * scale_factor))  # Scale font size, with a minimum of 8
            self.canvas.itemconfig(self.label_id, font=("Arial", font_size))
            self.canvas.coords(self.label_id, self.x + new_width // 2, self.y - 10)

            # Reposition and resize the ports (buttons) to stay aligned with the icon
            port_offset = 10  # Distance from the edge of the icon
            inlet_x = self.x - port_offset
            outlet_x = self.x + new_width + port_offset
            port_y = self.y + new_height // 2

            # Dynamically scale the button size based on icon size (scaled proportionally)
            button_size = max(1, int(2 * scale_factor))  # Scale button size with a minimum of 1

            # Update the inlet port size and position
            if self.inlet_button_window:
                self.inlet_button.config(width=button_size, height=button_size)
                self.canvas.coords(self.inlet_button_window, inlet_x, port_y)

            # Update the outlet port size and position
            if self.outlet_button_window:
                self.outlet_button.config(width=button_size, height=button_size)
                self.canvas.coords(self.outlet_button_window, outlet_x, port_y)

            # Adjust highlight rectangle to scale proportionally with the element
            if self.highlight_rect:
                self.canvas.coords(
                    self.highlight_rect,
                    self.x - port_offset, self.y - port_offset,
                    self.x + new_width + port_offset, self.y + new_height + port_offset
                )


    def add_background_menu_option(self, root):
        """Add an option to the menu to set background image."""
        # Assuming there's already a menu bar, find it and add a new command
        for menu in root.winfo_children():
            if isinstance(menu, tk.Menu):
                menu.add_separator()
                menu.add_command(label="Set Background Image", command=self.choose_background_image)
                break

    def choose_background_image(self):
        """Open a file dialog to choose a background image."""
        file_path = filedialog.askopenfilename(
            title="Choose Background Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.background_image_path = file_path
                self.set_background_image(file_path)
                messagebox.showinfo("Background Image", "Background image set successfully!")
            except Exception as e:
                messagebox.showerror("Image Error", f"Failed to set background image: {e}")

    def set_background_image(self, image_path):
        """Sets the background image without hindering canvas interactions."""
        try:
            image = Image.open(image_path)

            # Resize the image to fit the canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600  # Default size

            image = image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(image)

            # Remove existing background image
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)

            # Add the background image and lower it to the background layer
            self.bg_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
            self.canvas.tag_lower(self.bg_image_id)  # Keep it at the lowest level
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load background image: {e}")

    def resize_background(self, event):
        """Updates the background image size when the canvas is resized."""
        if self.background_image_path:
            self.set_background_image(self.background_image_path)

    def initialize_canvas(self, project_folder):
        """Sets up additional canvas-related elements."""
        self.element_counts = {}
        self.deleted_elements = set()
        self.file_manager = FileManager(project_folder)
        self.current_file = None
        self.is_file_open = False
        self.elements = []
        self.selected_element = None
        self.status_label = tk.Label(self, text="No file open", bg="lightgrey", anchor="w")
        self.status_label.pack(fill=tk.X)
        self.create_context_menu()
        self.canvas.bind("<Button-3>", self.show_context_menu)  # Right-click for context menu
        self.canvas.bind("<Button-1>", self.on_click)  # Left-click for element selection

    def set_background_image(self, image_path):
        """Sets the background image on the canvas."""
        try:
            # Open and resize the image to match the canvas size
            image = Image.open(image_path)
            self.bg_image = ImageTk.PhotoImage(
                image.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), Image.Resampling.LANCZOS)
            )

            # Add the image to the canvas (send to the back)
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)
            self.bg_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
            self.canvas.lower(self.bg_image_id)  # Ensure it's at the lowest layer
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load background image: {e}")
            messagebox.showerror("Image Error", f"Failed to load background image: {e}")

    def resize_background(self, event):
        """Resizes the background image to fit the canvas when resized."""
        if self.background_image_path:
            self.set_background_image(self.background_image_path)


    def create_context_menu(self):
        """Creates the context menu for adding elements and other actions."""
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Inlet Reservoir", command=self.add_inlet_reservoir)
        self.context_menu.add_command(label="Outlet Reservoir", command=self.add_outlet_reservoir)
        self.context_menu.add_command(label="Valve", command=self.add_valve)
        self.context_menu.add_command(label="Manifold", command=self.add_manifold)
        self.context_menu.add_command(label="Surge Tank", command=self.add_surge_tank)
        self.context_menu.add_command(label="Turbine", command=self.add_turbine)
        self.context_menu.add_command(label="Pipe", command=self.add_Pipe)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Duplicate", command=self.duplicate_element)
        self.context_menu.add_command(label="Delete", command=self.delete_element)

    def show_context_menu(self, event):
        """Displays the context menu only if a file is open."""
        if not self.is_file_open:
            messagebox.showwarning("Action Denied", "Please open or create a file first.")
            return

        # Find the closest item on the canvas where the right-click occurred
        item = self.canvas.find_closest(event.x, event.y)

        # Check if the clicked item corresponds to any element
        if item:
            for element in self.elements:
                if element.icon_item == item[0]:
                    if self.selected_element:
                        self.selected_element.remove_highlight()  # Remove highlight from the previous selection
                    self.selected_element = element  # Set the clicked element as the selected element
                    element.apply_highlight()  # Apply highlight to the selected element
                    break

        # Show the context menu at the position where the right-click occurred
        self.context_menu.post(event.x_root, event.y_root)

    def add_element(self, element_class):
        """Generates a new element and adds it to the canvas."""
        if not self.is_file_open:
            messagebox.showwarning("Action Denied", "Please open or create a file first.")
            return

        # Handle Pipe creation separately to avoid duplicating ports/labels
        if element_class == Pipe:
            new_pipe = element_class(self.canvas, f"Pipe_{len(self.elements) + 1}")
            # Create only the pipe without re-creating ports and labels
            self.elements.append(new_pipe)
            return new_pipe  # Don't call create here for Pipe

        # Handle normal element creation for all other types (Inlet, Outlet, etc.)
        # Initialize the counter for the element type if it's not already
        if element_class.__name__ not in self.element_counts:
            self.element_counts[element_class.__name__] = 0

        # Handle deletion adjustments: check if there are any deleted elements
        if self.deleted_elements:
            # Find the smallest deleted number and reuse it
            available_numbers = [
                int(name.split('_')[1].split()[0]) for name in self.deleted_elements if name.startswith(element_class.__name__)
            ]
            if available_numbers:
                next_available = min(available_numbers)
                name = f"{element_class.__name__}_{next_available}"
                
                # Check if the name is in the deleted list before removing it
                if name in self.deleted_elements:
                    self.deleted_elements.remove(name)  # Remove the name from deleted set
            else:
                self.element_counts[element_class.__name__] += 1
                name = f"{element_class.__name__}_{self.element_counts[element_class.__name__]}"
        else:
            # No deleted elements, continue as normal
            self.element_counts[element_class.__name__] += 1
            name = f"{element_class.__name__}_{self.element_counts[element_class.__name__]}"

        # Create and add the new element to the canvas
        element = element_class(self.canvas, name)
        element.create()
        self.elements.append(element)
        return element



    def add_inlet_reservoir(self):
        self.add_element(InletReservoir)

    def add_Pipe(self):
        """Handles the right-click option for adding a Pipe."""
        if not self.is_file_open:
            messagebox.showwarning("Action Denied", "Please open or create a file first.")
            return
        
        # Create a new Pipe without duplicating the ports and labels
        new_pipe = self.add_element(Pipe)  # Use the modified add_element method for Pipe
        new_pipe.create()  # Only create the pipe without inlet/outlet buttons

    def add_outlet_reservoir(self):
        self.add_element(OutletReservoir)

    def add_valve(self):
        self.add_element(Valve)

    def add_manifold(self):
        self.add_element(Manifold)

    def add_surge_tank(self):
        self.add_element(SurgeTank)

    def add_turbine(self):
        self.add_element(Turbine)

    def on_click(self, event):
        """Handles left-click events to select an element."""
        if not self.is_file_open:
            return

        item = self.canvas.find_closest(event.x, event.y)
        clicked_on_element = False

        # Check if the clicked item corresponds to any element
        for element in self.elements:
            if element.icon_item == item[0]:  # Match the icon item
                clicked_on_element = True

                # Unhighlight the previously selected element
                if self.selected_element and self.selected_element != element:
                    self.selected_element.remove_highlight()

                # Highlight the new element
                self.selected_element = element
                element.apply_highlight()
                break

        # If clicked outside any element, unhighlight the currently selected element
        if not clicked_on_element and self.selected_element:
            self.selected_element.remove_highlight()
            self.selected_element = None


    def duplicate_element(self):
        """Duplicate the currently selected element along with its input values."""
        if self.selected_element:
            # Retrieve the data representation of the original element
            original_data = self.selected_element.to_data()

            # Generate a new name for the duplicate
            duplicate_name = f"{original_data['name']} (copy)"
            original_data["name"] = duplicate_name

            # Offset the position to avoid overlap
            original_data["x"] += 20
            original_data["y"] += 20

            # Get the class of the original element
            element_class = type(self.selected_element)

            # Create a new instance using the updated data
            duplicate = element_class(self.canvas, duplicate_name)
            duplicate.load_from_data(original_data)
            duplicate.create()

            # Add the duplicate to the elements list
            self.elements.append(duplicate)

            # Optionally, set the duplicate as the currently selected element
            self.selected_element = duplicate



    def delete_element(self):
        """Deletes the selected element from the canvas."""
        if self.selected_element:
            # Track the name of the element before deletion
            element_name = self.selected_element.name
            if element_name:
                # Add the element name to the deleted set (so it can be reused later)
                self.deleted_elements.add(element_name)

            # Proceed with the actual deletion
            items_to_delete = [
                self.selected_element.icon_item,
                self.selected_element.label_id,
                self.selected_element.inlet_button_window,
                self.selected_element.outlet_button_window,
                self.selected_element.rect_item,
                self.selected_element.highlight_rect,
            ]
            for item in items_to_delete:
                if item:
                    self.canvas.delete(item)

            self.elements.remove(self.selected_element)
            self.selected_element = None


    def clear(self):
        """Clears all elements from the whiteboard."""
        for element in self.elements[:]:
            self.selected_element = element
            self.delete_element()
        self.elements.clear()
        self.selected_element = None


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
            
            # Clear existing elements before loading new ones
            self.whiteboard.clear()

            # Load elements into the canvas
            self.whiteboard.load_elements(elements_data['elements'])

            # Update file state
            self.current_file_name = file_path
            self.file_open = True  # Set the file open flag
            self.whiteboard.is_file_open = True  # Enable the whiteboard
            self.file_manager.file_path = file_path  # Update the file manager
            self.update_file_label()  # Update the file label
            self.console.log(f"Successfully loaded file: {os.path.basename(file_path)}",level="success")

            messagebox.showinfo("File Loaded", f"Successfully loaded file: {os.path.basename(file_path)}")

        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("File Error", f"Failed to load the file. Error: {e}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")


    def save_file(self):
        if self.current_file_name:
            self.file_manager.save_elements(
                self.current_file_name,
                [element.to_data() for element in self.whiteboard.elements]
            )
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
                self.file_manager.save_elements(
                    file_path, [element.to_data() for element in self.whiteboard.elements]
                )
                self.console.log(
                    f"File saved successfully: {os.path.basename(file_path)}",
                    level="success",
                )
            else:
                self.console.log("No file selected for saving.", level="error")




    def terminate_file(self):
        """Terminates the current file and clears the whiteboard."""
        if not self.is_file_open:
            messagebox.showwarning("Terminate Error", "No file is currently open.")
            return

        self.is_file_open = False
        self.current_file = None
        self.status_label.config(text="No file open")
        self.clear()

    def create_new_file(self):
        """Creates a new file, resets the current file state, and clears the whiteboard."""
        self.current_file = None  # Reset the current file state
        self.is_file_open = False
        self.status_label.config(text="No file open")  # Update the status
        self.clear()  # Clear the current whiteboard

    def load_elements(self, elements_data=None):
        """Load elements either from a file or directly passed data."""
        if elements_data is None:
            if not os.path.exists(self.file_path):
                print(f"Error: File does not exist: {self.file_path}")
                return

            with open(self.file_path, 'r') as file:
                try:
                    elements_data = json.load(file)
                except json.JSONDecodeError:
                    print("Error: The file content is not valid JSON.")
                    return

        if isinstance(elements_data, dict) and "elements" in elements_data:
            elements_data = elements_data["elements"]

        for element_data in elements_data:
            try:
                element_class = globals()[element_data["class"]]
                element = element_class(self.canvas, element_data["name"])
                element.load_from_data(element_data)
                element.create()
                self.elements.append(element)

            except Exception as e:
                print(f"Error loading element: {e}")

    def save_elements(self, file_path, elements_data):
        """Save elements to a serialized file (e.g., JSON format)."""
        try:
            # Ensure the data is in the correct format
            data_to_save = {"elements": elements_data}  # Wrap the data in the 'elements' key
            
            with open(file_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)  # Save the elements data in the correct format
            
            print(f"Data successfully saved to {file_path}")
        except TypeError:
            print("Error: The elements data is not serializable.")


    def on_inlet_click(self):
        print(f"Inlet button clicked for {self.label}")

    def on_outlet_click(self):
        print(f"Outlet button clicked for {self.label}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hydraulic Transient Simulation")
    project_folder = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata"  # Define your project folder here
    whiteboard = Whiteboard(root, project_folder)
    whiteboard.pack(fill=tk.BOTH, expand=True)

    # Adding file menu
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open File", command=whiteboard.open_file)
    file_menu.add_command(label="Save File", command=whiteboard.save_file)
    file_menu.add_command(label="Terminate File", command=whiteboard.terminate_file)
    file_menu.add_command(label="New File", command=whiteboard.create_new_file)
    menu_bar.add_cascade(label="File", menu=file_menu)

    root.config(menu=menu_bar)
    root.mainloop()
