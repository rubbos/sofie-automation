from pdf2image import convert_from_path
import pytesseract
import os
import re

# Load one file
file_path = "testpdf/sofie_form2.pdf"
doc = convert_from_path(file_path)
path, file_name = os.path.split(file_path)
file_base_name, file_extension = os.path.splitext(file_name)

# Convert doc to string
text = ""
for page_number, page_data in enumerate(doc):
    text += pytesseract.image_to_string(page_data)


def extract_text_between_keywords(
    text, start_keyword, end_keyword=None, max_length=100
):
    # Get the start_index of the provided start_keyword
    try:
        start_index = text.index(start_keyword) + len(start_keyword)
    except ValueError:
        return None

    # Find the end_index of the start_keyword
    end_index = text.find("\n", start_index)
    if end_index == -1:
        end_index = min(start_index + max_length, len(text))

    # If end_keyword is provided, adjust end_index
    if end_keyword:
        end_keyword_index = text.find(end_keyword, start_index)
        if end_keyword_index != -1:
            end_index = min(end_index, end_keyword_index)

    return text[start_index:end_index].strip()


# Check for date pattern dd/mm/yyyy, dd-mm-yyyy or dd.mm.yyyy
date_pattern = r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$"


def extract_date_after_keyword(text, keyword):
    # Find the position of the keyword
    keyword_position = text.find(keyword)
    if keyword_position == -1:
        return None  # Keyword not found

    # First, look for dates using regular expressions after the keyword
    matches = re.finditer(date_pattern, text)
    for match in matches:
        if match.start() > keyword_position:
            return match.group()  # Return the first matching date

    return None  # No date found after the keyword


def check_if_found(extracted_data, start_keyword):
    if extracted_data:
        print(f"Found keyword '{start_keyword}': {extracted_data}")
    else:
        print(f"Keyword {start_keyword} not found")


# Extract name from initials
keyword_name = "Initials"
initials_name = extract_text_between_keywords(text, keyword_name)
check_if_found(initials_name, keyword_name)

# Extract name from signature
keyword_signature_name = "Name: "
signature_name = extract_text_between_keywords(text, keyword_signature_name, "Date: ")
check_if_found(signature_name, keyword_signature_name)

# Extract arrival date
keyword_arrival_date = "Date of arrival in the Netherlands:"
arrival_date = extract_date_after_keyword(text, keyword_arrival_date)
check_if_found(arrival_date, keyword_arrival_date)
