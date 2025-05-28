import re
from utils import transform_methods as tm
from datetime import datetime

def extract_after_keyword(text: str, start_keyword: str) -> str | None:
    """Extract string after keyword till end of text"""
    start_index = text.find(start_keyword)
    if start_index == -1:
        return None
    return text[start_index + len(start_keyword) :]


def extract_between_keywords(
    text: str, start_keyword: str, end_keyword: str, clean=False) -> str | None:
    """Extract string between 2 keywords, and clean the text if needed"""
    start_index = text.find(start_keyword)
    end_index = text.find(end_keyword, start_index + len(start_keyword))
    
    # Check if the keywords are found and in the correct order
    if start_index == -1 or end_index == -1 or end_index < start_index:
        return None

    string = text[start_index + len(start_keyword) : end_index]

    # Clean the string if the clean flag is set
    if clean:
        string = tm.clean_text(string)

    return string


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
    date_pattern = r"(?i)\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|\b\d{1,2}(?:[-\s])?(?:Jan|Feb|Mar|Mrt|Apr|May|Mei|Jun|Jul|Aug|Sep|Oct|Okt|Nov|Dec|January|February|March|Maart|April|May|Mei|June|Juni|July|Juli|August|Augustus|September|October|Oktober|November|December)(?:[-\s])?\d{2,4}\b"
    pattern = re.compile(date_pattern)
    matches = pattern.findall(text)
    return matches

def extract_date(string: str, start_keyword: str, end_keyword: str, single_date=False) -> list[str] | str | None:
    """Extract all dates in string and transform to dd-mm-yyyy"""
    text = extract_between_keywords(string, start_keyword, end_keyword)
    if not text:
        return None
    dates = find_all_dates(text)
    cleaned_dates = [tm.transform_date(date) for date in dates]

    # Return as a string if its only one date
    if single_date: 
        if cleaned_dates:
            return cleaned_dates[0]
        return None
    return cleaned_dates

def extract_multiple_dates(string: str, start_keyword: str, end_keyword: str) -> list[str]:
    """Extract all dates and transform to dd-mm-yyyy and pair them together"""
    extracted_dates = extract_date(string, start_keyword, end_keyword)
    
    # If no dates are found, return None
    if not extracted_dates or extracted_dates == [[]]:
        return None

    # Only return paired dates
    pairs = []    
    for i in range(0, len(extracted_dates), 2):
        if i + 1 < len(extracted_dates):
            pairs.append([extracted_dates[i], extracted_dates[i + 1]])

    return pairs if pairs else None

def extract_place_of_residences(text: str):
    """Extract the complete data of places and dates from user and return it in a list"""
    all_data = []

    # Extract only the places of residence section from the full text
    text_section = extract_between_keywords(text, "Date from", "Have you")
    if not text_section:
        return all_data

    # Split by "Date from" except for the first section
    residence_sections = text_section.split("Date from")

    # Loop through each section after the first entry point
    for i, section in enumerate(residence_sections):
        data = []

        # If it's the first entry, we don't need "Date from" prepended
        if i == 0:
            dates_text = section
        else:
            dates_text = "Date from" + section

        # Extract dates, place, and location for each residence block
        dates = find_all_dates(dates_text) if dates_text else []
        place = extract_between_keywords(section, "Place", "Country") or ""
        location = extract_after_keyword(section, "Country") or ""

        # Clean and process data:
        cleaned_dates = [tm.transform_date(date) for date in dates if date]
        cleaned_place = tm.clean_text(place)
        cleaned_location = tm.clean_text(location)

        # Sort dates and remove the last date if odd number of dates
        if len(cleaned_dates) % 2 != 0:
            cleaned_dates = cleaned_dates[:-1]  
        sorted_dates = sorted(cleaned_dates)

        # Add cleaned data to list for this residence section
        data.extend(date for date in sorted_dates)
        data.append(cleaned_place)
        data.append(cleaned_location)

        # Append this residence's data to the main list if it's not empty
        if data:
            all_data.append(data)

    return all_data
