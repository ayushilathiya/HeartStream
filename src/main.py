import streamlit as st
from components.live_data import show_live_data_page
from components.analysis import show_analysis_page
from components.intro import show_intro_page
import traceback

# Page config
st.set_page_config(
    page_title="HeartStream",
    page_icon="public/monitor.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    try:
        # Add meta tags for link sharing
        st.markdown("""
            <meta name="description" content="Live ECG Monitoring & AI Diagnosis in One Platform">
            <meta property="og:title" content="HeartStream">
            <meta property="og:description" content="Live ECG Monitoring & AI Diagnosis in One Platform">
            <meta property="og:type" content="website">
            <meta name="twitter:card" content="summary">
            <meta name="twitter:title" content="HeartStream">
            <meta name="twitter:description" content="Live ECG Monitoring & AI Diagnosis in One Platform">
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            .nav-container {
                display: flex;
                justify-content: flex-end;
                gap: 20px;
                padding: 2.5rem 2.5rem;  /* Increased padding */
                background: white;
                position: fixed;
                top: 0;
                right: 0;
                left: 0;
                z-index: 9999;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Updated button styles */
            .stButton > button {
                background-color: #f8f9fa !important;
                font-family: 'Helvetica Neue', Helvetica, sans-serif;
                font-style: normal;
                font-weight: 900 !important;  /* Increased to maximum boldness */
                font-size: 1.1rem !important;  /* Slightly reduced */
                color: #1976D2 !important;
                border: none !important;
                padding: 0.6rem 1.2rem !important;  /* Reduced padding */
                transition: all 0.3s ease !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px !important;
                letter-spacing: 0.5px !important;  /* Increased letter spacing */
                text-transform: uppercase !important;  /* Added uppercase */
                white-space: nowrap !important;  /* Prevent text wrapping */
                min-width: 80px !important;  /* Reduced minimum width */
                max-width: 150px !important;  /* Added maximum width */
            }
            
            .stButton > button:hover {
                background-color: #1976D2 !important;
                color: white !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            /* Update the column layout */
            [data-testid="column"] {
                width: auto !important;
                min-width: fit-content !important;
                padding: 0 50px !important;  /* Reduced padding */
            }

            /* Rest of existing styles */
            .main-content {
                padding-top: 6rem;
            }
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)
        
        # Navigation container
        col1, col2, col3 = st.columns([6, 1, 1])  # Adjusted column ratios
        with col2:
            if st.button("Live ECG", use_container_width=True):
                st.query_params["page"] = "live"
                st.rerun()
        with col3:
            if st.button("Smart Analysis", use_container_width=True):
                st.query_params["page"] = "analysis"
                st.rerun()
        
        # Get current page from query params
        page = st.query_params.get("page", "intro")
        
        # Show back button if not on intro page
        if page != "intro":
            if st.button("← Back to Home"):
                st.query_params["page"] = "intro"
                st.rerun()
        
        if page == "intro":
            show_intro_page()
        elif page == "live":
            show_live_data_page()
        elif page == "analysis":
            show_analysis_page()
            
    except Exception as e:
        st.error("An error occurred:")
        st.error(str(e))
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()