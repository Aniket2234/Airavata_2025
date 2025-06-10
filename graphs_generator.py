import json
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import math
import numpy as np



def generate_advanced_data(time_points, element_class, parameters):
    """
    Generate graph data with wide lines and more aggressive scaling.
    """
    x_label = "Time (s)"
    y_label = "Value"
    graph_type = 'line'
    values = []

    # Extract specific parameters
    base_value = parameters.get('base_value', 0)
    max_value = parameters.get('max_value', base_value * 1.5)

    if element_class == "InletReservoir":
        x_label = "Time (s)"
        y_label = "Water Level (m)"
        graph_type = 'curved'
        values = [
            (base_value * math.exp(-0.1 * t) + np.random.normal(0, 0.2 * base_value)) * 0.5  # Scale more
            for t in time_points
        ]

    elif element_class == "OutletReservoir":
        x_label = "Time (s)"
        y_label = "Water Level (m)"
        graph_type = 'wave'
        values = [
            (base_value * (1 - math.cos(0.5 * t)) +
             0.2 * base_value * math.sin(0.2 * t) +
             np.random.normal(0, 0.1 * base_value)) * 0.6
            for t in time_points
        ]

    elif element_class == "Valve":
        x_label = "Time (s)"
        y_label = "Flow Rate (m³/s)"
        graph_type = 'curved'
        values = [
            max(0, (base_value * (1 - t / time_points[-1]) +
                    np.random.normal(0, 0.1 * base_value)) * 0.4)
            for t in time_points
        ]

    elif element_class == "Pipe":
        x_label = "Distance along Pipe (m)"
        y_label = "Flow Velocity (m/s)"
        graph_type = 'wave'
        values = [
            (base_value * (1 - abs(math.sin(t / 2)) * 0.3) +
             0.2 * base_value * math.sin(t) +
             np.random.normal(0, 0.05 * base_value)) * 0.4
            for t in time_points
        ]

    elif element_class == "Turbine":
        x_label = "Time (s)"
        y_label = "Power Output (kW)"
        graph_type = 'curved'
        values = [
            (base_value * math.sin(t / 2) * math.exp(-0.05 * t) +
             np.random.normal(0, 0.1 * base_value)) * 0.7
            for t in time_points
        ]

    elif element_class == "SurgeTank":
        x_label = "Time (s)"
        y_label = "Pressure (kPa)"
        graph_type = 'wave'
        values = [
            (base_value * (1 + 0.5 * math.sin(t)) * math.exp(-0.05 * t) +
             np.random.normal(0, 0.2 * base_value)) * 0.4
            for t in time_points
        ]

    elif element_class == "Manifold":
        x_label = "Branch Number"
        y_label = "Flow Distribution (%)"
        graph_type = 'step'
        values = [
            (base_value * (1 + 0.3 * math.sin(t)) +
             np.random.normal(0, 0.1 * base_value)) * 0.5
            for t in time_points
        ]

    else:
        values = [base_value * 0.3 for _ in time_points]  # Default aggressive scaling

    return x_label, y_label, values, graph_type



def run_simulation_and_generate_graphs(root, current_file_name):
    """Runs the simulation based on the file contents and generates graphs with realistic behavior."""
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
        sim_time = simulation_props.get("simulation_time", 20.0)
        time_step = simulation_props.get("time_step", 0.01)

        # Prepare time points
        time_points = [t * time_step for t in range(int(sim_time / time_step) + 1)]
        
        # Prepare graph data storage
        graph_data = {}
        pipe_elements = []

        # Generate graph data for each element
        for element in elements:
            element_class = element.get("class")
            element_name = element.get("name")

            # Determine base value and parameters for each element type
            if element_class == "InletReservoir":
                base_value = float(element.get("level_h", 10))
            elif element_class == "OutletReservoir":
                base_value = float(element.get("level_h", 5))
            elif element_class == "Valve":
                diameter = float(element.get("diameter", 0))
                base_value = math.pi * ((diameter / 2) ** 2)
            elif element_class == "Pipe":
                diameter = float(element.get("diameter", 0))
                length = float(element.get("length", 0))
                base_value = diameter * length
                pipe_elements.append(element_name)
            elif element_class == "Turbine":
                efficiency = float(element.get("efficiency", 0))
                base_value = efficiency * 10
            elif element_class == "SurgeTank":
                base_value = float(element.get("throttle_ao", 100))
            elif element_class == "Manifold":
                base_value = 5
            else:
                base_value = 0

            # Generate graph data
            parameters = {
                'base_value': base_value,
                'max_value': base_value * 1.5
            }
            
            x_label, y_label, values, graph_type = generate_advanced_data(
                time_points, 
                element_class, 
                parameters
            )
            
            graph_data[element_name] = {
                'time_points': time_points,
                'values': values,
                'x_label': x_label,
                'y_label': y_label,
                'graph_type': graph_type,
                'base_value': base_value  # Add base_value here
            }


        # Create the main property box with enhanced design
        property_box = tk.Toplevel(root)
        property_box.title("Realistic Hydraulic System Simulation Graph Generator")
        property_box.attributes('-fullscreen', True)

        # Title Frame
        title_frame = tk.Frame(property_box, bg='#2c3e50')
        title_frame.pack(fill=tk.X, pady=10)

        title_label = tk.Label(
            title_frame, 
            text="🌊 Realistic Hydraulic System Simulation Graph Generator 🌊", 
            font=('Arial', 16, 'bold'), 
            fg='white', 
            bg='#2c3e50',
            pady=10
        )
        title_label.pack()

        # Matplotlib figure for graphs
        plt.style.use('default')  # More neutral plot style
        fig, ax = plt.subplots(figsize=(12, 7), dpi=100)

        # Initial overall graph
        for name, data in graph_data.items():
            if data['graph_type'] == 'wave':
                ax.plot(data['time_points'], data['values'], label=name, linewidth=1, linestyle='-')
            elif data['graph_type'] == 'step':
                ax.step(data['time_points'], data['values'], label=name, linewidth=1, where='mid')
            elif data['graph_type'] == 'curved':
                ax.plot(data['time_points'], data['values'], label=name, linewidth=1, linestyle='--')
            else:
                ax.plot(data['time_points'], data['values'], label=name, linewidth=1)

        ax.set_title("Overall Simulation Overview", fontsize=15, fontweight='bold')
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("Simulated Values", fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Embed matplotlib figure in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=property_box)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Add Matplotlib Navigation Toolbar
        toolbar = NavigationToolbar2Tk(canvas, property_box)
        toolbar.update()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Dropdown selection frame
        selection_frame = tk.Frame(property_box, bg='#f0f0f0')  # Ensure selection_frame is defined before use
        selection_frame.pack(fill=tk.X, padx=20, pady=10)

        # Overall graph option
        element_list = ["Overall Simulation Graph"] + [name for name in graph_data.keys() if name not in pipe_elements]

        # Element selection dropdown
        element_label = tk.Label(
            selection_frame, 
            text="Select Element:", 
            font=('Arial', 12), 
            bg='#f0f0f0'
        )
        element_label.pack(side=tk.LEFT, padx=10)

        element_dropdown = ttk.Combobox(
            selection_frame, 
            values=element_list, 
            width=30, 
            state="readonly"
        )
        element_dropdown.set("Overall Simulation Graph")
        element_dropdown.pack(side=tk.LEFT, padx=10)

        # Pipes dropdown
        pipe_label = tk.Label(
            selection_frame, 
            text="Select Pipe:", 
            font=('Arial', 12), 
            bg='#f0f0f0'
        )
        pipe_label.pack(side=tk.LEFT, padx=10)

        pipe_dropdown = ttk.Combobox(
            selection_frame, 
            values=pipe_elements, 
            width=30, 
            state="readonly"
        )
        pipe_dropdown.pack(side=tk.LEFT, padx=10)

        # Close fullscreen button
        close_fullscreen_btn = tk.Button(
            selection_frame, 
            text="Exit Fullscreen", 
            command=lambda: property_box.attributes('-fullscreen', False)
        )
        close_fullscreen_btn.pack(side=tk.LEFT, padx=10)

        # Define the zoom in and zoom out functions before using them
        def zoom_in():
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim(xlim[0] * 0.8, xlim[1] * 0.8)
            ax.set_ylim(ylim[0] * 0.8, ylim[1] * 0.8)
            canvas.draw()

        def zoom_out():
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim(xlim[0] * 1.2, xlim[1] * 1.2)
            ax.set_ylim(ylim[0] * 1.2, ylim[1] * 1.2)
            canvas.draw()

        # Add Zoom In and Zoom Out buttons
        zoom_in_btn = tk.Button(
            selection_frame,
            text="Zoom In",
            command=zoom_in
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=10)

        zoom_out_btn = tk.Button(
            selection_frame,
            text="Zoom Out",
            command=zoom_out
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=10)

        # Store the initial axis limits when the graph is first created
        initial_xlim = fig.gca().get_xlim()  # Get initial x limits
        initial_ylim = fig.gca().get_ylim()  # Get initial y limits

        # Function to increase the Y-axis range
        def increase_y_axis():
            ylim = ax.get_ylim()
            ax.set_ylim(ylim[0] * 1.2, ylim[1] * 1.2)
            canvas.draw()

        # Function to increase the X-axis range
        def increase_x_axis():
            xlim = ax.get_xlim()
            ax.set_xlim(xlim[0] * 1.2, xlim[1] * 1.2)
            canvas.draw()

        # Function to decrease the Y-axis range
        def decrease_y_axis():
            ylim = ax.get_ylim()
            ax.set_ylim(ylim[0] * 0.8, ylim[1] * 0.8)
            canvas.draw()

        # Function to decrease the X-axis range
        def decrease_x_axis():
            xlim = ax.get_xlim()
            ax.set_xlim(xlim[0] * 0.8, xlim[1] * 0.8)
            canvas.draw()

        # Function to reset the axes and zoom to the original state
        def reset_axes():
            ax.set_xlim(initial_xlim)  # Reset x axis
            ax.set_ylim(initial_ylim)  # Reset y axis
            canvas.draw()  # Redraw the canvas to reflect changes

        # Add Increase Y-Axis, Increase X-Axis, Decrease Y-Axis, Decrease X-Axis and Reset buttons in the selection frame
        increase_y_btn = tk.Button(
            selection_frame,
            text="Increase Y-Axis",
            command=increase_y_axis
        )
        increase_y_btn.pack(side=tk.LEFT, padx=10)

        increase_x_btn = tk.Button(
            selection_frame,
            text="Increase X-Axis",
            command=increase_x_axis
        )
        increase_x_btn.pack(side=tk.LEFT, padx=10)

        decrease_y_btn = tk.Button(
            selection_frame,
            text="Decrease Y-Axis",
            command=decrease_y_axis
        )
        decrease_y_btn.pack(side=tk.LEFT, padx=10)

        decrease_x_btn = tk.Button(
            selection_frame,
            text="Decrease X-Axis",
            command=decrease_x_axis
        )
        decrease_x_btn.pack(side=tk.LEFT, padx=10)

        # Add Reset button
        reset_btn = tk.Button(
            selection_frame,
            text="Reset All",
            command=reset_axes
        )
        reset_btn.pack(side=tk.LEFT, padx=10)


        # Update graph functions
        def update_graph(event):
            ax.clear()
            
            selected_element = element_dropdown.get()
            
            if selected_element == "Overall Simulation Graph":
                for name, data in graph_data.items():
                    if data['graph_type'] == 'wave':
                        ax.plot(data['time_points'], data['values'], label=name, linewidth=1, linestyle='-')
                    elif data['graph_type'] == 'step':
                        ax.step(data['time_points'], data['values'], label=name, linewidth=1, where='mid')
                    elif data['graph_type'] == 'curved':
                        ax.plot(data['time_points'], data['values'], label=name, linewidth=1, linestyle='--')
                    else:
                        ax.plot(data['time_points'], data['values'], label=name, linewidth=1)
                
                ax.set_title("Overall Simulation Overview", fontsize=15, fontweight='bold')
                ax.set_xlabel("Time (s)", fontsize=12)
                ax.set_ylabel("Simulated Values", fontsize=12)
                ax.legend(loc='best')
                ax.grid(True, linestyle='--', alpha=0.7)
            else:
                data = graph_data[selected_element]
                if data['graph_type'] == 'wave':
                    ax.plot(data['time_points'], data['values'], color='red', linewidth=1, linestyle='-')
                elif data['graph_type'] == 'step':
                    ax.step(data['time_points'], data['values'], color='red', linewidth=1, where='mid')
                elif data['graph_type'] == 'curved':
                    ax.plot(data['time_points'], data['values'], color='red', linewidth=1, linestyle='--')
                else:
                    ax.plot(data['time_points'], data['values'], color='red', linewidth=1)
                
                ax.set_title(f"Graph for {selected_element}", fontsize=15, fontweight='bold')
                ax.set_xlabel(data['x_label'], fontsize=12)
                ax.set_ylabel(data['y_label'], fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.7)
            
            canvas.draw()

        def generate_pipe_data(time_points, base_value):
            """Generate data for a pipe with discharge and pressure annotations."""
            discharge_values = [
                max(0, (base_value * (1 - abs(math.sin(t / 2))) + 0.2 * base_value * math.sin(t)))
                for t in time_points
            ]
            pressure_head_values = [0.1 * discharge for discharge in discharge_values]  # Example relationship

            annotations = []
            for i in range(1, len(discharge_values) - 1):
                # Detect spikes
                if discharge_values[i] > discharge_values[i - 1] and discharge_values[i] > discharge_values[i + 1]:
                    annotations.append((time_points[i], discharge_values[i], pressure_head_values[i], "High"))
                elif discharge_values[i] < discharge_values[i - 1] and discharge_values[i] < discharge_values[i + 1]:
                    annotations.append((time_points[i], discharge_values[i], pressure_head_values[i], "Low"))

            return discharge_values, pressure_head_values, annotations

        def generate_detailed_pipe_data(time_points, base_value):
            """Generate highly fluctuating discharge and pressure head data with detailed spikes."""
            # Generate fluctuating discharge values
            discharge_values = [
                max(0, base_value * (1 + 0.5 * math.sin(10 * t)) + np.random.normal(0, 0.2 * base_value))
                for t in time_points
            ]
            pressure_head_values = [0.1 * discharge for discharge in discharge_values]  # Example relationship

            # Detect all spikes (local maxima and minima), but limit to 20 spikes
            annotations = []
            for i in range(1, len(discharge_values) - 1):
                if len(annotations) >= 5:  # Stop once 20 spikes are found
                    break
                if discharge_values[i] > discharge_values[i - 1] and discharge_values[i] > discharge_values[i + 1]:
                    annotations.append((time_points[i], discharge_values[i], pressure_head_values[i], "High"))
                elif discharge_values[i] < discharge_values[i - 1] and discharge_values[i] < discharge_values[i + 1]:
                    annotations.append((time_points[i], discharge_values[i], pressure_head_values[i], "Low"))

            return discharge_values, pressure_head_values, annotations

        def update_pipe_graph(event):
            selected_pipe = pipe_dropdown.get()
            if selected_pipe:
                ax.clear()

                data = graph_data[selected_pipe]
                discharge_values, pressure_head_values, annotations = generate_detailed_pipe_data(
                    data['time_points'], data['base_value']
                )

                # Plot congested discharge graph
                ax.plot(
                    data['time_points'],
                    discharge_values,
                    color='blue',
                    linewidth=1,
                    label="Discharge (m³/s)"
                )

                # Annotate only the first 20 spikes
                for t, discharge, pressure_head, status in annotations:
                    ax.annotate(
                        f"(pressure head: {pressure_head:.2f}, discharge: {discharge:.2f})",
                        xy=(t, discharge),
                        xytext=(t, discharge + 0.1),  # Offset text above the spike
                        fontsize=10,  # Increased text size for better visibility
                        color='red',
                        arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5)
                    )
                    ax.text(
                        t,
                        discharge - 0.15,  # Offset status text below the spike
                        f"{status}",
                        fontsize=10,  # Larger status text
                        color='green',
                        weight='bold'
                    )

                # Graph settings
                ax.set_title(f"Detailed Discharge-Time Graph for Pipe: {selected_pipe}", fontsize=16, fontweight='bold')
                ax.set_xlabel("Time (s)", fontsize=12)
                ax.set_ylabel("Discharge at Outlet (m³/s)", fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend()

                canvas.draw()




        element_dropdown.bind("<<ComboboxSelected>>", update_graph)
        pipe_dropdown.bind("<<ComboboxSelected>>", update_pipe_graph)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Failed to read the file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    current_file_name = "paste.txt"  # Your JSON file path
    run_simulation_and_generate_graphs(root, current_file_name)
