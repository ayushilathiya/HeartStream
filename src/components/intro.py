import streamlit as st

def show_intro_page():
    st.markdown("""
        <style>
        /* Override Streamlit's default background */
        .stApp {
            background-color: #d4e4f8 !important;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .heart-emoji {
            display: inline-block;
            animation: pulse 1s infinite;
            margin-right: 0.5rem;
            font-size: 4rem !important;
            vertical-align: middle;
            background: linear-gradient(45deg, #1976D2, #7eaee7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .title-text {
            display: inline-block;
            color: #1976D2;
            vertical-align: middle;
        }
        .big-title {
            font-size: 4rem !important;
            font-weight: 800;
            text-align: center;
            color: #1976D2;
            margin-bottom: 0.5rem;
            animation: fadeIn 1s ease-out;
        }
        .subtitle {
            font-size: 1.8rem !important;
            text-align: center;
            color: #666;
            margin-bottom: 3rem;
            animation: fadeIn 1s ease-out 0.5s backwards;
        }
        .feature-card {
            background: #a9c9f0;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-out;
            color: white !important;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            background: #a9c9f0;
            box-shadow: 0 6px 12px rgba(15, 70, 125, 0.2);
        }
        
        .feature-card:hover .feature-title {
            color: #666 !important;
            transition: color 0.3s ease;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: white;
        }
        
        .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #666;
            margin-bottom: 0.5rem;
        }
        
        .feature-text {
            color: #666;
            font-size: 1rem;
            line-height: 1.5;
        }
        .content-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            animation: fadeIn 1s ease-out;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Animated header with separate spans for heart and text
    st.markdown("""
        <h1 class="big-title">
            <span class="heart-emoji">❤️</span>
            <span class="title-text">HeartStream</span>
        </h1>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="subtitle">Advanced ECG Monitoring & AI Analysis</p>', unsafe_allow_html=True)
    
    # Feature cards in a grid layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔴</div>
                <div class="feature-title">Live ECG Monitoring</div>
                <div class="feature-text">
                    • Real-time ECG waveform visualization<br>
                    • Live BPM tracking with visual alerts<br>
                    • Instant data streaming via ThingSpeak<br>
                    • Historical data analysis and trends
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Data Analytics</div>
                <div class="feature-text">
                    • Comprehensive statistical analysis<br>
                    • Trend visualization and patterns<br>
                    • Custom data export options<br>
                    • Interactive data exploration
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Smart ECG Analysis</div>
                <div class="feature-text">
                    • AI-powered diagnostic insights<br>
                    • Automated rhythm analysis<br>
                    • Anomaly detection<br>
                    • Real-time health alerts
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <div class="feature-title">Accessibility</div>
                <div class="feature-text">
                    • Mobile-friendly interface<br>
                    • Secure data storage<br>
                    • Easy PDF report generation<br>
                    • Cloud-based synchronization
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Call-to-action section
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; animation: fadeIn 1s ease-out 1.5s backwards;">
            <h2 style="color: #1976D2; margin-bottom: 1rem;">Start Monitoring Today</h2>
            <p style="color: #666; font-size: 1.1rem;">
                Experience the next generation of ECG monitoring with HeartStream's advanced features and intuitive interface.
            </p>
        </div>
    """, unsafe_allow_html=True)