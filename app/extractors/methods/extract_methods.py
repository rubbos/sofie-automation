import re
import pandas as pd
from pytesseract import image_to_string
from pdf2image import convert_from_bytes
from extractors.methods import transform_methods as tm
import cv2
import numpy as np
import os
from datetime import datetime


def save_text(text: str, name: str) -> None:
    """Save the extracted text from pytesseract in a folder"""
    folder_path = "temp_files"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, f"{name}.txt")
    with open(file_path, "w") as text_file:
        text_file.write(text)


def preprocess_image(image):
    """Make pytesseract more accurate by processing the image"""
    img = np.array(image)
    resized_img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return resized_img


def file_to_raw_data(pdf_bytes, config_psm: int) -> str:
    """Convert uploaded file to string"""
    doc = convert_from_bytes(pdf_bytes)

    text = ""
    for page_data in doc:
        processed_data = preprocess_image(page_data)
        text += image_to_string(processed_data, config=f"--psm {config_psm}")
    return text


def extract_after_keyword(text: str, start_keyword: str) -> str | None:
    """Extract string after keyword till end of text"""
    start_index = text.find(start_keyword)
    if start_index == -1:
        return None
    return text[start_index + len(start_keyword) :]


def extract_between_keywords(
    text: str, start_keyword: str, end_keyword: str
) -> str | None:
    """Extract string between 2 keywords"""
    start_index = text.find(start_keyword)
    end_index = text.find(end_keyword, start_index + len(start_keyword))
    if start_index == -1 or end_index == -1 or end_index < start_index:
        return None
    return text[start_index + len(start_keyword) : end_index]


def extract_around_keywords(text: str, start_keyword: str, end_keyword: str):
    """Extract string between and including 2 keywords"""
    start_index = text.find(start_keyword)
    end_index = text.find(end_keyword, start_index + len(start_keyword))
    if start_index == -1 or end_index == -1 or end_index < start_index:
        return None
    return text[start_index : end_index + len(end_keyword)]


def remove_text_around_keywords(text: str, start_keyword: str, end_keyword: str):
    text_to_remove = extract_around_keywords(text, start_keyword, end_keyword)
    return text.replace(text_to_remove, "")


def extract_specific_words(
    text: str, start_keyword: str, end_keyword: str, words_list: list[str]
) -> str | None:
    text = extract_between_keywords(text, start_keyword, end_keyword)

    if not text:
        return None

    for word in words_list:
        if word in text:
            return word
    return "Not found"


def extract_multiple_between_keywords(
    text: str,
    start_keyword: str,
    end_keyword: str,
    split_keyword: str,
    multiple_keyword: str,
) -> list[str] | None:
    """Extract multiple repeating strings between 2 keywords from part of text"""
    text = extract_between_keywords(text, start_keyword, end_keyword)
    if not text:
        return None
    strings = text.split(split_keyword)
    strings = [" ".join(item.split()) for item in strings]
    strings.pop(0)
    strings = [extract_after_keyword(item, multiple_keyword) for item in strings]
    return strings


def find_all_dates(text: str) -> list[str]:
    """Find any kind of date format in string"""
    date_pattern = r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|\b\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-\s]\d{2,4}\b|\b\d{1,2}[-\s](?:January|February|March|April|May|June|July|August|September|October|November|December)[-\s]\d{2,4}\b"
    pattern = re.compile(date_pattern)
    matches = pattern.findall(text)
    return matches


def extract_dates(
    string: str, start_keyword: str, end_keyword: str
) -> list[str] | None:
    """Extract all dates in string and transform to dd-mm-yyyy"""
    text = extract_between_keywords(string, start_keyword, end_keyword)
    if not text:
        return None
    dates = find_all_dates(text)
    cleaned_dates = [tm.transform_date(date) for date in dates]
    return cleaned_dates


def extract_place_of_residences(text: str):
    data = []

    # Extract only the places of residence from the full text
    text = extract_between_keywords(text, "upload it again.", "Have you")

    # Extracts dates, place and location
    dates = extract_between_keywords(text, "Date from", "Address")
    dates = find_all_dates(dates)
    place = extract_between_keywords(text, "Place", "Country")
    location = extract_between_keywords(text, "Country", "Date from")

    # Cleaning data
    cleaned_dates = []
    for date in dates:
        cleaned_dates.append(tm.transform_date(date))
    cleaned_place = tm.clean_text(place)
    cleaned_location = tm.clean_text(location)

    # Sorts dates in list
    dates = [datetime.strptime(date, "%d-%m-%Y") for date in cleaned_dates]
    sorted_dates = sorted(dates)

    # Add cleaned_data to list
    [data.append(date.strftime("%d-%m-%Y")) for date in sorted_dates]
    data.append(cleaned_place)
    data.append(cleaned_location)

    return data
