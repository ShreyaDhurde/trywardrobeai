import streamlit as st
import os
from PIL import Image

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(images, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(images + [prompt])
    return response.text

def input_images_setup(uploaded_files):
    # Check if files have been uploaded
    if uploaded_files is not None and len(uploaded_files) > 0:
        image_parts = []
        for uploaded_file in uploaded_files:
            # Read the file into bytes
            bytes_data = uploaded_file.getvalue()
            image_parts.append(
                {
                    "mime_type": uploaded_file.type,
                    "data": bytes_data,
                }
            )
        return image_parts
    else:
        raise FileNotFoundError("No files uploaded")

st.set_page_config(page_title="Document & Image Analyzer")
st.header(':red[Vehicle Insurance Claim review co-pilot] 🚗', divider= 'rainbow')
st.sidebar.title("Upload Vehicle Images")
uploaded_files = st.sidebar.file_uploader(
    "Choose images...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

# Right portion to show uploaded images
if uploaded_files is not None and len(uploaded_files) > 0:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

submit = st.button("Analyze the Images")
input_prompt = """
               As an expert in analyzing vehicle images for insurance claims, your task is to evaluate multiple images of a car, potentially taken at different times (before and after an accident). For each set of images:

Identify Consistency: Determine if all images depict the same vehicle by checking the model, type, color, license plate number, and any unique features. Provide a similarity percentage.

Analyze Damage: Identify and describe any visible damages, including the affected parts and the severity of the damage.

Assess Claim Validity: Based on the analysis, decide if the claim should be approved or denied, considering the consistency of the images and the damage details.
               """

## If ask button is clicked
if submit:
    if uploaded_files is not None and len(uploaded_files) > 0:  # Add this check to ensure files are uploaded
        image_data = input_images_setup(uploaded_files)
        response = get_gemini_response(image_data, input_prompt)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload images.")
