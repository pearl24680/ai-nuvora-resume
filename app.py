import os
import base64
from pathlib import Path
import fitz
import streamlit as st
import plotly.express as px
import re
from dotenv import load_dotenv
from analyzer import process_image

# -------------------- Load Gemini API --------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("AIzaSyDT9MzjRdQqud1QcekSsQPRbmFhphAppVA")
if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    AI_ENABLED = True
else:
    AI_ENABLED = False

# -------------------- Streamlit Config --------------------
st.set_page_config(page_title="Nuvora AI Job Assistant", layout="wide")

# -------------------- Helper Functions --------------------
def pdf_to_jpg(pdf_path, output_folder="pdf_images", dpi=300):
    file_paths = []
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    pdf_document = fitz.open(pdf_path)
    for i, page in enumerate(pdf_document):
        pix = page.get_pixmap(dpi=dpi)
        out_file = output_folder / f"page_{i+1}.jpg"
        pix.save(str(out_file))
        file_paths.append(str(out_file))
    pdf_document.close()
    return file_paths

def extract_projects(text):
    pattern = r"(?i)(projects?|internships?|experience)\s*[:\-]?\s*(.+)"
    matches = re.findall(pattern, text)
    return list(set([m[1].strip() for m in matches]))

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def show_dashboard(overall_score, matched, missing, suggestions=None):
    col1, col2, col3 = st.columns([1,2,2])
    with col1:
        st.markdown('<div class="card" style="text-align:center;"><h3>Overall Score</h3></div>', unsafe_allow_html=True)
        fig = px.bar(
            x=[overall_score], y=["Resume Match"],
            orientation="h", text=[f"{overall_score}%"],
            color_discrete_sequence=["#2ECC71" if overall_score>=80 else "#F39C12" if overall_score>=60 else "#E74C3C"]
        )
        fig.update_traces(textposition="inside")
        fig.update_layout(xaxis=dict(range=[0,100]), height=150, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<div class="card"><h4>✅ Matched Skills</h4></div>', unsafe_allow_html=True)
        for skill in matched: st.markdown(f'<span class="skill-badge">{skill}</span>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h4>⚠️ Missing Skills</h4></div>', unsafe_allow_html=True)
        for skill in missing: st.markdown(f'<span class="missing-badge">{skill}</span>', unsafe_allow_html=True)
    if suggestions:
        st.markdown('<div class="card"><h4>💡 Suggestions</h4></div>', unsafe_allow_html=True)
        for s in suggestions: st.markdown(f'<span class="suggestion-badge">{s}</span>', unsafe_allow_html=True)

# -------------------- Sidebar --------------------
st.sidebar.title("📘 Nuvora AI Job Assistant")
page = st.sidebar.radio("Navigate", ["🏠 Home", "💼 Project Extractor", "🤖 Career Chatbot"])

# -------------------- HOME PAGE --------------------
if page=="🏠 Home":
    st.header("📊 AI Career Dashboard")
    if not AI_ENABLED:
        st.warning("⚠️ AI features are disabled. Set GEMINI_API_KEY in your .env to enable resume analysis.")
    st.subheader("📋 Job Description")
    job_description = st.text_area("Paste the job description here", height=200)
    st.subheader("📄 Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf"])
    if uploaded_file and job_description.strip() and AI_ENABLED:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        if st.button("🔍 Analyze Resume"):
            images = pdf_to_jpg(file_path)
            extracted_texts = [process_image(img, "Extract text from resume", type="image") for img in images]
            prompt = f"""
            Analyze resume text vs job description: {job_description}
            Resume Text: {extracted_texts}
            Return JSON: overall_score, keyword_matching, missing_keywords, suggestions
            """
            final_result = process_image(file_path=extracted_texts, prompt=prompt, type="text")
            show_dashboard(final_result.get("overall_score",0),
                           final_result.get("keyword_matching",[]),
                           final_result.get("missing_keywords",[]),
                           final_result.get("suggestions",[]))

# -------------------- PROJECT EXTRACTOR --------------------
elif page=="💼 Project Extractor":
    st.title("💼 Resume Project Extractor")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        show_pdf(file_path)
        if st.button("📂 Extract Projects"):
            images = pdf_to_jpg(file_path)
            full_text = ""
            for img in images:
                full_text += str(process_image(img, "Extract plain text", "image"))
            projects = extract_projects(full_text)
            if projects:
                st.success(f"✅ Found {len(projects)} projects:")
                for p in projects: st.markdown(f"🔹 **{p}**")
            else:
                st.warning("No clear projects found.")

# -------------------- CAREER CHATBOT --------------------
elif page=="🤖 Career Chatbot":
    st.title("🤖 AI Career Chat Assistant")
    if "chat_history" not in st.session_state: st.session_state.chat_history=[]
    user_input = st.text_input("You:", key="user_input")
    if user_input and AI_ENABLED:
        model = genai.GenerativeModel("gemini-1.5-flash-002")
        history = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in st.session_state.chat_history])
        prompt = f"You are a career coach AI.\nHistory:\n{history}\nUser query: {user_input}"
        response = model.generate_content(prompt)
        reply = response.candidates[0].content.parts[0].text if hasattr(response,"candidates") else "Sorry, I couldn’t process that."
        st.session_state.chat_history.append({"user": user_input, "bot": reply})
    for chat in st.session_state.chat_history[::-1]:
        st.markdown(f"👩‍💼 You: {chat['user']}")
        st.markdown(f"🤖 {chat['bot']}")
