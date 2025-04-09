import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
import google.ai.generativelanguage as glm

# Load environment variables from .env file
load_dotenv()

# Configure the Generative AI client with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, images):
    """
    Function to load Generative AI model and get response
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Prepare content parts for the model
    content_parts = [
        glm.Part(text=input_text)
    ]

    # Add each image data to content parts
    for img in images:
        content_parts.append(glm.Part(inline_data=img))

    # Generate content using the model
    response = model.generate_content(glm.Content(parts=content_parts), stream=True)

    # Ensure the response is fully processed
    response.resolve()

    # Access the response text
    return response.result.candidates[0].content.parts[0].text

def input_image_setup(uploaded_files):
    """
    Function to prepare image data for AI processing
    """
    image_parts = []
    for uploaded_file in uploaded_files:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts.append(glm.Blob(mime_type=uploaded_file.type, data=bytes_data))
    return image_parts

# Streamlit page configuration
st.set_page_config(page_title="Document & Image Analyzer")

# Page header
st.header(':red[Vehicle Insurance Claim Review Co-pilot] 🚗', divider='rainbow')
st.sidebar.title("Upload Vehicle Images")

# User input prompt
input_text = st.text_input("Input your Prompt: ", key="input")

# File uploader for multiple images
uploaded_files = st.sidebar.file_uploader(
    "Choose images...", type=["jpg", "png", "jpeg"], accept_multiple_files=True
)

# Display uploaded images
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)

# Button to submit and analyze images
submit = st.button("Analyze the Images")

# Default prompt for the AI model
input_prompt = """
    You are an expert in reading and analyzing damaged vehicle images for approving insurance claims.
    You will receive input images of the original image of the car. Your task is to 
    identify whether the damaged car matches the original image of the car and provide a percentage similarity.
"""

# If the Analyze button is clicked
if submit:
    if uploaded_files:
        try:
            # Prepare image data for analysis
            image_data = input_image_setup(uploaded_files)

            # Get the response from the AI model
            response = get_gemini_response(input_prompt, image_data)

            # Display the response
            st.subheader("The Response is")
            st.write(response)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.write("Please upload images.")

