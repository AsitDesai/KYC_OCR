from fastapi import FastAPI, UploadFile, File
import pytesseract
from PIL import Image
import openai
import re
import io
import json
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key (Make sure to set this in your .env file)
openai.api_key = "your_openai_api_key"

# Path to Tesseract OCR (Update accordingly)
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Initialize FastAPI
app = FastAPI(
    title="Passport Processing API",
    version="1.0",
    description="Extract passport details from images using OCR & GPT-4"
)

def extract_text_from_image(image):
    """
    Extracts raw text from a passport image using Tesseract OCR.
    """
    img = Image.open(image)
    extracted_text = pytesseract.image_to_string(img)
    return extracted_text

def clean_passport_text(raw_text):
    """
    Uses regex to extract key passport details: Passport No, Full Name, and Date of Birth.
    """
    passport_number = re.search(r'\b[A-Z0-9]{8,9}\b', raw_text)  # Usually 8-9 characters
    name = re.search(r'(?<=Given Names\s?:\s?)([A-Za-z ]+)', raw_text)  # Extract full name
    dob = re.search(r'(\d{1,2} [A-Za-z]+ \d{2,4})', raw_text)  # Matches '10 Aug 2002' or similar formats

    return {
        "passport_number": passport_number.group() if passport_number else "Not Found",
        "full_name": name.group() if name else "Not Found",
        "date_of_birth": dob.group() if dob else "Not Found",
        "raw_text": raw_text  # Keep this for debugging
    }

def refine_passport_details(passport_info):
    """
    Uses GPT-4 to validate and format extracted passport details.
    """
    prompt = f"""
    I extracted the following passport details using OCR:
    
    Passport Number: {passport_info['passport_number']}
    Full Name: {passport_info['full_name']}
    Date of Birth: {passport_info['date_of_birth']}

    If any detail is incorrect or missing, extract and correct it based on the raw passport text:
    
    Raw Text:
    {passport_info['raw_text']}

    Return a JSON object in the format:
    {{
        "passport_number": "XXXXXXX",
        "full_name": "FirstName LastName",
        "date_of_birth": "DD Month YYYY"
    }}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a document verification assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )

    refined_data = response["choices"][0]["message"]["content"]
    return json.loads(refined_data)

@app.post("/process_passport/")
async def process_passport(file: UploadFile = File(...)):
    """
    FastAPI endpoint to process passport image, extract information, and return results.
    """
    image_data = await file.read()
    image = io.BytesIO(image_data)
    
    raw_text = extract_text_from_image(image)
    passport_info = clean_passport_text(raw_text)
    
    refined_info = refine_passport_details(passport_info)
    
    return {
        "user_id": file.filename,  # Placeholder for user identification
        "passport_details": refined_info
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
