from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import requests

# Initialize FastAPI app
app = FastAPI()

# Set OpenAI API Key
openai.api_key = "your_openai_api_key"

# Define request model for input validation
class PassportRequest(BaseModel):
    image_urls: list[str]  # List of image URLs
    database_details: dict  # Database details containing name, DOB, and passport number

# Function to extract passport details using OpenAI Vision API
async def extract_passport_details(image_url: str):
    """
    Sends the image to OpenAI GPT-4 Vision API to extract passport details.
    """
    prompt = """
    Extract the following passport details from the image:
    - Passport Number
    - Full Name
    - Date of Birth

    If any of these details are missing, return a JSON object with an 'alert' field explaining the issue.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "You are an expert in passport data extraction."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": image_url}
                ]}
            ],
            max_tokens=300
        )

        extracted_data = response["choices"][0]["message"]["content"]
        return extracted_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting data: {str(e)}")

# Function to validate extracted passport details
def validate_passport_details(database_data: dict, extracted_data: dict):
    """
    Compares extracted passport details with the database records.
    """
    mismatched_fields = {}

    for key in ["passport_number", "full_name", "date_of_birth"]:
        if key in extracted_data and key in database_data:
            if extracted_data[key] != database_data[key]:
                mismatched_fields[key] = {
                    "expected": database_data[key],
                    "found": extracted_data[key]
                }

    validation_result = {
        "match": len(mismatched_fields) == 0,
        "mismatched_fields": mismatched_fields
    }

    return validation_result

# FastAPI Route: Accepts Passport Image URLs & Database Data, Extracts & Validates Details
@app.post("/process_passport")
async def process_passport(request: PassportRequest):
    """
    API Endpoint to process passport images, extract information, and validate with database records.
    """
    extracted_results = []

    for image_url in request.image_urls:
        extracted_data = await extract_passport_details(image_url)

        validation_result = validate_passport_details(request.database_details, extracted_data)

        response_data = {
            "extracted_data": extracted_data,
            "validation": validation_result
        }

        extracted_results.append(response_data)

    return {"results": extracted_results}

