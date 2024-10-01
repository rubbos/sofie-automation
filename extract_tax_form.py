from pdf2image import convert_from_path
import pytesseract
import os
import time
from methods import extract_methods as em
from methods import transform_methods as tm

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

full_name = em.extract_string(text, "Initials", "Has agreed")
arrival_date = em.extract_dates(text, "Date of arrival", "My address")
working_date = em.extract_dates(text, "working day", "Place")
place_date = em.extract_dates(text, "Date from", "Have you")

location_dict = {1: ["upload it again", "Have you"], 2: ["Place", "Date"]}
place_location = em.extract_nested_string(text, location_dict)
place_location = tm.clean_locations(place_date, place_location)

# Temp cleaning
place_location = [item.replace(":", "") for item in place_location]
place_location = [item.replace("Country", "") for item in place_location]
place_location = [" ".join(item.split()) for item in place_location]


nl_lived_date = em.extract_dates(text, "in the Netherlands?", "Were you registered")
nl_deregister_date = em.extract_dates(text, "deregister", "Have you previously worked")
nl_worked_date = em.extract_dates(text, "Have you previously worked", "private")
nl_private_date = em.extract_dates(text, "holiday", "outside")
nl_worked_outside_date = em.extract_dates(text, "outside", "undersigned")


signature_name = em.extract_string(text, "Name:", "Date")
signature_date = em.extract_dates(text, "undersigned", "Signature")

tax_form = {
    "Full name": full_name,
    "Arrival date": arrival_date,
    "First working date": working_date,
    "Places of residence dates": place_date,
    "Places of residence locations": place_location,
    "Residence in NL dates": nl_lived_date,
    "Deregister NL date": nl_deregister_date,
    "Worked in NL dates": nl_worked_date,
    "Private reasons NL dates": nl_private_date,
    "Worked for dutch employer outside NL dates": nl_worked_outside_date,
    "Signature name": signature_name,
    "Signature date": signature_date,
}

# print data
for item in tax_form.items():
    print(item)

# Runtime
print("--- %s seconds ---" % (time.time() - start_time))
