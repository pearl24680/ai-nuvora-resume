import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(page_title="Nuvora AI Job Assistant", layout="wide")

# ---------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------
st.markdown("""
<style>
body { background-color: #f0f5ff; }
div[data-testid="stSidebar"] { background-color: #cce0ff; }
.section {
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 0px 10px rgba(0,0,0,0.1);
    margin-bottom:20px;
}
.metric-box {
    background:#edf3ff;
    padding:15px;
    border-radius:10px;
    text-align:center;
    font-weight:bold;
}
.user-msg {
    background:#d9f2d9;
    border-radius:8px;
    padding:8px 12px;
    margin:6px 0;
}
.bot-msg {
    background:#cce0ff;
    border-radius:8px;
    padding:8px 12px;
    margin:6px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TEXT EXTRACTION
# ---------------------------------------------------
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# ---------------------------------------------------
# ANALYSIS FUNCTIONS
# ---------------------------------------------------
def analyze_resume(resume_text, jd_text=""):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower() if jd_text else ""

    ds_keywords = [
        "python", "machine learning", "data analysis", "sql", "excel", "pandas",
        "numpy", "deep learning", "statistics", "power bi", "tableau",
        "visualization", "modeling", "ai", "communication", "teamwork",
        "data cleaning", "eda", "nlp", "classification", "regression"
    ]

    found = [kw for kw in ds_keywords if kw in resume_text]
    missing = [kw for kw in ds_keywords if kw not in found]
    ats_score = int((len(found) / len(ds_keywords)) * 100)

    jd_keywords = []
    if jd_text:
        jd_keywords = list(set(re.findall(r'\b[a-zA-Z]{4,}\b', jd_text)))

    return ats_score, found, missing, jd_keywords

def extract_projects(resume_text):
    project_patterns = [
        r'(?i)(projects?|academic projects?|personal projects?|internship projects?)[:\-]?\s*(.*)',
        r'(?i)(?:\*\*|##|###)?\s*Project\s*[:\-]?\s*(.*)'
    ]
    matches = []
    for pattern in project_patterns:
        found = re.findall(pattern, resume_text)
        for f in found:
            if isinstance(f, tuple):
                matches.append(f[1])
            else:
                matches.append(f)
    return list(set(matches))

def plot_ats(ats_score):
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.barh(["ATS Match"], [ats_score], color="#6a9efc")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score (%)")
    for i, v in enumerate([ats_score]):
        ax.text(v + 2, i, f"{v}%", va='center', fontweight='bold')
    return fig

# ---------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------
st.sidebar.title("🧭 Navigation")
menu = ["🏠 Dashboard", "📊 ATS Analysis", "💼 Project Extraction", "🤖 AI Career Chat"]
choice = st.sidebar.radio("Go to:", menu)

# ---------------------------------------------------
# FILE UPLOAD (GLOBAL)
# ---------------------------------------------------
st.sidebar.subheader("📂 Upload Files")
resume_file = st.sidebar.file_uploader("Upload Resume", type=["pdf", "docx"])
jd_file = st.sidebar.file_uploader("Upload Job Description (optional)", type=["pdf", "docx", "txt"])

resume_text, jd_text = "", ""
if resume_file:
    resume_text = extract_text(resume_file)
if jd_file:
    if jd_file.name.endswith(".txt"):
        jd_text = jd_file.read().decode("utf-8")
    else:
        jd_text = extract_text(jd_file)

# ---------------------------------------------------
# 1️⃣ DASHBOARD
# ---------------------------------------------------
if choice == "🏠 Dashboard":
    st.title("💎 Nuvora AI Job Assistant Dashboard")

    if resume_file:
        ats_score, found, missing, jd_keywords = analyze_resume(resume_text, jd_text)
        projects = extract_projects(resume_text)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-box'>📊 ATS Score<br><span style='font-size:28px;color:#004080'>{ats_score}%</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'>✅ Matched Keywords<br><span style='font-size:28px;color:#008000'>{len(found)}</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box'>⚠️ Missing Keywords<br><span style='font-size:28px;color:#ff3300'>{len(missing)}</span></div>", unsafe_allow_html=True)

        st.markdown("### 📈 Resume Selection Probability")
        st.pyplot(plot_ats(ats_score))

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("✅ Matched Keywords")
        st.write(", ".join(found) if found else "No keywords found.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("⚠️ Missing Keywords")
        st.write(", ".join(missing) if missing else "None 🎉 Perfect coverage!")
        st.markdown("</div>", unsafe_allow_html=True)

        if jd_keywords:
            st.markdown("<div class='section'>", unsafe_allow_html=True)
            st.subheader("📋 Job Description Keywords")
            st.write(", ".join(jd_keywords[:40]) + " ...")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("💼 Detected Projects")
        if projects:
            for i, p in enumerate(projects, 1):
                st.write(f"**{i}.** {p.strip()}")
        else:
            st.write("No projects detected.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🧠 Resume Improvement Suggestions")
        st.markdown("""
        - Add missing **data tools or libraries** from the list above.  
        - Use **metrics or outcomes** in your project descriptions.  
        - Mirror **JD language** to improve ATS match.  
        - Keep your resume concise & skills highlighted clearly.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("👆 Upload your resume from the sidebar to generate your dashboard.")

# ---------------------------------------------------
# 2️⃣ ATS ANALYSIS PAGE
# ---------------------------------------------------
elif choice == "📊 ATS Analysis":
    st.title("📊 Detailed ATS Resume Analysis")

    if resume_file:
        ats_score, found, missing, jd_keywords = analyze_resume(resume_text, jd_text)
        st.metric("ATS Score", f"{ats_score}%")
        st.pyplot(plot_ats(ats_score))
        st.write("**Matched Keywords:**", ", ".join(found))
        st.write("**Missing Keywords:**", ", ".join(missing))
    else:
        st.warning("Please upload your resume to analyze.")

# ---------------------------------------------------
# 3️⃣ PROJECT EXTRACTION PAGE
# ---------------------------------------------------
elif choice == "💼 Project Extraction":
    st.title("💼 Resume Project Extraction")

    if resume_file:
        projects = extract_projects(resume_text)
        if projects:
            for i, p in enumerate(projects, 1):
                st.write(f"**{i}.** {p.strip()}")
        else:
            st.warning("No projects detected in resume.")
    else:
        st.info("Upload your resume to extract projects.")

# ---------------------------------------------------
# 4️⃣ AI CAREER CHATBOT
# ---------------------------------------------------
elif choice == "🤖 AI Career Chat":
    st.title("🤖 Nuvora AI Career Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("💬 Ask about resume, jobs, or data science careers:")
    if st.button("Send") and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        text_lower = user_input.lower()

        # Smart responses
        if "resume" in text_lower:
            response = "Ensure your resume highlights core skills, tools, and measurable impact."
        elif "ats" in text_lower:
            response = "ATS prefers clear formatting & keyword alignment with the job description."
        elif "data" in text_lower:
            response = "Include data cleaning, EDA, visualization, and model-building experience."
        elif "python" in text_lower:
            response = "Python is key for data roles—mention pandas, numpy, scikit-learn, etc."
        elif "sql" in text_lower:
            response = "Add SQL queries or database projects to strengthen your profile."
        elif "job" in text_lower:
            response = "Target roles like Data Analyst, ML Engineer, or AI Associate matching your resume."
        else:
            response = "That's great! I can guide you about ATS, resume structure, or data science careers."

        st.session_state.chat_history.append({"role": "assistant", "content": response})

    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="user-msg">{chat["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">{chat["content"]}</div>', unsafe_allow_html=True)
