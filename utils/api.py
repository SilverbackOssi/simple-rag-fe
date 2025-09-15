"""
API utility functions for backend communication.
"""
import requests
import streamlit as st
from typing import Dict, List, Any, Optional
import json

# Default backend URL - can be configured via environment or Streamlit secrets
DEFAULT_BACKEND_URL = "http://localhost:8000"

def get_backend_url() -> str:
    """Get backend URL from Streamlit secrets or environment."""
    try:
        return st.secrets.get("BACKEND_URL", DEFAULT_BACKEND_URL)
    except:
        return DEFAULT_BACKEND_URL

def call_search_api(query: str, mode: str, filters: Dict[str, Any]) -> Optional[Dict]:
    """
    Call the /search endpoint.
    
    Args:
        query: Search query string
        mode: "fast" or "enhanced"
        filters: Dictionary with entity_type filter
        
    Returns:
        API response as dictionary or None if error
    """
    if not query.strip():
        return None
        
    backend_url = get_backend_url()
    url = f"{backend_url}/search"
    
    payload = {
        "q": query,
        "mode": mode,
        "filters": filters
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to backend server. Please ensure the backend is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

def call_suggest_api(partial_query: str) -> List[str]:
    """
    Call the /suggest endpoint for autocomplete.
    
    Args:
        partial_query: Partial search query
        
    Returns:
        List of suggestions
    """
    if len(partial_query.strip()) <= 2:
        return []
        
    backend_url = get_backend_url()
    url = f"{backend_url}/suggest"
    
    try:
        response = requests.get(url, params={"q": partial_query}, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("suggestions", [])
    except:
        # Silently fail for suggestions to avoid UI disruption
        return []

def call_graph_api(entity_id: str, depth: int = 1) -> Optional[Dict]:
    """
    Call the /graph endpoint for relationship data.
    
    Args:
        entity_id: ID of the entity to explore
        depth: Traversal depth (1-3)
        
    Returns:
        Graph data with nodes and edges or None if error
    """
    backend_url = get_backend_url()
    url = f"{backend_url}/graph"
    
    try:
        response = requests.get(url, params={"entity_id": entity_id, "depth": depth}, timeout=30)
        response.raise_for_status()
        return response.json()
    except:
        return None

def call_generate_api(context: Dict) -> Optional[str]:
    """
    Call the /generate endpoint for AI summaries.
    
    Args:
        context: Context data for generation
        
    Returns:
        Generated summary text or None if error
    """
    backend_url = get_backend_url()
    url = f"{backend_url}/generate"
    
    try:
        response = requests.post(url, json={"context": context}, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("summary", "")
    except:
        return None