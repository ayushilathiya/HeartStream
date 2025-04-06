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
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

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
        
        # Skip header images based on position
        if position and position.get('y0', 0) < 400:
            return False
            
        # Check aspect ratio
        aspect_ratio = width / height
        if not (1.0 < aspect_ratio < 3.0):
            return False
            
        # Convert to grayscale if color
        if len(img_array.shape) == 3:
            img_array = np.mean(img_array, axis=2)
        
        # Look for ECG peak patterns
        row_means = np.mean(img_array, axis=0)
        peak_count = len(np.where(np.diff(np.signbit(np.diff(row_means))))[0])
        
        return peak_count > 50  # ECG should have multiple peaks
            
    except Exception as e:
        st.write(f"Error in ECG detection: {str(e)}")
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
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_info = page.get_image_info()[img_index]
                    position = {
                        'x0': image_info['bbox'][0],
                        'y0': image_info['bbox'][1],
                        'x1': image_info['bbox'][2],
                        'y1': image_info['bbox'][3]
                    }
                    
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    gray_image = image.convert('L')
                    
                    if (image.size[0] > 400 and  # Minimum width
                        image.size[1] > 200 and  # Minimum height
                        is_likely_ecg_plot(gray_image, position)):
                        data['images'].append(image)
                        break  # Take only the first matching ECG plot
                    
                except Exception as img_error:
                    continue
        
        doc.close()
        
        if not data['images']:
            st.warning(f"No ECG plots found in the PDF")
        
        return data
            
    except Exception as e:
        raise Exception(f"Error extracting PDF data: {str(e)}")

def analyze_ecg_data(data):
    """Analyze the extracted ECG data using the trained ECGNet model"""
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
            
            # Convert to grayscale and resize to match model input
            img_gray = ecg_image.convert('L')
            img_resized = img_gray.resize((250, 1))  # 250 samples as per model input
            
            # Preprocess similar to training
            img_array = np.array(img_resized).astype(np.float32)
            mean = np.mean(img_array)
            std = np.std(img_array) if np.std(img_array) != 0 else 1
            img_normalized = (img_array - mean) / std
            
            # Prepare tensor
            tensor = torch.FloatTensor(img_normalized).reshape(1, 1, -1)
            tensor = tensor.to(device)
            
            # Get prediction
            with torch.no_grad():
                outputs = model(tensor)
                probabilities = torch.softmax(outputs, dim=1)
                prediction = torch.argmax(outputs, dim=1).item()
                confidence = probabilities[0][prediction].item()
            
            result = {
                'prediction': CLASS_NAMES[prediction],
                'confidence': confidence,
                'details': {
                    'heart_rate': data['metadata'].get('heart_rate', 'N/A'),
                    'report_id': data['metadata'].get('report_id', 'N/A'),
                    'probabilities': {
                        name: float(prob) 
                        for name, prob in zip(CLASS_NAMES, probabilities[0].tolist())
                    }
                }
            }
            
            return result
            
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
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
    plt.figure(figsize=(10, 4))
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()
    img_buf.seek(0)
    return img_buf

def create_pdf_report(c, image, analysis_result, detailed_report):
    """Create a professional PDF report with matching live_data.py style"""
    width, height = letter
    c.setPageSize((width, height))
    margin = 50

    def draw_page_template(canvas, title=""):
        # Header with lighter theme color - reduced height
        canvas.setFillColor('#7eaee7')
        canvas.rect(0, height-80, width, 80, fill=True)  # Reduced from 100 to 80
        
        # White text for header - adjusted positions
        canvas.setFillColor('white')
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(margin, height-45, title or "ECG Analysis Report")  # Adjusted from -60
        
        # Add timestamp in header
        canvas.setFont("Helvetica", 12)
        canvas.drawString(margin, height-65, 
                        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Footer with gradient line
        canvas.setStrokeColorRGB(0.1, 0.46, 0.82)
        canvas.setLineWidth(2)
        canvas.line(margin, 50, width-margin, 50)
        
        # Footer text
        canvas.setFillColor('#666666')
        canvas.setFont("Helvetica", 8)
        canvas.drawString(margin, 30, "HeartStream - Advanced ECG Analysis System")
        canvas.drawString(margin, 20, 
                         "This report is generated automatically and should be reviewed by a healthcare professional.")
        
        # Page number
        canvas.drawString(width-margin-40, 30, f"Page {canvas.getPageNumber()}")

    # First Page - adjust starting position
    draw_page_template(c)
    y = height - 120  # Reduced from 140

    # Analysis Results Section with table
    c.setFillColor('#1976D2')
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Analysis Results")
    y -= 30

    # Results table with improved styling
    data = [
        ["Classification:", analysis_result['prediction']],
        ["Confidence:", f"{analysis_result['confidence']:.2%}"],
        ["Heart Rate:", f"{analysis_result['details']['heart_rate']} BPM"],
        ["Report ID:", str(analysis_result['details']['report_id'])]
    ]
    
    table = Table(data, colWidths=[1.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), '#1976D2'),
        ('TEXTCOLOR', (1, 0), (1, -1), '#666666'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, margin, y - table._height)
    y -= table._height + 40

    # ECG Plot
    c.setFillColor('#1976D2')
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "ECG Recording")
    y -= 30

    try:
        img_buf = plot_to_matplotlib(image)
        img = ImageReader(img_buf)
        img_width = width - 2*margin
        img_height = 200
        c.drawImage(img, margin, y - img_height, width=img_width, height=img_height)
        y -= img_height + 40
    except Exception as e:
        c.drawString(margin, y, "Error rendering ECG plot")
        y -= 40

    # Start new page for detailed analysis
    c.showPage()
    draw_page_template(c, "Detailed Medical Analysis")
    y = height - 120  # Start below header

    # Process and format detailed report with proper spacing
    c.setFillColor('#666666')
    c.setFont("Helvetica", 12)
    text_object = c.beginText(margin, y)
    
    # Clean up and format text
    sections = detailed_report.replace("**", "").replace("#", "").replace("===", "").split('\n\n')
    
    line_height = 14  # Approximate height per line
    available_height = y - margin - 60  # Available space on page
    current_height = 0
    
    for section in sections:
        if section.strip():
            lines = section.strip().split('\n')
            section_height = len(lines) * line_height + line_height  # Add extra space between sections
            
            # Check if section will fit on current page
            if current_height + section_height > available_height:
                # Draw current text and start new page
                c.drawText(text_object)
                c.showPage()
                draw_page_template(c, "Detailed Medical Analysis (continued)")
                
                # Reset text object and counters
                text_object = c.beginText(margin, height - 120)
                current_height = 0
            
            # Add section content
            for line in lines:
                if line.strip():
                    if line.startswith('*'):
                        text_object.textLine('  • ' + line[1:].strip())
                    else:
                        text_object.textLine(line.strip())
                current_height += line_height
            
            # Add space between sections
            text_object.textLine('')
            current_height += line_height
    
    # Draw remaining text
    c.drawText(text_object)
    
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
            margin-bottom: 2rem !important;
        }
        .analysis-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(15, 70, 125, 0.1);
        }
        div[data-testid="stVerticalBlock"] > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        .element-container {
            margin: 0 !important;
            padding: 0 !important;
        }
        .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        .analysis-header {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px 10px 0 0;  /* Rounded corners only at top */
            margin: 0 !important;
            border-bottom: none;
        }
        .analysis-content {
            background: white;
            padding: 1.5rem;
            border-radius: 0 0 10px 10px;  /* Rounded corners only at bottom */
            margin: 0 !important;
            border: 1px solid #e0e0e0;
            margin-bottom: 1.5rem !important;  /* Space between sections */
        }
        .analysis-section {
            margin-bottom: 1.5rem !important;  /* Consistent spacing between sections */
        }
        .download-button {
            margin-top: 2rem !important;
            margin-bottom: 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="page-title">Smart ECG Analysis</h1>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload ECG Report (PDF)", type=['pdf'], key="pdf_uploader")
    
    if uploaded_file:
        try:
            with st.spinner("📊 Analyzing ECG..."):
                data = extract_data_from_pdf(uploaded_file)
                analysis_result = analyze_ecg_data(data)
                
                if not data['images']:
                    st.warning("No valid ECG images found in the PDF")
                    return
                
                st.success("✨ Successfully extracted ECG")

                st.markdown("""
                    <div class="analysis-section">
                        <div class='analysis-header'>
                            <h3>ECG Analysis Results</h3>
                        </div>
                        <div class='analysis-content'>
                """, unsafe_allow_html=True)

                # Horizontal analysis bar
                st.markdown("""
                    <div style='background: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                             display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                        <div style='flex: 1; min-width: 200px; padding: 0.5rem;'>
                            <h4 style='color: #1976D2; margin: 0;'>Classification</h4>
                            <div style='font-size: 1.2rem; font-weight: 600;'>{}</div>
                            <div style='color: #666666;'>Confidence: {:.2%}</div>
                        </div>
                        <div style='flex: 1; min-width: 200px; padding: 0.5rem;'>
                            <h4 style='color: #1976D2; margin: 0;'>Heart Rate</h4>
                            <div style='font-size: 1.2rem;'>{} BPM</div>
                            <div style='color: #666666;'>Report ID: {}</div>
                        </div>
                    </div>
                """.format(
                    analysis_result['prediction'],
                    analysis_result['confidence'],
                    analysis_result['details']['heart_rate'],
                    analysis_result['details']['report_id']
                ), unsafe_allow_html=True)

                # ECG Image with smaller size
                _, col2, _ = st.columns([1, 2, 1])
                with col2:
                    st.image(data['images'][0], width=500)

                st.markdown("</div></div>", unsafe_allow_html=True)  # Close both divs

                # Add proper spacing before detailed analysis
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

                st.markdown("""
                    <div class="analysis-section">
                        <div class='analysis-header'>
                            <h3>Detailed Medical Analysis</h3>
                        </div>
                        <div class='analysis-content'>
                """, unsafe_allow_html=True)
                
                with st.spinner("🤖 Generating detailed medical analysis..."):
                    ai_analysis = get_detailed_analysis(analysis_result)
                    
                    if ai_analysis.get("success"):
                        # Remove markdown formatting from content
                        detailed_report = ai_analysis["content"].replace("**", "").replace("===", "").replace("=", "")
                        st.markdown(f"""
                            <div style='background: white; padding: 2rem; border-radius: 10px; 
                                      border: 1px solid #e0e0e0;'>
                                {detailed_report}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Generate PDF Report
                        buffer = io.BytesIO()
                        c = canvas.Canvas(buffer, pagesize=(792, 1224))
                        create_pdf_report(c, data['images'][0], analysis_result, detailed_report)
                        c.save()
                        buffer.seek(0)
                        
                        # Add proper spacing before download button
                        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

                        # Download button with proper spacing
                        st.markdown("<div class='download-button'>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥 Download Complete Analysis",
                            data=buffer,
                            file_name=f"ECG_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

                        # Interactive Chat Section
                        st.markdown("""
                            <div style='margin-top: 2rem;'>
                                <h4 style='color: #1976D2;'>Ask Questions About Your Analysis</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Create a form for the chat to prevent page refresh
                        with st.form(key='chat_form'):
                            user_question = st.text_input("Ask a question about your ECG analysis:")
                            submit_button = st.form_submit_button("Get Answer")
                            
                            if submit_button and user_question:
                                question_prompt = f"""Based on the ECG analysis above, answer the following question:
                                {user_question}
                                
                                Provide a clear, medically accurate response based on the available ECG data and analysis."""
                                
                                with st.spinner("Generating response..."):
                                    follow_up = generate_analysis(analysis_result, question_prompt)
                                    if follow_up.get("success"):
                                        st.markdown(f"""
                                            <div style='background: #f8f9fa; padding: 1rem; border-radius: 10px;'>
                                                {follow_up["content"]}
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.error(f"Error generating response: {follow_up.get('error')}")

        except Exception as e:
            st.error(f"❌ Error analyzing PDF: {str(e)}")
            st.code(traceback.format_exc())
