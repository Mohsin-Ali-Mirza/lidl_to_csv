import streamlit as st
import pandas as pd
from paddleocr import PaddleOCR
from googletrans import Translator
import os

def initialize_ocr(lang='de'):
    """Initialize PaddleOCR with specified language."""
    return PaddleOCR(lang=lang)

def initialize_translator():
    """Initialize Google Translator."""
    return Translator()

def perform_ocr(image_path, ocr):
    """Perform OCR on the specified image and return the results."""
    return ocr.ocr(image_path)

def extract_items(result, translator):
    """Extract items and their prices from the OCR result."""
    items_dict = {}
    to_write = False

    for line in result:
        for word in line:
            german_text = word[1][0]  # Extracted German text
            
            if german_text == "EUR":
                to_write = True
                continue  # Skip to the next iteration

            if german_text == "Bar":
                break  # Exit the loop if "Bar" is found

            if to_write:
                # Check if the next word contains a price format (with a comma and 'A')
                if 'A' in german_text and ',' in german_text:
                    # Attempt to find the item name preceding this price
                    if items_dict:  # Make sure we have an item before adding the price
                        item_name = list(items_dict.keys())[-1]  # Get the last item added
                        items_dict[item_name] = german_text  # Update the last item with its price
                else:
                    # Ignore pure integers
                    if german_text.isdigit():
                        continue
                    
                    # Assuming the current text is an item name
                    translated_text = translator.translate(german_text, src='de', dest='en').text  # Translate to English
                    items_dict[translated_text] = None  # Initialize item with no price yet
                    print(f"German: {german_text} -> English: {translated_text}")
    
    return items_dict

def clean_item_values(items_dict):
    """Clean item values by removing 'A' and replacing ',' with '.'."""
    cleaned_dict = {}
    for item, price in items_dict.items():
        # If price is None, keep it as None
        if price is None:
            cleaned_dict[item] = price
            continue
        # Remove 'A' and replace ',' with '.'
        cleaned_price = price.replace('A', '').replace(',', '.').strip()
        cleaned_dict[item] = cleaned_price
    return cleaned_dict

def create_dataframe(cleaned_dict):
    """Create a pandas DataFrame from the cleaned item dictionary."""
    df = pd.DataFrame(cleaned_dict.items(), columns=["Item Name", "Price"])
    return df

def update_total_price(df):
    """Update the total price in the DataFrame."""
    total_price = df.iloc[-1]["Item Name"]
    df.iloc[-2]["Price"] = total_price
    df = df.drop(df.index[-1])  # Remove the last row
    return df

# Streamlit application
st.title("OCR Invoice Reader")
st.write("Upload an image of an invoice to extract item names and prices.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary directory
    image_path = "temp_image.jpg"
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Process the image
    ocr = initialize_ocr()
    translator = initialize_translator()
    
    result = perform_ocr(image_path, ocr)
    items_dict = extract_items(result, translator)
    cleaned_dict = clean_item_values(items_dict)
    
    df = create_dataframe(cleaned_dict)
    df = update_total_price(df)

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

    # Clean up temporary file
    os.remove(image_path)
