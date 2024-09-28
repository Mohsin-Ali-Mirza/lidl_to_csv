import streamlit as st
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np

# Initialize the PaddleOCR model
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Set language as needed

# Streamlit UI
st.title("Text Extraction from Image")
st.write("Upload an image to extract text using PaddleOCR.")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load the image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    # Convert image to numpy array for PaddleOCR
    img_array = np.array(image)

    # Perform OCR
    results = ocr.ocr(img_array, cls=True)

    # Display the results
    st.write("Extracted Text:")
    for result in results:
        for line in result:
            text = line[1][0]
            confidence = line[1][1]
            st.write(f"{text} (Confidence: {confidence:.2f})")
