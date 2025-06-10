import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # To load and resize images for icons
import os
import json  # Add this import statement
from tkinter import messagebox
import tkinter.filedialog as filedialog
# other imports...

class Element:
    def __init__(self, canvas, name, icon_path):
        self.canvas = canvas
        self.name = name
        self.x = 90  # Default X position
        self.y = 70  # Default Y position
        self.label = name  # Set the name as label
        self.icon_path = icon_path  # Path to the element's icon
        self.icon = None
        self.inlet_button = None
        self.outlet_button = None
        self.inlet_button_window = None
        self.outlet_button_window = None
        self.label_id = None
        self.selected = False  # Track if the element is selected for dragging
        self.rect_item = None  # Initialize rect_item for rectangle
        self.icon_item = None  # Icon item for the canvas
        self.highlight_rect = None  # Highlight rectangle

        # Store original size when the element is created
        self.original_width = 90  # Default original width
        self.original_height = 70  # Default original height
        self.original_button_size = 2  # Default button size (inlet/outlet buttons)
        self.original_font_size = 12  # Default label font size

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
            font_size = max(12, int(self.original_font_size * scale_factor))  # Scale font size, with a minimum of 8
            self.canvas.itemconfig(self.label_id, font=("Arial", font_size))
            self.canvas.coords(self.label_id, self.x + new_width // 2, self.y - 10)

            # Reposition and resize the ports (buttons) to stay aligned with the icon
            port_offset = 10  # Distance from the edge of the icon
            inlet_x = self.x - port_offset
            outlet_x = self.x + new_width + port_offset
            port_y = self.y + new_height // 2

            # Dynamically scale the button size based on icon size (scaled proportionally)
            button_size = max(1, int(self.original_button_size * scale_factor))  # Scale button size with a minimum of 1

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

    def create(self): 
        """Create the element on the canvas.""" 
        # Load and resize the icon 
        icon_width, icon_height = self.original_width, self.original_height  # Use original size here
        img = Image.open(self.icon_path) 
        img = img.resize((icon_width, icon_height), Image.LANCZOS)  # Resize the icon to fit the element 
        self.icon = ImageTk.PhotoImage(img) 

        # Create the element icon on the canvas 
        self.icon_item = self.canvas.create_image(self.x + icon_width // 2, self.y + icon_height // 2, image=self.icon) 
        self.label_id = self.canvas.create_text(self.x + icon_width // 2, self.y - 10, text=self.label, fill="black") 

        # Create inlet and outlet buttons
        button_size = self.original_button_size  # Use the original button size
        self.inlet_button = tk.Button(self.canvas, width=button_size, height=button_size, bg="green", text="I", command=self.on_inlet_click)
        self.inlet_button_window = self.canvas.create_window(self.x - 10, self.y + icon_height // 2, window=self.inlet_button)

        self.outlet_button = tk.Button(self.canvas, width=button_size, height=button_size, bg="red", text="O", command=self.on_outlet_click)
        self.outlet_button_window = self.canvas.create_window(self.x + icon_width + 10, self.y + icon_height // 2, window=self.outlet_button) 

        # Create a rectangle to highlight the element on click, properly aligned around the icon 
        self.rect_item = self.canvas.create_rectangle( 
            self.x, self.y, self.x + 60, self.y + 40, outline="blue", width=2, state="hidden" 
        ) 

        # Bind mouse events for interaction 
        self.canvas.tag_bind(self.icon_item, "<Button-1>", self.on_click) 
        self.canvas.tag_bind(self.icon_item, "<Double-1>", self.on_double_click) 
        self.canvas.tag_bind(self.icon_item, "<B1-Motion>", self.on_drag_motion)  # Bind drag motion 
        self.canvas.tag_bind(self.icon_item, "<ButtonRelease-1>", self.on_drag_release)  # Release drag

    def reset_size(self):
        """Reset the element size, label, and ports to their original size."""
        # Reset icon size using the original dimensions
        img = Image.open(self.icon_path)
        img = img.resize((self.original_width, self.original_height), Image.Resampling.LANCZOS)
        self.icon = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.icon_item, image=self.icon)

        # Reset the position of the icon (keep it centered at the same place)
        self.canvas.coords(self.icon_item, self.x + self.original_width // 2, self.y + self.original_height // 2)

        # Reset label size (scale the font size back to normal)
        self.canvas.itemconfig(self.label_id, font=("Arial", self.original_font_size))  # Reset to original font size
        self.canvas.coords(self.label_id, self.x + self.original_width // 2, self.y - 10)

        # Reset the ports (buttons) size and position
        port_offset = 10  # Distance from the edge of the icon
        inlet_x = self.x - port_offset
        outlet_x = self.x + self.original_width + port_offset
        port_y = self.y + self.original_height // 2

        # Set the button size to the original value
        button_size = self.original_button_size  # Use original button size

        if self.inlet_button_window:
            self.inlet_button.config(width=button_size, height=button_size)
            self.canvas.coords(self.inlet_button_window, inlet_x, port_y)

        if self.outlet_button_window:
            self.outlet_button.config(width=button_size, height=button_size)
            self.canvas.coords(self.outlet_button_window, outlet_x, port_y)

        # Adjust the highlight rectangle to the original size
        if self.highlight_rect:
            self.canvas.coords(
                self.highlight_rect,
                self.x - port_offset, self.y - port_offset,
                self.x + self.original_width + port_offset, self.y + self.original_height + port_offset
            )


    def to_data(self):
        """Returns the element's data as a dictionary for saving."""
        return {
            "class": "Element:",
            "name": self.name,
            "x": self.x,
            "y": self.y
        }

    def load_from_data(self, data):
        """Loads data from a dictionary for initializing the element."""
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        # Implement the logic to re-create the element on the canvas

        # Bind canvas click event to remove highlight when clicking outside
        self.canvas.bind("<Button-1>", self.on_canvas_click)


    def on_inlet_click(self):
        """Handle inlet button click."""
        whiteboard = self.canvas.master  # Reference to Whiteboard
        if hasattr(whiteboard, 'selected_outlet_element') and whiteboard.selected_outlet_element:
            # Create a Pipe linking the selected outlet to this inlet
            outlet_element = whiteboard.selected_outlet_element
            inlet_element = self

            # Reset the selection after creating the pipe
            whiteboard.selected_outlet_element = None

            # Create and position the pipe
            pipe = Pipe(self.canvas, name=f"Pipe_{outlet_element.name}_to_{inlet_element.name}")
            pipe.x = (outlet_element.x + inlet_element.x) // 2
            pipe.y = (outlet_element.y + inlet_element.y) // 2
            pipe.inlet_element = inlet_element.name
            pipe.outlet_element = outlet_element.name

            # Add the pipe to the canvas
            pipe.create()

            # Track the pipe as part of the elements
            whiteboard.elements.append(pipe)

            print(f"Pipe created between {outlet_element.name} and {inlet_element.name}")
        else:
            print("No outlet element selected for linking.")
       

    def on_outlet_click(self):
        """Handle outlet button click."""
        whiteboard = self.canvas.master  # Reference to Whiteboard
        whiteboard.selected_outlet_element = self
        print(f"Outlet clicked: {self.name}")

    def apply_highlight(self):
        """Visually highlight the element."""
        if not self.highlight_rect:
            self.highlight_rect = self.canvas.create_rectangle(
                self.x - 10, self.y - 10,
                self.x + 100, self.y + 100,
                outline="blue", width=2
            )
        self.canvas.itemconfig(self.highlight_rect, state="normal")

    def remove_highlight(self):
        """Remove the visual highlight from the element."""
        if self.highlight_rect:
            self.canvas.itemconfig(self.highlight_rect, state="hidden")


    def on_click(self, event):
        """Highlight the rectangle when the icon is clicked."""
        # Initialize highlighted_element if it doesn't exist
        if not hasattr(self.canvas, 'highlighted_element'):
            self.canvas.highlighted_element = None

        # If this element is already highlighted, do nothing
        if self.canvas.highlighted_element == self:
            return

        # Remove highlight from previously selected element (if any)
        if self.canvas.highlighted_element:
            self.canvas.highlighted_element.remove_highlight()

        # Set the current element as the highlighted one
        self.canvas.highlighted_element = self

        # Create a highlight rectangle if not already created
        if not self.highlight_rect:
            self.highlight_rect = self.canvas.create_rectangle(
                self.x - 15, self.y - 40, self.x + 100, self.y + 80, outline="blue", width=2
            )

        # Show rectangle on click and highlight it
        self.canvas.itemconfig(self.highlight_rect, state="normal")  # Show the highlight rectangle


    def on_drag_motion(self, event):
        """Handle dragging motion of the element."""
        dx = event.x - self.x - 30  # Calculate the offset for movement
        dy = event.y - self.y - 20

        # Move the icon
        self.canvas.move(self.icon_item, dx, dy)
        self.canvas.move(self.label_id, dx, dy)
        self.canvas.move(self.inlet_button_window, dx, dy)
        self.canvas.move(self.outlet_button_window, dx, dy)
        self.canvas.move(self.rect_item, dx, dy)  # Move the rectangle along with the icon

        # Update the position of the element
        self.x = event.x - 30
        self.y = event.y - 20

        # Move the highlight rectangle to the new position as well
        if self.highlight_rect:
            self.canvas.coords(
                self.highlight_rect,
                self.x - 15,  # Ensure the highlight rectangle updates relative to the new position
                self.y - 40,
                self.x + 100,
                self.y + 80
            )


    def on_drag_release(self, event):
        """Handle drag release."""
        # Once drag is released, update the element's position
        self.x = event.x - 30
        self.y = event.y - 20

    def on_double_click(self, event):
        """Handle double-click events (open properties dialog)."""
        print(f"Double-clicked: {self.label}")
        self.open_properties_dialog()

    def open_properties_dialog(self):
        """Open a dialog to edit properties of the element."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")

        # Header
        tk.Label(dialog, text=f"Edit properties of {self.label}").pack()

        # Dictionary to store user input fields
        user_inputs = {}

        # Define element-specific properties dynamically
        element_properties = {
            "InletReservoir": ["flow_rate", "temperature"],
            "Pipe": ["inlet_port", "outlet_port"],
            "Valve": ["pressure", "diameter"],
            "Turbine": ["flow_rate", "efficiency"],
            "SurgeTank": ["capacity"],
            # Add properties for other elements as needed
        }

        # Get the properties for the current element class
        class_name = self.__class__.__name__
        if class_name in element_properties:
            for prop in element_properties[class_name]:
                current_value = getattr(self, prop, "")  # Get current value or default to ""
                user_inputs[prop] = self.add_property_field(dialog, prop.replace("_", " ").capitalize(), current_value)

        # Save button functionality
        def save_properties():
            for prop, entry in user_inputs.items():
                new_value = entry.get()  # Get the value from the entry field
                setattr(self, prop, new_value)  # Update the element's attribute dynamically
            dialog.destroy()  # Close the dialog

        # Add Save and Cancel buttons
        tk.Button(dialog, text="Save", command=save_properties).pack()
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

    def add_property_field(self, parent, label_text, value):
        """Add a label and entry field for a property."""
        tk.Label(parent, text=label_text).pack()
        entry = tk.Entry(parent)
        entry.insert(0, value)  # Prepopulate with the current value
        entry.pack()
        return entry

    def remove_highlight(self):
        """Remove the highlight from the selected item."""
        if self.highlight_rect:
            self.canvas.delete(self.highlight_rect)
            self.highlight_rect = None  # Clear the highlight rectangle

    def remove_highlight_on_outside_click(self, event):
        """Remove highlight if click is outside of any element."""
        if hasattr(self.canvas, 'highlighted_element') and self.canvas.highlighted_element:
            bbox = self.canvas.bbox(self.canvas.highlighted_element.highlight_rect)
            if not bbox or not (bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]):
                self.canvas.highlighted_element.remove_highlight()
                del self.canvas.highlighted_element  # Clear the reference

    def on_canvas_click(self, event):
        """Remove highlight from the selected element when clicking outside."""
        self.remove_highlight_on_outside_click(event)


# Global variable to store the selected element
selected_element = None

class InletReservoir(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/inlet_reservoir_icon.png")
        self.level_h = ""  # Default value for Level H
        self.pipe_z = ""  # Default value for Pipe Z
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/inlet_reservoir_image.png"  # Path to display image in the dialog
        
    def to_data(self):
        return {
            "class": "InletReservoir",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "level_h": self.level_h,
            "pipe_z": self.pipe_z,
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.level_h = data.get("level_h", "")
        self.pipe_z = data.get("pipe_z", "")

    def validate_input(self, input_value):
        """Validate that the input is a number or a float."""
        if input_value == "":
            return True  # Allow empty input
        try:
            float(input_value)  # Try converting to float
            return True
        except ValueError:
            return False

    def open_properties_dialog(self):
        """Open a beautiful, centered dialog to edit properties dynamically."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with the main window
        dialog.grab_set()  # Prevent interaction with other windows until this one is closed
        dialog.focus_set()  # Automatically focus on the dialog

        # Set size and center the dialog
        width, height = 400, 400
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)  # Disable resizing

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Add padding and a header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((200, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include in the dialog
        properties = {
            "Level H [m asl]": "level_h",
            "Pipe Z [m asl]": "pipe_z",
        }

        # Container for inputs
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            
            # Create a validation command
            validate_cmd = dialog.register(self.validate_input)
            entry = tk.Entry(field_frame, font=label_font, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons frame
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)

        # Create custom Save and Cancel buttons
        save_button = tk.Button(button_frame, text="Save", font=button_font, bg='#32CD32', width=10, height=1, command=lambda: self.save_properties(user_inputs, dialog))
        cancel_button = tk.Button(button_frame, text="Cancel", font=button_font, bg='#FF4040', width=10, height=1, command=dialog.destroy)

        # Pack the buttons with padding
        save_button.pack(side=tk.LEFT, padx=20)
        cancel_button.pack(side=tk.RIGHT, padx=20)

    def save_properties(self, user_inputs, dialog):
        """Save the properties and close the dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()


class Pipe(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/pipe_icon.png")
        self.diameter = ""  # Diameter D [m]
        self.length = ""    # Length L [m]
        self.celerity = ""  # Celerity a [m/s]
        self.manning_n = "" # Manning n [...]
        self.inlet_h1 = ""  # Inlet H1 [m]
        self.inlet_q1 = ""  # Inlet Q1 [m³/s]
        self.nodes_n = ""   # Nodes N [-]
        self.dt_max = "0.0" # dt max [s], constant value
        self.inlet_element = ""  # Selected inlet element
        self.outlet_element = "" # Selected outlet element
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/Pipe_image.png"

    def to_data(self):
        """Convert pipe attributes to a dictionary for saving."""
        return {
            "class": "Pipe",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "diameter": self.diameter,
            "length": self.length,
            "celerity": self.celerity,
            "manning_n": self.manning_n,
            "inlet_h1": self.inlet_h1,
            "inlet_q1": self.inlet_q1,
            "nodes_n": self.nodes_n,
            "dt_max": self.dt_max,
            "inlet_element": self.inlet_element,
            "outlet_element": self.outlet_element,
        }

    def load_from_data(self, data):
        """Load pipe attributes from a dictionary."""
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.diameter = data.get("diameter", "")
        self.length = data.get("length", "")
        self.celerity = data.get("celerity", "")
        self.manning_n = data.get("manning_n", "")
        self.inlet_h1 = data.get("inlet_h1", "")
        self.inlet_q1 = data.get("inlet_q1", "")
        self.nodes_n = data.get("nodes_n", "")
        self.dt_max = data.get("dt_max", "0.0")
        self.inlet_element = data.get("inlet_element", "")
        self.outlet_element = data.get("outlet_element", "")

    def validate_input(self, input_value):
        """Validate that the input is a number or a float."""
        if input_value == "":
            return True  # Allow empty input
        try:
            float(input_value)  # Try converting to float
            return True
        except ValueError:
            return False

    def open_properties_dialog(self):
        """Open a dialog for editing Pipe properties."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with main window
        dialog.grab_set()  # Prevent interaction with other windows
        dialog.focus_set()

        # Center dialog on the screen
        width, height = 550, 700
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)

        # Display image
        img = Image.open(self.image_path)
        img = img.resize((300, 250), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(dialog, image=img_tk)
        img_label.image = img_tk
        img_label.pack()

        # Input fields for basic properties
        properties = {
            "Diameter D [m]": "diameter",
            "Length L [m]": "length",
            "Celerity a [m/s]": "celerity",
            "Manning n [...]": "manning_n",
            "Inlet H1 [m]": "inlet_h1",
            "Inlet Q1 [m³/s]": "inlet_q1",
            "Nodes N [-]": "nodes_n",
            "dt max <= [s]": "dt_max",
        }

        user_inputs = {}
        for label, attr in properties.items():
            field_frame = tk.Frame(dialog)
            field_frame.pack(fill=tk.X, pady=5)
            tk.Label(field_frame, text=label, font=label_font).pack(side=tk.LEFT)
            validate_cmd = dialog.register(self.validate_input)
            entry = tk.Entry(field_frame, font=label_font, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attr, ""))
            entry.pack(side=tk.RIGHT)
            user_inputs[attr] = entry

        # Dropdowns for Inlet and Outlet
        dropdown_frame = tk.Frame(dialog)
        dropdown_frame.pack(fill=tk.X, pady=10)

        tk.Label(dropdown_frame, text="Select Inlet:", font=label_font).pack(side=tk.LEFT)
        inlet_var = tk.StringVar(value=self.inlet_element)
        inlet_dropdown = ttk.Combobox(dropdown_frame, textvariable=inlet_var)
        inlet_dropdown.pack(side=tk.LEFT, padx=10)

        tk.Label(dropdown_frame, text="Select Outlet:", font=label_font).pack(side=tk.LEFT)
        outlet_var = tk.StringVar(value=self.outlet_element)
        outlet_dropdown = ttk.Combobox(dropdown_frame, textvariable=outlet_var)
        outlet_dropdown.pack(side=tk.LEFT, padx=10)

        # Populate dropdowns with available elements
        elements_on_canvas = [elem.name for elem in self.canvas.master.elements if elem != self]
        inlet_dropdown['values'] = elements_on_canvas
        outlet_dropdown['values'] = elements_on_canvas

        # Bottom buttons frame
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)

        save_button = tk.Button(button_frame, text="Save", font=label_font, bg='#32CD32', width=10, height=1, 
                                command=lambda: self.save_properties(user_inputs, inlet_var.get(), outlet_var.get(), dialog))
        cancel_button = tk.Button(button_frame, text="Cancel", font=label_font, bg='#FF4040', width=10, height=1, command=dialog.destroy)

        save_button.pack(side=tk.LEFT, padx=20)
        cancel_button.pack(side=tk.RIGHT, padx=20)

    def save_properties(self, user_inputs, inlet, outlet, dialog):
        """Save the properties and close the dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())

        # Save selected inlet and outlet
        self.inlet_element = inlet
        self.outlet_element = outlet

        dialog.destroy()


class OutletReservoir(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/outlet_reservoir_icon.png")
        self.level_h = ""  # Default value for Level H
        self.level_z = ""  # Default value for Level Z
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/inlet_outletReservior_image.png"  # Path to display image in the dialog

    def to_data(self):
        return {
            "class": "OutletReservoir",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "level_h": self.level_h,
            "level_z": self.level_z,
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.level_h = data.get("level_h", "")
        self.level_z = data.get("level_z", "")

    def validate_input(self, input_value):
        """Validate that the input is a number or a float."""
        if input_value == "":
            return True  # Allow empty input
        try:
            float(input_value)  # Try converting to float
            return True
        except ValueError:
            return False
        
    def open_properties_dialog(self):
        """Open a beautiful, centered dialog to edit properties dynamically."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with the main window
        dialog.grab_set()  # Prevent interaction with other windows until this one is closed
        dialog.focus_set()  # Automatically focus on the dialog

        # Set size and center the dialog
        width, height = 400, 400
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)  # Disable resizing

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Add padding and a header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((200, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include in the dialog
        properties = {
            "Level H [m asl]": "level_h",
            "Level Z [m asl]": "level_z",
        }

        # Container for inputs
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            validate_cmd = dialog.register(self.validate_input)
            entry = tk.Entry(field_frame, font=label_font, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons frame
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)

        # Create custom Save and Cancel buttons
        save_button = tk.Button(button_frame, text="Save", font=button_font, bg='#32CD32', width=10, height=1, command=lambda: self.save_properties(user_inputs, dialog))
        cancel_button = tk.Button(button_frame, text="Cancel", font=button_font, bg='#FF4040', width=10, height=1, command=dialog.destroy)

        # Pack the buttons with padding
        save_button.pack(side=tk.LEFT, padx=20)
        cancel_button.pack(side=tk.RIGHT, padx=20)


    def save_properties(self, user_inputs, dialog):
        """Save the properties and close the dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()


class Valve(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/valve_icon.png")
        self.diameter = "0.0"  # Default value for Diameter (D)
        self.loss_coefficient = "0.0"  # Default value for Loss Coefficient (Kv)
        self.loss_factor = "0.0"  # Default value for Loss Factor (n)
        self.elevation_z = "0.0"  # Default value for Elevation Z
        self.O_C = "0.0"
        self.P_drop = "0.0"

        self.custom_values = []  # Holds the 2-column sheet values
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/valve_image.png"  # Path to the provided image

    def to_data(self):
        return {
            "class": "Valve",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "diameter": self.diameter,
            "loss_coefficient": self.loss_coefficient,
            "loss_factor": self.loss_factor,
            "elevation_z": self.elevation_z,
            "custom_values": self.custom_values,  # Save sheet data
            "O_C": self.O_C,
            "P_drop":self.P_drop
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.diameter = data.get("diameter", "0.0")
        self.loss_coefficient = data.get("loss_coefficient", "0.0")
        self.loss_factor = data.get("loss_factor", "0.0")
        self.elevation_z = data.get("elevation_z", "0.0")
        self.custom_values = data.get("custom_values", [])
        self.O_C = data.get("O_C","0.0")
        self.P_drop = data.get("P_drop","0.0")

    def validate_input(self, input_value):
        """Validate that the input is a number or a float."""
        if input_value == "":
            return True  # Allow empty input
        try:
            float(input_value)  # Try converting to float
            return True
        except ValueError:
            return False

    def open_properties_dialog(self):
        """Open a dynamic properties dialog for the Valve."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())
        dialog.grab_set()
        dialog.focus_set()

        # Set size and center the dialog
        width, height = 700, 600
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Main frame for layout
        main_frame = tk.Frame(dialog, bg="#ffffff")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Image and input fields
        left_frame = tk.Frame(main_frame, bg="#ffffff", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header
        header_label = tk.Label(left_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0", anchor="w")
        header_label.pack(fill=tk.X, pady=(0, 10))

        # Display the image
        img = Image.open(self.image_path)
        img = img.resize((250, 200), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(left_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack(pady=(0, 10))

        # Properties to include in the dialog
        properties = {
            "Diameter D [m]": "diameter",
            "Loss Coefficient Kv": "loss_coefficient",
            "Loss Factor n": "loss_factor",
            "Elevation Z [m asl]": "elevation_z",
            "Opening/closing Time(In Sec)":"O_C",
            "Pressure drop":"P_drop"
        }

        # Container for input fields
        inputs_frame = tk.Frame(left_frame, pady=10, padx=10, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            validate_cmd = dialog.register(self.validate_input)
            entry = tk.Entry(field_frame, font=label_font, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Right side: Two-column sheet
        right_frame = tk.Frame(main_frame, bg="#f0f0f0", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a label for the sheet
        sheet_label = tk.Label(right_frame, text="t [s] vs y [-]", font=header_font, bg="#f0f0f0")
        sheet_label.pack(pady=(0, 10))

        # Sheet frame with colored background
        sheet_frame = tk.Frame(right_frame, bg="#d4f1f9", padx=5, pady=5, relief=tk.RIDGE, bd=2)
        sheet_frame.pack(fill=tk.BOTH, expand=True)

        # Table header
        tk.Label(sheet_frame, text="t [s]", font=label_font, bg="#9ae3ff").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Label(sheet_frame, text="y [-]", font=label_font, bg="#9ae3ff").grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Create sheet entries
        sheet_entries = []

        def validate_input(action, value):
            if action == "1":  # Indicates an insertion
                if value in ("", "-"):  # Allow empty string or initial negative sign
                    return True
                try:
                    float(value)  # Check if the input can be cast to a float
                    return True
                except ValueError:
                    return False
            return True

        vcmd = sheet_frame.register(validate_input)  # Register the validation function

        for i in range(16):  # 16 rows
            t_entry = tk.Entry(
                sheet_frame,
                font=label_font,
                width=10,
                bg="#ffffff",
                justify="center",
                validate="key",
                validatecommand=(vcmd, "%d", "%P"),  # Pass action and new value to validation function
            )
            t_entry.grid(row=i + 1, column=0, padx=5, pady=2, sticky="ew")

            y_entry = tk.Entry(
                sheet_frame,
                font=label_font,
                width=10,
                bg="#ffffff",
                justify="center",
                validate="key",
                validatecommand=(vcmd, "%d", "%P"),  # Pass action and new value to validation function
            )
            y_entry.grid(row=i + 1, column=1, padx=5, pady=2, sticky="ew")

            # Pre-fill values if available
            if i < len(self.custom_values):
                t_entry.insert(0, self.custom_values[i][0])
                y_entry.insert(0, self.custom_values[i][1])

            sheet_entries.append((t_entry, y_entry))


        # Buttons frame
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)

        # Create custom Save and Cancel buttons
        save_button = tk.Button(button_frame, text="Save", font=button_font, bg='#32CD32', width=10, height=1, command=lambda: self.save_properties(user_inputs,sheet_entries, dialog))
        cancel_button = tk.Button(button_frame, text="Cancel", font=button_font, bg='#FF4040', width=10, height=1, command=dialog.destroy)

        # Pack the buttons with padding
        save_button.pack(side=tk.LEFT, padx=20)
        cancel_button.pack(side=tk.RIGHT, padx=20)



    def save_properties(self, user_inputs, sheet_entries, dialog):
        """Save the properties and the sheet values, then close the dialog."""
        # Save the main properties with validation
        for attribute, entry in user_inputs.items():
            value = entry.get()
            if attribute in ["diameter", "loss_coefficient", "loss_factor", "elevation_z"]:
                try:
                    # Ensure numerical fields are valid
                    float(value)
                except ValueError:
                    messagebox.showerror("Invalid Input", f"Please enter a valid number for {attribute.replace('_', ' ').capitalize()}.")
                    return
            setattr(self, attribute, value)

        # Save the sheet values
        self.custom_values = []
        for t_entry, y_entry in sheet_entries:
            t_value = t_entry.get().strip()
            y_value = y_entry.get().strip()
            if t_value or y_value:  # Save only non-empty rows
                self.custom_values.append((t_value, y_value))

        dialog.destroy()


class Manifold(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/manifold_icon.png")
        self.elev_z = ""  # Default value for Elev. Z
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/Manifold_image.png"  # Path to display image in the dialog
        self.No_of_sub_pipes = ""
        self.D_of_Subpipe = ""


    def to_data(self):
        return {
            "class": "Manifold",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "elev_z": self.elev_z,
            "No_of_sub_pipes":self.No_of_sub_pipes,
            "D_of_Subpipe":self.D_of_Subpipe
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.elev_z = data.get("elev_z", "")
        self.No_of_sub_pipes
        self.D_of_Subpipe

    def validate_input(self, input_value):
        """Validate that the input is a number or a float."""
        if input_value == "":
            return True  # Allow empty input
        try:
            float(input_value)  # Try converting to float
            return True
        except ValueError:
            return False

    def open_properties_dialog(self):
        """Open a dialog to edit properties dynamically."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())  # Associate with the main window
        dialog.grab_set()  # Prevent interaction with other windows until this one is closed
        dialog.focus_set()  # Automatically focus on the dialog

        # Set size and center the dialog
        width, height = 600, 450
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)  # Disable resizing

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Add padding and a header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((200, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include in the dialog
        properties = {
            "Elev. Z [m asl]": "elev_z",
            "No of Distributed Pipe":"No_of_sub_pipes",
            "D of Each pipe":"D_of_Subpipe"
        }

        # Container for inputs
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            validate_cmd = dialog.register(self.validate_input)
            entry = tk.Entry(field_frame, font=label_font, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons frame
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)

        # Create custom Save and Cancel buttons
        save_button = tk.Button(button_frame, text="Save", font=button_font, bg='#32CD32', width=10, height=1, command=lambda: self.save_properties(user_inputs, dialog))
        cancel_button = tk.Button(button_frame, text="Cancel", font=button_font, bg='#FF4040', width=10, height=1, command=dialog.destroy)

        # Pack the buttons with padding
        save_button.pack(side=tk.LEFT, padx=20)
        cancel_button.pack(side=tk.RIGHT, padx=20)


    def save_properties(self, user_inputs, dialog):
        """Save the properties and close the dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()


class SurgeTank(Element):
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/surge_tank_icon.png")
        self.throttle_ao = ""  # Throttle Ao [m2]
        self.stank_a = ""      # S-tank A [m2]
        self.throttle_kin = ""  # Throttle Kin
        self.throttle_kout = ""  # Throttle Kout
        self.throttle_el_zo = ""  # Throttle el. Zo [m3/s]
        self.D_ST = ""
        self.C_W_L= ""
        self.image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/surge_tank_image.png"  # Image to display in dialog

    def to_data(self):
        return {
            "class": "SurgeTank",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "throttle_ao": self.throttle_ao,
            "stank_a": self.stank_a,
            "throttle_kin": self.throttle_kin,
            "throttle_kout": self.throttle_kout,
            "throttle_el_zo": self.throttle_el_zo,
            "Diameter_surge_tank": self.D_ST,
            "Current_Water_level": self.C_W_L
        }

    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        self.throttle_ao = data.get("throttle_ao", "")
        self.stank_a = data.get("stank_a", "")
        self.throttle_kin = data.get("throttle_kin", "")
        self.throttle_kout = data.get("throttle_kout", "")
        self.throttle_el_zo = data.get("throttle_el_zo", "")
        self.D_ST= data.get("D_ST","")
        self.C_W_L = data.get("C_W_L","")

    def validate_input(self, input_value):
        """Validate that the input is a number or a float."""
        if input_value == "":
            return True  # Allow empty input
        try:
            float(input_value)  # Try converting to float
            return True
        except ValueError:
            return False

    def open_properties_dialog(self):
        """Open a centered dialog to edit SurgeTank properties."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())
        dialog.grab_set()
        dialog.focus_set()

        # Set size and center the dialog
        width, height = 500, 650
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        # Style settings
        header_font = ("Helvetica", 14, "bold")
        label_font = ("Helvetica", 12)
        button_font = ("Helvetica", 10)

        # Header
        header_frame = tk.Frame(dialog, bg="#f0f0f0", pady=10)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text=f"Properties of {self.label}", font=header_font, bg="#f0f0f0")
        header_label.pack()

        # Display image
        image_frame = tk.Frame(dialog, pady=10, bg="#ffffff")
        image_frame.pack()
        img = Image.open(self.image_path)
        img = img.resize((250, 250), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_frame, image=img_tk, bg="#ffffff")
        img_label.image = img_tk
        img_label.pack()

        # Properties to include
        properties = {
            "Throttle Ao [m2]": "throttle_ao",
            "S-tank A [m2]": "stank_a",
            "Throttle Kin": "throttle_kin",
            "Throttle Kout": "throttle_kout",
            "Throttle el. Zo [m3/s]": "throttle_el_zo",
            "Diameter_surge_tank":"D_ST",
            "Current_Water_level":"C_W_L"
        }

        # Inputs frame
        inputs_frame = tk.Frame(dialog, pady=10, padx=20, bg="#ffffff")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        user_inputs = {}

        # Generate input fields dynamically
        for label, attribute in properties.items():
            field_frame = tk.Frame(inputs_frame, pady=5, bg="#ffffff")
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=label, font=label_font, bg="#ffffff").pack(side=tk.LEFT, anchor="w")
            validate_cmd = dialog.register(self.validate_input)
            entry = tk.Entry(field_frame, font=label_font, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attribute, ""))
            entry.pack(side=tk.RIGHT, anchor="e")
            user_inputs[attribute] = entry

        # Buttons frame
        button_frame = tk.Frame(dialog, pady=10, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)

        # Create custom Save and Cancel buttons
        save_button = tk.Button(button_frame, text="Save", font=button_font, bg='#32CD32', width=10, height=1, command=lambda: self.save_properties(user_inputs, dialog))
        cancel_button = tk.Button(button_frame, text="Cancel", font=button_font, bg='#FF4040', width=10, height=1, command=dialog.destroy)

        # Pack the buttons with padding
        save_button.pack(side=tk.LEFT, padx=20)
        cancel_button.pack(side=tk.RIGHT, padx=20)


    def save_properties(self, user_inputs, dialog):
        """Save properties and close dialog."""
        for attribute, entry in user_inputs.items():
            setattr(self, attribute, entry.get())
        dialog.destroy()


class Turbine(Element): 
    def __init__(self, canvas, name):
        super().__init__(canvas, name, "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/turbine_icon.png")
        # Initialize turbine properties
        self.ho = "0.0"        # Ho [m]
        self.qo = "0.0"        # Qo [m3/s]
        self.do = "0.0"        # Do [m]
        self.no = "0.0"        # No [rpm]
        self.jh = "0.0"        # Jh [kgm2]
        self.efficiency = "0.9" # Efficiency no [pu]
        self.z_elev = "0.0"    # Z elev [m asl]
        self.turbine_type = "Francis 23"  # Default turbine type
        self.available_turbine_types = ["Francis 23", "Francis 67", "Francis 78", "Kaplan 115","hill.xlsx"]
        self.radio_var = None
        self.table = None
        self.transient_frame = None
        self.governor_frame = None
        self.image_label = None
        # Initialize for the Governor properties
        # For Emergency shutdown 
        self.delta_p = "-100%"
        self.t_load_rej = "0.0"
        self.dt_ramp = "0.0"
        self.table_data = [(0.0, 0.0)] * 7
        # For partial load rejection
        self.tg = "0.0"
        self.tr = "0.0"
        self.td = "0.0"
        self.bp = "0.0"
        self.governor_image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/governor_diagram.png" 
        # Image paths
        self.turbine_schematic = [
            "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/tur_image1.png",
            "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/tur_image2.png"
        ]
        self.graph_image_paths = {
    "Francis 23": "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/graph_francis23.png",
    "Francis 67": "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/graph_francis67.png",
    "Francis 78": "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/graph_francis78.png",
    "Kaplan 115": "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/graph_kaplan115.png",
    "hill.xlsx": "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/graph_hill.png"
}
        

    def to_data(self):
        return {
            # For main tab
            "class": "Turbine",
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "ho": self.ho,
            "qo": self.qo,
            "do": self.do,
            "no": self.no,
            "jh": self.jh,
            "efficiency": self.efficiency,
            "z_elev": self.z_elev,
            "turbine_type": self.turbine_type,
            # For Governor tab
            "delta_p": self.delta_p,
            "t_load_rej": self.t_load_rej,
            "dt_ramp": self.dt_ramp,
            "table_data": self.table_data,
            "tg": self.tg,
            "tr": self.tr,
            "td": self.td,
            "bp": self.bp,
            # For other tabs
            "governor_image_path": self.governor_image_path,
            "graph_image_paths": self.graph_image_paths,
        }


    def load_from_data(self, data):
        self.name = data["name"]
        self.x = data["x"]
        self.y = data["y"]
        # For main tab
        self.ho = data.get("ho", "0.0")
        self.qo = data.get("qo", "0.0")
        self.do = data.get("do", "0.0")
        self.no = data.get("no", "0.0")
        self.jh = data.get("jh", "0.0")
        self.efficiency = data.get("efficiency", "0.9")
        self.z_elev = data.get("z_elev", "0.0")
        # Validate turbine type
        turbine_type = data.get("turbine_type", "Francis 23")
        if turbine_type in self.available_turbine_types:
            self.turbine_type = turbine_type
        else:
            self.turbine_type = "Francis 23"  # Default value if not valid
        # For Governor tab
        self.delta_p = data.get("delta_p", "-100%")
        self.t_load_rej = data.get("t_load_rej", "0.0")
        self.dt_ramp = data.get("dt_ramp", "0.0")
        self.table_data = data.get("table_data", [(0.0, 0.0)] * 7)
        # Populate the table entries in the UI
        self.table_entries = []
        for i, (t_value, y_value) in enumerate(self.table_data):
            if i < len(self.table_entries):
                self.table_entries[i][0].delete(0, tk.END)
                self.table_entries[i][0].insert(0, t_value)
                self.table_entries[i][1].delete(0, tk.END)
                self.table_entries[i][1].insert(0, y_value)
        self.tg = data.get("tg", "0.0")
        self.tr = data.get("tr", "0.0")
        self.td = data.get("td", "0.0")
        self.bp = data.get("bp", "0.0")

    

    def create_schematic_panel(self, parent):
        """Create the turbine schematic panel with two images"""
        schematic_frame = tk.Frame(parent, bg='white', bd=1, relief='solid')
        schematic_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Load and display turbine schematics side by side
        image_frame = tk.Frame(schematic_frame, bg='white')
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        for img_path in self.turbine_schematic:
            try:
                img = Image.open(img_path)
                # Calculate aspect ratio to maintain image proportions
                aspect_ratio = img.width / img.height
                new_height = 200  # Fixed height
                new_width = int(new_height * aspect_ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(image_frame, image=photo, bg='white')
                label.image = photo  # Keep a reference
                label.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
                # Create empty placeholder
                label = tk.Label(image_frame, text="Image Not Found", bg='white', width=30, height=10)
                label.pack(side=tk.LEFT, padx=5)

    def create_graph_panel(self, parent, turbine_type):
        """Create the graph panel with a single plot based on turbine type."""
        graph_frame = tk.Frame(parent, bg='white', bd=1, relief='solid')
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        try:
            img_path = self.graph_image_paths[turbine_type]
            img = Image.open(img_path)
            aspect_ratio = img.width / img.height
            new_width = 400  # Fixed width for graph
            new_height = int(new_width / aspect_ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(graph_frame, image=photo, bg='white')
            label.image = photo  # Keep a reference
            label.pack(pady=5)
        except Exception as e:
            print(f"Error loading graph image for {turbine_type}: {e}")
            label = tk.Label(graph_frame, text="Graph Not Found", bg='white', width=40, height=15)
            label.pack(pady=5)

    def create_governor_schematic_panel(self, parent):
        """Create the schematic panel for the Governor tab."""
        panel = tk.Frame(parent, bg='white')
        panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(panel, text="Governor Schematic", bg='white', font=('Arial', 10, 'bold')).pack(anchor='w', padx=5)

        self.governor_image_label = tk.Label(panel, bg='white')
        img = tk.PhotoImage(file=self.governor_image_path)
        self.governor_image_label.image = img  # Keep reference to avoid garbage collection
        self.governor_image_label.config(image=img)
        self.governor_image_label.pack(pady=10)

    def create_governor_table_panel(self, parent):
        """Create the table panel for Governor characteristics."""
        panel = tk.Frame(parent, bg='white')
        panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(panel, text="Governor Characteristics Table", bg='white', font=('Arial', 10, 'bold')).pack(anchor='w', padx=5)

        self.governor_table = ttk.Treeview(panel, columns=("Time", "Value"), show="headings", height=10)
        self.governor_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.governor_table.heading("Time", text="Time (s)")
        self.governor_table.heading("Value", text="Value (%)")

        # Populate table with existing data
        for time, value in self.table_data:
            self.governor_table.insert("", "end", values=(time, value))


    def open_properties_dialog(self):
        """Open a dialog to edit Turbine properties matching the reference design."""
        dialog = tk.Toplevel(self.canvas)
        dialog.title(f"Properties of {self.label}")
        dialog.transient(self.canvas.winfo_toplevel())
        dialog.grab_set()

        # Set size and center the dialog
        width, height = 1200, 650
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.configure(bg='#f0f0f0')

        # Tab frame at top
        tab_frame = tk.Frame(dialog, bg='#f0f0f0')
        tab_frame.pack(fill=tk.X, padx=2, pady=2)

        # Content frame for the tabs
        content_frame = tk.Frame(dialog, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create frames for each tab
        main_frame = tk.Frame(content_frame, bg='white', relief='sunken', borderwidth=1)
        governor_frame = tk.Frame(content_frame, bg='white', relief='sunken', borderwidth=1)

        # Function to switch between tabs
        def switch_tab(selected_frame):
            main_frame.pack_forget()
            governor_frame.pack_forget()
            selected_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab buttons
        main_tab = tk.Button(tab_frame, text="Main", bg='#90EE90', relief='raised', borderwidth=1,
                            command=lambda: switch_tab(main_frame))
        governor_tab = tk.Button(tab_frame, text="Governor", bg='#f0f0f0', relief='raised', borderwidth=1,
                                command=lambda: switch_tab(governor_frame))

        main_tab.pack(side=tk.LEFT, padx=(2, 0))
        governor_tab.pack(side=tk.LEFT)

        # Initially show the Main tab
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Populate Main tab
        self.create_main_tab_content(main_frame)

        # Populate Governor tab
        self.create_governor_tab_content(governor_frame)

        # Bottom buttons frame
        button_frame = tk.Frame(dialog, bg='#f0f0f0', height=50)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # Create "Save" and "Cancel" buttons
        save_button = tk.Button(button_frame, text="Save", bg='#32CD32', width=10, height=1)
        cancel_button = tk.Button(button_frame, text="Cancel", bg='#FF4040', width=10, height=1)

        # Pack the buttons
        save_button.pack(side=tk.LEFT, padx=(width // 2 - 50, 10))
        cancel_button.pack(side=tk.LEFT)

        # Bind buttons to actions
        save_button.config(command=lambda: self.save_properties(self.main_entries, dialog))  # pass main_entries
        cancel_button.config(command=dialog.destroy)

        # Configure dialog resize behavior
        dialog.update_idletasks()
        dialog.resizable(False, False)

    def save_properties(self, entries, dialog):
        """Save properties and close dialog."""
        # Save Main Tab properties
        for attr, widget in entries.items():
            if isinstance(widget, tk.StringVar):
                value = widget.get()
            else:
                value = widget.get()
            setattr(self, attr, value)

        # Save Governor Tab properties
        for attr, widget in self.governor_entries.items():
            if isinstance(widget, tk.StringVar):
                value = widget.get()
            else:
                value = widget.get()
            setattr(self, attr, value)

        # Update table_data with current entry values
        self.table_data = []
        for t_entry, y_entry in self.table_entries:
            t_value = float(t_entry.get()) if t_entry.get().strip() else 0.0
            y_value = float(y_entry.get())
            self.table_data.append((t_value, y_value))
        # Example: Save to a JSON file
        data = self.to_data()  # Convert object data to dictionary format
        with open(f"{self.name}_turbine_data.json", 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Turbine properties saved to {self.name}_turbine_data.json")
        dialog.destroy()



    def create_main_tab_content(self, frame):
        """Populate the Main tab with the original content."""
        # Split into left and right panels
        left_panel = tk.Frame(frame, bg='white', width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_panel = tk.Frame(frame, bg='white', width=600)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create schematic and graph panels
        self.create_schematic_panel(left_panel)
        self.create_graph_panel(right_panel, self.turbine_type)

        # Turbine Data label and inputs
        data_frame = tk.Frame(left_panel, bg='white')
        data_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(data_frame, text="Turbine Data", bg='white', anchor='w', font=('Arial', 10, 'bold')).pack(fill=tk.X, padx=5)

        # Create left and right columns for inputs
        left_inputs = tk.Frame(data_frame, bg='white')
        left_inputs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        right_inputs = tk.Frame(data_frame, bg='white')
        right_inputs.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Register a validation function
        def validate_float(value):
            """Validate if entry is a valid float."""
            if value == "":
                return True  # Allow empty input
            try:
                float(value)  # Check if the value can be converted to float
                return True
            except ValueError:
                return False  # Invalid input

        # Register the validate function with the Tkinter `register` method
        validate_cmd = frame.register(validate_float)

        # Left column inputs
        input_pairs = [
            ("Ho [m]", "ho"),
            ("Qo [m3/s]", "qo"),
            ("Do [m]", "do"),
            ("No [rpm]", "no")
        ]

        entries = {}
        for label_text, attr in input_pairs:
            frame = tk.Frame(left_inputs, bg='white')
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=label_text, bg='white', width=10, anchor='w').pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attr))
            entry.pack(side=tk.LEFT, padx=5)
            entries[attr] = entry


        # Right column inputs
        select_frame = tk.Frame(right_inputs, bg='white')
        select_frame.pack(fill=tk.X, pady=2)
        tk.Label(select_frame, text="Select", bg='white', width=15, anchor='w').pack(side=tk.LEFT)

        # Create a StringVar for the turbine type
        type_var = tk.StringVar(value=self.turbine_type)

        # Update the Combobox to include all available turbine types
        type_combo = ttk.Combobox(select_frame, textvariable=type_var, values=self.available_turbine_types, width=17)
        type_combo.pack(side=tk.LEFT)

        # Store the StringVar in the entries dictionary
        entries["turbine_type"] = type_var

        right_pairs = [
            ("Jh [kgm2]", "jh"),
            ("Efficiency no [pu]", "efficiency"),
            ("Z elev [m asl]", "z_elev")
        ]

        for label_text, attr in right_pairs:
            frame = tk.Frame(right_inputs, bg='white')
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=label_text, bg='white', width=15, anchor='w').pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=20, validate="key", validatecommand=(validate_cmd, '%P'))
            entry.insert(0, getattr(self, attr))
            entry.pack(side=tk.LEFT)
            entries[attr] = entry

        self.main_entries = entries

    def create_governor_tab_content(self, frame):
        """Populate the Governor tab with content precisely matching the design and layout provided."""
        
        # **Mode Selection Label**
        tk.Label(
            frame, text="Operating Mode:", bg="white", font=("Arial", 12, "bold"),
            anchor="w"
        ).pack(side=tk.TOP, anchor="w", padx=20, pady=(0, 5))

        # Container for both modes
        modes_container = tk.Frame(frame, bg="white")
        modes_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.mode_var = tk.StringVar(value="Emergency")

        # Left side - Emergency Mode with its components
        emergency_container = tk.Frame(modes_container, bg="white")
        emergency_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        emergency_frame = tk.Frame(emergency_container, bg="white", relief=tk.GROOVE, bd=1)
        emergency_frame.pack(fill=tk.BOTH, expand=True)

        # Emergency Mode Content
        emergency_radio = tk.Radiobutton(
            emergency_frame, text="Emergency Shut Down", variable=self.mode_var,
            value="Emergency", bg="white", font=("Arial", 10), command=self.update_mode
        )
        emergency_radio.pack(anchor="w", padx=10, pady=5)

        self.emergency_info = tk.Label(
            emergency_frame, bg="white", justify="left", font=("Arial", 10),
            text="• ΔP = 100%\n• Turbine distributor closes according to table t - y(t)\n• Generator disconnects at Load Rejection Time"
        )
        self.emergency_info.pack(fill=tk.X, padx=10, pady=5)

        # Table inside Emergency section
        table_frame = tk.Frame(emergency_frame, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Register a validation function
        def validate_float(value):
            """Validate if entry is a valid float."""
            if value == "":
                return True  # Allow empty input
            try:
                float(value)  # Check if the value can be converted to float
                return True
            except ValueError:
                return False  # Invalid input

        # Register the validate function with the Tkinter `register` method
        validate_cmd = frame.register(validate_float)

        # Modify the table creation part to store data
        self.table_entries = []
        table_content = tk.Frame(table_frame, bg="white")
        table_content.pack(fill=tk.BOTH)

        def validate_float(value):
            """Validate if entry is a valid float"""
            if value == "":
                return True
            try:
                float(value)
                return True
            except ValueError:
                return False

        validate_cmd = frame.register(validate_float)

        def make_callback(index): 
            def callback(event): 
                try:
                    # Ensure the index is within the table_data range
                    if index < len(self.table_data):
                        t_entry = self.table_entries[index][0]
                        y_entry = self.table_entries[index][1]
                        
                        # Get values, use 0 if empty
                        t_value = float(t_entry.get()) if t_entry.get().strip() else 0
                        y_value = float(y_entry.get()) if y_entry.get().strip() else 0
                        
                        # Update the table data
                        self.table_data[index] = (t_value, y_value)
                except ValueError:
                    # If conversion fails, you might want to handle this case
                    print(f"Invalid input in row {index}")
            return callback

        # Create table with data storage 
        for i in range(len(self.table_data)):  
            row_frame = tk.Frame(table_content, bg="white") 
            row_frame.pack(fill=tk.X) 

            t_entry = tk.Entry(row_frame, width=15, validate="key", 
                            validatecommand=(validate_cmd, '%P')) 
            t_entry.pack(side=tk.LEFT) 
            t_entry.insert(0, self.table_data[i][0])  # Load existing value 

            y_entry = tk.Entry(row_frame, width=15, validate="key", 
                            validatecommand=(validate_cmd, '%P')) 
            y_entry.pack(side=tk.LEFT) 
            y_entry.insert(0, self.table_data[i][1])  # Load existing value 

            self.table_entries.append((t_entry, y_entry)) 

            # Add trace to update stored data for each entry
            t_entry.bind('<FocusOut>', make_callback(i)) 
            y_entry.bind('<FocusOut>', make_callback(i))

        # Ensure that the last row is created with default values if not already present
        if len(self.table_data) < 7:  # Assuming you want 7 rows
            last_row_index = len(self.table_data)
            last_row_frame = tk.Frame(table_content, bg="white")
            last_row_frame.pack(fill=tk.X)

            last_t_entry = tk.Entry(last_row_frame, width=15, validate="key", 
                                    validatecommand=(validate_cmd, '%P'))
            last_t_entry.pack(side=tk.LEFT)
            last_t_entry.insert(0, 0.0)  # Initialize with a default value

            last_y_entry = tk.Entry(last_row_frame, width=15, validate="key", 
                                    validatecommand=(validate_cmd, '%P'))
            last_y_entry.pack(side=tk.LEFT)
            last_y_entry.insert(0, 0.0)  # Initialize with a default value

            self.table_entries.append((last_t_entry, last_y_entry))

            # Add trace to update stored data for the last entry
            last_t_entry.bind('<FocusOut>', make_callback(last_row_index)) 
            last_y_entry.bind('<FocusOut>', make_callback(last_row_index))



        # Right side - Partial Load with its components
        partial_container = tk.Frame(modes_container, bg="white")
        partial_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        partial_frame = tk.Frame(partial_container, bg="white", relief=tk.GROOVE, bd=1)
        partial_frame.pack(fill=tk.BOTH, expand=True)

        # Partial Load Content
        partial_radio = tk.Radiobutton(
            partial_frame, text="Partial Load Rejection", variable=self.mode_var,
            value="Partial", bg="white", font=("Arial", 10), command=self.update_mode
        )
        partial_radio.pack(anchor="w", padx=10, pady=5)

        self.partial_info = tk.Label(
            partial_frame, bg="white", justify="left", font=("Arial", 10),
            text="• The unit rejects partial load at Load Rejection Time\n• ΔP is user-defined\n• After load rejection, the speed governor adjusts distributor opening"
        )
        self.partial_info.pack(fill=tk.X, padx=10, pady=5)

        # Circuit diagram inside Partial Load section
        diagram_frame = tk.Frame(partial_frame, bg="white")
        diagram_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        image_path = "C:/Users/Aniket/Desktop/SIH Software/Main folder Airavata/Icons/governor_diagram.png"
        try:
            img = Image.open(image_path)
            img = img.resize((300, 200))
            img_tk = ImageTk.PhotoImage(img)
            self.image_label = tk.Label(diagram_frame, image=img_tk, bg="white")
            self.image_label.image = img_tk
            self.image_label.pack(fill=tk.BOTH, expand=True)
        except:
            self.image_label = tk.Label(diagram_frame, text="Circuit Diagram", bg="white", height=10)
            self.image_label.pack(fill=tk.BOTH, expand=True)

        # **Main Input Sections**
        main_frame = tk.Frame(frame, bg="white")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=5)

        # --- Transient Events (Left Side) ---
        self.transient_frame = tk.LabelFrame(
            main_frame, text="Transient Event", bg="white", font=("Arial", 12, "bold"),
            labelanchor="n"
        )
        self.transient_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        transient_pairs = [
            ("ΔP [% of Rated]", "delta_p"),
            ("T Load Rej [s]", "t_load_rej"),
            ("Δt Ramp [s]", "dt_ramp"),
        ]

        self.governor_entries = {}

        for i, (label_text, attr) in enumerate(transient_pairs):
            tk.Label(
                self.transient_frame, text=label_text, bg="white", anchor="w", font=("Arial", 10)
            ).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = tk.Entry(self.transient_frame, font=("Arial", 10), validate="key", validatecommand=(validate_cmd, '%P'))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, getattr(self, attr, ""))
            self.governor_entries[attr] = entry


        # --- Governor Parameters (Right Side) ---
        self.governor_frame = tk.LabelFrame(
            main_frame, text="Governor Parameters", bg="white", font=("Arial", 12, "bold"),
            labelanchor="n"
        )
        self.governor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        governor_pairs = [
            ("Tg [s]", "tg"),
            ("Tr [s]", "tr"),
            ("Td [s]", "td"),
            ("bp [-]", "bp"),
        ]

        for i, (label_text, attr) in enumerate(governor_pairs):
            tk.Label(
                self.governor_frame, text=label_text, bg="white", anchor="w", font=("Arial", 10)
            ).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = tk.Entry(self.governor_frame, font=("Arial", 10), validate="key", validatecommand=(validate_cmd, '%P'))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, getattr(self, attr, ""))
            self.governor_entries[attr] = entry

        self.update_mode()

    def update_mode(self):
        """Update UI elements based on selected mode"""
        mode = self.mode_var.get()


        if mode == "Emergency":
            # Update visual feedback
            self.emergency_info.master.config(relief=tk.GROOVE, bd=2)
            self.partial_info.master.config(relief=tk.GROOVE, bd=1)
            
            # Enable table entries
            for t_entry, y_entry in self.table_entries:
                t_entry.config(state="normal")
                y_entry.config(state="normal")
            
            # Enable transient events
            for key, entry in self.governor_entries.items():
                if key in ["delta_p", "t_load_rej", "dt_ramp"]:
                    entry.config(state="normal")
                else:  # Governor parameters
                    entry.config(state="disabled")
                    
        else:  # Partial Load Rejection
            # Update visual feedback
            self.emergency_info.master.config(relief=tk.GROOVE, bd=1)
            self.partial_info.master.config(relief=tk.GROOVE, bd=2)
            
            # Disable table entries
            for t_entry, y_entry in self.table_entries:
                t_entry.config(state="disabled")
                y_entry.config(state="disabled")
            
            # Enable/disable appropriate sections
            for key, entry in self.governor_entries.items():
                if key in ["delta_p", "t_load_rej", "dt_ramp"]:
                    entry.config(state="disabled")
                else:  # Governor parameters
                    entry.config(state="normal")

    def get_table_data(self):
        """Return the current table data"""
        return self.table_data










