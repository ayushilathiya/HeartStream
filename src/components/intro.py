import streamlit as st
import base64

def get_image_base64():
    try:
        import os
        # Use relative path from the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        img_path = os.path.join(project_root, "src", "assets", "ecg.png")
        
        with open(img_path, "rb") as img_file:
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
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes bounceIn {
            0% { opacity: 0; transform: scale(0.3); }
            50% { opacity: 1; transform: scale(1.05); }
            70% { transform: scale(0.9); }
            100% { opacity: 1; transform: scale(1); }
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
            margin: 1rem 2rem;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-out;
            color: white !important;
            height: 100%;
            width: 90%;
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
        .stats-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: all 0.3s ease;
            animation: bounceIn 1s ease-out;
            text-align: center;
            border: 2px solid #a9c9f0;
        }
        .stats-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 8px 16px rgba(15, 70, 125, 0.2);
            border-color: #1976D2;
        }
        .stats-number {
            font-size: 3rem;
            font-weight: bold;
            color: #1976D2;
            margin-bottom: 0.5rem;
            animation: pulse 2s infinite;
        }
        .stats-label {
            font-size: 1.2rem;
            color: #666;
            font-weight: 500;
        }
        .benefit-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(15, 70, 125, 0.1);
            transition: all 0.3s ease;
            animation: slideIn 0.8s ease-out;
            border-left: 4px solid #a9c9f0;
        }
        .benefit-item:hover {
            transform: translateX(10px);
            box-shadow: 0 4px 8px rgba(15, 70, 125, 0.2);
            border-left-color: #1976D2;
        }
        .tech-badge {
            background: #a9c9f0;
            color: #666;
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            margin: 0.5rem;
            display: inline-block;
            font-weight: 500;
            transition: all 0.3s ease;
            animation: slideInRight 0.8s ease-out;
        }
        .tech-badge:hover {
            background: #1976D2;
            color: white;
            transform: scale(1.05);
        }
        .section-divider {
            height: 3px;
            background: linear-gradient(45deg, #1976D2, #7eaee7, #a9c9f0);
            border-radius: 2px;
            margin: 3rem auto;
            max-width: 200px;
            animation: fadeIn 1s ease-out;
        }
        .workflow-arrow {
            color: #1976D2;
            font-size: 2rem;
            margin: 0 1rem;
            animation: pulse 2s infinite;
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
        @keyframes dashStable {
            0% {
                stroke-dashoffset: 1000;
            }
            100% {
                stroke-dashoffset: 0;
            }
        }
        .ecg-line {
            position: relative;
            height: 100px;
            margin: 2rem auto;
            width: 100%;
            max-width: 1000px;
            opacity: 0;
            animation: fadeIn 0.5s ease-out 1s forwards;
        }
        .ecg-path {
            stroke: #1976D2;
            stroke-width: 3;
            fill: none;
            stroke-dasharray: 1000;
            stroke-dashoffset: 1000;
            animation: dashStable 8s linear infinite;
            animation-delay: 1.5s;
            animation-fill-mode: forwards;
        }
        .highlight-box {
            background: linear-gradient(135deg, #a9c9f0, #7eaee7);
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 800px;
            text-align: center;
            box-shadow: 0 6px 12px rgba(15, 70, 125, 0.2);
            animation: fadeIn 1s ease-out;
        }
        .highlight-text {
            color: white;
            font-size: 1.4rem;
            font-weight: 500;
            margin-bottom: 1rem;
        }
        .medical-app-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-out;
            border-top: 3px solid #a9c9f0;
            text-align: center;
        }
        .medical-app-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(15, 70, 125, 0.2);
            border-top-color: #1976D2;
        }
        .medical-app-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: #1976D2;
        }
        .medical-app-title {
            color: #1976D2;
            font-weight: 600;
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        .medical-app-desc {
            color: #666;
            font-size: 1rem;
            line-height: 1.5;
        }
        .cta-button {
            background: #f8f9fa;
            padding: 1rem 2rem;
            border-radius: 8px;
            color: #1976D2;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            border: 2px solid #1976D2;
            cursor: pointer;
        }
        .cta-button:hover {
            background: #1976D2;
            color: white;
            transform: translateY(-2px);
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

    # Statistics Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">HeartStream Performance Metrics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="stats-card">
                <div class="stats-number">99.7%</div>
                <div class="stats-label">Model Accuracy</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stats-card">
                <div class="stats-number">250Hz</div>
                <div class="stats-label">Sampling Rate</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stats-card">
                <div class="stats-number">48K+</div>
                <div class="stats-label">Training Samples</div>
            </div>
        """, unsafe_allow_html=True)

    # Feature cards in a grid layout
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding: 2rem;">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
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
    st.markdown('</div>', unsafe_allow_html=True)

    # How it Works Section - Moved up and with arrows
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="background: #a9c9f0; border-radius: 10px; padding: 2rem; margin: 2rem auto; box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1); transition: transform 0.3s ease; animation: fadeIn 1s ease-out; width: 100%; max-width: 1200px;"
             onmouseover="this.style.transform='translateY(-5px)';this.style.boxShadow='0 6px 12px rgba(15, 70, 125, 0.2)'"
             onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 6px rgba(15, 70, 125, 0.1)'">
            <div class="feature-title" style="font-size: 2.5rem;">
                <div style="text-align: center; margin-bottom: 2rem;">How HeartStream Works!</div>
            </div>
            <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 200px; transition: all 0.3s ease;"
                     onmouseover="this.style.transform='scale(1.05)'" 
                     onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size: 1.2rem; color: #666; font-weight: 600;">1. AD8232 Sensor<br>Captures ECG</div>
                </div>
                <div class="workflow-arrow">→</div>
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 200px; transition: all 0.3s ease;"
                     onmouseover="this.style.transform='scale(1.05)'" 
                     onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size: 1.2rem; color: #666; font-weight: 600;">2. ESP8266<br>Transmits Data</div>
                </div>
                <div class="workflow-arrow">→</div>
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 200px; transition: all 0.3s ease;"
                     onmouseover="this.style.transform='scale(1.05)'" 
                     onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size: 1.2rem; color: #666; font-weight: 600;">3. AI Model<br>Analyzes</div>
                </div>
                <div class="workflow-arrow">→</div>
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; min-width: 200px; transition: all 0.3s ease;"
                     onmouseover="this.style.transform='scale(1.05)'" 
                     onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size: 1.2rem; color: #666; font-weight: 600;">4. Generate<br>Insights</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Key Benefits Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">Why Choose HeartStream?</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="benefit-item">
                <h3 style="color: #1976D2; margin-bottom: 0.5rem;">🏥 Clinical Grade Accuracy</h3>
                <p style="color: #666;">Advanced algorithms trained on MIT-BIH Arrhythmia Database for medical-grade precision</p>
            </div>
            <div class="benefit-item">
                <h3 style="color: #1976D2; margin-bottom: 0.5rem;">⚡ Real-time Processing</h3>
                <p style="color: #666;">Instant analysis and alerts within milliseconds of data acquisition</p>
            </div>
            <div class="benefit-item">
                <h3 style="color: #1976D2; margin-bottom: 0.5rem;">🔒 Secure & Private</h3>
                <p style="color: #666;">Local processing ensures your health data remains confidential</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="benefit-item">
                <h3 style="color: #1976D2; margin-bottom: 0.5rem;">📱 User-Friendly Interface</h3>
                <p style="color: #666;">Intuitive design that makes complex cardiac data easy to understand</p>
            </div>
            <div class="benefit-item">
                <h3 style="color: #1976D2; margin-bottom: 0.5rem;">🤖 AI-Powered Insights</h3>
                <p style="color: #666;">Deep learning models provide comprehensive cardiac rhythm analysis</p>
            </div>
            <div class="benefit-item">
                <h3 style="color: #1976D2; margin-bottom: 0.5rem;">📊 Comprehensive Reports</h3>
                <p style="color: #666;">Detailed analysis reports perfect for medical documentation</p>
            </div>
        """, unsafe_allow_html=True)

    # Technology Stack Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">Powered by Advanced Technology</h2>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin: 2rem auto; max-width: 1000px;">
            <a href="https://pytorch.org/" target="_blank" style="text-decoration: none;"><span class="tech-badge">🧠 PyTorch Neural Networks</span></a>
            <a href="https://www.analog.com/en/products/ad8232.html" target="_blank" style="text-decoration: none;"><span class="tech-badge">📡 AD8232 ECG Sensor</span></a>
            <a href="https://towardsdatascience.com/making-decisions-from-live-sensor-data-1febf8db9464/" target="_blank" style="text-decoration: none;"><span class="tech-badge">📊 Real-time Data Processing</span></a>
            <a href="https://www.espressif.com/en/products/socs/esp8266" target="_blank" style="text-decoration: none;"><span class="tech-badge">🌐 ESP8266 WiFi Module</span></a>
            <a href="https://thingspeak.com/" target="_blank" style="text-decoration: none;"><span class="tech-badge">☁️ ThingSpeak Integration</span></a>
            <a href="https://www.ibm.com/topics/machine-learning" target="_blank" style="text-decoration: none;"><span class="tech-badge">🔄 Trained AI Models</span></a>
        </div>
    """, unsafe_allow_html=True)

    # Medical Applications Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">Medical Applications</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="medical-app-card">
                <div class="medical-app-icon">🏥</div>
                <div class="medical-app-title">Clinical Monitoring</div>
                <div class="medical-app-desc">
                    Continuous patient monitoring in hospitals, ICUs, and cardiac care units for early detection of arrhythmias
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="medical-app-card">
                <div class="medical-app-icon">🏃</div>
                <div class="medical-app-title">Sports Medicine</div>
                <div class="medical-app-desc">
                    Athletic performance monitoring and cardiac stress testing for professional athletes and fitness enthusiasts
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="medical-app-card">
                <div class="medical-app-icon">🏠</div>
                <div class="medical-app-title">Home Healthcare</div>
                <div class="medical-app-desc">
                    Remote patient monitoring for elderly care and chronic cardiac condition management at home
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Highlight Box
    st.markdown("""
        <div class="highlight-box">
            <div class="highlight-text">
                "Transforming cardiac care through intelligent monitoring and AI-driven insights"
            </div>
            <div style="color: white; font-size: 1.1rem;">
                Built on the renowned MIT-BIH Arrhythmia Database for maximum accuracy and reliability
            </div>
        </div>
    """, unsafe_allow_html=True)

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
            """
            st.markdown(card_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error rendering cards: {e}")

    # Call-to-action section and footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; animation: fadeIn 1s ease-out 1.5s backwards;">
            <h2 style="color: #1976D2; margin-bottom: 1rem;">Start Monitoring Today</h2>
            <p style="color: #666; font-size: 1.1rem;">
                Experience the next generation of ECG monitoring with HeartStream's advanced features and intuitive interface.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <footer style="text-align: center; margin-top: 3rem; padding-bottom: 2rem;">
            <p style="color: #666; font-size: 1.1rem;">All Rights Reserved. ©️ 2025 Ayushi Lathiya</p>
        </footer>
    """, unsafe_allow_html=True)