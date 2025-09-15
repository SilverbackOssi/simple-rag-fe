"""
Graph visualization component for the RAG frontend.
"""
import streamlit as st
from pyvis.network import Network
import tempfile
import os
from typing import List, Dict, Optional
from utils.api import call_graph_api

def render_graph(relationships: Optional[List[Dict]] = None):
    """
    Render interactive graph visualization.
    
    Args:
        relationships: List of relationship data from search results
    """
    st.subheader("🌐 Relationship Graph")
    
    # Get relationships from session state if not provided
    if relationships is None:
        search_results = st.session_state.get('search_results', {})
        relationships = search_results.get('relationships', [])
    
    # Check if we have any relationship data
    if not relationships:
        st.info("🔍 No relationship data found. Try searching for entities with known connections.")
        return
    
    # Graph controls
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        depth = st.slider(
            label="Traversal Depth",
            min_value=1,
            max_value=3,
            value=1,
            key="graph_depth",
            help="How many relationship hops to explore"
        )
    
    with col2:
        layout = st.selectbox(
            "Layout Algorithm",
            options=["hierarchical", "physics", "circular"],
            key="graph_layout",
            help="Graph layout style"
        )
    
    with col3:
        show_labels = st.checkbox(
            "Show Labels",
            value=True,
            key="show_labels",
            help="Display node labels"
        )
    
    # Advanced options
    with st.expander("🔧 Advanced Graph Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            node_size = st.slider("Node Size", 10, 50, 25, key="node_size")
            edge_width = st.slider("Edge Width", 1, 10, 3, key="edge_width")
        
        with col2:
            max_nodes = st.number_input(
                "Max Nodes",
                min_value=10,
                max_value=100,
                value=50,
                key="max_nodes",
                help="Limit nodes for performance"
            )
    
    try:
        # Create the network graph
        net = create_network_graph(
            relationships,
            depth=depth,
            layout=layout,
            show_labels=show_labels,
            node_size=node_size,
            edge_width=edge_width,
            max_nodes=max_nodes
        )
        
        if net is None:
            st.warning("⚠️ No graph data could be processed.")
            return
        
        # Generate and display the graph
        with st.spinner("Generating graph visualization..."):
            # Create a temporary file for the graph HTML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
                net.write_html(tmp_file.name)
                tmp_file_path = tmp_file.name
            
            try:
                # Read the HTML content
                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Display the graph
                st.components.v1.html(html_content, height=500, scrolling=True)
                
                # Graph statistics
                st.info(f"📊 Displaying {len(net.get_nodes())} nodes and {len(net.get_edges())} edges")
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
    
    except Exception as e:
        st.error(f"❌ Error creating graph visualization: {e}")
        
        # Fallback: show raw relationship data
        with st.expander("🔍 View Raw Relationship Data"):
            st.json(relationships)

def create_network_graph(
    relationships: List[Dict],
    depth: int = 1,
    layout: str = "physics",
    show_labels: bool = True,
    node_size: int = 25,
    edge_width: int = 3,
    max_nodes: int = 50
) -> Optional[Network]:
    """
    Create a PyVis network graph from relationship data.
    
    Args:
        relationships: List of relationship dictionaries
        depth: Traversal depth
        layout: Layout algorithm
        show_labels: Whether to show node labels
        node_size: Size of nodes
        edge_width: Width of edges
        max_nodes: Maximum number of nodes to display
        
    Returns:
        PyVis Network object or None if error
    """
    try:
        # Initialize the network
        net = Network(
            height="500px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000"
        )
        
        # Configure physics based on layout
        if layout == "physics":
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "stabilization": {"iterations": 100}
                }
            }
            """)
        elif layout == "hierarchical":
            net.set_options("""
            {
                "layout": {
                    "hierarchical": {
                        "enabled": true,
                        "direction": "UD"
                    }
                },
                "physics": {"enabled": false}
            }
            """)
        elif layout == "circular":
            net.set_options("""
            {
                "layout": {
                    "randomSeed": 42
                },
                "physics": {"enabled": false}
            }
            """)
        
        # Track nodes and edges to avoid duplicates
        added_nodes = set()
        added_edges = set()
        node_count = 0
        
        # Process relationship data
        for relationship in relationships:
            if node_count >= max_nodes:
                break
                
            nodes = relationship.get('nodes', [])
            edges = relationship.get('edges', [])
            
            # Add nodes
            for node in nodes:
                if node_count >= max_nodes:
                    break
                    
                node_id = node.get('id', str(node_count))
                
                if node_id not in added_nodes:
                    label = node.get('name', node.get('label', str(node_id)))
                    node_type = node.get('type', 'unknown')
                    
                    # Color nodes based on type
                    color = get_node_color(node_type)
                    
                    # Add node
                    net.add_node(
                        node_id,
                        label=label if show_labels else "",
                        color=color,
                        size=node_size,
                        title=f"{label} ({node_type})"  # Tooltip
                    )
                    
                    added_nodes.add(node_id)
                    node_count += 1
            
            # Add edges
            for edge in edges:
                if node_count >= max_nodes:
                    break
                    
                source = edge.get('source', edge.get('from'))
                target = edge.get('target', edge.get('to'))
                edge_type = edge.get('type', edge.get('relationship', 'connected'))
                
                if source and target:
                    edge_key = f"{source}-{target}-{edge_type}"
                    reverse_key = f"{target}-{source}-{edge_type}"
                    
                    if edge_key not in added_edges and reverse_key not in added_edges:
                        # Ensure both nodes exist
                        if source not in added_nodes and node_count < max_nodes:
                            net.add_node(source, label=str(source), size=node_size//2)
                            added_nodes.add(source)
                            node_count += 1
                        
                        if target not in added_nodes and node_count < max_nodes:
                            net.add_node(target, label=str(target), size=node_size//2)
                            added_nodes.add(target)
                            node_count += 1
                        
                        # Add edge
                        net.add_edge(
                            source,
                            target,
                            label=edge_type if show_labels else "",
                            width=edge_width,
                            title=edge_type  # Tooltip
                        )
                        
                        added_edges.add(edge_key)
        
        # If no nodes were added from relationships, try to create from search results
        if len(added_nodes) == 0:
            search_results = st.session_state.get('search_results', {})
            net = create_graph_from_search_results(search_results, show_labels, node_size)
        
        return net if len(added_nodes) > 0 else None
        
    except Exception as e:
        st.error(f"Error creating network graph: {e}")
        return None

def create_graph_from_search_results(search_results: Dict, show_labels: bool, node_size: int) -> Optional[Network]:
    """
    Create a simple graph from search results when no relationship data is available.
    
    Args:
        search_results: Search results dictionary
        show_labels: Whether to show labels
        node_size: Size of nodes
        
    Returns:
        PyVis Network object or None
    """
    try:
        net = Network(height="500px", width="100%", bgcolor="#ffffff", font_color="#000000")
        
        node_id = 0
        
        # Add business nodes
        businesses = search_results.get('business', [])
        for business in businesses[:10]:  # Limit to 10
            name = business.get('name', f'Business {node_id}')
            net.add_node(
                node_id,
                label=name if show_labels else "",
                color="#FF6B6B",  # Red for business
                size=node_size,
                title=f"Business: {name}"
            )
            node_id += 1
        
        # Add owner nodes and connect to businesses
        owners = search_results.get('owners', [])
        business_count = len(businesses[:10])
        
        for i, owner in enumerate(owners[:10]):  # Limit to 10
            name = owner.get('name', f'Person {node_id}')
            net.add_node(
                node_id,
                label=name if show_labels else "",
                color="#4ECDC4",  # Teal for people
                size=node_size,
                title=f"Person: {name}"
            )
            
            # Connect to a business if available
            if business_count > 0:
                business_node = i % business_count
                net.add_edge(business_node, node_id, label="affiliated")
            
            node_id += 1
        
        return net if node_id > 0 else None
        
    except Exception as e:
        st.error(f"Error creating fallback graph: {e}")
        return None

def get_node_color(node_type: str) -> str:
    """
    Get color for node based on its type.
    
    Args:
        node_type: Type of the node
        
    Returns:
        Color string
    """
    color_map = {
        'person': '#4ECDC4',      # Teal
        'business': '#FF6B6B',    # Red
        'organization': '#FFD93D', # Yellow
        'location': '#6BCF7F',    # Green
        'asset': '#A8E6CF',       # Light green
        'social': '#FFB347',      # Orange
        'unknown': '#95A5A6'      # Gray
    }
    
    return color_map.get(node_type.lower(), color_map['unknown'])

def render_graph_controls():
    """Render additional graph control options."""
    st.subheader("🎛️ Graph Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Graph", use_container_width=True):
            # Clear any cached graph data and regenerate
            if 'graph_cache' in st.session_state:
                del st.session_state['graph_cache']
            st.rerun()
    
    with col2:
        if st.button("📥 Export Graph Data", use_container_width=True):
            search_results = st.session_state.get('search_results', {})
            relationships = search_results.get('relationships', [])
            
            if relationships:
                import json
                graph_data = json.dumps(relationships, indent=2)
                st.download_button(
                    label="💾 Download JSON",
                    data=graph_data,
                    file_name="graph_data.json",
                    mime="application/json"
                )
            else:
                st.info("No graph data to export.")