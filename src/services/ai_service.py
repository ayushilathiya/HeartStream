import streamlit as st
import groq
from datetime import datetime, timedelta
from config.app_config import ANALYSIS_DAILY_LIMIT

def init_analysis_state():
    """Initialize analysis-related session state variables."""
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = datetime.now()
    if 'analysis_limit' not in st.session_state:
        st.session_state.analysis_limit = ANALYSIS_DAILY_LIMIT

def check_rate_limit():
    # Ensure state is initialized
    init_analysis_state()
    
    # Calculate time until reset
    time_until_reset = timedelta(days=1) - (datetime.now() - st.session_state.last_analysis)
    hours, remainder = divmod(time_until_reset.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    # Reset counter after 24 hours
    if time_until_reset.days < 0:
        st.session_state.analysis_count = 0
        st.session_state.last_analysis = datetime.now()
        return True, None
    
    # Check if limit reached
    if st.session_state.analysis_count >= ANALYSIS_DAILY_LIMIT:
        error_msg = f"Daily limit reached. Reset in {hours}h {minutes}m"
        return False, error_msg
    return True, None

def generate_analysis(data, system_prompt, check_only=False):
    """Generate analysis if within rate limits.
    
    Args:
        data: The data to analyze
        system_prompt: The prompt for the AI
        check_only: If True, only check rate limit without generating analysis
    """
    can_analyze, error_msg = check_rate_limit()
    if not can_analyze:
        return {"success": False, "error": error_msg}
    
    if check_only:
        return can_analyze, error_msg
        
    try:
        client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(data)}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        st.session_state.analysis_count += 1
        st.session_state.last_analysis = datetime.now()
        
        return {
            "success": True,
            "content": completion.choices[0].message.content
        }
    except Exception as e:
        return {"success": False, "error": f"Analysis failed: {str(e)}"}