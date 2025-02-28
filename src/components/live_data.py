import streamlit as st
import plotly.graph_objects as go
import requests
import json
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import time
import numpy as np
from PIL import Image
from reportlab.lib.utils import ImageReader

def get_thingspeak_field(channel_id, api_key, field_number):
    # Add results parameter to get last 60 data points
    url = f"https://api.thingspeak.com/channels/{channel_id}/fields/{field_number}.json"
    params = {
        'api_key': api_key,
        'results': 60,
        'dynamic': 'true'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        if 'feeds' not in data:
            raise ValueError("No feeds data in response")
        return data['feeds']
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data: {str(e)}")

def plot_data(data, field_number, title):
    fig = go.Figure()
    y_values = [float(entry[f'field{field_number}']) for entry in data if entry[f'field{field_number}'] is not None]
    fig.add_trace(go.Scatter(y=y_values, mode='lines', name=title))
    fig.update_layout(
        title=title,
        yaxis_title="Value",
        xaxis_title="Time",
        height=300
    )
    return fig

def create_bpm_gauge(bpm_value):
    """Create a gauge chart for BPM visualization"""
    if bpm_value is None:
        bpm_value = 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bpm_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {
                'range': [60, 150],
                'tickwidth': 1,
                'tickcolor': "#1976D2"
            },
            'bar': {'color': "#1976D2"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [60, 70], 'color': '#7eaee7'},
                {'range': [70, 120], 'color': '#a9c9f0'},
                {'range': [120, 150], 'color': '#7eaee7'}
            ],
            'threshold': {
                'line': {'color': "#1976D2", 'width': 4},
                'thickness': 0.75,
                'value': bpm_value
            }
        },
        title={
            'text': "BPM",
            'font': {'size': 24, 'color': '#1976D2'}
        },
        number={
            'font': {'size': 40, 'color': '#1976D2'},  # Reduced size
            'suffix': ""  # Removed BPM suffix
        }
    ))
    
    fig.update_layout(
        height=350,  # Reduced height
        margin=dict(
            l=40,
            r=40,
            t=80,
            b=40
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font={
            'color': "#1976D2",
            'family': "Arial",
            'size': 20
        },
        showlegend=False
    )
    
    return fig

def plot_to_matplotlib(fig):
    """Convert Plotly figure to Matplotlib figure and save to bytes"""
    try:
        if isinstance(fig, go.Figure):
            if len(fig.data) > 0 and hasattr(fig.data[0], 'y'):
                # R Peaks plot conversion
                plt.figure(figsize=(10, 6))
                y_values = fig.data[0].y
                plt.plot(y_values, color='#1976D2', linewidth=2)
                plt.title('PulsePeak Monitor', color='#1976D2', pad=20, fontsize=16)
                plt.xlabel('Time', color='#666666')
                plt.ylabel('Value', color='#666666')
                plt.grid(True, alpha=0.3)
                plt.fill_between(range(len(y_values)), y_values, alpha=0.2, color='#7eaee7')
                
                # Style improvements
                plt.gca().set_facecolor('#f8f9fa')
                plt.gcf().set_facecolor('#ffffff')
                for spine in plt.gca().spines.values():
                    spine.set_color('#dddddd')
                
            elif hasattr(fig.data[0], 'value'):
                # BPM Gauge conversion (existing code)
                plt.figure(figsize=(10, 8))
                value = fig.data[0].value
                
                # Create circular gauge background
                circle = plt.Circle((0.5, 0.5), 0.4, color='#a9c9f0', alpha=0.3)
                ax = plt.gca()
                ax.add_patch(circle)
                
                # Draw gauge arc
                ax.add_patch(plt.matplotlib.patches.Arc(
                    (0.5, 0.5), 0.8, 0.8, 
                    theta1=0, theta2=180, 
                    color='#1976D2', 
                    linewidth=2
                ))
                
                # Add tick marks and labels
                for i in range(60, 151, 30):
                    angle = np.pi * (1 - (i - 60) / 90)
                    x = 0.5 + 0.45 * np.cos(angle)
                    y = 0.5 + 0.45 * np.sin(angle)
                    plt.text(x, y, str(i), 
                           ha='center', va='center',
                           color='#1976D2',
                           fontsize=12)
                
                # Add arrow pointer
                angle = np.pi * (1 - (value - 60) / 90)
                dx = 0.4 * np.cos(angle)
                dy = 0.4 * np.sin(angle)
                plt.arrow(0.5, 0.5, dx, dy,
                         head_width=0.02,
                         head_length=0.02,
                         fc='#1976D2',
                         ec='#1976D2',
                         linewidth=2)
                
                # Add BPM value
                plt.text(0.5, 0.5, f'{value:.0f}',
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=36,
                        color='#1976D2',
                        fontweight='bold')
                
                plt.axis('equal')
                plt.axis('off')

            # Common save settings
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                       transparent=True, pad_inches=0.5,
                       facecolor='white')  # Ensure white background
            plt.close()
            buf.seek(0)
            
            image = Image.open(buf)
            return image
    except Exception as e:
        st.error(f"Error converting plot: {str(e)}")
        return None

def show_live_data_page():
    st.markdown("""
        <style>
        .stApp {
            background-color: #d4e4f8 !important;
        }
        
        .page-title {
            font-size: 4rem !important;
            font-weight: 800;
            text-align: center;
            background: linear-gradient(45deg, #1976D2, #7eaee7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 3rem !important;  /* Increased spacing */
            animation: fadeIn 1s ease-out;
        }
        
        .metric-card {
            background: #a9c9f0 !important;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-out;
            text-align: center !important;
        }
        
        .metric-card h3 {
            color: #1976D2 !important;
            font-size: 1.5rem !important;
            text-align: center !important;
            margin-bottom: 1rem !important;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            background: #7eaee7 !important;
        }
        
        .download-section {
            background: #d4e4f8;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            text-align: center;
            animation: fadeIn 1s ease-out;
        }
        
        .download-section h3 {
            color: #1976D2 !important;
        }
        
        .stButton>button {
            background-color: #1976D2 !important;
            color: white !important;
            border: none !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            background-color: #0f467d !important;
            transform: translateY(-2px);
        }
        
        /* Override Plotly chart background */
        .js-plotly-plot .plotly .main-svg {
            background: transparent !important;
        }

        /* Active page indicator */
        [data-testid="stSidebarNav"] ul li:nth-child(2) div {
            background-color: #0f467d !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown('<h1 class="page-title">Live ECG</h1>', unsafe_allow_html=True)

    # ThingSpeak credentials from secrets
    channel_id = st.secrets["THINGSPEAK_CHANNEL_ID"]
    api_key = st.secrets["THINGSPEAK_API_KEY"]
    
    # Create two columns for R Peaks and BPM
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3 style="color: #1976D2; margin-bottom: 1rem;">PulsePeak Monitor</h3>
            </div>
        """, unsafe_allow_html=True)
        try:
            field1_data = get_thingspeak_field(channel_id, api_key, 1)
            fig1 = plot_data(field1_data, 1, "R Peaks")
            fig1.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
                yaxis=dict(gridcolor='rgba(0,0,0,0.1)')
            )
            st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading R Peaks data: {str(e)}")
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h3 style="color: #1976D2; margin-bottom: 1rem;">Heart Rate Monitor</h3>
            </div>
        """, unsafe_allow_html=True)
        try:
            field2_data = get_thingspeak_field(channel_id, api_key, 2)
            latest_bpm = float(field2_data[-1]['field2']) if field2_data and field2_data[-1]['field2'] else 0
            fig_gauge = create_bpm_gauge(latest_bpm)
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading BPM data: {str(e)}")

    # Refresh and Download section
    st.markdown("""
        <div class="download-section">
            <h3 style="color: #1976D2; margin-bottom: 1rem;">Actions</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
            st.rerun()
    
    with col2:
        if st.button("📥 Download Report", use_container_width=True, type="secondary"):
            try:
                with st.spinner("Generating PDF Report..."):
                    # Convert plots to PIL images
                    img1 = plot_to_matplotlib(fig1)
                    img2 = plot_to_matplotlib(fig_gauge)
                    
                    if img1 is None or img2 is None:
                        st.error("Failed to convert plots")
                        return
                    
                    # Create PDF
                    buffer = io.BytesIO()
                    c = canvas.Canvas(buffer, pagesize=(612, 792))  # Standard letter size
                    
                    # Add title and timestamp
                    c.setFont("Helvetica-Bold", 24)
                    c.setFillColor('#1976D2')
                    c.drawString(50, 750, "ECG Monitoring Report")
                    
                    c.setFont("Helvetica", 12)
                    c.setFillColor('#666666')
                    c.drawString(50, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Add plots using ImageReader
                    c.drawImage(ImageReader(img1), 50, 400, width=500, height=300, preserveAspectRatio=True)
                    c.drawImage(ImageReader(img2), 50, 50, width=500, height=300, preserveAspectRatio=True)
                    
                    c.save()
                    buffer.seek(0)
                    
                    st.success("PDF generated successfully!")
                    
                    # Create download button
                    st.download_button(
                        label="💾 Save PDF",
                        data=buffer,
                        file_name=f"ecg_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error("Error during PDF generation:")
                st.error(str(e))
                import traceback
                st.code(traceback.format_exc())

if __name__ == "__main__":
    show_live_data_page()