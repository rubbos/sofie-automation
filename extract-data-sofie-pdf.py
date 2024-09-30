from pdf2image import convert_from_path
from datetime import datetime
import pytesseract
import os
import re
import time

# Calc runtime
start_time = time.time()

file = ["clean", "img", "date"]
file_path = f"pdf_examples/sofie_form_{file[2]}.pdf"
doc = convert_from_path(file_path)
path, file_name = os.path.split(file_path)
file_base_name, file_extension = os.path.splitext(file_name)

# Check if file is extracted already to speedup testing
if not os.path.isfile(f"{path}/extracted_{file_base_name}.txt"):
    # Convert to string with OCR.
    # Not using OpenCV because user can fill the document by hand and make pictures of it.
    text = ""
    for page_number, page_data in enumerate(doc):
        # Psm 12 extracts the data better, but takes more time than others
        text += pytesseract.image_to_string(page_data, config="--psm 12")

    text = text.replace("\n", " ")

    # Save string to .txt for testing purposes
    with open(f"{path}/extracted_{file_base_name}.txt", "w") as text_file:
        text_file.write(text)

# If file exists, skip the pytesseract to speedup testing
else:
    with open(f"{path}/extracted_{file_base_name}.txt", "r") as text_file:
        text = text_file.read()


def extract_between_keywords(text, start_keyword, end_keyword, find_all=False):
    """Extract data between 2 keywords in a string"""
    results = []
    start = 0

    while True:
        start_index = text.find(start_keyword, start)
        if start_index == -1:
            break

        end_index = text.find(end_keyword, start_index + len(start_keyword))
        if end_index == -1:
            substring = text[start_index + len(start_keyword) :]
            results.append(substring.strip())
            break

        if end_index > start_index:
            substring = text[start_index + len(start_keyword) : end_index]
            results.append(substring.strip())

        if not find_all:
            return " ".join(results)

        start = end_index + len(end_keyword)
    return results


def check_if_found(extracted_data, start_keyword):
    """Testing purpose"""
    if extracted_data:
        print(f"Found keyword '{start_keyword}': {extracted_data}")
    else:
        print(f"Keyword {start_keyword} not found")


def find_date(text):
    """Find any kind of dates formats in a string"""
    date_pattern = r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|\b\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-\s]\d{2,4}\b|\b\d{1,2}[-\s](?:January|February|March|April|May|June|July|August|September|October|November|December)[-\s]\d{2,4}\b"
    pattern = re.compile(date_pattern)
    matches = pattern.findall(text)
    return matches


def transform_date(date):
    """Convert different date formats into dd-mm-yyyy"""
    date_formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d-%b-%Y",
        "%d %b %Y",
        "%d-%B-%Y",
        "%d %B %Y",
        "%d-%b-%y",
        "%d %b %y",
        "%d-%m-%y",
        "%d/%m/%y",
        "%d.%m.%y",
    ]

    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date, date_format)
            return parsed_date.strftime("%d-%m-%Y")
        except ValueError:
            pass
    return date


def clean_locations(dates, locations):
    """
    Every location has a start date and end date.
    This cleans up the excess locations list.
    """
    if len(dates) % 2 == 0:
        if len(dates) <= 2:
            return locations[:1]
        return locations[: -len(dates) // 2]


def extract_string(string, start_keyword, end_keyword):
    extracted_data = extract_between_keywords(string, start_keyword, end_keyword)
    check_if_found(extracted_data, start_keyword)
    return extracted_data


def extract_nested_string(string, keywords_dict):
    keywords = keywords_dict.values()
    for keyword in keywords:
        if keyword == list(keywords)[-1]:
            string = extract_between_keywords(
                str(string), keyword[0], keyword[1], find_all=True
            )
        else:
            string = extract_between_keywords(str(string), keyword[0], keyword[1])
    check_if_found(string, list(keywords)[0])
    return string


def extract_dates(string, start_keyword, end_keyword):
    extracted_data = extract_between_keywords(string, start_keyword, end_keyword)
    extracted_data = find_date(extracted_data)
    extracted_data = [transform_date(date) for date in extracted_data]
    check_if_found(extracted_data, start_keyword)
    return extracted_data


full_name = extract_string(text, "Initials", "Has agreed")
signature_name = extract_string(text, "Name:", "Date")
arrival_date = extract_dates(text, "Date of arrival", "My address")
working_date = extract_dates(text, "working day", "Place")
place_date = extract_dates(text, "Date from", "Have you")

location_dict = {1: ["upload it again", "Have you"], 2: ["Place", "Date"]}
place_location = extract_nested_string(text, location_dict)
place_location = clean_locations(place_date, place_location)

# Temp cleaning
place_location = [item.replace(":", "") for item in place_location]
place_location = [item.replace("Country", "") for item in place_location]
place_location = [" ".join(item.split()) for item in place_location]
check_if_found(place_location, "test")


def cleaning_data():
    pass


# Runtime
print("--- %s seconds ---" % (time.time() - start_time))
