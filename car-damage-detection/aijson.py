import streamlit as st
import os
import json
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(images, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(images + [prompt])
    return response.text


def input_images_setup(uploaded_files):
    if uploaded_files:
        image_parts = []
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.getvalue()
            image_parts.append({
                "mime_type": uploaded_file.type,
                "data": bytes_data,
            })
        return image_parts
    else:
        raise FileNotFoundError("No files uploaded")

st.set_page_config(page_title="Document & Image Analyzer")
st.header(':red[Text Extraction for Knowledge Base] 🗄️', divider='rainbow')
st.sidebar.title("Upload Vehicle Images")
uploaded_files = st.sidebar.file_uploader("Choose images...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

submit = st.button("Analyze the Images")

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

for Driving Licence

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
        image_data = input_images_setup(uploaded_files)
        response_text = get_gemini_response(image_data, input_prompt)
        try:
            response_json = json.loads(response_text)
            st.subheader("Extracted Details (JSON Format)")
            st.json(response_json)
        except json.JSONDecodeError:
            st.error("Failed to parse response as JSON. Here is the raw output:")
            st.text(response_text)
    else:
        st.write("Please upload images.")
