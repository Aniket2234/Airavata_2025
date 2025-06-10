import os
import json
import tkinter.filedialog as filedialog
import pandas as pd
import json  # Add this import statement
import tkinter.filedialog as filedialog
# other imports...



class FileManager:
    def __init__(self, project_folder=None):
        """Initializes the file manager. The project_folder is optional."""
        self.project_folder = project_folder if project_folder else os.getcwd()  # Use provided folder or default to current directory
        self.file_path = None  # Initialize the file path as None initially

    def close_file(self):
        """Logic to close the current file (e.g., clear the loaded data or release resources)."""
        self.file_path = None

    @property
    def current_file(self):
        """Return the current file path, if any."""
        return self.file_path

    def load_data_file(self, file_path):
        """Load the `.dat` project file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r') as file:
            data = file.read().strip()  # Read and strip any whitespace

        if not data:
            # If the file is empty, return a default structure
            return ""
        
        return data

    def load_txt_files(self):
        """Load valve and turbine operation data from `.txt` files."""
        txt_files = [f for f in os.listdir(self.project_folder) if f.endswith('.txt')]
        return txt_files

    def save_data_file(self, file_path, data):
        """Save the `.dat` project file."""
        with open(file_path, 'w') as file:
            file.write(data)

    def export_to_excel(self, data, output_path):
        """Export data to `.xlsx` format."""
        df = pd.DataFrame(data)
        df.to_excel(output_path, index=False)

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




    def create_new_file(self):
        """Create a new file using the save file dialog."""
        return self.save_file()  # Creates a new file with the save dialog

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


