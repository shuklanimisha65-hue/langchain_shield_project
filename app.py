import streamlit as st
import os
import requests
import base64
import cv2  
import tempfile  
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache

st.set_page_config(page_title="Deepfake Shield", page_icon="🎃")
st.title("🎃 Deepfake Shield Web Interface")

@st.cache_resource
def initialize_shield_engine():
    """Loads environment variables, initializes models, and sets up the standalone engine."""
    load_dotenv()
    set_llm_cache(InMemoryCache())
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    rag_prompt = ChatPromptTemplate.from_messages([
       ("system", (
           "You are a secure Deepfake Shield validation system.\n"
           "Analyze the user's enquiry based on your internal deepfake forensic knowledge.\n"
           "Provide a highly technical analysis covering risk rating and structural artifacts."
       )),
       ("human", "{user_question}")
    ])

    rag_chain = rag_prompt | llm | StrOutputParser()
    return rag_chain

# Only returning the execution chain now
rag_chain = initialize_shield_engine()

@st.cache_data(ttl=3600)
def check_global_news(keyword):
    """Hits NewsAPI to see if a claim has a historical digital footprint."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return []
    url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=relevance&pageSize=2&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("status") == "ok" and data.get("totalResults", 0) > 0:
            return data.get("articles")
        return []
    except Exception as e:
        st.error(f"Network error: {e}")
        return []
    
def process_image_to_base64(uploaded_file):
    """Encodes a single uploaded image file into a Base64 string."""
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

def extract_video_frames_to_base64(uploaded_file, num_frames=3):
    """Saves video bytes to a temp file, samples frames evenly, and returns Base64 strings."""
    base64_frames = []
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    video_capture = cv2.VideoCapture(temp_path)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames > 0:
        frame_indices = [int(total_frames * i / (num_frames + 1)) for i in range(1, num_frames + 1)]
        
        for idx in frame_indices:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, idx)
            success, frame = video_capture.read()
            if success:
                _, encoded_buffer = cv2.imencode('.jpg', frame)
                base64_str = base64.b64encode(encoded_buffer).decode('utf-8')
                base64_frames.append(base64_str)
                
    video_capture.release()
    os.unlink(temp_path) 
    return base64_frames


with st.sidebar:
    st.header("Global Media Registry")
    st.markdown("Your background news verification feeds will render here once analysis begins.")

st.markdown("###  Submit Evidence Dropzone")
st.write("Provide text, link, or upload an asset file. The system will auto-route outputs.")

user_text_or_url = st.text_input("Associated Text / URL Claim:", placeholder="Describe what happens in the video, or paste its source link...")
uploaded_file = st.file_uploader("Upload Media Asset (Image, Video frame, or MP4):", type=["png", "jpg", "jpeg", "mp4"])

st.write("---")
col1, col2 = st.columns(2)

with col1:
    run_news = st.button(" STEP 1: Scan Online News Wire", use_container_width=True)

with col2:
    run_rag = st.button(" STEP 2: Run Local AI Forensics (RAG)", use_container_width=True)


if run_news:
    text_query = ""
    if user_text_or_url:
        if user_text_or_url.startswith("http://") or user_text_or_url.startswith("https://"):
            text_query = user_text_or_url.split("/")[-1].replace("-", " ").replace("_", " ")
        else:
            text_query = user_text_or_url
    elif uploaded_file:
        text_query = uploaded_file.name.split(".")[0].replace("-", " ").replace("_", " ")

    if not text_query:
        st.warning("Input Required: Provide a text claim or upload a file first.")
    else:
        with st.sidebar:
            st.write("---")
            st.subheader("🔍 Active Archive Scan...")
            st.info(f"Searching news databases for: `{text_query}`")
            
            news_articles = check_global_news(text_query)
            if news_articles:
                st.success(f" MATCH FOUND! ({len(news_articles)} Sources)")
                for article in news_articles:
                    with st.expander(f" {article.get('source', {}).get('name', 'News Wire')}"):
                        st.markdown(f"**[{article.get('title')}]({article.get('url')})**")
                        st.write(article.get("description"))
            else:
                st.info("CLEAR REGISTRY: No matching records found in global news archives.")


if run_rag:
    st.subheader("Deepfake Shield Prediction Report")
    
    system_instruction = (
        "You are an expert AI Forensic Investigator specializing in synthetic media detection.\n"
        "Analyze the user's inquiry or visual asset to evaluate its likelihood of being a deepfake.\n\n"
        "Provide a comprehensive, highly technical analysis covering:\n"
        "1. RISK RATING: Assess likelihood of manipulation (Low, Medium, High).\n"
        "2. STRUCTURAL ARTIFACTS: Point out spatial, lighting, texture, or border inconsistencies natively inside the file.\n"
        "3. LOGICAL CONSISTENCY: Evaluate the context described.\n"
        "4. VERIFICATION VERDICT: Provide actionable next steps for verification."
    )

    if uploaded_file:
        with st.spinner("Processing media file layouts..."):
            try:
                vision_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.1)
                
                content_payload = [
                    {"type": "text", "text": f"{system_instruction}\n\nUser Context/Claim: {user_text_or_url if user_text_or_url else 'No text provided.'}"}
                ]
                
                if uploaded_file.name.lower().endswith(".mp4"):
                    st.info("🎥 Video file detected. Extracting key temporal frames...")
                    frames = extract_video_frames_to_base64(uploaded_file, num_frames=3)
                    
                    for frame_b64 in frames:
                        content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}})
                else:
                    st.info("👁️ Static image detected. Analyzing raw pixel patches...")
                    base64_image = process_image_to_base64(uploaded_file)
                    content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
                
                multimodal_message = HumanMessage(content=content_payload)
                st.write_stream(vision_llm.stream([multimodal_message]))
                
            except Exception as e:
                st.error(f"Multimodal Analysis Failed: {e}")

    elif user_text_or_url:
        st.info("✍️ Initiating Pure Text Conceptual Forensics...")
        with st.spinner("Executing deep-learning heuristic prediction rules..."):
            st.write_stream(rag_chain.stream({
                "user_question": user_text_or_url
            }))
            
    else:
        st.warning(" Input Required: Drop an image/video asset or type a textual claim first.")