import json
import os
import sys
from typing import List, Dict, Any

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float, returning default if conversion fails
    
    Args:
        value: Input value to convert
        default: Default value to return if conversion fails
    
    Returns:
        Converted float value
    """
    try:
        # Handle both string and numeric inputs
        if value == '' or value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def prepare_whamo_detailed_input(input_json_file: str) -> str:
    """
    Generate a detailed WHAMO input file with dynamic content from JSON input
    """
    # Load JSON data
    with open(input_json_file, 'r') as file:
        data = json.load(file)
    
    elements = data.get("elements", {}).get("elements", [])
    sim_props = data.get("elements", {}).get("simulation_properties", {})
    
    # Generate WHAMO input sections
    sections = []
    
    # Project Name Section
    sections.append("C Project Name\nC  SYSTEM CONNECTIVITY")
    
    # System Connectivity Section
    system_connectivity = generate_system_connectivity(elements)
    sections.append("\nSYSTEM\n" + system_connectivity)
    
    # Node Elevations Section
    node_elevations = generate_node_elevations(elements)
    sections.append("\n" + node_elevations)
    
    # Element Properties Section
    sections.append("\nC ELEMENT PROPERTIES")
    
    # Reservoir
    reservoir = next((e for e in elements if e['class'] == 'InletReservoir'), None)
    if reservoir:
        reservoir_section = generate_reservoir_section(reservoir)
        sections.append(reservoir_section)
    
    # Conduit Properties
    conduit_section = generate_conduit_properties(elements)
    sections.append(conduit_section)
    
    # Surge Tank
    surge_tank = next((e for e in elements if e['class'] == 'SurgeTank'), None)
    if surge_tank:
        surge_tank_section = generate_surge_tank_section(surge_tank)
        sections.append(surge_tank_section)
    
    # Flow Boundary Conditions
    flow_bc_section = generate_flow_boundary_conditions(elements)
    sections.append(flow_bc_section)
    
    # Output Request Section
    output_request_section = generate_output_request_section()
    sections.append("\nC OUTPUT REQUEST\n" + output_request_section)
    
    # Computational Parameters
    comp_params_section = generate_computational_parameters(sim_props)
    sections.append("\nC COMPUTATIONAL PARAMETERS\n" + comp_params_section)
    
    # Execution Control
    sections.append("\nC EXECUTION CONTROL\nGO\nGOODBYE")
    
    return "\n".join(sections)

def generate_system_connectivity(elements: List[Dict]) -> str:
    """Generate system connectivity section"""
    pipes = [e for e in elements if e['class'] == 'Pipe']
    
    # Create a mapping of elements to their node numbers
    element_nodes = {}
    current_node = 1
    node_mapping = {}
    
    # First pass: assign nodes to unique elements
    for pipe in pipes:
        inlet_element = pipe.get('outlet_element', f'Node_{current_node}')
        outlet_element = pipe.get('inlet_element', f'Node_{current_node+1}')
        
        if inlet_element not in node_mapping:
            node_mapping[inlet_element] = current_node
            current_node += 1
        
        if outlet_element not in node_mapping:
            node_mapping[outlet_element] = current_node
            current_node += 1
    
    # Build connectivity section
    connectivity_lines = []
    connectivity_lines.append("ELEM HW AT 1")
    
    # Sort pipes to ensure a logical flow
    sorted_pipes = sorted(pipes, key=lambda x: node_mapping.get(x.get('outlet_element', ''), 0))
    
    # Create pipe connections
    for pipe in sorted_pipes:
        inlet_node = node_mapping.get(pipe.get('outlet_element', f'Node_{current_node}'), 2)
        outlet_node = node_mapping.get(pipe.get('inlet_element', f'Node_{current_node+1}'), 2)
        connectivity_lines.append(f"ELEM {pipe['name']} LINK {inlet_node} {outlet_node}")
        
        if inlet_node not in [1, 2]:
            connectivity_lines.append(f"JUNCTION AT {inlet_node}")
        
        if outlet_node not in [1, 2]:
            connectivity_lines.append(f"JUNCTION AT {outlet_node}")
    
    return "\n".join(connectivity_lines)

def generate_node_elevations(elements: List[Dict]) -> str:
    """Generate node elevations section"""
    node_mapping = {}
    current_node = 1
    elevation_lines = []
    
    for element in elements:
        # Use safe conversion with default values
        if element['class'] in ['InletReservoir', 'OutletReservoir', 'Pipe', 'Valve', 'Manifold']:
            # Try to get elevation from different possible keys
            elevation_keys = ['level_h', 'level_z', 'elev_z', 'elevation_z', 'pipe_z']
            elevation = 0.0
            for key in elevation_keys:
                value = element.get(key, '')
                elevation = safe_float(value)
                if elevation != 0.0:
                    break
            
            # Convert to feet and round
            elevation_ft = elevation * 3.281
            
            # Assign or get existing node number
            if element['name'] not in node_mapping:
                node_mapping[element['name']] = current_node
                elevation_lines.append(f"NODE {current_node} ELEV {elevation_ft:.2f}")
                current_node += 1
    
    elevation_lines.append("FINISH")
    return "\n".join(elevation_lines)

def generate_reservoir_section(reservoir: Dict) -> str:
    """Generate reservoir section"""
    # Use safe_float with multiple possible keys for elevation
    elevation_keys = ['level_h', 'level_z', 'elev_z', 'elevation_z']
    elevation = 0.0
    for key in elevation_keys:
        value = reservoir.get(key, '')
        elevation = safe_float(value)
        if elevation != 0.0:
            break
    
    # Convert to feet
    elevation_ft = elevation * 3.281
    return f"""RESERVOIR
 ID HW
 ELEV {elevation_ft:.2f}
 FINISH"""

def generate_conduit_properties(elements: List[Dict]) -> str:
    """Generate conduit properties section"""
    conduit_lines = []
    
    # Pipes
    pipes = [e for e in elements if e['class'] == 'Pipe']
    for pipe in pipes:
        name = pipe['name']
        
        # Safe conversions with defaults
        length = safe_float(pipe.get('length', 1)) * 3.281
        diameter = safe_float(pipe.get('diameter', 1)) * 3.281
        celerity = safe_float(pipe.get('celerity', 1000)) * 3.281
        friction = safe_float(pipe.get('manning_n', 0.01), 0.01)
        
        conduit_lines.append(f"""CONDUIT ID {name} LENG {length:.2f} DIAM {diameter:.2f} CELE {celerity:.2f} FRIC {friction:.4f}  
ADDEDLOSS CPLUS 0.1 CMINUS 0.1 NUMSEG 5 FINISH""")
    
    # Dummy conduits (if needed)
    dummy_conduits = [
        ("D1", "19.36", "2.367", "2.041"),
        ("D2", "27.3", "2.367", "2.041"),
        ("D3", "27.3", "2.367", "2.041")
    ]
    
    for d_id, diameter, cplus, cminus in dummy_conduits:
        conduit_lines.append(f"""CONDUIT ID {d_id} 
 DUMMY 
 DIAMETER {diameter}
 ADDEDLOSS 
 CPLUS {cplus}
 CMINUS {cminus}
FINISH""")
    
    return "\n".join(conduit_lines)

def generate_surge_tank_section(surge_tank: Dict) -> str:
    """Generate surge tank section"""
    # Safe conversions with defaults and multiple possible keys
    top_elev = safe_float(surge_tank.get('throttle_el_zo', 4215.88))
    bottom_elev = safe_float(surge_tank.get('stank_a', 3918.96))
    diameter = safe_float(surge_tank.get('Diameter_surge_tank', 101.71), 10)
    celerity = safe_float(surge_tank.get('throttle_ao', 2499.63), 1000)
    
    return f"""SURGETANK 
 ID ST SIMPLE
 ELTOP {top_elev:.2f}
 ELBOTTOM {bottom_elev:.2f}
 DIAM {diameter:.2f}
 CELERITY {celerity:.2f}
 FRICTION 0.0057
FINISH"""

def generate_flow_boundary_conditions(elements: List[Dict]) -> str:
    """Generate flow boundary conditions section"""
    flow_bc_lines = []
    
    # Create 4 flow boundary conditions
    for i in range(1, 5):
        flow_bc_lines.append(f"FLOWBC ID FB{i} QSCHEDULE {i} FINISH")
    
    flow_bc_lines.append("\nSCHEDULE")
    for i in range(1, 5):
        flow_bc_lines.append(f" QSCHEDULE {i} T 0 Q 3000 T 20 Q 0 T 3000 Q 0")
    
    flow_bc_lines.append("FINISH")
    
    return "\n".join(flow_bc_lines)

def generate_output_request_section() -> str:
    """Generate output request section"""
    return """HISTORY
 NODE 2 Q HEAD
 ELEM ST Q ELEV
 NODE 51 PRESSURE HEAD
 NODE 52 PRESSURE HEAD
 NODE 53 PRESSURE HEAD
 NODE 54 PRESSURE HEAD
FINISH"""

def generate_computational_parameters(sim_props: Dict) -> str:
    """Generate computational parameters section"""
    time_step = safe_float(sim_props.get('time_step', 0.01), 0.01)
    sim_time = safe_float(sim_props.get('simulation_time', 500.0), 500.0)
    
    return f"""CONTROL
 DTCOMP {time_step} DTOUT .1 TMAX {sim_time}
FINISH"""

def run_simulation_from_file(input_file_path: str = "input.json"):
    """Run simulation by generating WHAMO input file"""
    try:
        # Generate WHAMO input
        whamo_input = prepare_whamo_detailed_input(input_file_path)
        
        # Save WHAMO input file
        output_path = os.path.splitext(input_file_path)[0] + "_whamo_input.txt"
        with open(output_path, 'w') as f:
            f.write(whamo_input)
        
        print(f"WHAMO input file generated: {output_path}")
        return True
    
    except Exception as e:
        print(f"Error generating WHAMO input: {e}")
        return False

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.json"
    run_simulation_from_file(input_file)
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.json"
    run_simulation_from_file(input_file)