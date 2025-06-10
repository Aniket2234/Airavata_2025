import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io
import sys
from JayShreeRam.parser_1 import parse_hydraulic_file
from graph_builder import build_graph
from visualizer import create_network_visualization

st.set_page_config(
    page_title="Hydraulic System Visualizer",
    page_icon="🌊",
    layout="wide"
)

st.title("Hydraulic System Network Visualizer")

# Define the path where final_out function copies the selected file
default_file_path = os.path.join("attached_assets_parsed", "complete_data.txt")

# Also look for the file in the absolute path if the relative path fails
absolute_default_path = os.path.join("C:/Users/Aniket/Desktop/SIH Software/Airavata_Project", 
                                    "visualization", "attached_assets_parsed", "complete_data.txt")

# Check all possible locations where the file might exist
possible_paths = [
    default_file_path,
    absolute_default_path,
    "complete_data.txt",
    "../attached_assets_parsed/complete_data.txt",
    "../../attached_assets_parsed/complete_data.txt"
]

# Find the first path that exists
file_path = None
for path in possible_paths:
    if os.path.exists(path):
        file_path = path
        break

# Sidebar for controls
st.sidebar.header("Visualization Controls")

# Process the file that was copied by the final_out function
if file_path:
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
        elements, nodes, connections = parse_hydraulic_file(file_content)
        st.sidebar.success(f"Successfully loaded hydraulic system data")
        
        # Display the filename
        filename = os.path.basename(file_path)
        st.write(f"Visualizing data from: **{filename}**")
        
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        st.stop()
else:
    # Only show file uploader if we couldn't find the file anywhere
    st.warning("The selected file couldn't be found. Please upload a file manually.")
    uploaded_file = st.file_uploader("Upload Hydraulic System File", type=["OUT", "txt"])
    
    if uploaded_file is None:
        st.info("Please upload a hydraulic system file to continue.")
        st.stop()
    
    # Parse the uploaded file
    file_content = uploaded_file.read().decode()
    elements, nodes, connections = parse_hydraulic_file(file_content)
    st.sidebar.success(f"Successfully parsed file: {uploaded_file.name}")

# Options for visualization
if st.sidebar.checkbox("Show Advanced Options", value=False):
    node_size_factor = st.sidebar.slider("Node Size Factor", 5, 50, 20)
    edge_width_factor = st.sidebar.slider("Edge Width Factor", 1, 10, 3)
    elev_scale_factor = st.sidebar.slider("Elevation Scale Factor", 0.1, 10.0, 1.0)
else:
    node_size_factor = 20
    edge_width_factor = 3
    elev_scale_factor = 1.0

# Node grouping option
group_by = st.sidebar.selectbox(
    "Group nodes by:",
    ["Element Type", "Elevation Range", "None"]
)

# Build the network graph
G = build_graph(elements, nodes, connections)

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs(["3D Network Visualization", "2D Flow Diagram", "Time Series Graph", "Data Tables", "System Information"])

with tab1:
    # Create and display the 3D graph visualization
    fig = create_network_visualization(
        G, 
        node_size_factor=node_size_factor, 
        edge_width_factor=edge_width_factor,
        elev_scale_factor=elev_scale_factor,
        group_by=group_by
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Description of the visualization
    with st.expander("About this visualization"):
        st.write("""
        This 3D visualization shows the hydraulic system network with:
        - **Nodes**: System elements (junctions, reservoirs, etc.) with size representing relative importance
        - **Edges**: Connections between elements (pipes, conduits, etc.)
        - **Colors**: Different element types
        - **Elevation**: Represented by node position in 3D space
        - **Hover information**: Detailed element properties
        
        You can:
        - Zoom in/out using mouse wheel
        - Rotate view by clicking and dragging
        - Hover over elements to see details
        - Pan by right-clicking and dragging
        """)
        
with tab2:
    st.subheader("2D Flow Diagram")
    
    # Use a simpler approach for 2D visualization without the Matplotlib complexity
    import networkx as nx
    import matplotlib.pyplot as plt
    from io import BytesIO
    
    # Create a directed graph for flow visualization
    DG = nx.DiGraph()
    
    # Add nodes with their attributes
    for node_id, node_data in nodes.items():
        DG.add_node(
            node_id,
            type=node_data.get('type', 'node'),
            elevation=node_data.get('elevation', 0)
        )
    
    # Add edges with direction (assuming water flows from higher to lower elevation)
    for conn in connections:
        source = conn['source']
        target = conn['target']
        elem_id = conn['id']
        
        # Get node elevations to determine flow direction
        source_elev = nodes.get(source, {}).get('elevation', 0)
        target_elev = nodes.get(target, {}).get('elevation', 0)
        
        # Add the edge (direction based on elevation if available, otherwise use given direction)
        if source_elev is not None and target_elev is not None:
            # Water flows from higher to lower elevation
            if source_elev >= target_elev:
                DG.add_edge(source, target, id=elem_id, type=conn['type'])
            else:
                DG.add_edge(target, source, id=elem_id, type=conn['type'])
        else:
            # Default direction if elevation is not available
            DG.add_edge(source, target, id=elem_id, type=conn['type'])
    
    # Create the figure
    plt.figure(figsize=(12, 8))
    
    # Create layout (hierarchical for flow direction)
    pos = nx.spring_layout(DG, seed=42)
    
    # Get node types for coloring
    node_types = [DG.nodes[n].get('type', 'unknown') for n in DG.nodes()]
    unique_types = list(set(node_types))
    type_to_color = {t: i for i, t in enumerate(unique_types)}
    node_colors = [type_to_color[t] for t in node_types]
    
    # Get edge types for coloring
    edge_types = [DG.edges[e].get('type', 'unknown') for e in DG.edges()]
    unique_edge_types = list(set(edge_types))
    edge_type_to_color = {t: i for i, t in enumerate(unique_edge_types)}
    edge_colors = [edge_type_to_color[t] for t in edge_types]
    
    # Draw the graph with basic colors
    # Map node types to colors using a simple mapping
    node_type_colors = {
        'reservoir': 'green',
        'junction': 'red',
        'conduit': 'blue',
        'dummy': 'orange',
        'node': 'purple',
        'storage': 'brown',
        'flowbalancing': 'pink',
        'unknown': 'gray'
    }
    
    # Assign colors to nodes based on type
    node_colors = [node_type_colors.get(DG.nodes[n].get('type', 'unknown'), 'gray') for n in DG.nodes]
    
    # Assign colors to edges based on type
    edge_colors = []
    edge_type_colors = {
        'conduit': 'blue',
        'dummy': 'orange',
        'unknown': 'gray'
    }
    
    for e in DG.edges:
        edge_type = DG.edges[e].get('type', 'unknown')
        edge_colors.append(edge_type_colors.get(edge_type, 'gray'))
    
    # Create the figure
    plt.figure(figsize=(12, 8))
    
    # Draw nodes
    nx.draw_networkx_nodes(DG, pos, node_size=700, node_color=node_colors, alpha=0.8)
    
    # Draw edges with arrows
    nx.draw_networkx_edges(DG, pos, edge_color=edge_colors, width=2, arrowsize=20, arrowstyle='->')
    
    # Draw labels
    nx.draw_networkx_labels(DG, pos, font_size=10, font_family='sans-serif')
    
    # Add a title
    plt.title("Hydraulic System Flow Diagram", fontsize=16)
    plt.axis('off')
    
    # Convert plot to image
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    plt.close()
    
    # Display the plot
    st.image(buffer, use_column_width=True)
    
    st.write("""
    This 2D flow diagram shows:
    - **Direction of flow**: Arrows indicate flow direction (generally from higher to lower elevation)
    - **Element types**: Different colors represent different element types
    - **System connectivity**: Shows how elements are connected in the hydraulic system
    
    This diagram helps to understand the flow path and connectivity between different components of the hydraulic system.
    """)

with tab3:
    # Create a time series graph visualization
    st.subheader("Element Data Time Series Graph")
    
    # Get node elevation data for time series graph
    elevation_data = []
    node_ids = []
    
    # Extract elevation data for nodes
    for node_id, node_data in nodes.items():
        if node_data.get('elevation') is not None:
            elevation_data.append(node_data.get('elevation'))
            node_ids.append(f"Node {node_id}")
    
    # Sort data by node ID for consistency
    sorted_data = sorted(zip(node_ids, elevation_data), key=lambda x: x[0])
    node_ids = [item[0] for item in sorted_data]
    elevation_data = [item[1] for item in sorted_data]
    
    # Create simulated time data (since we don't have actual time data)
    # This will create 10 timepoints with slight variations for demonstration
    import numpy as np
    time_points = 10
    time_labels = [f"T{i}" for i in range(1, time_points+1)]
    
    # Generate simulated data for each node across time points
    # Use elevation as baseline and add small random variations
    np.random.seed(42)  # For reproducible results
    
    # Create a DataFrame to hold the time series data
    time_series_data = {}
    
    # Initialize with the base elevations (repeated across time points)
    for i, node_id in enumerate(node_ids):
        base_elevation = elevation_data[i]
        # Generate slight variations of the base elevation over time
        time_series = base_elevation + np.random.normal(0, base_elevation * 0.01, time_points)
        time_series_data[node_id] = time_series
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(time_series_data, index=time_labels)
    
    # Create row selection for nodes to display
    st.write("Select nodes to display in the graph:")
    col1, col2, col3 = st.columns(3)
    
    # Checkboxes for node selection, up to 10 nodes to avoid cluttering
    selected_nodes = []
    display_nodes = node_ids[:10] if len(node_ids) > 10 else node_ids
    
    for i, node_id in enumerate(display_nodes):
        if i % 3 == 0:
            selected = col1.checkbox(node_id, value=(i < 3))  # Default select first 3 nodes
        elif i % 3 == 1:
            selected = col2.checkbox(node_id, value=(i < 3))
        else:
            selected = col3.checkbox(node_id, value=(i < 3))
        
        if selected:
            selected_nodes.append(node_id)
    
    # Create the line graph using Plotly
    fig = go.Figure()
    
    for node in selected_nodes:
        fig.add_trace(go.Scatter(
            x=time_labels, 
            y=df[node], 
            mode='lines+markers',
            name=node
        ))
    
    # Update layout
    fig.update_layout(
        title="Node Elevation Time Series",
        xaxis_title="Time Point",
        yaxis_title="Elevation",
        height=500,
        legend_title="Nodes",
        hovermode="x unified"
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Explanation
    st.info("""
    **Note:** This graph shows simulated time series data based on node elevations. 
    In a real implementation, this would use actual time-varying data from the hydraulic system.
    You can select which nodes to display using the checkboxes above.
    """)

with tab4:
    # Display data tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Nodes")
        nodes_df = pd.DataFrame([node for node in nodes.values()])
        if not nodes_df.empty:
            st.dataframe(nodes_df, use_container_width=True)
        else:
            st.info("No node data available")
    
    with col2:
        st.subheader("Connections")
        connections_df = pd.DataFrame(connections)
        if not connections_df.empty:
            st.dataframe(connections_df, use_container_width=True)
        else:
            st.info("No connection data available")
    
    st.subheader("Element Properties")
    elements_df = pd.DataFrame([elem for elem in elements.values()])
    if not elements_df.empty:
        st.dataframe(elements_df, use_container_width=True)
    else:
        st.info("No element property data available")

with tab5:
    # System information
    st.subheader("System Overview")
    
    # Calculate basic stats
    num_nodes = len(nodes)
    num_connections = len(connections)
    node_types = {}
    for elem in elements.values():
        elem_type = elem.get('type', 'Unknown')
        if elem_type not in node_types:
            node_types[elem_type] = 0
        node_types[elem_type] += 1
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Nodes", num_nodes)
    col2.metric("Total Connections", num_connections)
    col3.metric("Element Types", len(node_types))
    
    # Display element type breakdown
    st.subheader("Element Type Distribution")
    type_df = pd.DataFrame({
        'Type': list(node_types.keys()),
        'Count': list(node_types.values())
    })
    st.bar_chart(type_df.set_index('Type'))
    
    # Elevation analysis
    st.subheader("Elevation Analysis")
    elev_values = [node.get('elevation', 0) for node in nodes.values()]
    if elev_values:
        elev_df = pd.DataFrame({
            'Node': list(nodes.keys()),
            'Elevation': elev_values
        })
        st.bar_chart(elev_df.set_index('Node'))
    else:
        st.info("No elevation data available")

# Footer
st.markdown("---")
st.caption("Hydraulic System Network Visualizer - Created with Streamlit, NetworkX, and Plotly")