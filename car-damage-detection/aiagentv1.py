import streamlit as st
import os
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
    if uploaded_files is not None and len(uploaded_files) > 0:
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
st.header(':red[Document Knowledge] 🚗', divider='rainbow')
st.sidebar.title("Upload Vehicle Images")
uploaded_files = st.sidebar.file_uploader("Choose images...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files is not None and len(uploaded_files) > 0:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

submit = st.button("Analyze the Images")
input_prompt = """
    Extract the following details:
    
    Aadhaar Card:
    1. Aadhaar Card Number
    2. Name
    3. Gender
    4. Date of Birth
    5. Address
    
    PAN Card:
    1. PAN Card Number
    2. Name
    3. Address
    4. Date of Birth
    5. Father's Name
    
    Ensure all details are captured in the exact format specified.
"""

expected_parameters = {
    "Aadhaar Card": ["Aadhaar Card Number", "Name", "Gender", "Date of Birth", "Address"],
    "PAN Card": ["PAN Card Number", "Name", "Address", "Date of Birth", "Father's Name"]
}

if submit:
    if uploaded_files is not None and len(uploaded_files) > 0:
        image_data = input_images_setup(uploaded_files)
        response = get_gemini_response(image_data, input_prompt)
        
        st.subheader("Extracted Details")
        st.write(response)
        
        extracted_details = {detail.split(":")[0].strip(): detail.split(":")[1].strip() for detail in response.split("\n") if ":" in detail}
        
        missing_params = {}
        extra_params = {}
        
        for doc_type, expected_keys in expected_parameters.items():
            missing_params[doc_type] = [param for param in expected_keys if param not in extracted_details]
            extra_params[doc_type] = [param for param in extracted_details if param not in expected_keys]
        
        st.subheader("Verification Results")
        if all(not missing_params[doc] and not extra_params[doc] for doc in expected_parameters):
            st.success("All expected parameters are correctly extracted.")
        else:
            if any(missing_params[doc] for doc in expected_parameters):
                st.warning("Missing Parameters:")
                for doc, params in missing_params.items():
                    if params:
                        st.write(f"{doc}: {', '.join(params)}")
            
            if any(extra_params[doc] for doc in expected_parameters):
                st.warning("Extra Parameters Found:")
                for doc, params in extra_params.items():
                    if params:
                        st.write(f"{doc}: {', '.join(params)}")
        
        final_parameters = {}
        
        for param in set(expected_parameters["Aadhaar Card"] + expected_parameters["PAN Card"]):
            aadhaar_value = extracted_details.get(param + " (Aadhaar Card)", "")
            pan_value = extracted_details.get(param + " (PAN Card)", "")
            
            if aadhaar_value and pan_value:
                if aadhaar_value == pan_value:
                    final_parameters[param] = aadhaar_value
                else:
                    final_parameters[param] = f"Aadhaar: {aadhaar_value}, PAN: {pan_value}"
            elif aadhaar_value:
                final_parameters[param] = aadhaar_value
            elif pan_value:
                final_parameters[param] = pan_value
        
        st.subheader("Final List of Extracted Parameters")
        st.write(final_parameters)
    else:
        st.write("Please upload images.")
