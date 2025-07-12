import streamlit as st
import plotly.graph_objects as go
import requests
import json
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
from datetime import datetime
import time
import numpy as np
from PIL import Image
from reportlab.lib.utils import ImageReader
import queue
import threading
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

DATA_SOURCE_THINGSPEAK = "ThingSpeak"
MAX_DATA_POINTS = 200  # Increased from 100

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
        yaxis_title="Value",
        xaxis_title="Time",
        height=500,  # Increased height for bigger graph
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            gridwidth=1
        )
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
    try:
        if not isinstance(fig, go.Figure):
            return None
            
        if not hasattr(fig, 'data') or not fig.data:
            return None
            
        if hasattr(fig.data[0], 'y'):
            # R Peaks plot conversion
            plt.figure(figsize=(10, 6))
            y_values = getattr(fig.data[0], 'y', [])
            plt.plot(y_values, color='#1976D2', linewidth=2)
            plt.title('Live ECG', color='#1976D2', pad=20, fontsize=16)  # Changed from 'PulsePeak Monitor' to 'Live ECG'
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
            # BPM Gauge conversion
            plt.figure(figsize=(10, 8))
            value = getattr(fig.data[0], 'value', 0)
            
            # Create circular gauge
            circle = patches.Circle((0.5, 0.5), 0.4, color='#a9c9f0', alpha=0.3)
            ax = plt.gca()
            ax.add_patch(circle)
            
            # Draw gauge arc
            ax.add_patch(patches.Arc(
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
                   facecolor='white')
        plt.close()
        buf.seek(0)
        
        return Image.open(buf)
    except Exception as e:
        st.error(f"Error converting plot: {str(e)}")
        return None

def create_pdf_report(c, fig1, fig2, field1_data, latest_bpm):
    """Create a professional PDF report with additional content"""
    # Title and header
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor('#1976D2')
    c.drawString(50, 1180, "ECG Monitoring Report")
    
    # Add logo/header image if available
    # c.drawImage("path/to/logo.png", 500, 1150, width=100, height=100)
    
    # Basic Information Section
    c.setFont("Helvetica", 12)
    c.setFillColor('#666666')
    current_time = datetime.now()
    c.drawString(50, 1160, f"Generated on: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 1140, f"Report ID: {current_time.strftime('%Y%m%d%H%M%S')}")
    
    # Add separator line
    c.setStrokeColor('#1976D2')
    c.line(50, 1130, 742, 1130)
    
    # ECG Analysis Section
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor('#1976D2')
    c.drawString(60, 1100, "ECG Analysis")
    
    # Live ECG plot
    c.drawImage(ImageReader(plot_to_matplotlib(fig1)), 50, 600, width=700, height=500)
    
    # Signal Statistics
    c.setFont("Helvetica-Bold", 14)
    if field1_data and len(field1_data) > 0:
        values = [float(d['field1']) for d in field1_data if d['field1'] is not None]
        if values:
            c.drawString(50, 580, "Signal Statistics:")
            c.setFont("Helvetica", 12)
            c.drawString(70, 560, f"Maximum Amplitude: {max(values):.2f}")
            c.drawString(70, 540, f"Minimum Amplitude: {min(values):.2f}")
            c.drawString(70, 520, f"Average Amplitude: {sum(values)/len(values):.2f}")
    
    # Heart Rate Analysis Section
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor('#1976D2')
    c.drawString(50, 480, "Heart Rate Analysis")
    
    # Heart Rate plot
    c.drawImage(ImageReader(plot_to_matplotlib(fig2)), 50, 100, width=500, height=350)
    
    # Heart Rate Assessment
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 80, f"Current Heart Rate: {latest_bpm:.0f} BPM")
    
    c.setFont("Helvetica", 12)
    # Add heart rate interpretation
    hr_status = "Normal"
    if latest_bpm < 60:
        hr_status = "Bradycardia (Low Heart Rate)"
    elif latest_bpm > 100:
        hr_status = "Tachycardia (High Heart Rate)"
    
    c.drawString(50, 60, f"Status: {hr_status}")
    c.drawString(50, 40, "Normal Range: 60-100 BPM")
    
    # Footer with standard Helvetica font instead of Italic
    c.setFont("Helvetica", 8)  # Changed from Helvetica-Italic
    c.setFillColor('#666666')  # Added gray color for footer
    footer_text = "This report is generated automatically and should be reviewed by a healthcare professional."
    c.drawString(50, 20, footer_text)
    c.drawString(50, 10, "HeartStream - Advanced ECG Monitoring System")

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
            background-color: #7eaee7 !important;
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
    st.markdown('<h1 class="page-title">Live ECG Monitor</h1>', unsafe_allow_html=True)

    try:
        # Get ThingSpeak credentials from secrets
        channel_id = st.secrets["THINGSPEAK_CHANNEL_ID"]
        api_key = st.secrets["THINGSPEAK_API_KEY"]

        # 1. Live ECG (full width)
        st.markdown("""
            <div class="metric-card">
                <h3>Live ECG</h3>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            field1_data = get_thingspeak_field(channel_id, api_key, 1)
            fig1 = plot_data(field1_data, 1, "ECG Signal")
            st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading ECG data: {str(e)}")

        # Add spacing
        st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

        # 2. Heart Rate Monitor (centered, below ECG)
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <h3>Heart Rate Monitor</h3>
                </div>
            """, unsafe_allow_html=True)
            try:
                field2_data = get_thingspeak_field(channel_id, api_key, 2)
                latest_bpm = float(field2_data[-1]['field2']) if field2_data and field2_data[-1]['field2'] else 0
                fig_gauge = create_bpm_gauge(latest_bpm)
                st.plotly_chart(fig_gauge, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading BPM data: {str(e)}")

        st.markdown("<hr style='margin: 4rem 0; border: none; height: 2px; background: linear-gradient(to right, #1976D2, #7eaee7); opacity: 0.3;'>", unsafe_allow_html=True)


        # Add refresh button
        _, col1, col2 = st.columns([0.7, 1, 1])  # Add padding columns for centering
            
        with col1:
                st.button("🔄 Refresh Data", key="secondary_button")
            
        with col2:
                if st.button("📥 Generate PDF"):
                    try:
                        with st.spinner("Generating PDF Report..."):
                            buffer = io.BytesIO()
                            c = canvas.Canvas(buffer, pagesize=(792, 1224))
                            create_pdf_report(c, fig1, fig_gauge, field1_data, latest_bpm)
                            c.save()
                            buffer.seek(0)
                            
                            st.success("PDF generated successfully!")
                            
                            # Create download button
                            st.download_button(
                                label="💾 Save PDF",
                                data=buffer,
                                file_name=f"ECG_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                    except Exception as e:
                        st.error("Error during PDF generation:")
                        st.error(str(e))
                        import traceback
                        st.code(traceback.format_exc())

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    show_live_data_page()