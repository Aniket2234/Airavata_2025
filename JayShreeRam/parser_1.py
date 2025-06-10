import re

def parse_hydraulic_file(file_content):
    """
    Parse the hydraulic system file content and extract nodes, connections, and properties.
    
    Args:
        file_content (str): Content of the hydraulic system file
    
    Returns:
        tuple: (elements, nodes, connections) dictionaries containing the parsed data
    """
    # Initialize data structures
    elements = {}  # Store element properties
    nodes = {}     # Store node information
    connections = []  # Store connections between nodes
    
    # Flag to track section of the file
    in_system_connectivity = False
    in_element_properties = False
    current_element = None
    
    # Process each line in the file
    for line in file_content.splitlines():
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Determine the section
        if "SYSTEM CONNECTIVITY" in line:
            in_system_connectivity = True
            in_element_properties = False
            continue
        
        if "ELEMENT PROPERTIES" in line:
            in_system_connectivity = False
            in_element_properties = True
            continue
        
        if "FINISH" in line and current_element:
            current_element = None
            continue
            
        # Process system connectivity section
        if in_system_connectivity:
            # Extract ELEM definitions
            elem_match = re.match(r'ELEM\s+(\w+)\s+AT\s+(\d+)', line)
            if elem_match:
                elem_id, node_id = elem_match.groups()
                node_id = int(node_id)
                
                # Add element to elements dictionary
                element_type = get_element_type(elem_id)
                elements[elem_id] = {
                    'id': elem_id,
                    'type': element_type,
                    'node': node_id,
                    'properties': {}
                }
                
                # Add the node if it doesn't exist
                if node_id not in nodes:
                    nodes[node_id] = {
                        'id': node_id,
                        'element': elem_id,
                        'type': element_type,
                        'elevation': None,
                        'connections': []
                    }
                continue
            
            # Extract ELEM LINK definitions
            link_match = re.match(r'ELEM\s+(\w+)\s+LINK\s+(\d+)\s+(\d+)', line)
            if link_match:
                elem_id, node1_id, node2_id = link_match.groups()
                node1_id, node2_id = int(node1_id), int(node2_id)
                
                # Add element to elements dictionary
                element_type = get_element_type(elem_id)
                elements[elem_id] = {
                    'id': elem_id,
                    'type': element_type,
                    'source': node1_id,
                    'target': node2_id,
                    'properties': {}
                }
                
                # Add the connection
                connections.append({
                    'id': elem_id,
                    'source': node1_id,
                    'target': node2_id,
                    'type': element_type
                })
                
                # Add nodes if they don't exist
                for node_id in [node1_id, node2_id]:
                    if node_id not in nodes:
                        nodes[node_id] = {
                            'id': node_id,
                            'type': 'junction',
                            'elevation': None,
                            'connections': []
                        }
                
                # Update node connections
                nodes[node1_id]['connections'].append(node2_id)
                nodes[node2_id]['connections'].append(node1_id)
                continue
            
            # Extract JUNCTION definitions
            junction_match = re.match(r'JUNCTION\s+AT\s+(\d+)', line)
            if junction_match:
                node_id = int(junction_match.group(1))
                
                if node_id not in nodes:
                    nodes[node_id] = {
                        'id': node_id,
                        'type': 'junction',
                        'elevation': None,
                        'connections': []
                    }
                else:
                    nodes[node_id]['type'] = 'junction'
                continue
            
            # Extract NODE ELEV definitions
            node_elev_match = re.match(r'NODE\s+(\d+)\s+ELEV\s+([\d\.]+)', line)
            if node_elev_match:
                node_id, elevation = node_elev_match.groups()
                node_id = int(node_id)
                elevation = float(elevation)
                
                if node_id in nodes:
                    nodes[node_id]['elevation'] = elevation
                else:
                    nodes[node_id] = {
                        'id': node_id,
                        'type': 'node',
                        'elevation': elevation,
                        'connections': []
                    }
                continue
                
        # Process element properties section
        if in_element_properties:
            # Start of a new element definition
            reservoir_match = re.match(r'RESERVOIR', line)
            if reservoir_match:
                current_element = {
                    'type': 'reservoir',
                    'properties': {}
                }
                continue
                
            # Extract CONDUIT properties
            conduit_match = re.match(r'CONDUIT\s+ID\s+(\w+)', line)
            if conduit_match:
                elem_id = conduit_match.group(1)
                
                # Extract other properties from the same line
                properties = {}
                prop_matches = re.findall(r'(\w+)\s+([\d\.]+)', line)
                for prop_name, prop_value in prop_matches:
                    properties[prop_name.lower()] = float(prop_value)
                
                # Update the element properties
                if elem_id in elements:
                    elements[elem_id]['properties'].update(properties)
                    
                continue
                
            # Element ID definition
            id_match = re.match(r'ID\s+(\w+)', line)
            if id_match and current_element:
                elem_id = id_match.group(1)
                if elem_id in elements:
                    elements[elem_id]['properties'].update(current_element['properties'])
                    elements[elem_id]['type'] = current_element['type']
                continue
                
            # Element ELEVATION definition
            elev_match = re.match(r'ELEV\s+([\d\.]+)', line)
            if elev_match and current_element:
                elevation = float(elev_match.group(1))
                current_element['properties']['elevation'] = elevation
                continue
                
            # Element DUMMY definition
            if "DUMMY" in line and current_element:
                current_element['type'] = 'dummy'
                continue
                
            # Extract other element properties
            if current_element:
                # Extract diameter
                diam_match = re.match(r'DIAMETER\s+([\d\.]+)', line)
                if diam_match:
                    current_element['properties']['diameter'] = float(diam_match.group(1))
                    continue
                
                # Extract added loss coefficients
                cplus_match = re.match(r'CPLUS\s+([\d\.]+)', line)
                if cplus_match:
                    current_element['properties']['cplus'] = float(cplus_match.group(1))
                    continue
                
                cminus_match = re.match(r'CMINUS\s+([\d\.]+)', line)
                if cminus_match:
                    current_element['properties']['cminus'] = float(cminus_match.group(1))
                    continue
    
    return elements, nodes, connections


def get_element_type(elem_id):
    """
    Determine the element type based on its ID.
    
    Args:
        elem_id (str): Element identifier
    
    Returns:
        str: Type of the element
    """
    prefix = elem_id[0] if elem_id else ''
    
    if prefix == 'C':
        return 'conduit'
    elif prefix == 'D':
        return 'dummy'
    elif elem_id == 'HW':
        return 'reservoir'
    elif prefix == 'F':
        return 'flowbalancing'
    elif elem_id == 'ST':
        return 'storage'
    else:
        return 'unknown'
