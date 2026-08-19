"""
Furniture Lead Agent - Streamlit Web App
A lead generation tool for finding furniture sales opportunities
"""

import streamlit as st
import pandas as pd
from agent import furniture_agent
from supabase_client import save_leads, get_last_error

# Page configuration
st.set_page_config(
    page_title="Furniture Lead Hunter",
    page_icon="🪑",
    layout="wide"
)

# Custom CSS for dashboard styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #1E3A5F !important;
        margin-bottom: 10px !important;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 18px !important;
        color: #666 !important;
        margin-bottom: 30px !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 2px solid #E9ECEF;
    }
    
    /* Card hover effect */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 14px;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%) !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3) !important;
    }
    
    /* Divider styling */
    hr {
        margin: 20px 0;
    }
    
    /* Info box styling */
    .stInfo {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)


# Segment options
SEGMENTS = [
    "Office",
    "Coworking", 
    "Hotel",
    "Restaurant",
    "Residential",
    "Retail"
]


def get_score_color(score: int) -> str:
    """Return color based on intent score."""
    if score >= 9:
        return "🟢"
    elif score >= 7:
        return "🟡"
    else:
        return "🔴"


def display_lead_card(lead: dict):
    """Display a single lead as a styled card."""
    score_emoji = get_score_color(lead["intent_score"])
    
    # Card background color based on score
    if lead["intent_score"] >= 9:
        card_color = "#E8F5E9"  # Light green
        border_color = "#4CAF50"
    elif lead["intent_score"] >= 7:
        card_color = "#FFF8E1"  # Light yellow
        border_color = "#FFC107"
    else:
        card_color = "#FFEBEE"  # Light red
        border_color = "#F44336"
    
    # Custom CSS for card
    st.markdown(f"""
    <div style="
        background-color: {card_color};
        border-left: 5px solid {border_color};
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h3 style="margin: 0; color: #333;">🏢 {lead['company']}</h3>
            <span style="font-size: 18px;">{score_emoji} <b>{lead['intent_score']}/10</b></span>
        </div>
        <p style="margin: 5px 0;"><b>🌐 Website:</b> <a href="{lead['website']}" target="_blank">{lead['website']}</a></p>
        <p style="margin: 5px 0;"><b>🏢 Segment:</b> {lead['segment']}</p>
        <p style="margin: 5px 0;"><b>📍 City:</b> {lead.get('city', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>👤 Decision Maker:</b> {lead['decision_maker']}</p>
        <div style="margin-top: 10px; padding: 10px; background-color: rgba(255,255,255,0.7); border-radius: 5px;">
            <b>📊 Intent Signal:</b><br>
            <span style="color: #666;">{lead['intent_signal'][:200]}{'...' if len(lead['intent_signal']) > 200 else ''}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown("<h1 class='main-title'>🪑 Furniture Lead Hunter</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Find new buildings and offices with potential to sell furniture</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Input form
    with st.sidebar:
        st.markdown("<h2 style='color: #1E3A5F;'>🎯 Search Parameters</h2>", unsafe_allow_html=True)
        
        city = st.text_input(
            "City",
            placeholder="e.g., Chennai, Mumbai, Bangalore",
            help="Enter the target city for lead search"
        )
        
        segment = st.selectbox(
            "Segment",
            options=SEGMENTS,
            help="Select the type of building/space to search for"
        )
        
        limit = st.slider(
            "Number of Results",
            min_value=1,
            max_value=20,
            value=10,
            help="Maximum number of leads to return"
        )
        
        search_button = st.button("🔍 Hunt for Leads", type="primary", use_container_width=True)
        
        st.divider()
        
        # Info section
        st.markdown("""
        <div style="background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin-top: 20px;">
        <b>Segments:</b>
        <ul style="margin: 5px 0;">
            <li><b>Office:</b> Corporate offices, business parks</li>
            <li><b>Coworking:</b> Shared workspaces, incubators</li>
            <li><b>Hotel:</b> Hotels, resorts, hospitality</li>
            <li><b>Restaurant:</b> Restaurants, cafes, dining</li>
            <li><b>Residential:</b> Apartments, housing complexes</li>
            <li><b>Retail:</b> Stores, malls, showrooms</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    if search_button:
        if not city:
            st.error("Please enter a city name!")
            return
        
        # Show progress
        with st.spinner(f"🔎 Hunting for {segment} leads in {city}..."):
            try:
                # Run the agent
                leads = furniture_agent(city, segment, limit)
                
                if not leads:
                    st.warning("No leads found. Try a different city or segment.")
                    return
                
                save_ok = save_leads(leads)
                if save_ok:
                    st.success("Saved leads to Supabase.")
                else:
                    st.warning("Leads were not saved to Supabase. Check credentials or RLS.")
                
                # Display metrics
                st.markdown("---")
                st.markdown("### 📊 Results Summary")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Leads", len(leads))
                
                with col2:
                    avg_score = sum(l["intent_score"] for l in leads) / len(leads)
                    st.metric("Avg Intent Score", f"{avg_score:.1f}/10")
                
                with col3:
                    high_intent = len([l for l in leads if l["intent_score"] >= 9])
                    st.metric("High Intent Leads", high_intent)
                
                # Display leads
                st.markdown("---")
                st.markdown(f"### 🎯 Found {len(leads)} Leads")
                
                for lead in leads:
                    display_lead_card(lead)
                
                # Data table view
                st.markdown("---")
                st.markdown("### 📋 Table View")
                
                # Convert to DataFrame for table display
                df = pd.DataFrame(leads)
                df = df[["company", "segment", "city", "intent_score", "website", "decision_maker"]]
                df = df.rename(columns={
                    "company": "Company",
                    "segment": "Segment", 
                    "city": "City",
                    "intent_score": "Score",
                    "website": "Website",
                    "decision_maker": "Decision Maker"
                })
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # CSV Export
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"furniture_leads_{city}_{segment}.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please check your API keys in the .env file.")
    
    else:
        # Welcome message when not searching
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background-color: #F8F9FA; border-radius: 15px; margin: 20px 0;">
            <h2 style="color: #1E3A5F;">👋 Welcome to Furniture Lead Hunter!</h2>
            <p style="font-size: 16px; color: #666;">
                Use the sidebar to search for potential furniture sales leads.
            </p>
            <div style="text-align: left; max-width: 400px; margin: 30px auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <b>How it works:</b><br><br>
                1. 📍 Enter a city name<br>
                2. 🏢 Select a segment (Office, Coworking, Hotel, etc.)<br>
                3. 📊 Choose the number of results<br>
                4. 🔍 Click "Hunt for Leads"
            </div>
            <p style="color: #666;">The agent will search for new buildings and spaces that may need furniture!</p>
        </div>
        <div style="text-align: center; margin-top: 30px; padding: 20px;">
            <span style="font-size: 48px;">👈</span>
            <p style="color: #2196F3; font-weight: 600;">Enter your search parameters in the sidebar to get started!</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
