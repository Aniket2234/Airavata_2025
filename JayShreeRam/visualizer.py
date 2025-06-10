import plotly.graph_objects as go
import numpy as np
from utils import get_element_color, get_node_group_colors

def create_network_visualization(G, node_size_factor=20, edge_width_factor=3, elev_scale_factor=1.0, group_by="Element Type"):
    """
    Create a Plotly visualization of the hydraulic system network.
    
    Args:
        G (nx.Graph): NetworkX graph of the hydraulic system
        node_size_factor (float): Factor to scale node sizes
        edge_width_factor (float): Factor to scale edge widths
        elev_scale_factor (float): Factor to scale elevation differences
        group_by (str): How to group nodes for coloring ("Element Type", "Elevation Range", "None")
    
    Returns:
        go.Figure: Plotly figure with the network visualization
    """
    # Extract node positions
    x_nodes = []
    y_nodes = []
    z_nodes = []
    node_sizes = []
    node_labels = []
    node_colors = []
    node_types = []
    node_elevations = []
    node_hover_texts = []
    node_ids = []
    
    # Extract nodes data
    for node_id in G.nodes():
        node = G.nodes[node_id]
        x, y, z = node.get('pos', (0, 0, 0))
        z = z * elev_scale_factor  # Apply elevation scaling
        
        x_nodes.append(x)
        y_nodes.append(y)
        z_nodes.append(z)
        
        # Scale node sizes
        node_size = node.get('size', 10) * node_size_factor / 10
        node_sizes.append(node_size)
        
        # Collect node attributes for display
        node_ids.append(node_id)
        node_labels.append(node.get('label', f"Node {node_id}"))
        node_types.append(node.get('type', 'node'))
        node_elevations.append(node.get('elevation', 0))
        
        # Assign color based on node type
        if group_by == "None":
            node_colors.append(get_element_color(node.get('type', 'node')))
        else:
            # Colors will be assigned later based on grouping
            node_colors.append(node.get('type', 'node'))
        
        # Create hover text
        hover_text = [
            f"ID: {node_id}",
            f"Type: {node.get('type', 'node').capitalize()}"
        ]
        
        # Safely handle elevation which might be None
        elevation = node.get('elevation')
        if elevation is not None:
            hover_text.append(f"Elevation: {elevation:.2f}")
        else:
            hover_text.append("Elevation: Unknown")
        
        # Add element ID if available
        if node.get('element'):
            hover_text.append(f"Element: {node.get('element')}")
        
        # Add connections count
        hover_text.append(f"Connections: {G.degree(node_id)}")
        
        node_hover_texts.append("<br>".join(hover_text))
    
    # Create edge traces
    edge_traces = []
    
    # Group edges by type for legend
    edges_by_type = {}
    
    # Extract edges data
    for source, target, data in G.edges(data=True):
        # Get node positions
        x0, y0, z0 = G.nodes[source].get('pos', (0, 0, 0))
        x1, y1, z1 = G.nodes[target].get('pos', (0, 0, 0))
        
        # Apply elevation scaling
        z0 = z0 * elev_scale_factor
        z1 = z1 * elev_scale_factor
        
        # Edge properties
        edge_type = data.get('type', 'unknown')
        edge_color = data.get('color', 'rgba(100, 100, 100, 0.8)')
        
        # Calculate edge width based on diameter or a default value
        diameter = data.get('diameter', None)
        if diameter:
            edge_width = np.log1p(diameter) * edge_width_factor
        else:
            edge_width = edge_width_factor
        
        # Create hover text for edge
        properties = data.get('properties', {})
        hover_text = [
            f"ID: {data.get('id', 'Unknown')}",
            f"Type: {edge_type.capitalize()}"
        ]
        
        # Add length if available
        if 'length' in data and data['length']:
            hover_text.append(f"Length: {data['length']:.2f}")
            
        # Add diameter if available
        if 'diameter' in data and data['diameter']:
            hover_text.append(f"Diameter: {data['diameter']:.2f}")
            
        # Add friction if available
        if 'friction' in data and data['friction']:
            hover_text.append(f"Friction: {data['friction']:.5f}")
        
        # Additional properties from the elements data
        for key, value in properties.items():
            if key not in ['leng', 'diam', 'fric']:  # Skip duplicates
                hover_text.append(f"{key.capitalize()}: {value}")
        
        edge_hover_text = "<br>".join(hover_text)
        
        # Group edges by type for legend
        if edge_type not in edges_by_type:
            # First edge of this type - create a new trace for the legend
            edge_trace = go.Scatter3d(
                x=[x0, x1, None],
                y=[y0, y1, None],
                z=[z0, z1, None],
                mode='lines',
                line=dict(
                    width=edge_width,
                    color=edge_color
                ),
                hoverinfo='text',
                hovertext=edge_hover_text,
                name=edge_type.capitalize(),
                showlegend=True
            )
            edges_by_type[edge_type] = edge_trace
            edge_traces.append(edge_trace)
        else:
            # Subsequent edges of this type - append to existing trace data
            # But create a new trace for the actual edge (without legend entry)
            edge_trace = go.Scatter3d(
                x=[x0, x1, None],
                y=[y0, y1, None],
                z=[z0, z1, None],
                mode='lines',
                line=dict(
                    width=edge_width,
                    color=edge_color
                ),
                hoverinfo='text',
                hovertext=edge_hover_text,
                showlegend=False
            )
            edge_traces.append(edge_trace)
    
    # Assign colors based on grouping
    if group_by == "Element Type":
        # Use the type-based colors already assigned
        unique_types = list(set(node_types))
        color_map = {t: get_element_color(t) for t in unique_types}
        node_colors = [color_map[t] for t in node_colors]
        
        # Node trace with colors by element type
        node_trace = go.Scatter3d(
            x=x_nodes,
            y=y_nodes,
            z=z_nodes,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                opacity=0.8,
                line=dict(width=1, color='rgba(0, 0, 0, 0.5)')
            ),
            text=node_labels,
            hoverinfo='text',
            hovertext=node_hover_texts,
            name='Nodes'
        )
        
        # Add a separate trace for each node type for legend
        node_traces = [node_trace]  # Start with all nodes
        
        # Create a trace for each node type (for legend only)
        for node_type in unique_types:
            legend_trace = go.Scatter3d(
                x=[x_nodes[0]],
                y=[y_nodes[0]],
                z=[z_nodes[0]],
                mode='markers',
                marker=dict(
                    size=10,
                    color=get_element_color(node_type),
                    opacity=0.8
                ),
                name=node_type.capitalize(),
                showlegend=True,
                visible='legendonly'  # Hide the actual point, just show in legend
            )
            node_traces.append(legend_trace)
        
    elif group_by == "Elevation Range":
        # Group nodes by elevation ranges
        elev_min = min(node_elevations)
        elev_max = max(node_elevations)
        
        # Define elevation groups
        n_groups = 5
        elev_range = elev_max - elev_min
        if elev_range == 0:
            elev_range = 1  # Handle case where all elevations are the same
            
        group_size = elev_range / n_groups
        
        # Function to get group for an elevation
        def get_elev_group(elev):
            if elev_range == 1:  # All same elevation
                return 0
            return min(int((elev - elev_min) / group_size), n_groups - 1)
        
        elev_groups = [get_elev_group(elev) for elev in node_elevations]
        
        # Get colors for elevation groups
        elev_colors = get_node_group_colors(n_groups)
        node_colors = [elev_colors[group] for group in elev_groups]
        
        # Node trace with colors by elevation range
        node_trace = go.Scatter3d(
            x=x_nodes,
            y=y_nodes,
            z=z_nodes,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                opacity=0.8,
                line=dict(width=1, color='rgba(0, 0, 0, 0.5)')
            ),
            text=node_labels,
            hoverinfo='text',
            hovertext=node_hover_texts,
            name='Nodes'
        )
        
        # Add a separate trace for each elevation group for legend
        node_traces = [node_trace]
        
        # Create a trace for each elevation group (for legend only)
        for i in range(n_groups):
            legend_trace = go.Scatter3d(
                x=[x_nodes[0]],
                y=[y_nodes[0]],
                z=[z_nodes[0]],
                mode='markers',
                marker=dict(
                    size=10,
                    color=elev_colors[i],
                    opacity=0.8
                ),
                name=f'Elev: {elev_min + i*group_size:.1f}-{elev_min + (i+1)*group_size:.1f}',
                showlegend=True,
                visible='legendonly'  # Hide the actual point, just show in legend
            )
            node_traces.append(legend_trace)
    else:
        # Simple display without grouping
        node_trace = go.Scatter3d(
            x=x_nodes,
            y=y_nodes,
            z=z_nodes,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                opacity=0.8,
                line=dict(width=1, color='rgba(0, 0, 0, 0.5)')
            ),
            text=node_labels,
            hoverinfo='text',
            hovertext=node_hover_texts,
            name='Nodes'
        )
        node_traces = [node_trace]

    # Create the figure
    fig = go.Figure(
        data=edge_traces + node_traces,
        layout=go.Layout(
            title='Hydraulic System Network',
            scene=dict(
                xaxis=dict(showticklabels=False, title=''),
                yaxis=dict(showticklabels=False, title=''),
                zaxis=dict(title='Elevation (scaled)')
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            legend=dict(
                title='Element Types',
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            hovermode='closest'
        )
    )
    
    return fig
