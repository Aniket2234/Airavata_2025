import json
import os
import webbrowser
from tkinter import messagebox
from conclusions import generate_conclusions, generate_final_conclusion
# Add this import at the top of the file, along with other imports
from Word_tasks import run_simulation_from_file
from cfd_gradient_visualization import process_cfd_gradient

from tkinter import Toplevel, Label, ttk

def show_validation_window(validation_results):
    """Display a validation window with a table of issues."""
    validation_window = Toplevel()
    validation_window.title("Validation Results")
    validation_window.geometry("800x600")
    
    Label(validation_window, text="Validation Results", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Create a table to display the results
    columns = ("Element", "Parameter", "Value", "Suggestion", "Consequence")
    table = ttk.Treeview(validation_window, columns=columns, show="headings", height=20)
    table.pack(fill="both", expand=True, padx=10, pady=10)
    
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=150, anchor="center")
    
    # Add data to the table
    for result in validation_results:
        table.insert("", "end", values=result)

    # Add a close button
    ttk.Button(validation_window, text="Close", command=validation_window.destroy).pack(pady=10)

def validate_elements(elements):
    validation_results = []
    for element in elements:
        element_name = element.get("name")
        element_class = element.get("class")

        if element_class == "InletReservoir":
            level_h = float(element.get("level_h", 0))
            if level_h < 5 or level_h > 50:
                validation_results.append((
                    element_name, "level_h", level_h,
                    "Adjust the reservoir level (5-50).",
                    "May lead to insufficient inflow or reservoir overflow."
                ))

        elif element_class == "OutletReservoir":
            level_h = float(element.get("level_h", 0))
            if level_h < 20 or level_h > 150:
                validation_results.append((
                    element_name, "level_h", level_h,
                    "Adjust the outlet level (20-150).",
                    "Could cause water backup or insufficient flow downstream."
                ))

        elif element_class == "Valve":
            diameter = float(element.get("diameter", 0))
            loss_coefficient = float(element.get("loss_coefficient", 0))
            if diameter < 1 or diameter > 20:
                validation_results.append((
                    element_name, "diameter", diameter,
                    "Set valve diameter within range (1-20).",
                    "Incorrect diameter can restrict or overburden flow."
                ))
            if loss_coefficient < 0.1 or loss_coefficient > 5:
                validation_results.append((
                    element_name, "loss_coefficient", loss_coefficient,
                    "Adjust loss coefficient (0.1-5).",
                    "High loss may increase head loss significantly."
                ))

        elif element_class == "Manifold":
            elev_z = float(element.get("elev_z", 0))
            if elev_z < 0 or elev_z > 30:
                validation_results.append((
                    element_name, "elev_z", elev_z,
                    "Ensure manifold elevation is within range (0-30).",
                    "Improper elevation may affect flow distribution."
                ))

        elif element_class == "SurgeTank":
            throttle_ao = float(element.get("throttle_ao", 0))
            stank_a = float(element.get("stank_a", 0))
            if throttle_ao < 5 or throttle_ao > 50:
                validation_results.append((
                    element_name, "throttle_ao", throttle_ao,
                    "Adjust throttle area opening (5-50).",
                    "Incorrect settings may destabilize surge control."
                ))
            if stank_a < 10 or stank_a > 100:
                validation_results.append((
                    element_name, "stank_a", stank_a,
                    "Set tank area within range (10-100).",
                    "Improper area may affect stability of flow dynamics."
                ))

        elif element_class == "Turbine":
            ho = float(element.get("ho", 0))
            qo = float(element.get("qo", 0))
            efficiency = float(element.get("efficiency", 0))
            if ho < 10 or ho > 150:
                validation_results.append((
                    element_name, "ho", ho,
                    "Adjust head height (10-150).",
                    "Improper head may lead to insufficient energy generation or turbine damage."
                ))
            if qo < 1 or qo > 500:
                validation_results.append((
                    element_name, "qo", qo,
                    "Ensure flow rate is within range (1-500).",
                    "Too high flow rate may overburden the turbine, causing failures."
                ))
            if efficiency < 0.1 or efficiency > 1:
                validation_results.append((
                    element_name, "efficiency", efficiency,
                    "Set efficiency within realistic range (0.1-1).",
                    "Unrealistic efficiency values may yield incorrect simulations."
                ))

        elif element_class == "Pipe":
            diameter = float(element.get("diameter", 0))
            length = float(element.get("length", 0))
            if diameter < 0.5 or diameter > 10:
                validation_results.append((
                    element_name, "diameter", diameter,
                    "Set pipe diameter within range (0.5-10).",
                    "Improper diameter may cause pipe burst or flow restriction."
                ))
            if length < 1 or length > 500:
                validation_results.append((
                    element_name, "length", length,
                    "Ensure pipe length is within range (1-500).",
                    "Too long pipes may increase head loss significantly."
                ))

    return validation_results


def run_simulation_and_generate_html(root, current_file_name):
    """Runs the simulation based on the file contents and generates an HTML file with results."""
    if not current_file_name:
        messagebox.showerror("Error", "No file is currently open!")
        return

    try:
        # Read the JSON file
        with open(current_file_name, 'r') as file:
            file_content = json.load(file)

        elements = file_content.get("elements", {}).get("elements", [])
        simulation_props = file_content.get("elements", {}).get("simulation_properties", {})

        # Extract simulation properties
        sim_time = simulation_props.get("simulation_time", 10.0)
        time_step = simulation_props.get("time_step", 0.01)
        gravity = simulation_props.get("gravity", 9.81)
        fluid_density = simulation_props.get("fluid_density", 1000.0)


        # Validate element parameters
        validation_results = validate_elements(elements)
        if validation_results:
            show_validation_window(validation_results)
            return  # Stop further execution until issues are resolved



        # Build connections for pipes and compute results for each element
        results = []
        flow_connections = {}
        flow_path = []

        # Define colors for different elements
        element_colors = {
            "InletReservoir": "#A9D0F5",  # Light blue
            "OutletReservoir": "#F6B3B3",  # Light red
            "Valve": "#D8BFD8",  # Light purple
            "Manifold": "#FFF0F5",  # Light pink
            "SurgeTank": "#D3D3D3",  # Light gray
            "Turbine": "#F0E68C",  # Light yellow
            "Pipe": "#E0FFFF"  # Light cyan
        }

        # Initialize inlet_h1
        inlet_h1 = None

        # Compute results and prepare flow path
        for element in elements:
            element_class = element.get("class")
            element_name = element.get("name")
            
            # Initialize additional variables
            flow_rate = None
            head_loss = None
            energy_output = None
            efficiency = None
            flow_conclusion = ""
            final_level = 0  # Default value for final level

            # Inlet Reservoir
            if element_class == "InletReservoir":
                level_h = float(element.get("level_h", 0)) if element.get("level_h") else None
                pipe_z = float(element.get("pipe_z", 0)) if element.get("pipe_z") else None
                final_level = level_h if level_h else 0
                flow_rate = 0  # No flow rate for inlet reservoir
                flow_conclusion = "Inlet reservoir level is sufficient."
                inlet_h1 = level_h  # Store the inlet height for later use

            # Outlet Reservoir
            elif element_class == "OutletReservoir":
                level_h = float(element.get("level_h", 0)) if element.get("level_h") else None
                level_z = float(element.get("level_z", 0)) if element.get("level_z") else None
                final_level = level_h if level_h else 0
                flow_rate = 0  # No flow rate for outlet reservoir
                flow_conclusion = "Outlet reservoir is ready to receive flow."

            # Valve
            elif element_class == "Valve":
                diameter = float(element.get("diameter", 0)) if element.get("diameter") else None
                loss_coefficient = float(element.get("loss_coefficient", 0)) if element.get("loss_coefficient") else None
                loss_factor = float(element.get("loss_factor", 0)) if element.get("loss_factor") else None
                elevation_z = float(element.get("elevation_z", 0)) if element.get("elevation_z") else None
                custom_values = element.get("custom_values", [])
                # Use custom values in some calculation (e.g., average)
                avg_custom_value = sum(float(val[0]) for val in custom_values) / len(custom_values) if custom_values else 0
                flow_velocity = 2.0  # Placeholder for flow velocity
                head_loss = loss_coefficient * (flow_velocity ** 2) / (2 * gravity) + avg_custom_value
                flow_rate = 10.0  # Placeholder for flow rate
                flow_conclusion = f"Valve head loss is {head_loss:.2f} m."

            # Manifold
            elif element_class == "Manifold":
                elev_z = float(element.get("elev_z", 0)) if element.get("elev_z") else None
                flow_rate = 20.0  # Placeholder for flow rate
                flow_conclusion = f"Manifold elevation is {elev_z} m and distributing flow effectively."

            # Surge Tank
            elif element_class == "SurgeTank":
                throttle_ao = float(element.get("throttle_ao", 0)) if element.get("throttle_ao") else None
                stank_a = float(element.get("stank_a", 0)) if element.get("stank_a") else None
                throttle_kin = float(element.get("throttle_kin", 1)) if element.get("throttle_kin") else 1.0
                throttle_kout = float(element.get("throttle_kout", 0)) if element.get("throttle_kout") else None
                throttle_el_zo = float(element.get("throttle_el_zo", 0)) if element.get("throttle_el_zo") else None
                energy_h = 100.0  # Placeholder for energy head
                z_oscillation = energy_h - (throttle_kin * (flow_velocity ** 2) / (2 * gravity))
                flow_rate = 15.0  # Placeholder for flow rate
                flow_conclusion = f"Surge tank is stabilizing flow with throttle settings: AO={throttle_ao}, KIN={throttle_kin}, KOUT={throttle_kout}."

            # Turbine
            elif element_class == "Turbine":
                ho = float(element.get("ho", 0)) if element.get("ho") else None
                qo = float(element.get("qo", 0)) if element.get("qo") else None
                efficiency = float(element.get("efficiency", 0.9)) if element.get("efficiency") else None
                delta_p = float(element.get("delta_p", 0)) if element.get("delta_p") else 0
                load_rejection = delta_p / 100 if delta_p else 0
                energy_output = ho * qo * efficiency * load_rejection
                flow_conclusion = f"Turbine output is {energy_output:.2f} kW with efficiency {efficiency}."

            # Pipe
            elif element_class == "Pipe":
                diameter = float(element.get("diameter", 0)) if element.get("diameter") else None
                length = float(element.get("length", 0)) if element.get("length") else None
                celerity = float(element.get("celerity", 0)) if element.get("celerity") else None
                manning_n = float(element.get("manning_n", 0)) if element.get("manning_n") else None
                inlet_h1 = float(element.get("inlet_h1", 0)) if element.get("inlet_h1") else None
                hydraulic_radius = diameter / 4  # Example calculation
                if inlet_h1 is not None and length is not None:  # Ensure values are defined
                    flow_rate = (1 / manning_n) * (hydraulic_radius ** (2 / 3)) * (inlet_h1 / length) ** 0.5
                else:
                    flow_rate = None  # Handle the case where values are not available
                flow_conclusion = f"Pipe flow rate is {flow_rate:.2f} m³/s." if flow_rate is not None else "N/A"

            # Append results with additional details
            results.append([element_name, element_class, f"{final_level:.2f} m" if final_level else "N/A", 
                            f"{flow_rate:.2f} m³/s" if flow_rate is not None else "N/A", 
                            f"{head_loss:.2f} m" if head_loss is not None else "N/A", 
                            f"{energy_output:.2f} kW" if energy_output is not None else "N/A", 
                            flow_conclusion, element_colors[element_class]])

        # Map connections for flow path
        for element in elements:
            inlet_element = element.get("inlet_element")
            outlet_element = element.get("outlet_element")
            if inlet_element and outlet_element:
                flow_connections[outlet_element] = (inlet_element, element.get("name"))

        # Trace the flow path
        flow_path = []
        current_element = None
        for element in elements:
            if element.get("class") == "InletReservoir":  # Fixed typo here
                current_element = element.get("name")
                flow_path.append(current_element)
                break

        while current_element:
            connection = flow_connections.get(current_element)
            if connection:
                inlet_element, pipe_name = connection
                flow_path.append(pipe_name)  # Add pipe to flow path
                flow_path.append(inlet_element)  # Add connected element
                current_element = inlet_element
            else:
                break

        # Compile the flow path as a readable string
        flow_path_str = " → ".join(flow_path)

        # Generate conclusions based on results
        element_conclusions = generate_conclusions(results)
        final_conclusion = generate_final_conclusion(results)

        # Create HTML content with enhanced styling and animation
        html_content = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }}
            h1 {{ color: #333; text-align: center; }}
            .flow-path {{ font-weight: bold; color: #2e8b57; }}
            table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                padding: 15px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
                animation: highlight 0.5s ease-in-out;
            }}
            @keyframes highlight {{
                0% {{ background-color: #f9f9f9; }}
                100% {{ background-color: #f1f1f1; }}
            }}
            .flow-path-container {{
                width: 90%;
                margin: 0 auto;
                overflow: hidden;
                white-space: nowrap;
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
            }}
            .flow-path-container p {{
                display: inline-block;
                padding: 0;
                margin: 0;
                animation: marquee 40s linear infinite;  /* Increased duration for slower speed */
            }}
            @keyframes marquee {{
                0% {{ transform: translateX(100%); }}
                100% {{ transform: translateX(-100%); }}
            }}
            h2 {{
                color: #4CAF50; /* Green color for headings */
                text-align: center;
                margin-top: 20px;
            }}
            ul {{
                list-style-type: none; /* Remove default list styling */
                padding: 0;
                margin: 0;
                max-width: 600px; /* Limit width for better readability */
                margin: 20px auto; /* Center the list */
                background-color: #f9f9f9; /* Light background for the list */
                border-radius: 5px; /* Rounded corners */
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Subtle shadow */
            }}
            li {{
                padding: 10px;
                border-bottom: 1px solid #ddd; /* Divider between items */
                transition: background-color 0.3s; /* Smooth background change */
            }}
            li:hover {{
                background-color: #e0f7fa; /* Light blue on hover */
            }}
        </style>
        <script>
            function openInFullScreen() {{
                var elem = document.documentElement;  // This will make the entire document go full-screen
                if (elem.requestFullscreen) {{
                    elem.requestFullscreen();
                }} else if (elem.mozRequestFullScreen) {{ // Firefox
                    elem.mozRequestFullScreen();
                }} else if (elem.webkitRequestFullscreen) {{ // Chrome, Safari, Opera
                    elem.webkitRequestFullscreen();
                }} else if (elem.msRequestFullscreen) {{ // IE/Edge
                    elem.msRequestFullscreen();
                }}
            }}

            window.onload = function() {{
                openInFullScreen();  // Trigger full-screen mode as soon as the page loads
            }};
        </script>
        </head>
        <body>
            <h1>Simulation Results</h1>
            <div class="flow-path-container">
                <p class="flow-path">Water Flow Path: {flow_path_str}</p>
            </div>
            <table>
                <tr>
                    <th>Element</th>
                    <th>Class</th>
                    <th>Result</th>
                    <th>Flow Rate (m³/s)</th>
                    <th>Head Loss (m)</th>
                    <th> Energy Output (kW)</th>
                    <th>Flow Conclusion</th>
                </tr>
        """

        # Add table rows dynamically with calculated results
        for result in results:
            element_name, element_class, result_value, flow_rate, head_loss, energy_output, flow_conclusion, color = result
            html_content += f"""
            <tr style="background-color:{color}">
                <td>{element_name}</td>
                <td>{element_class}</td>
                <td>{result_value}</td>
                <td>{flow_rate}</td>
                <td>{head_loss}</td>
                <td>{energy_output}</td>
                <td>{flow_conclusion}</td>
            </tr>
            """

        html_content += "</table>"
        
        # Add conclusions section
        html_content += "<h2>Element Conclusions</h2><ul>"
        for conclusion in element_conclusions:
            html_content += f"<li>{conclusion}</li>"
        html_content += "</ul>"

        # Add final conclusion section
        html_content += f"<h2>Final Conclusion</h2><p>{final_conclusion}</p>"
        html_content += "</body></html>"

        # Determine the file path to save the HTML file
        directory = os.path.dirname(current_file_name)
        html_file_path = os.path.join(directory, "simulation_results.html")

        # Save the HTML content to the file using utf-8 encoding
        with open(html_file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        # Open the HTML file in the default web browser
        webbrowser.open(f"file://{html_file_path}")


        # After generating the HTML file, call Word_tasks simulation
        run_simulation_from_file(current_file_name)

        # process_cfd_gradient(current_file_name)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Failed to read the file: {e}")