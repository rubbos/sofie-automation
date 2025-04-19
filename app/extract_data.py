import os
import cv2
import numpy as np
from pytesseract import image_to_string
from pdf2image import convert_from_bytes
from extractors.methods import extract_methods as em

def preprocess_image(image, margin=50):
    """Preprocess the image for pytesseract by resizing and cropping fixed margins."""
    img = np.array(image)
    resized_img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    height, width = resized_img.shape[:2]
    cropped_img = resized_img[margin : height - margin, margin : width - margin]
    return cropped_img

def file_to_raw_data(pdf_bytes, config_psm: int) -> str:
    """Convert uploaded file to string"""
    doc = convert_from_bytes(pdf_bytes)
    text = ""
    for page_data in doc:
        processed_data = preprocess_image(page_data)
        text += image_to_string(processed_data, config=f"--psm {config_psm}")
    return text

def save_text(text: str, name: str) -> None:
    """Save text from tesseract to a temporary file."""
    folder_path = "temp_files"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{name}.txt")
    with open(file_path, "w") as text_file:
        text_file.write(text)

def extract_specific_data(sofie_raw_data, topdesk_raw_data) -> dict:
    """Extract specific data from the raw data."""
    request_type = ""
    name = em.extract_between_keywords(sofie_raw_data, "Initials", "Has agreed")
    arrival_date = em.extract_dates(sofie_raw_data, "Date of arrival", "My address")
    first_work_date = em.extract_dates(sofie_raw_data, "working day", "Place")
    places_of_residence = em.extract_place_of_residences(sofie_raw_data)
    nl_residence_dates = em.extract_multiple_dates(sofie_raw_data, "Have you previously", "Were you registered")
    nl_deregister_date = em.extract_dates(sofie_raw_data, "deregister", "Have you")
    nl_worked_dates = em.extract_multiple_dates(sofie_raw_data, "Have you previously worked", "private")
    nl_private_dates = em.extract_multiple_dates(sofie_raw_data, "holiday", "outside")
    nl_dutch_employer_dates= em.extract_multiple_dates(sofie_raw_data, "outside", "undersigned")

    #FIXME Add more data from other files
    print("REQUEST TYPE", request_type)
    print("NAME", name)
    print("ARRIVAL DATE", arrival_date) 
    print("FIRST WORK DATE", first_work_date)
    print("PLACES OF RESIDENCE", places_of_residence)
    print("NL RESIDENCE DATES", nl_residence_dates)
    print("NL DEREGISTER DATE", nl_deregister_date)
    print("NL PRIVATE DATES", nl_private_dates)         
    print("NL DUTCH EMPLOYER DATES", nl_dutch_employer_dates)
    print("NL WORKED DATES", nl_worked_dates)
    return []

def main(sofie_data, topdesk_data, dev_mode=False) -> dict:
    """Extract data from the uploaded files."""
    if not dev_mode:
        sofie_data = file_to_raw_data(sofie_data, config_psm=11)
        topdesk_data = file_to_raw_data(topdesk_data, config_psm=4)
        em.save_text(sofie_data, "sofie_data")
        em.save_text(topdesk_data, "topdesk_data")
    extracted_data = extract_specific_data(sofie_data, topdesk_data)
    return extracted_data

