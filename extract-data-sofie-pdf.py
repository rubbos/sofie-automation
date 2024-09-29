from pdf2image import convert_from_path
from datetime import datetime
import pytesseract
import os
import re
import time

# Calc runtime
start_time = time.time()

# Load file
file_path = "pdf_examples/sofie_form_date.pdf"
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

    # Cleanup the string for easier extracting
    text = text.replace("\n", " ")

    # Save string to .txt for testing purposes
    with open(f"{path}/extracted_{file_base_name}.txt", "w") as text_file:
        text_file.write(text)

# If file exists, skip the pytesseract to speedup testing
else:
    with open(f"{path}/extracted_{file_base_name}.txt", "r") as text_file:
        text = text_file.read()


# Extract the data between 2 keywords if it exists
def extract_text_between_keywords(text, start_keyword, end_keyword):
    try:
        start_index = text.index(start_keyword) + len(start_keyword)
        end_index = text.find(end_keyword, start_index)
    except ValueError:
        return None

    return text[start_index:end_index].strip()


def extract_multiple_text_between_keywords(text, start_keyword, end_keyword):
    pattern = rf"{re.escape(start_keyword)}(.*?){re.escape(end_keyword)}"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


# Testing purpose
def check_if_found(extracted_data, start_keyword):
    if extracted_data:
        print(f"Found keyword '{start_keyword}': {extracted_data}")
    else:
        print(f"Keyword {start_keyword} not found")


def find_date(text):
    date_pattern = r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|\b\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-\s]\d{2,4}\b|\b\d{1,2}[-\s](?:January|February|March|April|May|June|July|August|September|October|November|December)[-\s]\d{2,4}\b"
    pattern = re.compile(date_pattern)
    matches = pattern.findall(text)
    return matches


# Function to convert date formats to dd-mm-yyyy
def transform_date(date):
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
    # If no format matched, return original string
    return date


# Extract name from initials
keyword_name = "Initials"
initials_name = extract_text_between_keywords(text, keyword_name, "Has agreed")
check_if_found(initials_name, keyword_name)

# Extract name from signature
keyword_signature_name = "Name:"
signature_name = extract_text_between_keywords(text, keyword_signature_name, "Date")
check_if_found(signature_name, keyword_signature_name)

# Extract arrival date
keyword_arrival_date = "Date of arrival"
arrival_date = extract_text_between_keywords(text, keyword_arrival_date, "My address")
arrival_date = find_date(arrival_date)
arrival_date = [transform_date(date) for date in arrival_date]
check_if_found(arrival_date, keyword_arrival_date)

# Extract first working date
keyword_working_date = "working day"
working_date = extract_text_between_keywords(text, keyword_working_date, "Place")
working_date = find_date(working_date)
working_date = [transform_date(date) for date in working_date]
check_if_found(working_date, keyword_working_date)

# Extract place date(s)
keyword_place_date = "Date from"
place_date = extract_text_between_keywords(text, keyword_place_date, "Have you")
place_date = find_date(place_date)
place_date = [transform_date(date) for date in place_date]
check_if_found(place_date, keyword_place_date)

# Extract location(s)
keyword_place_location = "upload it again"
keyword_place_location_specified = "Place:"
place_location = extract_text_between_keywords(text, keyword_place_location, "Have you")

place_location = place_location.replace(" ", "")
place_location = place_location.replace(":", "")
place_location = place_location.replace("Country", ", ")

place_location = extract_multiple_text_between_keywords(place_location, "Place", "Date")

check_if_found(place_location, keyword_place_location)

# Runtime
print("--- %s seconds ---" % (time.time() - start_time))
