import os
import base64
from pathlib import Path
import fitz
import streamlit as st
from analyzer import process_image

st.set_page_config(page_title="Nuvora AI Job Assistant", layout="wide")

st.title("📘 Nuvora AI Job Assistant")
st.info("Upload your resume and analyze with Gemini AI")

uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
if uploaded_file:
    file_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.markdown("Uploaded file: "+uploaded_file.name)
