import os
import cv2
import numpy as np
from pytesseract import image_to_string
from pdf2image import convert_from_bytes
from utils import extract_methods as em
from utils import validation as va
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import date
from pprint import pprint

@dataclass
class Residence:
    start_date: date
    end_date: date
    location: str
    country: str

@dataclass
class DateRange:
    start_date: date
    end_date: date

@dataclass
class ExtractedData:
    request_type: str = ""
    name: str = ""
    arrival_date: date = None
    first_work_date: date = None
    places_of_residence: List[Residence] = field(default_factory=list)
    nl_residence_dates: List[DateRange] = field(default_factory=list)
    nl_deregister_date: date = None
    nl_private_dates: List[DateRange] = field(default_factory=list)
    nl_dutch_employer_dates: List[DateRange] = field(default_factory=list)
    nl_worked_dates: List[DateRange] = field(default_factory=list)
    employer: str = ""
    payroll_tax_number: str = ""
    employer_type: str = ""
    date_of_birth: date = None
    bsn: str = ""
    job_title: str = ""
    contract_start_date: date = None
    ufo_code: str = ""
    application_date: date = None
    contract_signed_date: date = None
    explain_will_agreement: str = ""
    previous_jobs: str = ""
    nl_explain: str = ""

def extract_specific_data(sofie_raw_data, topdesk_raw_data) -> dict:
    """Extract specific data from the raw data."""
    
    data = ExtractedData(
        # Extract data from Sofie form
        request_type = None, # Select button to be implemented between 4 options
        name = em.extract_between_keywords(sofie_raw_data, "Initials", "Has agreed", clean=True),
        arrival_date = em.extract_date(sofie_raw_data, "Date of arrival", "My address", single_date=True),
        first_work_date = em.extract_date(sofie_raw_data, "working day", "Place", single_date=True),
        places_of_residence = em.extract_place_of_residences(sofie_raw_data),
        nl_residence_dates = em.extract_multiple_dates(sofie_raw_data, "Have you previously", "Were you registered"),
        nl_deregister_date = em.extract_date(sofie_raw_data, "deregister", "Have you", single_date=True),
        nl_worked_dates = em.extract_multiple_dates(sofie_raw_data, "Have you previously worked", "private"),
        nl_private_dates = em.extract_multiple_dates(sofie_raw_data, "holiday", "outside"),
        nl_dutch_employer_dates= em.extract_multiple_dates(sofie_raw_data, "outside", "undersigned"),
        
        # Extract data from Topdesk form
        employer = em.extract_between_keywords(topdesk_raw_data, "Name of employer", "\n", clean=True),
        payroll_tax_number = em.extract_between_keywords(topdesk_raw_data, "LH number", "\n", clean=True),
        employer_type = None, # Public or Private 
        date_of_birth = em.extract_date(topdesk_raw_data, "Birth", "\n", single_date=True),
        bsn = em.extract_between_keywords(topdesk_raw_data, "BSN Number", "\n", clean=True),
        job_title = em.extract_between_keywords(topdesk_raw_data, "Title", "\n", clean=True),
        contract_start_date = em.extract_date(topdesk_raw_data, "into service", "\n", single_date=True),
        ufo_code = em.extract_between_keywords(topdesk_raw_data, "UFO code", "\n", clean=True),
        application_date = em.extract_date(topdesk_raw_data, "Created at", "by", single_date=True),

        # Extract data from cv and work contract (not implemented yet)
        contract_signed_date = None,  
        explain_will_agreement = None,
        previous_jobs = None,
        nl_explain = None,
    )

    data_dict = asdict(data)
    return data_dict

def validate(extracted_data: dict) -> dict:
    """"Check if the university is correct, and update other related values"""
    transformed_data = va.university(extracted_data)  
    return transformed_data

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

def main(sofie_data, topdesk_data, dev_mode=False) -> dict:
    """Extract data from the uploaded files."""
    if not dev_mode:
        sofie_data = file_to_raw_data(sofie_data, config_psm=11)
        topdesk_data = file_to_raw_data(topdesk_data, config_psm=4)
        save_text(sofie_data, "sofie_data")
        save_text(topdesk_data, "topdesk_data")
    extracted_data = extract_specific_data(sofie_data, topdesk_data)
    validated_data = validate(extracted_data)
    
    pprint(validated_data)
    
    return validated_data

