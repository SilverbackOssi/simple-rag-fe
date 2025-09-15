"""
Main Streamlit application for the RAG-based People and Business Intelligence Search Platform.
Stage 2: Core Component Development
"""
import streamlit as st
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.search import render_search, get_search_state
from components.results import render_results, get_stored_results
from components.graph import render_graph, render_graph_controls

# Page configuration
st.set_page_config(
    page_title="RAG Search Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "RAG-based People and Business Intelligence Search Platform"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        font-size: 12px;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
    }
    
    /* Info box styling */
    .stInfo {
        background-color: #e7f3ff;
        border-left: 4px solid #2196f3;
    }
    
    /* Error box styling */
    .stError {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    
    /* Success box styling */
    .stSuccess {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Application header
    st.title("🔍 RAG Search Platform")
    st.markdown("**People and Business Intelligence Search with Relationship Mapping**")
    
    # Initialize session state
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    
    # Render search interface (sidebar)
    query, mode, filters = render_search()
    
    # Get current search state
    search_performed, last_query, last_mode, last_filters = get_search_state()
    
    # Main content area
    if search_performed and last_query:
        # Create main layout columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📊 Search Results")
            
            # Render results
            results = render_results(last_query, last_mode, last_filters)
            
            # Add spacing
            st.divider()
            
            # Render graph visualization
            if results:
                relationships = results.get('relationships', [])
                render_graph(relationships)
        
        with col2:
            st.header("🎛️ Controls")
            render_graph_controls()
            
            # Search summary
            with st.expander("🔍 Search Summary", expanded=True):
                st.write(f"**Query:** {last_query}")
                st.write(f"**Mode:** {last_mode.title()}")
                if last_filters:
                    st.write(f"**Filters:** {', '.join(last_filters.get('entity_type', []))}")
            
            # Additional information
            with st.expander("ℹ️ About This Platform"):
                st.write("""
                This platform provides:
                - **Fast Retrieval**: Quick search across people and business data
                - **Enhanced Generation**: AI-powered insights and summaries
                - **Relationship Mapping**: Interactive visualization of connections
                - **Multi-Entity Search**: Filter by people, businesses, and assets
                """)
                
                st.write("**Backend API Endpoints:**")
                st.code("""
                /search - Main search functionality
                /graph - Relationship traversal
                /generate - AI summary generation
                /suggest - Query autocomplete
                """)
    
    else:
        # Welcome screen
        show_welcome_screen()

def show_welcome_screen():
    """Display the welcome screen when no search has been performed."""
    
    # Create centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👋 Welcome to the RAG Search Platform")
        st.write("""
        Get started by entering a search query in the sidebar. This platform helps you:
        
        🔍 **Search** across people, businesses, and assets  
        🤖 **Generate** AI-powered insights and summaries  
        🌐 **Visualize** relationships and connections  
        📊 **Analyze** aggregated data from multiple sources  
        """)
        
        st.info("💡 **Tip:** Use the sidebar to enter your search query and select filters to get started!")
    
    # Example queries section
    st.markdown("### 🎯 Example Queries")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **People Search:**
        - "John Smith CEO"
        - "Sarah Johnson LinkedIn"
        - "Tech startup founders"
        """)
    
    with col2:
        st.markdown("""
        **Business Search:**
        - "AI startups San Francisco"
        - "Healthcare companies"
        - "Fortune 500 CEOs"
        """)
    
    with col3:
        st.markdown("""
        **Relationship Search:**
        - "Board members connections"
        - "Investment relationships"
        - "Company acquisitions"
        """)
    
    # Feature highlights
    st.markdown("### ✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🚀 Fast Retrieval Mode**
        - Quick search results
        - Basic entity information
        - Structured data display
        - CSV export capability
        """)
    
    with col2:
        st.markdown("""
        **🧠 Enhanced Generation Mode**
        - AI-powered summaries
        - Contextual insights
        - Relationship analysis
        - Interactive visualizations
        """)
    
    # Backend status check
    st.markdown("### 🔧 System Status")
    
    # Simple backend connectivity check
    try:
        from utils.api import get_backend_url
        backend_url = get_backend_url()
        st.success(f"✅ Backend configured: {backend_url}")
        st.info("🔄 Backend connectivity will be verified when you perform your first search.")
    except Exception as e:
        st.warning(f"⚠️ Backend configuration issue: {e}")

if __name__ == "__main__":
    main()