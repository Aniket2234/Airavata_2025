import json
import os
import webbrowser
from tkinter import messagebox, Toplevel, Label, ttk

def validate_elements(elements):
    """
    Validate element parameters with suggestions and consequences.
    
    Args:
        elements (list): List of simulation elements
    
    Returns:
        list: Validation results with suggestions
    """
    validation_results = []
    
    for element in elements:
        element_name = element.get("name")
        element_class = element.get("class")

        # Validation logic similar to transient_simulation.py
        if element_class == "InletReservoir":
            level_h = float(element.get("level_h", 0))
            if level_h < 5 or level_h > 50:
                validation_results.append((
                    element_name, "level_h", level_h,
                    "Adjust inlet reservoir level (5-50).",
                    "May impact water supply and system dynamics."
                ))

        elif element_class == "OutletReservoir":
            level_h = float(element.get("level_h", 0))
            if level_h < 20 or level_h > 150:
                validation_results.append((
                    element_name, "level_h", level_h,
                    "Adjust outlet reservoir level (20-150).",
                    "Could affect downstream water distribution."
                ))

        elif element_class == "Valve":
            diameter = float(element.get("diameter", 0))
            loss_coefficient = float(element.get("loss_coefficient", 0))
            if diameter < 1 or diameter > 20:
                validation_results.append((
                    element_name, "diameter", diameter,
                    "Set valve diameter within range (1-20).",
                    "Incorrect diameter may restrict fluid flow."
                ))
            if loss_coefficient < 0.1 or loss_coefficient > 5:
                validation_results.append((
                    element_name, "loss_coefficient", loss_coefficient,
                    "Adjust valve loss coefficient (0.1-5).",
                    "Extreme values can significantly impact flow characteristics."
                ))

        # Add similar validation for other element classes
        # (Manifold, SurgeTank, Turbine, Pipe, etc.)

    return validation_results

def show_validation_window(validation_results):
    """
    Display validation results in a Tkinter window.
    
    Args:
        validation_results (list): List of validation issues
    """
    validation_window = Toplevel()
    validation_window.title("CFD Gradient Validation Results")
    validation_window.geometry("800x600")
    
    Label(validation_window, text="Validation Results", font=("Arial", 14, "bold")).pack(pady=10)
    
    columns = ("Element", "Parameter", "Value", "Suggestion", "Consequence")
    table = ttk.Treeview(validation_window, columns=columns, show="headings", height=20)
    table.pack(fill="both", expand=True, padx=10, pady=10)
    
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=150, anchor="center")
    
    for result in validation_results:
        table.insert("", "end", values=result)

    ttk.Button(validation_window, text="Close", command=validation_window.destroy).pack(pady=10)

def process_cfd_gradient(root, current_file_name):
    """
    Process CFD gradient data and generate visualization.
    
    Args:
        root: Tkinter root window
        current_file_name (str): Path to the input JSON file
    """
    if not current_file_name:
        messagebox.showerror("Error", "No file is currently open!")
        return

    try:
        # Read the JSON file
        with open(current_file_name, 'r') as file:
            file_content = json.load(file)

        elements = file_content.get("elements", {}).get("elements", [])
        simulation_props = file_content.get("elements", {}).get("simulation_properties", {})

        # Validate element parameters
        validation_results = validate_elements(elements)
        if validation_results:
            show_validation_window(validation_results)
            return

        # Process elements and collect data
        processed_elements = []
        
        # Element color mapping
        element_colors = {
            "InletReservoir": "#A9D0F5",  # Light blue
            "OutletReservoir": "#F6B3B3",  # Light red
            "Valve": "#D8BFD8",  # Light purple
            "Manifold": "#FFF0F5",  # Light pink
            "SurgeTank": "#D3D3D3",  # Light gray
            "Turbine": "#F0E68C",  # Light yellow
            "Pipe": "#E0FFFF"  # Light cyan
        }

        # Process each element
        for element in elements:
            element_class = element.get("class")
            element_name = element.get("name")
            
            # Extract parameters based on element type
            params = {}
            if element_class == "InletReservoir":
                params = {
                    "level_h": float(element.get("level_h", 0)),
                    "pipe_z": float(element.get("pipe_z", 0))
                }
            
            elif element_class == "OutletReservoir":
                params = {
                    "level_h": float(element.get("level_h", 0)),
                    "level_z": float(element.get("level_z", 0))
                }
            
            elif element_class == "Valve":
                params = {
                    "diameter": float(element.get("diameter", 0)),
                    "loss_coefficient": float(element.get("loss_coefficient", 0)),
                    "elevation_z": float(element.get("elevation_z", 0))
                }
            
            # Add processing for other element types...

            processed_elements.append({
                "name": element_name,
                "class": element_class,
                "parameters": params,
                "color": element_colors.get(element_class, "#FFFFFF")
            })

        # Generate HTML visualization
        html_content = generate_cfd_html(processed_elements, simulation_props)
        
        # Determine file path for HTML output
        directory = os.path.dirname(current_file_name)
        html_file_path = os.path.join(directory, "cfd_gradient_results.html")

        # Save HTML file
        with open(html_file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        # Open in default web browser
        webbrowser.open(f"file://{html_file_path}")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Failed to read the file: {e}")

def generate_cfd_html(processed_elements, simulation_props):
    """
    Generate HTML visualization of CFD gradient data.
    
    Args:
        processed_elements (list): Processed simulation elements
        simulation_props (dict): Simulation properties
    
    Returns:
        str: HTML content for visualization
    """
    html_content = f"""
    <html>
    <head>
        <title>CFD Gradient Visualization</title>
        <style>
            /* Similar styling to transient_simulation.py HTML generation */
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; }}
            table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                background-color: #fff;
            }}
            th, td {{
                padding: 15px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <h1>CFD Gradient Analysis</h1>
        <table>
            <tr>
                <th>Element Name</th>
                <th>Element Class</th>
                <th>Parameters</th>
            </tr>
    """

    # Add table rows for each processed element
    for element in processed_elements:
        params_str = "<br>".join([f"{k}: {v}" for k, v in element['parameters'].items()])
        html_content += f"""
            <tr style="background-color:{element['color']}">
                <td>{element['name']}</td>
                <td>{element['class']}</td>
                <td>{params_str}</td>
            </tr>
        """

    html_content += """
        </table>
        <h2>Simulation Properties</h2>
        <table>
    """

    # Add simulation properties
    for prop, value in simulation_props.items():
        html_content += f"""
            <tr>
                <td>{prop}</td>
                <td>{value}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    return html_content

# You would integrate this function into your main application
# For example, by adding it to a menu item or button in the main GUI