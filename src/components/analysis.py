import streamlit as st
import io

# Try importing pdfplumber, handle if not installed
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

def show_analysis_page():
    st.markdown("""
        <style>
        .stApp {
            background-color: #d4e4f8 !important;
        }
        
        h1 {
            font-size: 4rem !important;
            font-weight: 800;
            text-align: center;
            background: linear-gradient(45deg, #1976D2, #7eaee7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 3rem !important;
        }
        
        .stUploadedFile {
            background: #a9c9f0 !important;
            border-radius: 10px;
            padding: 1rem;
        }
        
        .stButton > button {
            background-color: #7eaee7 !important;
            color: white !important;
        }
        
        .stButton > button:hover {
            background-color: #0f467d !important;
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Smart ECG Analysis")
    
    if not PDF_SUPPORT:
        st.error("""
        PDF support is not available. Please install required package:
        ```
        pip install pdfplumber
        ```
        """)
        return
    
    # File upload
    uploaded_file = st.file_uploader("Upload ECG PDF", type=['pdf'])
    
    if uploaded_file:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            # Analysis section
            if st.button("Analyze ECG", type="primary"):
                with st.spinner("Analyzing ECG..."):
                    st.info("AI analysis feature coming soon!")
                    st.markdown("""
                    ### Sample Analysis Report
                    - Heart Rate: Pending AI analysis
                    - Rhythm: Pending AI analysis
                    - Abnormalities: Pending AI analysis
                    - Recommendations: Pending AI analysis
                    """)
                        
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")