"""
Search interface component for the RAG frontend.
"""
import streamlit as st
from typing import Tuple, Dict, List
from utils.api import call_suggest_api

def render_search() -> Tuple[str, str, Dict]:
    """
    Render the search interface in the sidebar.
    
    Returns:
        Tuple of (query, mode, filters)
    """
    st.sidebar.header("🔍 Search Interface")
    
    # Initialize session state for suggestions
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []
    if 'selected_suggestion' not in st.session_state:
        st.session_state.selected_suggestion = ""
    
    # Main search input
    query = st.sidebar.text_input(
        label="Search Query",
        key="query",
        placeholder="Enter your search query...",
        help="Search for people, businesses, or assets"
    )
    
    # Handle autocomplete suggestions
    if query and len(query) > 2 and query != st.session_state.selected_suggestion:
        # Only fetch suggestions if query changed
        suggestions = call_suggest_api(query)
        if suggestions and suggestions != st.session_state.suggestions:
            st.session_state.suggestions = suggestions
    
    # Show suggestions if available
    if st.session_state.suggestions and query:
        selected_suggestion = st.sidebar.selectbox(
            "Suggestions",
            options=[""] + st.session_state.suggestions,
            key="suggestion_select",
            help="Select a suggestion or continue typing"
        )
        
        # If user selects a suggestion, update the query
        if selected_suggestion and selected_suggestion != st.session_state.selected_suggestion:
            st.session_state.selected_suggestion = selected_suggestion
            st.session_state.query = selected_suggestion
            # Clear suggestions after selection
            st.session_state.suggestions = []
            st.rerun()
    
    # Search mode selection
    mode_display = st.sidebar.selectbox(
        label="Search Mode",
        options=["Fast Retrieval", "Enhanced Generation"],
        key="mode",
        help="Fast: Quick results, Enhanced: AI-powered insights"
    )
    
    # Map display names to API values
    mode = "fast" if mode_display == "Fast Retrieval" else "enhanced"
    
    # Entity type filters
    entity_filters = st.sidebar.multiselect(
        label="Entity Type Filters",
        options=["People", "Business", "Assets"],
        key="filters",
        help="Filter results by entity type"
    )
    
    # Map display names to API values
    filters = {}
    if entity_filters:
        # Convert to lowercase for API
        api_filters = []
        for f in entity_filters:
            if f == "People":
                api_filters.append("people")
            elif f == "Business":
                api_filters.append("business")
            elif f == "Assets":
                api_filters.append("assets")
        
        if api_filters:
            filters["entity_type"] = api_filters
    
    # Advanced options
    with st.sidebar.expander("Advanced Options"):
        max_results = st.number_input(
            "Max Results",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="Maximum number of results to return"
        )
        
        # Add max_results to filters if different from default
        if max_results != 50:
            filters["max_results"] = max_results
    
    # Search button and validation
    search_disabled = not query or not query.strip()
    
    if search_disabled:
        st.sidebar.info("💡 Enter a search query to begin")
    
    search_clicked = st.sidebar.button(
        "🚀 Search",
        disabled=search_disabled,
        type="primary",
        use_container_width=True
    )
    
    # Store search state
    if search_clicked and not search_disabled:
        st.session_state.search_performed = True
        st.session_state.last_query = query
        st.session_state.last_mode = mode
        st.session_state.last_filters = filters
    
    # Clear results button
    if st.session_state.get('search_performed', False):
        if st.sidebar.button("🗑️ Clear Results", use_container_width=True):
            # Clear search state
            for key in ['search_performed', 'last_query', 'last_mode', 'last_filters', 'search_results']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    return query, mode, filters

def get_search_state() -> Tuple[bool, str, str, Dict]:
    """
    Get the current search state from session state.
    
    Returns:
        Tuple of (search_performed, query, mode, filters)
    """
    search_performed = st.session_state.get('search_performed', False)
    query = st.session_state.get('last_query', '')
    mode = st.session_state.get('last_mode', 'fast')
    filters = st.session_state.get('last_filters', {})
    
    return search_performed, query, mode, filters