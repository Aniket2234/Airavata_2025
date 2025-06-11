import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io
import sys
from pathlib import Path
from parser_1 import parse_hydraulic_file
from graph_builder import build_graph
from visualizer import create_network_visualization

st.set_page_config(
    page_title="Hydraulic System Visualizer",
    page_icon="🌊",
    layout="wide"
)

st.title("Hydraulic System Network Visualizer")

def find_data_file():
    """
    Find the complete_data.txt file in various possible locations
    Returns the path if found, None otherwise
    """
    # Get the current script directory
    current_dir = Path(__file__).parent.absolute()
    
    # Define possible file locations relative to the script
    possible_locations = [
        # Same directory as script
        current_dir / "complete_data.txt",
        
        # In attached_assets_parsed subdirectory
        current_dir / "attached_assets_parsed" / "complete_data.txt",
        
        # One level up, then in attached_assets_parsed
        current_dir.parent / "attached_assets_parsed" / "complete_data.txt",
        
        # Two levels up, then in attached_assets_parsed
        current_dir.parent.parent / "attached_assets_parsed" / "complete_data.txt",
        
        # In a data directory
        current_dir / "data" / "complete_data.txt",
        
        # In parent's data directory
        current_dir.parent / "data" / "complete_data.txt",
        
        # Look in common project structure locations
        current_dir / "visualization" / "attached_assets_parsed" / "complete_data.txt",
        current_dir.parent / "visualization" / "attached_assets_parsed" / "complete_data.txt",
        
        # Check if running from a different directory structure
        Path.cwd() / "attached_assets_parsed" / "complete_data.txt",
        Path.cwd() / "complete_data.txt",
    ]
    
    # Also check environment variable if set
    if "HYDRAULIC_DATA_PATH" in os.environ:
        env_path = Path(os.environ["HYDRAULIC_DATA_PATH"])
        possible_locations.insert(0, env_path)
    
    # Find the first existing file
    for path in possible_locations:
        if path.exists() and path.is_file():
            return str(path)
    
    return None

def create_sample_data_structure():
    """
    Create a sample directory structure guide for users
    """
    st.info("""
    **Expected Directory Structure:**
    
    ```
    your_project/
    ├── streamlit_app.py (this file)
    ├── parser_1.py
    ├── graph_builder.py
    ├── visualizer.py
    └── attached_assets_parsed/
        └── complete_data.txt
    ```
    
    **Alternative structures also supported:**
    - Place `complete_data.txt` in the same directory as this script
    - Set environment variable `HYDRAULIC_DATA_PATH` to point to your data file
    - Place data in a `data/` subdirectory
    """)

# Sidebar for controls
st.sidebar.header("Visualization Controls")

# Try to find the data file automatically
file_path = find_data_file()

if file_path:
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
        elements, nodes, connections = parse_hydraulic_file(file_content)
        st.sidebar.success(f"✅ Successfully loaded hydraulic system data")
        st.sidebar.info(f"📁 Using file: `{os.path.basename(file_path)}`")
        
        # Show the relative path for reference
        current_dir = Path(__file__).parent.absolute()
        try:
            relative_path = Path(file_path).relative_to(current_dir)
            st.sidebar.caption(f"Location: `./{relative_path}`")
        except ValueError:
            # If we can't make it relative, show the full path
            st.sidebar.caption(f"Location: `{file_path}`")
        
    except Exception as e:
        st.error(f"❌ Error parsing file: {str(e)}")
        st.stop()
else:
    # Show helpful information about expected structure
    st.warning("⚠️ Hydraulic system data file not found automatically.")
    
    with st.expander("📖 Setup Instructions", expanded=True):
        create_sample_data_structure()
        
        st.markdown("""
        **Quick Setup Options:**
        
        1. **Recommended**: Create an `attached_assets_parsed/` folder next to this script and place your `complete_data.txt` there
        
        2. **Simple**: Copy your data file to the same directory as this script and rename it to `complete_data.txt`
        
        3. **Advanced**: Set environment variable:
           ```bash
           export HYDRAULIC_DATA_PATH="/path/to/your/complete_data.txt"
           ```
        """)
    
    # Fallback to file uploader
    st.subheader("📤 Manual File Upload")
    uploaded_file = st.file_uploader(
        "Upload your hydraulic system file", 
        type=["OUT", "txt"],
        help="Upload a .OUT or .txt file containing hydraulic system data"
    )
    
    if uploaded_file is None:
        st.info("👆 Please upload a hydraulic system file to continue, or set up the automatic file detection above.")
        st.stop()
    
    # Parse the uploaded file
    try:
        file_content = uploaded_file.read().decode('utf-8')
        elements, nodes, connections = parse_hydraulic_file(file_content)
        st.sidebar.success(f"✅ Successfully parsed uploaded file: {uploaded_file.name}")
    except Exception as e:
        st.error(f"❌ Error parsing uploaded file: {str(e)}")
        st.stop()

# Options for visualization
if st.sidebar.checkbox("🔧 Show Advanced Options", value=False):
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 3D Network", 
    "📊 2D Flow Diagram", 
    "📈 Time Series", 
    "📋 Data Tables", 
    "ℹ️ System Info"
])

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
    with st.expander("ℹ️ About this visualization"):
        st.write("""
        This 3D visualization shows the hydraulic system network with:
        - **Nodes**: System elements (junctions, reservoirs, etc.) with size representing relative importance
        - **Edges**: Connections between elements (pipes, conduits, etc.)
        - **Colors**: Different element types
        - **Elevation**: Represented by node position in 3D space
        - **Hover information**: Detailed element properties
        
        **Interaction Controls:**
        - 🖱️ **Zoom**: Mouse wheel or pinch
        - 🔄 **Rotate**: Click and drag
        - 📋 **Details**: Hover over elements
        - 👆 **Pan**: Right-click and drag (or Shift+drag)
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
    
    # Assign colors to nodes based on type
    node_type_colors = {
        'reservoir': '#2E8B57',      # Sea Green
        'junction': '#DC143C',       # Crimson
        'conduit': '#4169E1',        # Royal Blue
        'dummy': '#FF8C00',          # Dark Orange
        'node': '#9370DB',           # Medium Purple
        'storage': '#8B4513',        # Saddle Brown
        'flowbalancing': '#FF1493',  # Deep Pink
        'unknown': '#696969'         # Dim Gray
    }
    
    node_colors = [node_type_colors.get(DG.nodes[n].get('type', 'unknown'), '#696969') for n in DG.nodes]
    
    # Assign colors to edges based on type
    edge_type_colors = {
        'conduit': '#4169E1',  # Royal Blue
        'dummy': '#FF8C00',    # Dark Orange
        'unknown': '#696969'   # Dim Gray
    }
    
    edge_colors = []
    for e in DG.edges:
        edge_type = DG.edges[e].get('type', 'unknown')
        edge_colors.append(edge_type_colors.get(edge_type, '#696969'))
    
    # Draw nodes
    nx.draw_networkx_nodes(DG, pos, node_size=700, node_color=node_colors, alpha=0.8)
    
    # Draw edges with arrows
    nx.draw_networkx_edges(DG, pos, edge_color=edge_colors, width=2, arrowsize=20, arrowstyle='->')
    
    # Draw labels
    nx.draw_networkx_labels(DG, pos, font_size=10, font_family='sans-serif')
    
    # Add a title
    plt.title("Hydraulic System Flow Diagram", fontsize=16, pad=20)
    plt.axis('off')
    
    # Convert plot to image
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    plt.close()
    
    # Display the plot
    st.image(buffer, use_column_width=True)
    
    st.info("""
    **Flow Diagram Legend:**
    - 🟢 **Reservoirs**: Water sources
    - 🔴 **Junctions**: Connection points  
    - 🔵 **Conduits**: Flow paths
    - 🟠 **Dummy elements**: System connectors
    - ➡️ **Arrows**: Flow direction (high to low elevation)
    """)

with tab3:
    # Create a time series graph visualization
    st.subheader("Element Data Time Series")
    
    # Get node elevation data for time series graph
    elevation_data = []
    node_ids = []
    
    # Extract elevation data for nodes
    for node_id, node_data in nodes.items():
        if node_data.get('elevation') is not None:
            elevation_data.append(node_data.get('elevation'))
            node_ids.append(f"Node {node_id}")
    
    if not elevation_data:
        st.warning("No elevation data available for time series visualization.")
        st.stop()
    
    # Sort data by node ID for consistency
    sorted_data = sorted(zip(node_ids, elevation_data), key=lambda x: x[0])
    node_ids = [item[0] for item in sorted_data]
    elevation_data = [item[1] for item in sorted_data]
    
    # Create simulated time data (since we don't have actual time data)
    import numpy as np
    time_points = 10
    time_labels = [f"T{i}" for i in range(1, time_points+1)]
    
    # Generate simulated data for each node across time points
    np.random.seed(42)  # For reproducible results
    
    # Create a DataFrame to hold the time series data
    time_series_data = {}
    
    # Initialize with the base elevations (repeated across time points)
    for i, node_id in enumerate(node_ids):
        base_elevation = elevation_data[i]
        # Generate slight variations of the base elevation over time
        time_series = base_elevation + np.random.normal(0, abs(base_elevation) * 0.01, time_points)
        time_series_data[node_id] = time_series
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(time_series_data, index=time_labels)
    
    # Create row selection for nodes to display
    st.write("**Select nodes to display in the graph:**")
    col1, col2, col3 = st.columns(3)
    
    # Checkboxes for node selection, up to 15 nodes to avoid cluttering
    selected_nodes = []
    display_nodes = node_ids[:15] if len(node_ids) > 15 else node_ids
    
    for i, node_id in enumerate(display_nodes):
        if i % 3 == 0:
            selected = col1.checkbox(node_id, value=(i < 3))  # Default select first 3 nodes
        elif i % 3 == 1:
            selected = col2.checkbox(node_id, value=(i < 3))
        else:
            selected = col3.checkbox(node_id, value=(i < 3))
        
        if selected:
            selected_nodes.append(node_id)
    
    if not selected_nodes:
        st.warning("Please select at least one node to display.")
    else:
        # Create the line graph using Plotly
        fig = go.Figure()
        
        # Color palette for different nodes
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for i, node in enumerate(selected_nodes):
            fig.add_trace(go.Scatter(
                x=time_labels, 
                y=df[node], 
                mode='lines+markers',
                name=node,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            ))
        
        # Update layout
        fig.update_layout(
            title="📈 Node Elevation Time Series",
            xaxis_title="Time Point",
            yaxis_title="Elevation",
            height=500,
            legend_title="Nodes",
            hovermode="x unified",
            template="plotly_white"
        )
        
        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    # Explanation
    st.info("""
    📊 **Note:** This graph shows simulated time series data based on node elevations. 
    In a real implementation, this would display actual time-varying data from the hydraulic system sensors.
    """)

with tab4:
    # Display data tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Nodes")
        nodes_df = pd.DataFrame([{**node, 'id': node_id} for node_id, node in nodes.items()])
        if not nodes_df.empty:
            st.dataframe(nodes_df, use_container_width=True, height=300)
        else:
            st.info("No node data available")
    
    with col2:
        st.subheader("🔀 Connections")
        connections_df = pd.DataFrame(connections)
        if not connections_df.empty:
            st.dataframe(connections_df, use_container_width=True, height=300)
        else:
            st.info("No connection data available")
    
    st.subheader("⚙️ Element Properties")
    elements_df = pd.DataFrame([{**elem, 'id': elem_id} for elem_id, elem in elements.items()])
    if not elements_df.empty:
        st.dataframe(elements_df, use_container_width=True, height=400)
    else:
        st.info("No element property data available")

with tab5:
    # System information
    st.subheader("📊 System Overview")
    
    # Calculate basic stats
    num_nodes = len(nodes)
    num_connections = len(connections)
    num_elements = len(elements)
    
    # Element type analysis
    node_types = {}
    for elem in elements.values():
        elem_type = elem.get('type', 'Unknown')
        node_types[elem_type] = node_types.get(elem_type, 0) + 1
    
    # Display stats in a nice grid
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔗 Total Nodes", num_nodes)
    col2.metric("🔀 Total Connections", num_connections)
    col3.metric("⚙️ Total Elements", num_elements)
    col4.metric("🏷️ Element Types", len(node_types))
    
    # Display element type breakdown
    if node_types:
        st.subheader("📈 Element Type Distribution")
        type_df = pd.DataFrame({
            'Type': list(node_types.keys()),
            'Count': list(node_types.values())
        })
        
        # Create a bar chart with Plotly for better styling
        fig = go.Figure(data=[
            go.Bar(x=type_df['Type'], y=type_df['Count'],
                  marker_color='#1f77b4',
                  text=type_df['Count'],
                  textposition='auto')
        ])
        fig.update_layout(
            title="Element Types in Hydraulic System",
            xaxis_title="Element Type",
            yaxis_title="Count",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Elevation analysis
    st.subheader("📏 Elevation Analysis")
    elev_values = []
    elev_nodes = []
    
    for node_id, node in nodes.items():
        if node.get('elevation') is not None:
            elev_values.append(node.get('elevation'))
            elev_nodes.append(str(node_id))
    
    if elev_values:
        # Create elevation statistics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📈 Max Elevation", f"{max(elev_values):.2f}")
        col2.metric("📉 Min Elevation", f"{min(elev_values):.2f}")
        col3.metric("📊 Mean Elevation", f"{sum(elev_values)/len(elev_values):.2f}")
        col4.metric("📏 Elevation Range", f"{max(elev_values) - min(elev_values):.2f}")
        
        # Create elevation chart
        elev_df = pd.DataFrame({
            'Node': elev_nodes,
            'Elevation': elev_values
        })
        
        # Sort by elevation for better visualization
        elev_df = elev_df.sort_values('Elevation')
        
        fig = go.Figure(data=[
            go.Bar(x=elev_df['Node'], y=elev_df['Elevation'],
                  marker_color='#2ca02c',
                  name='Elevation')
        ])
        fig.update_layout(
            title="Node Elevations",
            xaxis_title="Node ID",
            yaxis_title="Elevation",
            template="plotly_white",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No elevation data available")
    
    # File information
    if file_path:
        st.subheader("📁 File Information")
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        col1, col2 = st.columns(2)
        col1.info(f"**File Size:** {file_size:,} bytes ({file_size/1024:.1f} KB)")
        col2.info(f"**File Path:** `{os.path.basename(file_path)}`")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    🌊 <strong>Hydraulic System Network Visualizer</strong><br>
    Built with Streamlit • NetworkX • Plotly
</div>
""", unsafe_allow_html=True)