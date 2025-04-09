#does shows image 

import streamlit as st
from PIL import Image


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
    else:
        st.info("Please upload both images to proceed.")

if __name__ == "__main__":
    main()
