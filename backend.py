# backend.py

from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
from googletrans import Translator
import pandas as pd
import uvicorn
from fastapi.responses import JSONResponse
import os

app = FastAPI()

ocr = PaddleOCR(lang='de')
translator = Translator()

def perform_ocr(image_path):
    """Perform OCR on the specified image and return the results."""
    return ocr.ocr(image_path)

def extract_items(result):
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

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint to upload an image and process it."""
    image_path = "temp_image.jpg"
    with open(image_path, "wb") as f:
        f.write(await file.read())

    result = perform_ocr(image_path)
    items_dict = extract_items(result)
    cleaned_dict = clean_item_values(items_dict)
    df = create_dataframe(cleaned_dict)

    # Clean up temporary file
    os.remove(image_path)

    # Return the DataFrame as JSON
    return JSONResponse(content=df.to_dict(orient="records"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
