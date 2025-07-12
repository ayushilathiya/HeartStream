import streamlit as st

def show_learn_more_page():
    st.markdown("""
        <style>
        /* Override Streamlit's default background */
        .stApp {
            background-color: #d4e4f8 !important;
        }
        
        /* Add main content padding to avoid navigation overlap */
        .main-content {
            padding-top: 6rem;
            padding-bottom: 2rem;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .page-title {
            font-size: 3rem !important;
            font-weight: 800;
            text-align: center;
            color: #1976D2;
            margin-bottom: 2rem;
            animation: fadeIn 1s ease-out;
        }
        
        .section-divider {
            height: 3px;
            background: linear-gradient(45deg, #1976D2, #7eaee7, #a9c9f0);
            border-radius: 2px;
            margin: 3rem auto;
            max-width: 200px;
            animation: fadeIn 1s ease-out;
        }
        
        .spec-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(15, 70, 125, 0.1);
            transition: all 0.3s ease;
            animation: slideIn 0.8s ease-out;
            border-left: 3px solid #a9c9f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .spec-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(15, 70, 125, 0.2);
            border-left-color: #1976D2;
        }
        
        .spec-label {
            color: #1976D2;
            font-weight: 600;
            font-size: 1rem;
        }
        
        .spec-value {
            color: #666;
            font-weight: 500;
            font-size: 1rem;
        }
        
        .hardware-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 800px;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            animation: fadeIn 1s ease-out;
        }
        
        .hardware-title {
            color: #1976D2;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .hardware-desc {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.6;
            text-align: center;
        }
        
        .classification-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: all 0.3s ease;
            animation: fadeIn 1s ease-out;
            border-top: 3px solid #a9c9f0;
            text-align: center;
        }
        
        .classification-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(15, 70, 125, 0.2);
            border-top-color: #1976D2;
        }
        
        .classification-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .classification-title {
            color: #1976D2;
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }
        
        .classification-desc {
            color: #666;
            font-size: 1rem;
            line-height: 1.4;
        }
        
        .feature-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: transform 0.3s ease;
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(15, 70, 125, 0.2);
        }
        
        .feature-card h3 {
            color: #1976D2;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .feature-card ul {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Add main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Page title
    st.markdown('<h1 class="page-title">📚 Learn More About HeartStream</h1>', unsafe_allow_html=True)
    
    # Hardware Components Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="hardware-info">
            <div class="hardware-title">🔧 Hardware Components</div>
            <div class="hardware-desc">
                HeartStream utilizes professional-grade hardware components including the <strong>AD8232 ECG sensor</strong> 
                for precise cardiac signal acquisition and <strong>ESP8266 microcontroller</strong> for seamless wireless 
                connectivity and real-time data transmission to ThingSpeak cloud platform.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Technical Specifications Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">Technical Specifications</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div style="background: #f8f9fa; border-radius: 10px; padding: 2rem; margin: 1rem; box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);">
                <h3 style="color: #1976D2; margin-bottom: 1.5rem; text-align: center;">🔧 Hardware Requirements</h3>
                <div class="spec-item">
                    <span class="spec-label">CPU</span>
                    <span class="spec-value">Intel i5 or AMD Ryzen 5+</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">RAM</span>
                    <span class="spec-value">8GB minimum, 16GB recommended</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Storage</span>
                    <span class="spec-value">2GB available space</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">OS</span>
                    <span class="spec-value">Windows 10+, macOS 10.14+, Linux</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">GPU</span>
                    <span class="spec-value">CUDA-compatible (optional)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="background: #f8f9fa; border-radius: 10px; padding: 2rem; margin: 1rem; box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);">
                <h3 style="color: #1976D2; margin-bottom: 1.5rem; text-align: center;">📡 Data Processing</h3>
                <div class="spec-item">
                    <span class="spec-label">Sampling Rate</span>
                    <span class="spec-value">360 Hz</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Input Channels</span>
                    <span class="spec-value">2-lead ECG (Lead I, Lead II)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Signal Range</span>
                    <span class="spec-value">±5 mV</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Resolution</span>
                    <span class="spec-value">12-bit ADC</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Latency</span>
                    <span class="spec-value">&lt; 100ms processing time</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ECG Beat Classification Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">ECG Beat Classification</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem; margin-bottom: 2rem;">HeartStream accurately identifies 5 different types of cardiac rhythms using advanced neural networks</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
            <div class="classification-card">
                <div class="classification-icon">💓</div>
                <div class="classification-title">Normal (N)</div>
                <div class="classification-desc">Regular sinus rhythm with normal cardiac cycles</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="classification-card">
                <div class="classification-icon">⚡</div>
                <div class="classification-title">Supraventricular (S)</div>
                <div class="classification-desc">Premature beats originating above ventricles</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="classification-card">
                <div class="classification-icon">🔥</div>
                <div class="classification-title">Ventricular (V)</div>
                <div class="classification-desc">Abnormal beats from ventricular chambers</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="classification-card">
                <div class="classification-icon">🔄</div>
                <div class="classification-title">Fusion (F)</div>
                <div class="classification-desc">Combined ventricular and supraventricular beats</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
            <div class="classification-card">
                <div class="classification-icon">❓</div>
                <div class="classification-title">Unknown (Q)</div>
                <div class="classification-desc">Unclassified or artifact-affected beats</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Additional Features Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">Additional Features</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>📋 Comprehensive Analysis</h3>
                <ul>
                    <li>Multi-beat ECG interpretation</li>
                    <li>Heart rate variability analysis</li>
                    <li>Rhythm classification accuracy</li>
                    <li>Morphology assessment</li>
                    <li>Trend analysis over time</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>🔧 Smart Integration</h3>
                <ul>
                    <li>Real-time data streaming</li>
                    <li>CSV export functionality</li>
                    <li>PDF report generation</li>
                    <li>Cloud storage compatibility</li>
                    <li>API for third-party applications</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Model Information Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">AI Model Information</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>🧠 Neural Network Architecture</h3>
                <ul>
                    <li>PyTorch-based deep learning model</li>
                    <li>Convolutional Neural Network (CNN)</li>
                    <li>Trained on MIT-BIH Arrhythmia Database</li>
                    <li>48,000+ ECG samples for training</li>
                    <li>5-class classification system</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>📊 Performance Metrics</h3>
                <ul>
                    <li>99.7% overall accuracy</li>
                    <li>360 Hz sampling rate</li>
                    <li>Real-time processing capability</li>
                    <li>Low latency (&lt; 100ms)</li>
                    <li>Robust noise handling</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # System Requirements Section
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1976D2; margin-bottom: 2rem; font-size: 2.5rem;">System Requirements</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>💻 Software Dependencies</h3>
                <ul>
                    <li>Python 3.8 or higher</li>
                    <li>Streamlit framework</li>
                    <li>PyTorch for AI inference</li>
                    <li>NumPy for numerical operations</li>
                    <li>Pandas for data manipulation</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>🌐 Network Requirements</h3>
                <ul>
                    <li>WiFi connection for ESP8266</li>
                    <li>Internet access for ThingSpeak</li>
                    <li>Minimum 1 Mbps bandwidth</li>
                    <li>Low latency network preferred</li>
                    <li>Port 80/443 access required</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <footer style="text-align: center; margin-top: 3rem; padding-bottom: 2rem;">
            <p style="color: #666; font-size: 1.1rem;">
                For more information or technical support, please contact our development team.
            </p>
            <p style="color: #666; font-size: 1.1rem;">All Rights Reserved. ©️ 2025 HeartStream</p>
        </footer>
    """, unsafe_allow_html=True)
    
    # Close main content wrapper
    st.markdown('</div>', unsafe_allow_html=True) 