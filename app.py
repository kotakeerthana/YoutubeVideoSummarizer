import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import docx
from io import BytesIO
import time

# Setup 
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title="YouTube Gemini Summarizer", page_icon="", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville&display=swap');

body, .stApp {
    background-image: url("https://images.pexels.com/photos/1382073/pexels-photo-1382073.jpeg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Libre Baskerville', serif;
    color: #000 !important;
}
.block-container {
    background-color: rgba(255, 255, 255, 0.75);
    padding: 2rem 3rem;
    border-radius: 10px;
}
header[data-testid="stHeader"] {
    color: white !important;
}
header[data-testid="stHeader"] * {
    color: white !important;
    fill: white !important;
}
h1, h2, h3, h4 {
    text-align: center;
}
input[type="text"], textarea, .stTextInput input,
div[data-baseweb="select"] {
    background-color: #fffef2 !important;
    color: #000 !important;
    border: 1px solid #ccc !important;
    border-radius: 10px !important;
    padding: 10px !important;
}
label, .stSelectbox label, .stRadio label, .stTextInput label {
    color: #000 !important;
}
.stButton > button, .stDownloadButton > button {
    background-color: #fff8dc !important;
    color: #000 !important;
    border: 1px dashed #888 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
    font-size: 16px !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background-color: #f5deb3 !important;
    transform: scale(1.02);
}
details {
    background-color: #fffef2 !important;
    border: 1px dashed #a6a6a6 !important;
    border-radius: 10px;
    padding: 10px;
}
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #a6a6a6;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- Utilities ---
def get_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1]
    return ""

@st.cache_data(show_spinner=False)
def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript_list])
    except Exception as e:
        if "Subtitles are disabled" in str(e) or "Could not retrieve a transcript" in str(e):
            st.warning("Transcript not available for this video. Try another video with subtitles enabled.")
        else:
            st.error(f"Unexpected error while fetching transcript: {e}")
        return ""

def call_gemini(prompt: str, transcript: str) -> str:
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
        start = time.time()
        response = model.generate_content(prompt + transcript)
        st.caption(f"Generated in {time.time() - start:.2f} seconds")
        return response.text
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return ""

def create_pdf(text: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("Missing DejaVuSans.ttf in the project folder.")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "", 12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin1'))
    buffer.seek(0)
    return buffer

def create_word(text: str) -> BytesIO:
    doc = docx.Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

PROMPTS = {
    "tl_dr": "TL;DR this transcript:\n\n",
    "bullet_points": "Summarize this transcript into bullet points (max 250 words):\n\n",
    "detailed_summary": "Write a detailed summary of this transcript:\n\n",
    "key_takeaways": "List key takeaways from the transcript:\n\n",
    "translate": lambda lang: f"Translate this transcript into {lang}:\n\n",
    "keywords": "Extract 10 important keywords from this transcript:\n\n",
    "related_articles": (
        "Generate 2 fictional related article titles with 1–2 line summaries. For each, include a realistic URL.\n\n"
        "1. **[Title](https://example.com)**\nSummary: ..."
    ),
    "chat_base": "You are an expert answering questions based only on the transcript below:\n\n"
}

# App UI
st.title(" YouTube Video Summarizer with Gemini")

youtube_url = st.text_input(" Enter YouTube Video URL:")
if youtube_url:
    video_id = get_video_id(youtube_url)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

    if st.button(" Get Transcript"):
        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(video_id)
            if transcript:
                st.session_state.transcript = transcript
                st.success("Transcript Loaded")

if "transcript" in st.session_state:
    transcript = st.session_state.transcript
    MAX_CHARS = 10000
    if len(transcript) > MAX_CHARS:
        transcript = transcript[:MAX_CHARS]
        st.info("Transcript truncated for performance.")

    st.markdown("---")
    st.subheader(" Video Transcript")
    with st.expander(" Click to view full transcript"):
        st.write(transcript)

    tabs = st.tabs([" Generate Summary", " Ask Questions"])

    with tabs[0]:
        st.markdown(" Generate Summary")
        label_to_key = {
            "TL;DR": "tl_dr",
            "Bullet Points": "bullet_points",
            "Detailed Summary": "detailed_summary",
            "Key Takeaways": "key_takeaways",
            "Translate": "translate",
            "Keyword Extraction": "keywords",
            "Related Articles": "related_articles"
        }
        option = st.selectbox(" Select Summary Type", list(label_to_key.keys()))
        generate_clicked = st.button("Generate")
        prompt_key = label_to_key[option]

        if "summary_result" not in st.session_state:
            st.session_state.summary_result = ""

        if generate_clicked:
            if prompt_key == "translate":
                lang = st.selectbox("Choose Language", ["Hindi", "Spanish", "French", "Telugu", "German"])
                st.session_state.summary_result = call_gemini(PROMPTS["translate"](lang), transcript)
            else:
                st.session_state.summary_result = call_gemini(PROMPTS[prompt_key], transcript)

        if st.session_state.summary_result:
            st.success(" Summary Ready")
            st.markdown("Summary Output")
            st.markdown(st.session_state.summary_result)

            with st.expander(" Download your summary"):
                format = st.selectbox("Choose download format", ["TXT", "PDF", "Word (.docx)"])
                if format == "TXT":
                    st.download_button(" Download as .txt", st.session_state.summary_result,
                                       file_name="summary.txt", mime="text/plain")
                elif format == "PDF":
                    st.download_button(" Download as .pdf", create_pdf(st.session_state.summary_result),
                                       file_name="summary.pdf", mime="application/pdf")
                elif format == "Word (.docx)":
                    st.download_button(" Download as .docx", create_word(st.session_state.summary_result),
                                       file_name="summary.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with tabs[1]:
        st.markdown("Ask Questions About This Video")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        user_question = st.text_input("Type your question...")
        ask_clicked = st.button("Ask Gemini")
        if ask_clicked and user_question.strip():
            full_prompt = PROMPTS["chat_base"] + transcript + "\n\nQuestion: " + user_question
            answer = call_gemini(full_prompt, "")
            st.session_state.chat_history.append((user_question, answer))
        for q, a in reversed(st.session_state.chat_history):
            with st.chat_message("user"):
                st.markdown(f"**You:** {q}")
            with st.chat_message("assistant"):
                st.markdown(f"**Gemini:** {a}")
