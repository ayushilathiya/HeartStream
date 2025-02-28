import streamlit as st
from components.live_data import show_live_data_page
from components.analysis import show_analysis_page
from components.intro import show_intro_page
import traceback

# Page config
st.set_page_config(
    page_title="HeartStream",
    page_icon="❤️",
    layout="wide"
)

def main():
    try:
        st.markdown("""
            <style>
            .nav-container {
                display: flex;
                justify-content: flex-end;
                gap: 20px;
                padding: 1rem 2rem;
                background: white;
                position: fixed;
                top: 0;
                right: 0;
                left: 0;
                z-index: 9999;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Update button styles */
            .stButton > button {
                background-color: #f8f9fa !important;
                color: #1976D2 !important;
                border: none !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton > button:hover {
                background-color: #a9c9f0 !important;
                color: white !important;
                transform: translateY(-2px);
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
        col1, col2, col3 = st.columns([6, 1, 1])
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