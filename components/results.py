"""
Results display component for the RAG frontend.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Optional
from utils.api import call_search_api

def render_results(query: str, mode: str, filters: Dict) -> Optional[Dict]:
    """
    Render search results with different sections.
    
    Args:
        query: Search query string
        mode: Search mode ("fast" or "enhanced")
        filters: Search filters dictionary
        
    Returns:
        API response dictionary for use by other components
    """
    if not query or not query.strip():
        return None
    
    # Show loading spinner while fetching results
    with st.spinner(f"Searching for '{query}'..."):
        response = call_search_api(query, mode, filters)
    
    if response is None:
        st.error("❌ Failed to fetch results. Please check your connection and try again.")
        
        # Retry button
        if st.button("🔄 Retry Search"):
            st.rerun()
        return None
    
    # Store results in session state for other components
    st.session_state.search_results = response
    
    # Check if we have any results
    has_business = response.get("business") and len(response["business"]) > 0
    has_owners = response.get("owners") and len(response["owners"]) > 0
    has_socials = response.get("socials") and len(response["socials"]) > 0
    has_ai_summary = response.get("ai_summary") and mode == "enhanced"
    has_relationships = response.get("relationships") and len(response["relationships"]) > 0
    
    if not any([has_business, has_owners, has_socials, has_ai_summary]):
        st.info("🔍 No matches found. Try adjusting your query or filters.")
        return response
    
    # Display results summary
    st.subheader(f"📊 Search Results for: '{query}'")
    
    # Results summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        business_count = len(response.get("business", []))
        st.metric("Businesses", business_count)
    
    with col2:
        owners_count = len(response.get("owners", []))
        st.metric("People", owners_count)
    
    with col3:
        socials_count = len(response.get("socials", []))
        st.metric("Social Profiles", socials_count)
    
    with col4:
        relationships_count = len(response.get("relationships", []))
        st.metric("Relationships", relationships_count)
    
    # Create tabs for different result sections
    tab_names = []
    if has_business:
        tab_names.append("🏢 Business Overview")
    if has_owners:
        tab_names.append("👥 Affiliated Persons")
    if has_socials:
        tab_names.append("🌐 Social Profiles")
    if has_ai_summary:
        tab_names.append("🤖 AI Summary")
    
    if tab_names:
        tabs = st.tabs(tab_names)
        tab_index = 0
        
        # Business Overview Tab
        if has_business:
            with tabs[tab_index]:
                render_business_section(response["business"])
            tab_index += 1
        
        # Affiliated Persons Tab
        if has_owners:
            with tabs[tab_index]:
                render_owners_section(response["owners"])
            tab_index += 1
        
        # Social Profiles Tab
        if has_socials:
            with tabs[tab_index]:
                render_socials_section(response["socials"])
            tab_index += 1
        
        # AI Summary Tab
        if has_ai_summary:
            with tabs[tab_index]:
                render_ai_summary_section(response["ai_summary"])
    
    return response

def render_business_section(business_data):
    """Render the business overview section."""
    if not business_data:
        st.info("No business data found.")
        return
    
    st.write("### Business Entities")
    
    try:
        # Convert to DataFrame for better display
        df = pd.DataFrame(business_data)
        
        # Clean up the dataframe for display
        if not df.empty:
            # Reorder columns if they exist
            preferred_columns = ['name', 'type', 'location', 'description', 'status', 'id']
            existing_columns = [col for col in preferred_columns if col in df.columns]
            other_columns = [col for col in df.columns if col not in preferred_columns]
            column_order = existing_columns + other_columns
            
            if column_order:
                df = df[column_order]
            
            # Display as an interactive dataframe
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Business Data (CSV)",
                data=csv,
                file_name="business_data.csv",
                mime="text/csv"
            )
        else:
            st.info("No business data to display.")
            
    except Exception as e:
        st.error(f"Error displaying business data: {e}")
        st.json(business_data)

def render_owners_section(owners_data):
    """Render the affiliated persons section."""
    if not owners_data:
        st.info("No person data found.")
        return
    
    st.write("### Affiliated Persons")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(owners_data)
        
        if not df.empty:
            # Reorder columns if they exist
            preferred_columns = ['name', 'role', 'company', 'location', 'email', 'phone', 'id']
            existing_columns = [col for col in preferred_columns if col in df.columns]
            other_columns = [col for col in df.columns if col not in preferred_columns]
            column_order = existing_columns + other_columns
            
            if column_order:
                df = df[column_order]
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Persons Data (CSV)",
                data=csv,
                file_name="persons_data.csv",
                mime="text/csv"
            )
        else:
            st.info("No person data to display.")
            
    except Exception as e:
        st.error(f"Error displaying person data: {e}")
        st.json(owners_data)

def render_socials_section(socials_data):
    """Render the social profiles section."""
    if not socials_data:
        st.info("No social profiles found.")
        return
    
    st.write("### Social Media Profiles")
    
    try:
        # Group by platform if available
        if isinstance(socials_data, list) and socials_data:
            for profile in socials_data:
                if isinstance(profile, dict):
                    platform = profile.get('platform', 'Unknown')
                    url = profile.get('url', '')
                    username = profile.get('username', '')
                    followers = profile.get('followers', '')
                    
                    # Create a nice display for each profile
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            if url:
                                st.markdown(f"**{platform}**: [{username or url}]({url})")
                            else:
                                st.markdown(f"**{platform}**: {username}")
                        
                        with col2:
                            if followers:
                                st.write(f"👥 {followers} followers")
                
                st.divider()
                
        else:
            # Fallback to simple list display
            for profile in socials_data:
                if isinstance(profile, dict) and 'url' in profile:
                    st.markdown(f"- [{profile['url']}]({profile['url']})")
                elif isinstance(profile, str):
                    st.markdown(f"- {profile}")
                    
    except Exception as e:
        st.error(f"Error displaying social profiles: {e}")
        st.json(socials_data)

def render_ai_summary_section(ai_summary):
    """Render the AI summary section."""
    if not ai_summary:
        st.info("No AI summary available.")
        return
    
    st.write("### AI-Generated Summary")
    
    # Display the summary in a nice format
    st.markdown(ai_summary)
    
    # Option to regenerate summary
    if st.button("🔄 Regenerate Summary"):
        with st.spinner("Regenerating summary..."):
            # Could call generate API here with current context
            st.info("Summary regeneration feature coming soon!")

def get_stored_results() -> Optional[Dict]:
    """Get search results from session state."""
    return st.session_state.get('search_results', None)