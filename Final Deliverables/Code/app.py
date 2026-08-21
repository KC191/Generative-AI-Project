import os
import uuid
import base64
from io import BytesIO
import streamlit as st
import google.generativeai as genai
from PIL import Image
from deep_translator import GoogleTranslator

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="🌍 Landmark Explorer", page_icon="🗺️", layout="centered")

# --- API KEY & SECRETS CONFIGURATION ---
# Checks Streamlit Cloud Secrets first, then falls back to system environment variables
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is missing! Please configure it in Streamlit Secrets or environment variables.")
    st.stop()

genai.configure(api_key=api_key)

# --- HELPER FUNCTIONS ---
def get_gemini_response(image, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash-001')
    response = model.generate_content([prompt, image[0]])
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    raise FileNotFoundError("No file uploaded")

def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    return GoogleTranslator(source='auto', target=target_lang).translate(text)

def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- STATE MANAGEMENT ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR ---
st.sidebar.title("🧭 Explorer Panel")

selected_language = st.sidebar.selectbox("🌐 Language", {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Marathi": "mr",
    "Tamil": "ta", "Telugu": "te", "Gujarati": "gu", "Punjabi": "pa",
    "Kannada": "kn", "Malayalam": "ml", "Spanish": "es", "French": "fr",
    "German": "de", "Chinese (Simplified)": "zh-cn", "Japanese": "ja",
    "Russian": "ru", "Arabic": "ar"
})

st.sidebar.markdown("---")
scenario = st.sidebar.selectbox("🎯 Scenario", [
    "Discovering Iconic Landmarks (Traveler)",
    "Tour Guide Assistance",
    "Virtual Tours and Educational Resources",
    "Personal Exploration and Curiosity"
])

st.sidebar.markdown("---")
st.sidebar.subheader("📜 Past Descriptions")
if st.session_state.history:
    for i, past in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.sidebar.markdown(f"**{i}.** {past[:100]}...")
else:
    st.sidebar.write("No history yet.")

# --- MAIN CONTENT ---
st.markdown("""
    <div style="text-align:center">
        <h1 style="color:#2c3e50;">🗺️ Gemini Landmark Explorer</h1>
        <p style="font-size:18px;">Upload a photo of a landmark, and let AI tell its story!</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

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

# Upload Section
uploaded_file = st.file_uploader("📤 Upload a Landmark Photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_base64 = get_image_base64(image)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <img src="data:image/png;base64,{img_base64}" 
                 style="max-height: 300px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);" />
        </div>
        """, unsafe_allow_html=True
    )

    if st.button("🔍 Discover Landmark Info"):
        try:
            image_data = input_image_setup(uploaded_file)
            prompt = scenario_prompts[scenario]
            with st.spinner(f"🔎 Analyzing landmark using scenario: {scenario}"):
                description = get_gemini_response(image_data, prompt)
                translated = translate_text(description, selected_language)

                st.success("✅ Description Ready!")
                st.markdown("### 📖 Landmark Information")
                st.markdown(f"<div style='max-width:700px; margin:auto; font-size:17px;'>{translated}</div>", unsafe_allow_html=True)

                st.session_state.history.append(translated)

                filename = f"landmark_description_{uuid.uuid4().hex[:8]}.txt"
                st.download_button(
                    label="📥 Download Description",
                    data=translated,
                    file_name=filename,
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
else:
    st.info("Please upload an image to get started.")
