from pdf2image import convert_from_path
import easyocr
import os

# Convert PDF pages to images
pages = convert_from_path("../pdf_examples/sofie_form_5.pdf", dpi=300)

# Initialize EasyOCR
reader = easyocr.Reader(["en"], gpu=False)

# Create a folder to save images if it doesn't exist
os.makedirs("pdf_images", exist_ok=True)

# Example of processing one page at a time
for page_num, page in enumerate(pages):
    # Save the page as an image file
    image_path = f"pdf_images/page_{page_num + 1}.jpg"
    page.save(image_path, "JPEG")

    # Use EasyOCR to extract text from the saved image file
    results = reader.readtext(image_path)

    print(f"Page {page_num + 1}")
    for result in results:
        print(result[1])  # result[1] contains the recognized text

    # Optionally, delete the image file after processing to save memory
    os.remove(image_path)
