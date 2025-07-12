import streamlit as st
import pdfplumber
import numpy as np
import pandas as pd
from PIL import Image
import io
import re
import torch
import traceback
import os
import sys
from PIL import UnidentifiedImageError
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
from scipy import signal as scipy_signal

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.models.ecgnet import ECGNet
from src.services.ai_service import generate_analysis

# Load trained ECGNet model
try:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ECGNet(num_classes=5)
    model_path = os.path.join(project_root, 'best_model.pth')
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    model = model.to(device)
    CLASS_NAMES = ['Normal', 'LBBB', 'RBBB', 'APB', 'PVC']
except Exception as e:
    st.error(f"Error loading model: {e}")
    model = None

def is_likely_ecg_plot(image, position=None):
    """Enhanced helper function to identify ECG plots"""
    try:
        # Convert to numpy array for analysis
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # More lenient position filter - only skip very small y positions
        if position and position.get('y0', 0) < 100:
            return False
            
        # More lenient aspect ratio - allow wider range
        aspect_ratio = width / height
        if not (0.5 < aspect_ratio < 8.0):
            return False
            
        # Convert to grayscale if color
        if len(img_array.shape) == 3:
            img_array = np.mean(img_array, axis=2)
        
        # Look for ECG peak patterns - more lenient threshold
        row_means = np.mean(img_array, axis=0)
        peak_count = len(np.where(np.diff(np.signbit(np.diff(row_means))))[0])
        
        # More lenient peak count - ECG should have some variation
        return peak_count > 20  # Reduced from 50
            
    except Exception as e:
        return False

def extract_data_from_pdf(pdf_file):
    """Extract ECG data and metadata from PDF"""
    try:
        # Extract text and metadata using pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            data = {
                'text': [],
                'images': [],
                'metadata': {}
            }
            
            for page in pdf.pages:
                text = page.extract_text() or ""
                data['text'].append(text)
                
                if 'Report ID:' in text:
                    report_id = re.search(r'Report ID: (\d+)', text)
                    if report_id:
                        data['metadata']['report_id'] = report_id.group(1)
                
                if 'Current Heart Rate:' in text:
                    bpm = re.search(r'Current Heart Rate: (\d+)', text)
                    if bpm:
                        data['metadata']['heart_rate'] = int(bpm.group(1))

        # Extract images using PyMuPDF
        pdf_bytes = io.BytesIO(pdf_file.getvalue())
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        all_images = []  # Store all images for debugging
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Get image dimensions from the image list (more compatible)
                    bbox = img[1:5] if len(img) > 4 else [0, 0, 0, 0]
                    position = {
                        'x0': bbox[0],
                        'y0': bbox[1], 
                        'x1': bbox[2],
                        'y1': bbox[3]
                    }
                    
                    image = Image.open(io.BytesIO(image_bytes))
                    gray_image = image.convert('L')
                    
                    # More lenient size requirements
                    if (image.size[0] > 200 and  # Reduced minimum width
                        image.size[1] > 100):     # Reduced minimum height
                        all_images.append((image, gray_image, position))
                        
                        # Check if it's likely an ECG plot
                        if is_likely_ecg_plot(gray_image, position):
                            data['images'].append(image)
                            break
                    
                except Exception as img_error:
                    st.error(f"Error processing image {img_index + 1}: {str(img_error)}")
                    continue
        
        doc.close()
        
        # If no ECG plots found, try to use the largest image as fallback
        if not data['images'] and all_images:
            largest_image = max(all_images, key=lambda x: x[0].size[0] * x[0].size[1])
            data['images'].append(largest_image[0])
        
        if not data['images']:
            st.error(f"No suitable images found in the PDF")
        
        return data
            
    except Exception as e:
        raise Exception(f"Error extracting PDF data: {str(e)}")

def analyze_ecg_data(data):
    """Analyze the extracted ECG data using the trained ECGNet model with improved preprocessing"""
    try:
        if model is None:
            return {
                'prediction': 'Model not loaded',
                'confidence': 0,
                'details': {
                    'heart_rate': data['metadata'].get('heart_rate', 'N/A'),
                    'report_id': data['metadata'].get('report_id', 'N/A')
                }
            }
        
        if data['images']:
            ecg_image = data['images'][0]
            
            # Improved preprocessing for better accuracy
            # Convert to grayscale
            img_gray = ecg_image.convert('L')
            
            # Resize to a reasonable intermediate size first
            img_resized = img_gray.resize((500, 200))  # Better aspect ratio
            
            # Convert to numpy array
            img_array = np.array(img_resized).astype(np.float32)
            
            # Extract signal from the middle row (where ECG signal is typically located)
            middle_row = img_array.shape[0] // 2
            signal = img_array[middle_row, :]
            
            # Normalize the signal (invert if needed - ECG should have peaks going up)
            signal_mean = np.mean(signal)
            if signal_mean > 127:  # If background is white and signal is dark
                signal = 255 - signal
            
            # Resample to 250 points for model input
            if len(signal) != 250:
                signal = scipy_signal.resample(signal, 250)
            
            # Normalize similar to training data
            signal = np.array(signal, dtype=np.float32)
            signal = (signal - np.mean(signal)) / (np.std(signal) + 1e-8)
            
            # Prepare tensor
            tensor = torch.FloatTensor(signal).reshape(1, 1, -1)
            tensor = tensor.to(device)
            
            # Get prediction with temperature scaling for better confidence
            with torch.no_grad():
                outputs = model(tensor)
                # Apply temperature scaling for better calibrated confidence
                temperature = 1.5
                outputs = outputs / temperature
                probabilities = torch.softmax(outputs, dim=1)
                prediction_idx = torch.argmax(outputs, dim=1).item()
                prediction_idx = int(prediction_idx)
                confidence = probabilities[0][prediction_idx].item()
            
            # Create probability dictionary
            prob_dict = {
                name: float(prob) 
                for name, prob in zip(CLASS_NAMES, probabilities[0].tolist())
            }
            
            result = {
                'prediction': CLASS_NAMES[prediction_idx],
                'confidence': confidence,
                'details': {
                    'heart_rate': data['metadata'].get('heart_rate', 'N/A'),
                    'report_id': data['metadata'].get('report_id', 'N/A'),
                    'probabilities': prob_dict
                }
            }
            
            return result
            
    except Exception as e:
        return {
            'prediction': 'Error',
            'confidence': 0,
            'details': str(e)
        }

def get_detailed_analysis(analysis_result):
    """Generate detailed medical analysis using Groq AI"""
    prompt = f"""Given the following ECG analysis results, provide a detailed medical interpretation:
- Primary Classification: {analysis_result['prediction']}
- Confidence Score: {analysis_result['confidence']:.2%}
- Heart Rate: {analysis_result['details']['heart_rate']} BPM
- Individual Class Probabilities:
{chr(10).join([f'  - {k}: {v:.2%}' for k,v in analysis_result['details']['probabilities'].items()])}

Provide a comprehensive analysis including:
1. Primary diagnosis and interpretation
2. Clinical significance of the findings
3. Potential underlying causes
4. Common complications associated with this condition
5. General management recommendations
6. Whether immediate medical attention is needed
7. What the patient should monitor

Format the response in a clear, professional medical style with sections."""

    ai_response = generate_analysis(analysis_result, prompt)
    return ai_response

def plot_to_matplotlib(image):
    """Convert PIL image to matplotlib plot for PDF inclusion with medical styling"""
    plt.figure(figsize=(10, 6))
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.title('ECG Recording Analysis', fontsize=16, fontweight='bold', color='#1976D2', pad=20)
    
    # Style improvements to match live_data.py
    plt.gca().set_facecolor('#ffffff')  # White background
    plt.gcf().set_facecolor('#ffffff')  # White figure background
    
    # Add medical-grade styling
    plt.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', pad_inches=0.5)
    plt.close()
    img_buf.seek(0)
    return img_buf

def create_pdf_report(c, image, analysis_result, detailed_report):
    """Create a professional PDF report with website theme colors"""
    width, height = A4
    c.setPageSize((width, height))
    margin = 50  # Balanced margin for A4

    # Header section with website colors
    c.setFillColor('#0f467d')  # Dark blue header
    c.rect(0, height-80, width, 80, fill=True)
    
    # Title in white on dark blue background
    c.setFillColor('#ffffff')
    c.setFont("Helvetica-Bold", 26)  # Slightly reduced font size
    c.drawString(margin, height-45, "ECG ANALYSIS REPORT")
    
    # Institution name
    c.setFont("Helvetica", 12)
    c.drawString(margin, height-65, "HeartStream Advanced ECG Analysis System")
    
    # Report information box
    c.setFillColor('#d4e4f8')  # Light blue background
    c.rect(margin-30, height-180, width-2*margin+60, 90, fill=True)
    
    c.setFillColor('#0f467d')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, height-105, "REPORT INFORMATION")
    
    current_time = datetime.now()
    c.setFont("Helvetica", 11)
    c.drawString(margin, height-125, f"Report Generated: {current_time.strftime('%B %d, %Y at %H:%M:%S')}")
    c.drawString(margin, height-140, f"Report ID: ANALYSIS-{current_time.strftime('%Y%m%d%H%M%S')}")
    c.drawString(margin, height-155, f"Analysis Type: AI-Powered ECG Classification")
    
    # AI Analysis Results Section
    c.setFillColor('#1976D2')
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height-210, "AI ANALYSIS RESULTS")
    
    # Results box
    c.setFillColor('#a9c9f0')  # Medium blue background
    c.rect(margin-30, height-320, width-2*margin+60, 100, fill=True)
    
    c.setFillColor('#0f467d')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, height-240, "CLASSIFICATION RESULTS")
    
    c.setFont("Helvetica", 11)
    c.drawString(margin, height-260, f"Primary Classification: {analysis_result['prediction']}")
    c.drawString(margin, height-275, f"Confidence Level: {analysis_result['confidence']:.2%}")
    c.drawString(margin, height-290, f"Heart Rate: {analysis_result['details']['heart_rate']} BPM")
    c.drawString(margin, height-305, f"Analysis Status: Complete")
    
    # ECG Recording Section
    c.setFillColor('#1976D2')
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height-350, "ECG RECORDING")

    # ECG plot
    try:
        img_buf = plot_to_matplotlib(image)
        img = ImageReader(img_buf)
        img_width = width - 2*margin
        img_height = 180
        c.drawImage(img, margin, height-550, width=img_width, height=img_height)
    except Exception as e:
        c.setFillColor('#ff4444')
        c.drawString(margin, height-380, "Error rendering ECG plot")
    
    # Recommendations box - made larger to fit all text
    c.setFillColor('#d4e4f8')  # Very light blue
    c.rect(margin-30, height-720, width-2*margin+60, 140, fill=True)
    
    c.setFillColor('#0f467d')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, height-600, "RECOMMENDATIONS")
    
    c.setFont("Helvetica", 10)
    recommendations = [
        "• This AI analysis requires professional validation",
        "• Results should be interpreted by a healthcare provider",
        "• Consider additional diagnostic tests if indicated",
        "• Follow standard protocols for AI-assisted diagnosis",
        "• Recommend additional ECG analysis if needed"
    ]
    
    y_pos = height-620
    for rec in recommendations:
        c.drawString(margin, y_pos, rec)
        y_pos -= 15
    
    # Footer
    c.setFillColor('#0f467d')
    c.rect(0, 40, width, 30, fill=True)
    
    c.setFillColor('#ffffff')
    c.setFont("Helvetica", 9)
    c.drawString(margin, 55, "DISCLAIMER: This AI analysis requires professional review and interpretation.")
    c.drawString(margin, 45, "Generated by HeartStream ECG Analysis System")
    
    # Check if we need a new page for detailed analysis
    # Only create new page if we have substantial content
    content_lines = [line for line in detailed_report.split('\n') if line.strip()]
    estimated_content_lines = len(content_lines)
    
    # Create second page if there's any meaningful detailed analysis
    if estimated_content_lines > 5 and len(detailed_report.strip()) > 100:
        c.showPage()
        
        # Second page header
        c.setFillColor('#0f467d')
        c.rect(0, height-80, width, 80, fill=True)
        
        c.setFillColor('#ffffff')
        c.setFont("Helvetica-Bold", 26)
        c.drawString(margin, height-45, "DETAILED ANALYSIS")
        
        c.setFont("Helvetica", 12)
        c.drawString(margin, height-65, "HeartStream Advanced ECG Analysis System - Page 2")
        
        # Process and format ALL detailed report content
        c.setFillColor('#0f467d')
        c.setFont("Helvetica", 10)
        
        current_y = height - 120
        line_height = 12
        text_width = width - 2 * margin
        max_chars_per_line = int(text_width / 5.5)
        footer_space = 80  # Space needed for footer
        
        # Use the detailed report exactly as it appears in web interface
        # Clean up markdown symbols but preserve exact content
        clean_text = detailed_report.replace("###", "").replace("##", "").replace("#", "")
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip()]
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Split paragraph into lines
                lines = paragraph.split('\n')
                
            for line in lines:
                if line.strip():
                        # Check if this line is a heading (starts with number and period, or common heading patterns)
                        is_heading = (
                            line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or
                            'Diagnosis' in line or 'Clinical Significance' in line or 'Underlying Causes' in line or
                            'Complications' in line or 'Management' in line or 'Medical Attention' in line or
                            'Monitoring' in line or 'Interpretation' in line
                        )
                        
                        # Set font based on whether it's a heading
                        if is_heading:
                            c.setFont("Helvetica-Bold", 12)  # Larger, bold font for headings
                        else:
                            c.setFont("Helvetica", 10)  # Normal font for regular text
                        
                        # Process long lines by wrapping them
                        remaining_text = line.strip()
                        
                        while remaining_text:
                            # Check if we need a new page
                            if current_y <= footer_space:
                                # Create new page
                                c.showPage()
                                
                                # New page header
                                c.setFillColor('#0f467d')
                                c.rect(0, height-80, width, 80, fill=True)
                                
                                c.setFillColor('#ffffff')
                                c.setFont("Helvetica-Bold", 24)
                                c.drawString(margin, height-45, "DETAILED ANALYSIS (CONTINUED)")
                                
                                c.setFont("Helvetica", 10)
                                c.drawString(margin, height-65, f"HeartStream Analysis - Page {c.getPageNumber()}")
                                
                                current_y = height - 120
                                c.setFillColor('#0f467d')
                                
                                # Reset font after page break
                                if is_heading:
                                    c.setFont("Helvetica-Bold", 12)
                                else:
                                    c.setFont("Helvetica", 10)
                            
                            # Adjust character limit based on font size
                            if is_heading:
                                chars_per_line = int(text_width / 6.5)  # Larger font needs fewer chars
                            else:
                                chars_per_line = max_chars_per_line
                            
                            # Find the best break point for this line
                            if len(remaining_text) <= chars_per_line:
                                # Line fits, draw it exactly as is
                                c.drawString(margin, current_y, remaining_text)
                                current_y -= line_height
                                remaining_text = ""
                            else:
                                # Line too long, find break point
                                break_point = chars_per_line
                                
                                # Look for good break points (space, punctuation)
                                for i in range(chars_per_line, max(0, chars_per_line-30), -1):
                                    if i < len(remaining_text) and remaining_text[i] in ' .,;:!?-':
                                        break_point = i
                                        break
                                
                                # Draw the line segment exactly as is
                                line_segment = remaining_text[:break_point].strip()
                                if line_segment:
                                    c.drawString(margin, current_y, line_segment)
                                    current_y -= line_height
                                
                                # Continue with remaining text
                                remaining_text = remaining_text[break_point:].strip()
                
                # Add small space between paragraphs
                current_y -= line_height * 0.5
        
        # Footer for final page
        c.setFillColor('#0f467d')
        c.rect(0, 40, width, 30, fill=True)
        
        c.setFillColor('#ffffff')
        c.setFont("Helvetica", 9)
        c.drawString(margin, 55, "END OF REPORT - This analysis requires professional review.")
        c.drawString(margin, 45, f"Generated by HeartStream ECG Analysis System - Page {c.getPageNumber()}")
    
    return c

def show_analysis_page():
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
            margin-bottom: 3rem !important;
            animation: fadeIn 1s ease-out;
        }
        
        .upload-section {
            background: #a9c9f0 !important;
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            transition: transform 0.3s ease;
            text-align: center;
        }
        
        .upload-section:hover {
            transform: translateY(-5px);
            background: #7eaee7 !important;
        }
        
        .upload-section h3 {
            color: #0f467d !important;
            font-size: 1.8rem !important;
            margin-bottom: 1rem !important;
        }
        
        .results-card {
            background: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 6px 12px rgba(15, 70, 125, 0.15);
            border: 2px solid #a9c9f0;
            animation: slideIn 0.5s ease-out;
        }
        
        .confidence-bar {
            background: linear-gradient(90deg, #0f467d, #1976D2, #7eaee7);
            height: 10px;
            border-radius: 5px;
            margin: 1rem 0;
            position: relative;
            overflow: hidden;
        }
        
        .confidence-fill {
            background: linear-gradient(90deg, #0f467d, #1976D2);
            height: 100%;
            border-radius: 5px;
            transition: width 1s ease-out;
        }
        
        .metric-display {
            background: linear-gradient(135deg, #d4e4f8, #a9c9f0);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            text-align: center;
            border: 1px solid #7eaee7;
            min-height: 140px;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            box-sizing: border-box;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0f467d;
            margin: 0.5rem 0;
            line-height: 1.1;
        }
        
        .metric-label {
            font-size: 1.1rem;
            color: #1976D2;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .analysis-detailed {
            background: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 8px rgba(15, 70, 125, 0.1);
            border-left: 5px solid #1976D2;
        }
        
        .probability-bar {
            background: #7eaee7;
            border-radius: 10px;
            margin: 0.8rem 0;
            overflow: hidden;
            height: 45px;
            position: relative;
            border: 2px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .probability-fill {
            background: linear-gradient(90deg, #0f467d, #1976D2);
            height: 100%;
            border-radius: 8px;
            position: relative;
            transition: width 0.8s ease-out;
        }
        
        .probability-text {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-weight: 700;
            font-size: 1rem;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            z-index: 10;
        }
        
        .download-section {
            background: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
            text-align: center;
            border: 2px solid #d4e4f8;
        }
        
        .stButton > button {
            background-color: #f8f9fa !important;
            font-family: 'Helvetica Neue', Helvetica, sans-serif !important;
            font-style: normal !important;
            font-weight: 900 !important;
            font-size: 1.1rem !important;
            color: #1976D2 !important;
            border: none !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            white-space: nowrap !important;
            min-width: 80px !important;
            max-width: 150px !important;
        }
        
        .stButton > button:hover {
            background-color: #1976D2 !important;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="page-title">Smart ECG Analysis</h1>', unsafe_allow_html=True)
    
    # Upload section with improved styling
    st.markdown("""
        <div class="upload-section">
            <h3>📋 Upload Your ECG Report</h3>
            <p style="color: #0f467d; font-size: 1.1rem; margin-bottom: 1rem;">
                Upload a PDF containing ECG data for AI-powered analysis
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=['pdf'], key="pdf_uploader", 
                                   help="Upload a PDF file containing ECG data")
    
    if uploaded_file:
        try:
            with st.spinner("🔍 Analyzing ECG data..."):
                data = extract_data_from_pdf(uploaded_file)
                analysis_result = analyze_ecg_data(data)
                
                if not data['images']:
                    st.warning("No valid ECG images found in the PDF")
                    return
                
                st.success("✨ Successfully extracted and analyzed ECG")

                # Main results card
                if analysis_result is None:
                    analysis_result = {'prediction': 'Unknown', 'confidence': 0.0, 'details': {}}
                
                prediction = analysis_result.get('prediction', 'Unknown')
                confidence = analysis_result.get('confidence', 0.0)
                details = analysis_result.get('details', {})
                heart_rate = details.get('heart_rate', 'N/A') if details else 'N/A'
                report_id = details.get('report_id', 'N/A') if details else 'N/A'
                probabilities = details.get('probabilities', {}) if details else {}
                
                st.markdown("""
                    <div class="results-card">
                        <h2 style="color: #0f467d; text-align: center; margin-bottom: 2rem;">
                            🫀 ECG Analysis Results
                        </h2>
                """, unsafe_allow_html=True)

                # Main metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                        <div class="metric-display">
                            <div class="metric-label">Classification</div>
                            <div class="metric-value">{prediction}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-display">
                            <div class="metric-label">Confidence</div>
                            <div class="metric-value">{confidence:.1%}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="metric-display">
                            <div class="metric-label">Heart Rate</div>
                            <div class="metric-value">{heart_rate}</div>
                            <div style="font-size: 0.9rem; color: #666;">BPM</div>
                        </div>
                    """, unsafe_allow_html=True)

                # Confidence bar
                st.markdown(f"""
                    <div style="margin: 2rem 0;">
                        <h4 style="color: #1976D2; margin-bottom: 1rem;">Confidence Level</h4>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {confidence*100}%;"></div>
                        </div>
                        <div style="text-align: center; margin-top: 0.5rem; color: #666;">
                            {confidence:.1%} confident in {prediction} classification
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Probability breakdown
                st.markdown("""
                    <h4 style="color: #1976D2; margin-top: 2rem; margin-bottom: 1rem;">
                        Classification Probabilities
                    </h4>
                """, unsafe_allow_html=True)
                
                if probabilities and len(probabilities) > 0:
                    for class_name, prob in probabilities.items():
                        st.markdown(f"""
                            <div class="probability-bar">
                                <div class="probability-fill" style="width: {max(prob*100, 5)}%;"></div>
                                <div class="probability-text">{class_name}: {prob:.1%}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center;">
                            <p style="color: #666; margin: 0;">
                                Probability breakdown not available
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)  # Close results card

                # ECG Image section
                st.markdown("""
                    <div class="results-card">
                        <h3 style="color: #0f467d; text-align: center; margin-bottom: 1.5rem;">
                            📈 ECG Recording
                        </h3>
                """, unsafe_allow_html=True)
                
                # Display ECG image centered
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    st.image(data['images'][0], caption="Extracted ECG Signal", use_container_width=True)

                st.markdown("</div>", unsafe_allow_html=True)  # Close ECG card

                # Detailed Analysis Section
                st.markdown("""
                    <div class="analysis-detailed">
                        <h3 style="color: #0f467d; text-align: center; margin-bottom: 2rem;">
                            🤖 AI-Powered Detailed Analysis
                        </h3>
                """, unsafe_allow_html=True)
                
                with st.spinner("🤖 Generating detailed analysis..."):
                    ai_analysis = get_detailed_analysis(analysis_result)
                    detailed_report = ""
                    
                    # Ensure ai_analysis is a dict
                    if isinstance(ai_analysis, dict) and ai_analysis.get("success"):
                        # Get the raw content exactly as generated by AI
                        detailed_report = ai_analysis.get("content", "")
                        
                        # Display in web interface (minimal cleaning for display)
                        display_content = detailed_report.replace("**", "").replace("===", "").replace("=", "").replace("###", "").replace("##", "").replace("#", "")
                        st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #f8f9fa, #ffffff); 
                                      padding: 2rem; border-radius: 12px; border: 2px solid #d4e4f8;
                                      box-shadow: 0 4px 8px rgba(15, 70, 125, 0.1);'>
                                <div style='color: #0f467d; line-height: 1.6; font-size: 1.1rem;'>
                                    {display_content}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Use the same display content for PDF (no additional processing)
                        detailed_report = display_content
                        
                    else:
                        error_msg = ai_analysis.get("error", "Unknown error") if isinstance(ai_analysis, dict) else "Error generating analysis"
                        st.error(f"Error generating detailed analysis: {error_msg}")
                        st.markdown("""
                            <div style='background: #fff3cd; padding: 2rem; border-radius: 12px; 
                                      border: 2px solid #ffeaa7; margin: 2rem 0;'>
                                <p style='color: #856404; margin: 0;'>
                                    ⚠️ Unable to generate detailed analysis. The basic classification results above are still valid.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        detailed_report = "Basic analysis completed. Unable to generate detailed interpretation."
                
                st.markdown("</div>", unsafe_allow_html=True)  # Close analysis-detailed div
                
                # Generate PDF Report (always available)
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                create_pdf_report(c, data['images'][0], analysis_result, detailed_report)
                c.save()
                buffer.seek(0)
                
                # Download section - removed empty div
                st.download_button(
                    label="📥 Download Complete Analysis Report",
                    data=buffer,
                    file_name=f"ECG_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Interactive Chat Section (always available)
                st.markdown("""
                    <div class="results-card" style="padding: 1rem; margin: 1rem 0;">
                        <h4 style='color: #1976D2; text-align: center; margin-bottom: 1rem; font-size: 1.2rem;'>
                            💬 Ask Questions About Your Analysis
                        </h4>
                        """, unsafe_allow_html=True)
                        
                # Create a form for the chat to prevent page refresh
                with st.form(key='chat_form'):
                    user_question = st.text_input("Ask a question about your ECG analysis:",
                                                 placeholder="e.g., What does this classification mean?")
                    submit_button = st.form_submit_button("Get Answer")
                    
                    if submit_button and user_question:
                        question_prompt = f"""Based on the ECG analysis above, answer the following question:
                        {user_question}
                        
                        Provide a clear, medically accurate response based on the available ECG data and analysis."""
                        
                        with st.spinner("Generating response..."):
                            follow_up = generate_analysis(analysis_result, question_prompt)
                            # Ensure follow_up is a dict
                            if isinstance(follow_up, dict) and follow_up.get("success"):
                                st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #e3f2fd, #f8f9fa); 
                                      padding: 1.5rem; border-radius: 10px; margin-top: 1rem;
                                      border-left: 4px solid #1976D2;'>
                                <div style='color: #0f467d; line-height: 1.6;'>
                                        {follow_up.get("content", "")}
                                </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                error_msg = follow_up.get("error", "Unknown error") if isinstance(follow_up, dict) else "Error generating response"
                                st.error(f"Error generating response: {error_msg}")
                
                st.markdown("</div>", unsafe_allow_html=True)  # Close chat section

        except Exception as e:
            st.error(f"❌ Error analyzing PDF: {str(e)}")
