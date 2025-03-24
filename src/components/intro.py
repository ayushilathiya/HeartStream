import streamlit as st
import base64

def get_image_base64():
    try:
        with open("C:/Users/AYUSHI LATHIYA/Desktop/HeartStream/src/assets/ecg.png", "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return ""

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
            padding: 2rem;
            margin: 1rem 2rem;  /* Added horizontal margin */
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-out;
            color: white !important;
            height: 100%;  /* Ensure equal height */
            width: 90%;   /* Control width */
        }
        .feature-textcard {
                background: #ffffff;
                border-radius: 10px;
                padding: 1rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
                transition: transform 0.3s ease;
                animation: fadeIn 1s ease-out;
        }
                
        .feature-image {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 1rem;
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
        
        .feature-title {
            font-size: 2rem;
            font-weight: 600;
            color: #666;
            margin-bottom: 0.5rem;
        }
        .feature-icon {
            font-size: 1rem;
            color: #666;
        }        
                
        .feature-text {
            color: #666;
            font-size: 1.2rem;
            line-height: 1.5;
        }
        .content-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            animation: fadeIn 1s ease-out;
        }
        .image-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
        }
        
            @keyframes dash {
            from {
                stroke-dashoffset: 2000;
            }
            to {
                stroke-dashoffset: 0;
            }
        }
    
        .ecg-line {
            position: relative;
            height: 100px;
            margin: 2rem auto;
            width: 100%;
            max-width: 1000px;
        }
        
        .ecg-path {
            stroke: #1976D2;
            stroke-width: 3;
            fill: none;
            animation: dash 7s linear infinite;
            stroke-dasharray: 1000;
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
    
    # Add animated ECG line
    st.markdown("""
        <div class="ecg-line">
            <svg viewBox="0 0 1000 100" preserveAspectRatio="none">
                <path class="ecg-path" d="M0,50 
                    L100,50 L120,50 L130,20 L140,80 L150,40 L160,70 L170,50 
                    L200,50 L220,50 L230,30 L240,80 L250,10 L260,80 L270,50 
                    L300,50 L320,50 L330,10 L340,90 L350,20 L360,60 L370,50 
                    L400,50 L420,50 L430,20 L440,65 L450,35 L460,93 L470,50 
                    L500,50 L520,50 L530,12 L540,84 L550,20 L560,70 L570,50 
                    L600,50 L620,50 L630,34 L640,55 L650,20 L660,89 L670,50 
                    L700,50 L720,50 L730,10 L740,67 L750,30 L760,69 L770,50 
                    L800,50 L820,50 L830,20 L840,80 L850,17 L860,79 L870,50 
                    L900,50 L920,50 L930,30 L940,70 L950,40 L960,90 L970,50 
                    L1000,50" />
            </svg>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature cards in a grid layout
    st.markdown('<div style="padding: 2rem;">', unsafe_allow_html=True)  # Add padding container
    col1, col2 = st.columns([1, 1])  # Equal width columns
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-title">Live ECG Monitoring</div>
                    <div class="feature-textcard">
                        <div class="feature-text">
                            • Real-time ECG waveform visualization<br>
                            • Live BPM tracking with visual alerts<br>
                            • Instant data streaming via ThingSpeak<br>
                            • Historical data analysis and trends
                        </div>
                    </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-card">  
                <div class="feature-title">Smart ECG Analysis</div>
                    <div class="feature-textcard">
                        <div class="feature-text">
                            • AI-powered diagnostic insights<br>
                            • Automated rhythm analysis<br>
                            • Anomaly detection<br>
                            • Real-time health alerts
                        </div>
                    </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close padding container

    # After the two columns, close their container first
    st.markdown('</div>', unsafe_allow_html=True)  # Close padding container
    
    # Create feature card with integrated image
    try:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            card_html = f"""
                <div style="background: #f8f9fa; border-radius: 10px; padding: 2rem; margin: 1rem 2rem; box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1); transition: transform 0.3s ease; animation: fadeIn 1s ease-out; height: 100%; width: 90%; max-width: 1000px; margin: 1rem auto;"
                     onmouseover="this.style.transform='translateY(-5px)';this.style.boxShadow='0 6px 12px rgba(15, 70, 125, 0.2)'"
                     onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 6px rgba(15, 70, 125, 0.1)'">
                    <div class="feature-title">
                        <div style="text-align: center; font-size:1em; letter-spacing: 0.5px !important;">Harnessing AI for Smart Cardiac Health</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #f8f9fa;">
                        <img src="data:image/png;base64,{get_image_base64()}" 
                            style="max-width: 600px; width: 100%; border-radius: 8px; margin: 1rem auto; display: block;"
                            alt="ECG Analysis"/>
                    </div>
                </div>


                <!-- How it Works Section -->
                <div style="background: #a9c9f0; border-radius: 10px; padding: 2rem; margin: 4rem auto; box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1); transition: transform 0.3s ease; animation: fadeIn 1s ease-out; width: 100%; max-width: 1100px;"
                     onmouseover="this.style.transform='translateY(-5px)';this.style.boxShadow='0 6px 12px rgba(15, 70, 125, 0.2)'"
                     onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 6px rgba(15, 70, 125, 0.1)'">
                    <div class="feature-title" style="font-size: 2rem;">
                        <div style="text-align: center; margin-bottom: 2rem;">How HeartStream Works!</div>
                    </div>
                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 1.5rem;">
                        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 150px; transition: all 0.3s ease;"
                             onmouseover="this.style.transform='scale(1.05)'" 
                             onmouseout="this.style.transform='scale(1)'">
                            <div style="font-size: 1.2rem; color: #666; font-weight: 600;">1. Connect Device</div>
                        </div>
                        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 150px; transition: all 0.3s ease;"
                             onmouseover="this.style.transform='scale(1.05)'" 
                             onmouseout="this.style.transform='scale(1)'">
                            <div style="font-size: 1.2rem; color: #666; font-weight: 600;">2. Start Monitoring</div>
                        </div>
                        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 150px; transition: all 0.3s ease;"
                             onmouseover="this.style.transform='scale(1.05)'" 
                             onmouseout="this.style.transform='scale(1)'">
                            <div style="font-size: 1.2rem; color: #666; font-weight: 600;">3. Get Insights</div>
                        </div>
                        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 150px; transition: all 0.3s ease;"
                             onmouseover="this.style.transform='scale(1.05)'" 
                             onmouseout="this.style.transform='scale(1)'">
                            <div style="font-size: 1.2rem; color: #666; font-weight: 600;">4. Share Reports</div>
                        </div>
                    </div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error rendering cards: {e}")

    # Call-to-action section
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; animation: fadeIn 1s ease-out 1.5s backwards;">
            <h2 style="color: #1976D2; margin-bottom: 1rem;">Start Monitoring Today</h2>
            <p style="color: #666; font-size: 1.1rem;">
                Experience the next generation of ECG monitoring with HeartStream's advanced features and intuitive interface.
            </p>
            <footer style="text-align: center; margin-top: 3rem;">
                <p style="color: #666; font-size: 1.1rem;> All Rights Reserved. ©️ 2025 HeartStream </p>
            </footer>
        </div>
    """, unsafe_allow_html=True)