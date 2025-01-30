import requests
import streamlit as st

st.title('Passport Processing with OCR & GPT-4')

uploaded_file = st.file_uploader("Upload Passport Image", type=["png", "jpg", "jpeg"])

def process_passport_image(image_file):
    """
    Sends the passport image to the FastAPI backend and returns extracted details.
    """
    files = {"file": image_file}
    # response = requests.post("http://localhost:8000/process_passport/", files=files)

    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     return {"error": "Failed to process the image"}

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Passport Image", use_container_width=True)
    st.write("Processing...")

    #response_data = process_passport_image(uploaded_file)

    # if "error" not in response_data:
    #     st.subheader("Extracted Passport Details:")
    #     st.json(response_data["passport_details"])
    # else:
    #     st.error(response_data["error"])
    st.write("Processing Completed! verify the extracted details below")
