import networkx as nx
import numpy as np
from utils import get_element_color

def build_graph(elements, nodes, connections):
    """
    Build a NetworkX graph from the parsed hydraulic system data.
    
    Args:
        elements (dict): Dictionary of element properties
        nodes (dict): Dictionary of node information
        connections (list): List of connections between nodes
    
    Returns:
        nx.Graph: NetworkX graph representing the hydraulic system
    """
    # Create a new graph
    G = nx.Graph()
    
    # Add nodes
    for node_id, node_data in nodes.items():
        G.add_node(
            node_id,
            id=node_id,
            label=f"Node {node_id}",
            type=node_data.get('type', 'node'),
            elevation=node_data.get('elevation', 0),
            element=node_data.get('element', None),
            color=get_element_color(node_data.get('type', 'node')),
            size=10  # Default size, will be adjusted later
        )
    
    # Add edges
    for conn in connections:
        source = conn['source']
        target = conn['target']
        elem_id = conn['id']
        elem_type = conn['type']
        
        # Get properties for this element
        properties = elements.get(elem_id, {}).get('properties', {})
        
        # Calculate weight based on length or a default value
        weight = properties.get('leng', 1.0)
        
        G.add_edge(
            source,
            target,
            id=elem_id,
            type=elem_type,
            weight=weight,
            length=properties.get('leng', None),
            diameter=properties.get('diam', None),
            friction=properties.get('fric', None),
            properties=properties,
            color=get_element_color(elem_type)
        )
    
    # Add node position based on graph layout and elevation
    # First create a 2D layout
    pos = nx.spring_layout(G, weight='weight', iterations=100, seed=42)
    
    # Add elevation as z-coordinate
    for node_id in G.nodes():
        elevation = G.nodes[node_id]['elevation'] or 0
        x, y = pos[node_id]
        G.nodes[node_id]['pos'] = (x, y, elevation/1000)  # Scale elevation for visualization
        
        # Set node size based on degree (number of connections)
        degree = G.degree(node_id)
        G.nodes[node_id]['size'] = 5 + (degree * 2)
        
        # Improve node label
        node_type = G.nodes[node_id]['type']
        elem_id = G.nodes[node_id].get('element', '')
        if elem_id:
            G.nodes[node_id]['label'] = f"{elem_id} ({node_id})"
        else:
            G.nodes[node_id]['label'] = f"{node_type.capitalize()} {node_id}"
    
    return G
