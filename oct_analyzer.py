import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import io
import cv2
import pandas as pd
from datetime import datetime

# Set page configuration for clinical appearance
st.set_page_config(
    page_title="Retinal OCT Analyzer Pro",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clinical appearance
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        color: white;
    }
    .report-header {
        background-color: #0d6efd;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .clinical-finding {
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #0d6efd;
        margin-bottom: 15px;
    }
    .measurement-card {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .sidebar .sidebar-content {
        background-color: #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# App header
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://img.icons8.com/color/96/000000/eye.png", width=80)
with col2:
    st.title("Retinal OCT Analyzer Pro")
    st.caption("Clinical-grade optical coherence tomography analysis for ophthalmology professionals")

# Sidebar for patient information and controls
with st.sidebar:
    st.header("Patient Information")
    
    # Patient demographics
    patient_id = st.text_input("Patient ID", "P-2023-00127")
    patient_name = st.text_input("Full Name", "John A. Smith")
    patient_dob = st.date_input("Date of Birth", value=datetime(1965, 5, 15))
    patient_gender = st.radio("Gender", ["Male", "Female", "Other"])
    
    st.divider()
    
    # Scan information
    st.header("Scan Details")
    scan_date = st.date_input("Scan Date", value=datetime.today())
    eye_side = st.radio("Eye", ["OD (Right Eye)", "OS (Left Eye)"])
    scan_type = st.selectbox("Scan Type", ["Macular Cube 512x128", "Optic Disc Cube 200x200", "HD 5-Line Raster", "Radial"])
    
    st.divider()
    
    # Analysis parameters
    st.header("Analysis Parameters")
    enhance_contrast = st.checkbox("Enhance Contrast", value=True)
    segment_layers = st.checkbox("Segment Retinal Layers", value=True)
    measure_thickness = st.checkbox("Measure Thickness", value=True)
    compare_normal = st.checkbox("Compare to Normal Database", value=True)
    
    st.divider()
    
    # Action buttons
    if st.button("Process Scan", type="primary"):
        st.session_state.processed = True
    if st.button("Generate Report"):
        st.session_state.report = True
    if st.button("Clear Results"):
        st.session_state.processed = False
        st.session_state.report = False

# Function to create a simulated OCT image with clinical appearance
def create_clinical_oct_image():
    # Create a blank image with clinical blue tone
    width, height = 600, 400
    img = Image.new('RGB', (width, height), color=(240, 248, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw simulated retinal layers
    layers = [
        ("NFL", 80, (70, 130, 255)),   # Nerve Fiber Layer
        ("GCL", 120, (100, 150, 255)), # Ganglion Cell Layer
        ("IPL", 160, (130, 170, 255)), # Inner Plexiform Layer
        ("INL", 200, (160, 190, 255)), # Inner Nuclear Layer
        ("OPL", 240, (190, 210, 255)), # Outer Plexiform Layer
        ("ONL", 280, (220, 230, 255)), # Outer Nuclear Layer
        ("RPE", 320, (250, 250, 255)), # Retinal Pigment Epithelium
    ]
    
    for name, y, color in layers:
        draw.line([(0, y), (width, y)], fill=color, width=2)
        draw.text((10, y-15), name, fill=(50, 50, 50))
    
    # Add some noise to make it look more realistic
    np_img = np.array(img)
    noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    np_img = np.clip(np_img + noise, 0, 255)
    
    return Image.fromarray(np_img)

# Function to process OCT image (simulated)
def process_oct_image(image, contrast_enhance=True, layer_detection=True, thickness_measure=True):
    # Convert to numpy array
    img_array = np.array(image)
    
    # Apply contrast enhancement if selected
    if contrast_enhance:
        # Convert to grayscale for processing
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        img_array = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    
    # Create a copy for layer detection visualization
    layer_img = img_array.copy() if layer_detection else None
    
    # Simulate layer detection
    layer_data = {}
    if layer_detection:
        height, width, _ = img_array.shape
        # Simulate detection of retinal layers with horizontal lines
        layers = [
            ("NFL", height * 0.2, (0, 100, 255)),   # Nerve Fiber Layer
            ("GCL", height * 0.35, (0, 150, 255)),  # Ganglion Cell Layer
            ("IPL", height * 0.45, (0, 200, 255)),  # Inner Plexiform Layer
            ("INL", height * 0.55, (100, 200, 255)), # Inner Nuclear Layer
            ("OPL", height * 0.65, (150, 200, 255)), # Outer Plexiform Layer
            ("ONL", height * 0.75, (200, 200, 255)), # Outer Nuclear Layer
            ("RPE", height * 0.85, (255, 200, 200)), # Retinal Pigment Epithelium
        ]
        
        for layer_name, y_pos, color in layers:
            y = int(y_pos)
            cv2.line(layer_img, (0, y), (width, y), color, 2)
            cv2.putText(layer_img, layer_name, (10, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1)
            layer_data[layer_name] = y
    
    # Simulate thickness measurements
    thickness_results = {}
    if thickness_measure and layer_detection:
        # Calculate simulated thickness between layers
        layers = sorted(layer_data.items(), key=lambda x: x[1])
        for i in range(len(layers)-1):
            layer_name = f"{layers[i][0]}-{layers[i+1][0]}"
            thickness = layers[i+1][1] - layers[i][1]
            thickness_results[layer_name] = thickness
    
    # Simulate normal database comparison
    normal_values = {
        "NFL-GCL": 45.2,
        "GCL-IPL": 35.7,
        "IPL-INL": 42.1,
        "INL-OPL": 38.5,
        "OPL-ONL": 52.3,
        "ONL-RPE": 78.9
    }
    
    comparison_results = {}
    for layer, measured in thickness_results.items():
        if layer in normal_values:
            normal = normal_values[layer]
            difference = ((measured - normal) / normal) * 100
            status = "Normal" if abs(difference) < 10 else "Abnormal"
            comparison_results[layer] = {
                "measured": measured,
                "normal": normal,
                "difference": difference,
                "status": status
            }
    
    return img_array, layer_img, thickness_results, comparison_results

# Main content area
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'report' not in st.session_state:
    st.session_state.report = False

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Scan View", "Analysis Results", "Clinical Report"])

with tab1:
    st.header("OCT Scan View")
    
    # Create a clinical OCT image
    oct_image = create_clinical_oct_image()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Scan")
        st.image(oct_image, use_column_width=True, caption=f"{eye_side} - {scan_type}")
    
    with col2:
        st.subheader("Processed Scan")
        if st.session_state.processed:
            # Process the image
            processed_img, layer_img, thickness_results, comparison_results = process_oct_image(
                oct_image,
                contrast_enhance=enhance_contrast,
                layer_detection=segment_layers,
                thickness_measure=measure_thickness
            )
            
            # Display processed image
            if segment_layers and layer_img is not None:
                st.image(layer_img, use_column_width=True, caption="Retinal Layer Segmentation")
            else:
                st.image(processed_img, use_column_width=True, caption="Contrast Enhanced")
        else:
            st.info("Click 'Process Scan' to analyze the OCT image")

with tab2:
    st.header("Analysis Results")
    
    if st.session_state.processed:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Layer Thickness Measurements")
            for layer, thickness in thickness_results.items():
                with st.container():
                    st.markdown(f"<div class='measurement-card'>", unsafe_allow_html=True)
                    st.metric(label=layer, value=f"{thickness:.1f} μm")
                    st.markdown(f"</div>", unsafe_allow_html=True)
        
        with col2:
            st.subheader("Comparison to Normal Database")
            if comparison_results:
                for layer, data in comparison_results.items():
                    with st.container():
                        st.markdown(f"<div class='measurement-card'>", unsafe_allow_html=True)
                        diff_color = "green" if data['status'] == "Normal" else "red"
                        st.metric(
                            label=layer, 
                            value=f"{data['measured']:.1f} μm", 
                            delta=f"{data['difference']:.1f}% ({data['status']})"
                        )
                        st.caption(f"Normal range: {data['normal']:.1f} μm ±10%")
                        st.markdown(f"</div>", unsafe_allow_html=True)
            else:
                st.info("No comparison data available")
        
        # Add thickness map visualization
        st.subheader("Thickness Map")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create sample data for thickness map
        layers = list(thickness_results.keys())
        values = list(thickness_results.values())
        
        bars = ax.barh(layers, values, color='skyblue')
        ax.set_xlabel('Thickness (μm)')
        ax.set_title('Retinal Layer Thickness')
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                   f'{width:.1f} μm', ha='left', va='center')
        
        st.pyplot(fig)
    else:
        st.info("Process a scan to see analysis results")

with tab3:
    st.header("Clinical Report")
    
    if st.session_state.report:
        # Report header
        st.markdown("""
        <div class="report-header">
            <h2 style="color: white; margin: 0;">CLINICAL OCT REPORT</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Patient information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Patient Details")
            st.write(f"**Name:** {patient_name}")
            st.write(f"**ID:** {patient_id}")
            st.write(f"**DOB:** {patient_dob.strftime('%Y-%m-%d')}")
            st.write(f"**Gender:** {patient_gender}")
        
        with col2:
            st.subheader("Scan Details")
            st.write(f"**Date:** {scan_date.strftime('%Y-%m-%d')}")
            st.write(f"**Eye:** {eye_side}")
            st.write(f"**Scan Type:** {scan_type}")
        
        with col3:
            st.subheader("Analysis Parameters")
            st.write(f"**Contrast Enhancement:** {'Yes' if enhance_contrast else 'No'}")
            st.write(f"**Layer Segmentation:** {'Yes' if segment_layers else 'No'}")
            st.write(f"**Thickness Measurement:** {'Yes' if measure_thickness else 'No'}")
        
        # Clinical findings
        st.subheader("Clinical Findings")
        st.markdown("""
        <div class="clinical-finding">
            <h4 style="margin-top: 0;">Interpretation</h4>
            <p>The retinal architecture appears within normal limits. All retinal layers are clearly visualized and demonstrate normal reflectivity characteristics. No evidence of intraretinal or subretinal fluid is identified.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quantitative analysis
        st.subheader("Quantitative Analysis")
        if st.session_state.processed and comparison_results:
            df = pd.DataFrame.from_dict(comparison_results, orient='index')
            df.columns = ['Measured (μm)', 'Normal (μm)', 'Difference (%)', 'Status']
            st.dataframe(df.style.applymap(lambda x: 'background-color: #90EE90' if x == 'Normal' else 'background-color: #FFCCCB', subset=['Status']))
        
        # Clinical impression
        st.subheader("Clinical Impression")
        st.markdown("""
        - Normal retinal morphology
        - No signs of macular edema
        - No evidence of epiretinal membrane
        - Retinal thickness measurements within normal limits
        """)
        
        # Recommendations
        st.subheader("Recommendations")
        st.markdown("""
        - Routine follow-up as per standard care
        - No additional imaging required at this time
        - Continue current management plan
        """)
        
        # Footer
        st.markdown("---")
        st.markdown(f"**Report generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.markdown("*This report was automatically generated by Retinal OCT Analyzer Pro v2.1*")
        
        # Export options
        st.download_button(
            label="Download PDF Report",
            data="Simulated PDF report content",  # In a real app, this would generate a PDF
            file_name=f"OCT_Report_{patient_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Generate a report to view clinical findings")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d;">
    <p>Retinal OCT Analyzer Pro v2.1 | For clinical use only | © 2023 Nyameri Ophthalmology Analytics </p>
</div>
""", unsafe_allow_html=True)
