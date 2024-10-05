import re
import os
from pytesseract import image_to_string
from pdf2image import convert_from_bytes
from extractors.methods import transform_methods as tm


# TODO split up this function into smaller ones
def file_to_raw_data(pdf_bytes: str) -> str:
    """Locate the file and convert it to string, and save it as raw data"""
    doc = convert_from_bytes(pdf_bytes)
    path, file_name = os.path.split(pdf_bytes)
    file_base_name, file_extension = os.path.splitext(file_name)
    text = ""
    # Convert doc to string with OCR, since users often upload a img of the original pdf.
    # Psm 12 extracts the data better, but takes more time
    for page_number, page_data in enumerate(doc):
        text += image_to_string(page_data, config="--psm 12")
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
    if (start_index == -1 or end_index == -1) or end_index < start_index:
        return None
    return text[start_index + len(start_keyword) : end_index]


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
    strings = extract_between_keywords(text, start_keyword, end_keyword)
    if not strings:
        return None
    strings = strings.split(split_keyword)
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
    extracted_data = extract_between_keywords(string, start_keyword, end_keyword)
    if not extracted_data:
        return None
    extracted_data = find_all_dates(extracted_data)
    extracted_data = [tm.transform_date(date) for date in extracted_data]
    return extracted_data
