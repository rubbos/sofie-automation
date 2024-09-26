from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import cv2
import os
import spacy

file_path = 'testpdf/sofie_form.pdf'
doc = convert_from_path(file_path)
path, file_name = os.path.split(file_path)
file_base_name, file_extension = os.path.splitext(file_name)

txt = ''
for page_number, page_data in enumerate(doc):
    txt += pytesseract.image_to_string(page_data)

nlp = spacy.load('en_core_web_sm')
doc = nlp(txt)

# refactor this bs

def extract_text_between_keywords(txt, start_keyword, end_keyword=None):
    if start_keyword in txt:
        start_index = txt.index(start_keyword) + len(start_keyword)
        
        # Find the next newline
        end_index_newline = txt.find('\n', start_index)
        
        if end_keyword:
            # Find the specified end keyword
            end_index_keyword = txt.find(end_keyword, start_index)
            
            # Determine the smaller index to stop at: newline or end keyword
            if end_index_keyword != -1:
                end_index = min(end_index_newline, end_index_keyword)
            else:
                end_index = end_index_newline
        else:
            end_index = end_index_newline
        
        # Capture text up to the determined end index
        return txt[start_index:end_index].strip() if end_index != -1 else None
    return None

# Extract initials
initials_text = extract_text_between_keywords(txt, "Initials")
if initials_text:
    print("Found initials:", initials_text)
else:
    print("Keyword 'Initials' not found in the text.")

# Extract name until "Date: "
signature_name = extract_text_between_keywords(txt, "Name: ", "Date: ")
if signature_name:
    print(f"Found signature name: {signature_name}")
else:
    print("Keyword 'Name:' not found in the text.")
