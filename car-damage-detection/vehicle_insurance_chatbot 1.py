

import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# MySQL database connection details
db_config = {
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'database': os.getenv("DB_DATABASE"),
}

# Function to check if data exists in MySQL database and get claim status
def check_data_existence(claim_request_id, vehicle_no):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = """
    SELECT claim_status 
    FROM claim_request 
    WHERE claim_request_id = %s AND vehicle_no = %s
    """
    cursor.execute(query, (claim_request_id, vehicle_no))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]  # return claim_status
    else:
        return None

# Function to update remark and image reference in MySQL database
def update_claim_request(claim_request_id, remark, img_reference):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = """
    UPDATE claim_request 
    SET remarks = %s, img_reference = %s 
    WHERE claim_request_id = %s
    """
    cursor.execute(query, (remark, img_reference, claim_request_id))
    conn.commit()
    cursor.close()
    conn.close()

# Function to generate a remark using Google Generative AI
def generate_remark(input_prompt, images_data, max_length=100):
    # Prepare image data in the required format
    image_parts = []
    for image_data in images_data:
        image_parts.append({
            "mime_type": "image/jpeg",  # Adjust mime type as needed based on your image type
            "data": image_data,
        })
    
    # Generate remark using Google Generative AI
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_prompt] + image_parts)
    
    # Truncate the response to fit within the column's length constraint
    remark_text = response.text
    if len(remark_text) > max_length:
        remark_text = remark_text[:max_length]
    
    return remark_text

# Streamlit app
st.header(":blue_car: Vehicle Insurance Claim Image Uploader")

# Input fields for claim details
st.subheader("Enter Claim Details")
claim_request_id = st.text_input("Claim Request ID")
vehicle_no = st.text_input("Vehicle Number")

# Button to check details
if st.button("Check Details"):
    if claim_request_id.strip() == "" or vehicle_no.strip() == "":
        st.error("Please enter all details.")
    else:
        claim_status = check_data_existence(claim_request_id, vehicle_no)
        if claim_status is None:
            st.error("Data does not exist for this claim. Please check your input.")
        else:
            st.success(f"Data exists for this claim and status is {claim_status.lower()}. You can now upload images and update remarks.")
            st.session_state.checked_details = True

# Photo upload section if details are correct
if st.session_state.get("checked_details", False):
    st.header("Upload Photos")
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files is not None:
        image_paths = []
        images_data = []
        upload_folder = f"claims/{claim_request_id}"
        os.makedirs(upload_folder, exist_ok=True)
        
        for uploaded_file in uploaded_files:
            image_path = os.path.join(upload_folder, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                images_data.append(uploaded_file.getvalue())
            image_paths.append(image_path)
        
        # Display the uploaded images
        for image_path in image_paths:
            st.image(Image.open(image_path), caption="Uploaded Image", use_column_width=True)
        
        # Generate remark using Google Generative AI
        input_prompt = """
                       You are an expert in reading and analyzing damaged vehicle images for approving insurance claims.
                       Please describe the damage shown in the uploaded images.
                       Read Images from multiple angles to get a correct and precise description in a short way.
                       """
        remark = generate_remark(input_prompt, images_data)
        
        st.write("Generated Remark:", remark)
        
        # Submit button to update remark and image reference in the database
        if st.button("Submit"):
            img_reference = ','.join(image_paths)  # Store paths as a comma-separated string
            update_claim_request(claim_request_id, remark, img_reference)
            st.success("Remark and image references updated successfully for Claim Request ID: " + claim_request_id)
else:
    if st.session_state.get("checked_details") is not None:
        st.info("Please check details to proceed.")
