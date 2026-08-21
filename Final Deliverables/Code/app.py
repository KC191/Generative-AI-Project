import os
import uuid
import base64
from io import BytesIO
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ReportLab Imports for PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="🌍 Landmark Explorer",
    page_icon="🗺️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ADAPTIVE CSS FOR MOBILE & DESKTOP ---
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding-bottom: 10px;
    }
    .main-title {
        font-weight: 700;
        margin-bottom: 5px;
    }
    .main-subtitle {
        opacity: 0.8;
    }

    [data-testid="stVerticalBlock"] > div:has(div.result-card) {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 10px;
    }

    @media (min-width: 768px) {
        .main-title { font-size: 2.5rem; }
        .main-subtitle { font-size: 1.1rem; }
    }

    @media (max-width: 767px) {
        .main-title { font-size: 1.7rem; }
        .main-subtitle { font-size: 0.9rem; }
        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- API KEY & SECRETS ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is missing! Please configure it in Streamlit Secrets or environment variables.")
    st.stop()

genai.configure(api_key=api_key)

# --- HELPER FUNCTIONS ---
def get_gemini_response(image_data, prompt, target_language):
    model = genai.GenerativeModel('gemini-3.6-flash')
    full_prompt = f"{prompt}\n\nIMPORTANT: Write your entire response in {target_language}. Format the response clearly using clean Markdown."
    response = model.generate_content([full_prompt, image_data[0]])
    return response.text

def process_and_compress_image(uploaded_file, max_size=(1024, 1024), quality=80):
    image = Image.open(uploaded_file)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=quality, optimize=True)
    compressed_bytes = buffered.getvalue()
    
    return image, compressed_bytes

def input_image_setup(compressed_bytes):
    return [{"mime_type": "image/jpeg", "data": compressed_bytes}]

def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_pdf(image_pil, description_text):
    """Generates a PDF document with the image and text description."""
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#2C3E50"))
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=11, leading=16, textColor=colors.HexColor("#333333"))

    story = []
    
    # PDF Title
    story.append(Paragraph("🗺️ Gemini Landmark Analysis", title_style))
    story.append(Spacer(1, 15))
    
    # Process & Scale Image for PDF
    img_buffer = BytesIO()
    image_pil.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    
    # Scale image maintaining aspect ratio
    img_w, img_h = image_pil.size
    aspect = img_h / float(img_w)
    pdf_img_w = 400
    pdf_img_h = 400 * aspect
    
    if pdf_img_h > 300:
        pdf_img_h = 300
        pdf_img_w = 300 / aspect

    story.append(RLImage(img_buffer, width=pdf_img_w, height=pdf_img_h))
    story.append(Spacer(1, 20))
    
    # Convert Description Text line-by-line into Paragraph elements
    for line in description_text.split('\n'):
        if line.strip():
            # Basic markdown cleanup for PDF compatibility
            clean_line = line.replace('***', '').replace('**', '<b>').replace('**', '</b>')
            clean_line = clean_line.replace('###', '').replace('##', '')
            story.append(Paragraph(clean_line, body_style))
            story.append(Spacer(1, 6))

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# --- STATE MANAGEMENT ---
if 'history' not in st.session_state:
    st.session_state.history = []

if 'result' not in st.session_state:
    st.session_state.result = None

# --- MAIN HEADER ---
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🗺️ Gemini Landmark Explorer</h1>
        <p class="main-subtitle">Upload a landmark photo to discover its history!</p>
    </div>
    """, unsafe_allow_html=True)

# --- CONTROLS SECTION ---
col1, col2 = st.columns(2)

with col1:
    selected_language = st.selectbox("🌐 Target Language", [
        "English", "Hindi", "Bengali", "Marathi", "Tamil", "Telugu", 
        "Gujarati", "Punjabi", "Kannada", "Malayalam", "Spanish", 
        "French", "German", "Chinese (Simplified)", "Japanese", 
        "Russian", "Arabic"
    ])

with col2:
    scenario = st.selectbox("🎯 Exploration Scenario", [
        "Discovering Iconic Landmarks (Traveler)",
        "Tour Guide Assistance",
        "Virtual Tours and Educational Resources",
        "Personal Exploration and Curiosity"
    ])

# --- SIDEBAR (HISTORY) ---
with st.sidebar:
    st.title("🧭 Explorer Panel")
    st.subheader("📜 Past Descriptions")
    if st.session_state.history:
        for i, past in enumerate(reversed(st.session_state.history[-5:]), 1):
            st.markdown(f"**{i}.** {past[:90]}...")
    else:
        st.write("No history yet.")

# --- SCENARIO PROMPTS ---
scenario_prompts = {
    "Discovering Iconic Landmarks (Traveler)": """
        You are a helpful travel assistant. Analyze the image of the landmark and describe:
        - The landmark’s name and location
        - Why it's famous and its historical or cultural context
        - Key visual/architectural features
        - Tips for travelers visiting this place
    """,
    "Tour Guide Assistance": """
        You're assisting a professional tour guide. Analyze the landmark image and provide:
        - Brief background and facts
        - Anecdotes or historical stories related to it
        - Architecture style and unique elements
        - Talking points to engage tourists
    """,
    "Virtual Tours and Educational Resources": """
        This is for an educational tour. Based on the image, provide:
        - Name and precise location
        - Historical, political, or cultural importance
        - Architectural overview
        - Learning points for students and young learners
    """,
    "Personal Exploration and Curiosity": """
        A history and architecture enthusiast wants to know more. From the image, explain:
        - The landmark's identity and origin
        - Historical timeline and transformation
        - Intriguing facts and architectural details
        - Local myths or cultural associations
    """
}

# --- UPLOAD SECTION ---
uploaded_file = st.file_uploader("📤 Upload a Landmark Photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    compressed_img, compressed_bytes = process_and_compress_image(uploaded_file)
    img_base64 = get_image_base64(compressed_img)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin: 15px 0;">
            <img src="data:image/jpeg;base64,{img_base64}" 
                 style="max-width: 100%; height: auto; max-height: 250px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);" />
        </div>
        """, unsafe_allow_html=True
    )

submit = st.button("🔍 Discover Landmark Info", use_container_width=True)

if submit:
    if not uploaded_file:
        st.warning("Please upload a photo first to analyze!")
    else:
        try:
            compressed_img, compressed_bytes = process_and_compress_image(uploaded_file)
            image_data = input_image_setup(compressed_bytes)
            prompt = scenario_prompts[scenario]
            
            with st.spinner(f"⚡ Analyzing landmark in {selected_language}..."):
                description = get_gemini_response(image_data, prompt, selected_language)

                st.session_state.result = description
                st.session_state.history.append(description)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# --- DISPLAY RESULTS & PDF DOWNLOAD ---
if st.session_state.result and uploaded_file:
    st.markdown("---")
    st.success("✅ Analysis Complete!")
    st.markdown("### 📖 Landmark Details")
    
    with st.container():
        st.markdown('<div class="result-card"></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.result)

    # Generate PDF with compressed image + description
    compressed_img, _ = process_and_compress_image(uploaded_file)
    pdf_bytes = create_pdf(compressed_img, st.session_state.result)

    filename = f"landmark_report_{uuid.uuid4().hex[:8]}.pdf"
    st.write("")
    st.download_button(
        label="📄 Download PDF Report (With Photo)",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True
    )
