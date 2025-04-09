import streamlit as st
from PIL import Image
import base64
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Configure Generative AI with API key
genai.configure(api_key=api_key)

# Initialize the GenerativeModel with the specified model name
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to encode an image to base64
def encode_image_to_base64(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to generate content based on the input prompt and images
def generate_content_with_images(before_image_base64, after_image_base64):
    # Define the prompt
    input_prompt = {
        "text": (
            "You are given two images of a vehicle. The first image is taken before an accident, and the second image is taken after the accident. "
            "Your task is to determine if the vehicle in the 'after' image is the same as the vehicle in the 'before' image. "
            "Consider all visible aspects such as model, color, unique identifiers, and any damages. Provide a detailed analysis and give a percentage "
            "similarity score indicating how likely it is that both images are of the same vehicle."
        )
    }

    # Prepare the image parts as base64
    image_parts = [
        {"inline_data": {"mime_type": "image/jpeg", "data": before_image_base64}},
        {"inline_data": {"mime_type": "image/jpeg", "data": after_image_base64}}
    ]

    # Combine the input prompt and image parts
    content_parts = [input_prompt] + image_parts

    try:
        # Generate content using the model
        response = model.generate_content(content_parts)
        result = response["choices"][0]["text"]
        return result
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def main():
    st.title("Car Accident Image Comparison")

    # Upload images
    st.header("Upload Images")

    before_image = st.file_uploader("Upload 'Before' Image", type=['jpg', 'jpeg', 'png'], key='before')
    after_image = st.file_uploader("Upload 'After' Image", type=['jpg', 'jpeg', 'png'], key='after')

    # Display images
    if before_image and after_image:
        st.header("Uploaded Images")
        col1, col2 = st.columns(2)

        with col1:
            st.image(before_image, caption='Before Accident', use_column_width=True)

        with col2:
            st.image(after_image, caption='After Accident', use_column_width=True)

        # Compare images using the Generative AI model
        if st.button("Compare Images"):
            # Convert images to base64 strings
            before_image_base64 = encode_image_to_base64(before_image)
            after_image_base64 = encode_image_to_base64(after_image)

            comparison_result = generate_content_with_images(before_image_base64, after_image_base64)
            if comparison_result:
                st.header("Comparison Result")
                st.write(comparison_result)
    else:
        st.info("Please upload both images to proceed.")

if __name__ == "__main__":
    main()
