import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Google Generative AI API key
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def get_gemini_response(images, prompt):
    """Generate a response from Gemini model using images and a prompt."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(images + [prompt])
    return response.text

def input_images_setup(image_paths):
    """Read and prepare image data from provided file paths."""
    image_parts = []
    for image_path in image_paths:
        if os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    image_parts.append({
                        "mime_type": "image/jpeg",  # or detect based on file extension
                        "data": f.read(),
                    })
                print(f"Successfully loaded: {image_path}")
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
        else:
            print(f"File does not exist: {image_path}")
    return image_parts

def main():
    """Main function to handle user input and analyze images."""
    # Input image paths
    image_paths_input = input("Enter the image file paths, separated by commas: ")
    
    # Split the input by commas and strip extra spaces
    image_paths = [path.strip() for path in image_paths_input.split(",")]

    # Prepare image data
    image_data = input_images_setup(image_paths)
    
    # Define the input prompt for the analysis
    input_prompt = """
    As an expert in analyzing vehicle images for insurance claims, your task is to evaluate multiple images of a car, potentially taken at different times (before and after an accident). For each set of images:

    - Identify Consistency: Determine if all images depict the same vehicle by checking the model, type, color, license plate number, and any unique features. Provide a similarity percentage.
    - Analyze Damage: Identify and describe any visible damages, including the affected parts and the severity of the damage.
    - Assess Claim Validity: Based on the analysis, decide if the claim should be approved or denied, considering the consistency of the images and the damage details.
    """

    # Get response from Gemini model
    response = get_gemini_response(image_data, input_prompt)
    print("\nThe Response is:")
    print(response)

if __name__ == "__main__":
    main()
