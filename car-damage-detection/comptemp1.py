import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
import google.generativeai as genai
import google.ai.generativelanguage as glm

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
API_KEY = os.getenv('GOOGLE_API_KEY')

# Check if API_KEY is loaded
if API_KEY is None:
    st.error("API_KEY is not set in the environment variables.")
else:
    # Configure the Generative AI client with the API key
    genai.configure(api_key=API_KEY)

    # Streamlit page configuration
    st.set_page_config(page_title="Image Analysis", page_icon="📸", layout="centered", initial_sidebar_state='collapsed')

    # Page header
    st.header("Vehicle Image Analysis")

    # File uploader widget
    uploaded_file = st.file_uploader("Choose an Image file", accept_multiple_files=False, type=['jpg', 'png'])

    if uploaded_file is not None:
        # Open and display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Get the byte data of the uploaded file
        bytes_data = uploaded_file.getvalue()

        # Button to trigger the image analysis
        if st.button("Analyze!"):
            try:
                # Initialize the GenerativeModel with the specified model name
                model = genai.GenerativeModel('gemini-1.5-flash')

                # Create the content parts for the request
                content_parts = [
                    glm.Part(text="Please analyze the vehicle in this image. Provide the following details: vehicle number, model, color, and any visible damage or unique features."),
                    glm.Part(inline_data=glm.Blob(mime_type='image/jpeg', data=bytes_data))
                ]

                # Generate content using the model with streaming
                response = model.generate_content(glm.Content(parts=content_parts), stream=True)

                # Ensure the response is fully processed
                response.resolve()  # Wait for the streaming response to complete

                # Access the response text
                result = response.result.candidates[0].content.parts[0].text

                # Display the result in the Streamlit app
                st.write(result)

            except Exception as e:
                st.error(f"Error: {e}")
