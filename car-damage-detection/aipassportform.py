import streamlit as st
import os
import json
import pdfplumber
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdfs(uploaded_files):
    extracted_text = ""
    for uploaded_file in uploaded_files:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() + "\n"
    return extracted_text

def get_gemini_response(text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([text, prompt])
    return response.text

st.set_page_config(page_title="Document & PDF Analyzer")
st.header(':red[Text Extraction for Knowledge Base] 🗄️', divider='rainbow')
st.sidebar.title("Upload PDF Documents")
uploaded_files = st.sidebar.file_uploader("Choose PDFs...", type=["pdf"], accept_multiple_files=True)

submit = st.button("Analyze the PDFs")

input_prompt = """
Extract the following details in JSON format:

For Aadhaar Card:
{
    "aadhaar_number": "",
    "name": "",
    "gender": "",
    "date_of_birth": "",
    "address": ""
}

For PAN Card:
{
    "pan_number": "",
    "name": "",
    "address": "",
    "date_of_birth": "",
    "father_name": ""
}

For Driving Licence:
{
    "driving_licence_number": "",
    "date_of_registration": "",
    "valid_till": "",
    "authorized_vehicle_classes": [],
    "date_of_birth": "",
    "blood_group": "",
    "name": "",
    "address": ""
}

Ensure the output is a valid JSON object.
"""

if submit:
    if uploaded_files:
        extracted_text = extract_text_from_pdfs(uploaded_files)
        response_text = get_gemini_response(extracted_text, input_prompt)
        try:
            response_json = json.loads(response_text)
            st.subheader("Extracted Details (JSON Format)")
            st.json(response_json)
        except json.JSONDecodeError:
            st.error("Failed to parse response as JSON. Here is the raw output:")
            st.text(response_text)
    else:
        st.write("Please upload PDF documents.")
