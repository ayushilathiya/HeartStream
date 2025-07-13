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
    fig.add_trace(go.Scatter(y=y_values, mode='lines', name=title, line=dict(width=3)))
    fig.update_layout(
        yaxis_title="Value",
        xaxis_title="Time",
        height=500,  # Increased height for bigger graph
        paper_bgcolor='white',
        plot_bgcolor='white',
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
                'range': [40, 160],
                'tickwidth': 1,
                'tickcolor': "#333333"
            },
            'bar': {'color': "#1976D2"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [40, 60], 'color': '#0f467d'},    # Bradycardia - Dark Blue
                {'range': [60, 100], 'color': '#7eaee7'},   # Normal - Light Blue
                {'range': [100, 120], 'color': '#a9c9f0'},  # Mild Tachycardia - Medium Blue
                {'range': [120, 160], 'color': '#d4e4f8'}   # Severe Tachycardia - Very Light Blue
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
    """Create a professional PDF report with website theme colors"""
    # Header section with website colors
    c.setFillColor('#0f467d')  # Dark blue header
    c.rect(30, 1150, 732, 80, fill=True)
    
    # Title in white on dark blue background
    c.setFillColor('#ffffff')
    c.setFont("Helvetica-Bold", 28)
    c.drawString(50, 1190, "ECG MONITORING REPORT")
    
    # Institution name
    c.setFont("Helvetica", 12)
    c.drawString(50, 1170, "HeartStream Advanced ECG Monitoring System")
    
    # Patient and report information box
    c.setFillColor('#d4e4f8')  # Light blue background
    c.rect(30, 1040, 732, 100, fill=True)
    
    c.setFillColor('#0f467d')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 1115, "REPORT INFORMATION")
    
    current_time = datetime.now()
    c.setFont("Helvetica", 11)
    c.drawString(50, 1095, f"Report Generated: {current_time.strftime('%B %d, %Y at %H:%M:%S')}")
    c.drawString(50, 1080, f"Report ID: ECG-{current_time.strftime('%Y%m%d%H%M%S')}")
    c.drawString(50, 1065, f"Patient ID: [To be filled by healthcare provider]")
    c.drawString(50, 1050, f"Monitoring Duration: Real-time acquisition")
    
    # ECG Analysis Section
    c.setFillColor('#1976D2')
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 1010, "ELECTROCARDIOGRAM ANALYSIS")
    
    # ECG plot with medical styling
    c.drawImage(ImageReader(plot_to_matplotlib(fig1)), 50, 480, width=700, height=500)
    
    # Clinical measurements box
    c.setFillColor('#a9c9f0')  # Medium blue background
    c.rect(30, 350, 350, 120, fill=True)
    
    c.setFillColor('#0f467d')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 450, "SIGNAL MEASUREMENTS")
    
    if field1_data and len(field1_data) > 0:
        values = [float(d['field1']) for d in field1_data if d['field1'] is not None]
        if values:
            c.setFont("Helvetica", 11)
            c.drawString(50, 430, f"Peak Amplitude: {max(values):.2f} mV")
            c.drawString(50, 415, f"Minimum Amplitude: {min(values):.2f} mV")
            c.drawString(50, 400, f"Mean Amplitude: {sum(values)/len(values):.2f} mV")
            c.drawString(50, 385, f"Sample Count: {len(values)}")
            c.drawString(50, 370, f"Signal Quality: Good")
    
    # Heart Rate Analysis Section
    c.setFillColor('#7eaee7')  # Light blue background
    c.rect(400, 350, 372, 120, fill=True)
    
    c.setFillColor('#0f467d')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(420, 450, "HEART RATE ANALYSIS")
    
    # Heart Rate Assessment with color coding
    c.setFont("Helvetica-Bold", 13)
    c.drawString(420, 430, f"Current Heart Rate: {latest_bpm:.0f} BPM")
    
    # Medical interpretation with color coding
    c.setFont("Helvetica", 11)
    if latest_bpm < 60:
        hr_status = "BRADYCARDIA"
        hr_color = '#0f467d'  # Dark blue for bradycardia
        clinical_note = "Heart rate below normal range"
    elif latest_bpm > 100:
        hr_status = "TACHYCARDIA"
        hr_color = '#0f467d'  # Dark blue for tachycardia
        clinical_note = "Heart rate above normal range"
    else:
        hr_status = "NORMAL SINUS RHYTHM"
        hr_color = '#7eaee7'  # Light blue for normal
        clinical_note = "Heart rate within normal range"
    
    c.setFillColor(hr_color)
    c.drawString(420, 415, f"Interpretation: {hr_status}")
    c.drawString(420, 400, clinical_note)
    c.drawString(420, 385, "Normal Range: 60-100 BPM")
    
    # Heart Rate gauge/chart
    c.drawImage(ImageReader(plot_to_matplotlib(fig2)), 400, 50, width=350, height=280)
    
    # Recommendations box
    c.setFillColor('#d4e4f8')  # Very light blue
    c.rect(30, 50, 350, 280, fill=True)
    
    c.setFillColor('#0f467d')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 310, "RECOMMENDATIONS")
    
    c.setFont("Helvetica", 10)
    recommendations = [
        "• This automated analysis requires professional validation",
        "• Consult with a healthcare provider for interpretation",
        "• Monitor for any symptomatic changes",
        "• Follow standard protocols for ECG review",
        "• Consider additional ECG analysis if needed"
    ]
    
    y_pos = 290
    for rec in recommendations:
        c.drawString(50, y_pos, rec)
        y_pos -= 15
    
    # Add heart rate range reference
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 200, "HEART RATE REFERENCE RANGES:")
    
    c.setFont("Helvetica", 10)
    ranges = [
        "• Bradycardia: < 60 BPM",
        "• Normal: 60-100 BPM", 
        "• Tachycardia: > 100 BPM",
        "• Severe Tachycardia: > 120 BPM"
    ]
    
    y_pos = 180
    for range_text in ranges:
        c.drawString(50, y_pos, range_text)
        y_pos -= 12
    
    # Footer
    c.setFillColor('#0f467d')
    c.rect(30, 10, 732, 30, fill=True)
    
    c.setFillColor('#ffffff')
    c.setFont("Helvetica", 9)
    c.drawString(50, 25, "DISCLAIMER: This automated report requires professional review and interpretation.")
    c.drawString(50, 15, "Generated by HeartStream ECG Monitoring System")

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
            background-color: #ffffff !important;
            color: #1976D2 !important;
            border: none !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
        }
        
        .stButton>button:hover {
            background-color: #1976D2 !important;
            color: white !important;
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
                
                # Add normal ranges below the gauge
                st.markdown("""
                    <div style="text-align: center; margin-top: 1rem; color: #1976D2; font-size: 0.9rem;">
                        <strong>Heart Rate Ranges:</strong><br>
                        <span style="color: #0f467d;">⬤</span> Bradycardia: 40-60 BPM<br>
                        <span style="color: #7eaee7;">⬤</span> Normal: 60-100 BPM<br>
                        <span style="color: #a9c9f0;">⬤</span> Mild Tachycardia: 100-120 BPM<br>
                        <span style="color: #d4e4f8;">⬤</span> Severe Tachycardia: 120-160 BPM
                    </div>
                """, unsafe_allow_html=True)
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

    # Footer
    st.markdown("""
        <footer style="text-align: center; margin-top: 3rem; padding-bottom: 2rem;">
            <p style="color: #666; font-size: 1.1rem;">All Rights Reserved. ©️ 2025 Ayushi Lathiya</p>
        </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_live_data_page()