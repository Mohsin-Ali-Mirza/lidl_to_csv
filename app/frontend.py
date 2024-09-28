# frontend.py

import streamlit as st
import requests
import pandas as pd
import io

# Streamlit application
st.title("OCR Invoice Reader")
st.write("Upload an image of an invoice to extract item names and prices.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Send the file to the FastAPI backend
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post("http://127.0.0.1:8000/upload/", files=files)

    if response.status_code == 200:
        # Process the response
        items = response.json()
        df = pd.DataFrame(items)

        # Display DataFrame
        st.write("Extracted Items:")
        st.dataframe(df)

        # Download CSV option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='output.csv',
            mime='text/csv'
        )
    else:
        st.error("Error processing the image.")
