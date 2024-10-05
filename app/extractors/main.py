from .tax_form import main as extract_from_file1
from .application_form import main as extract_from_file2


def extract_data_from_pdf(pdf_bytes, method):
    if method == "file1":
        return extract_from_file1(pdf_bytes)
    elif method == "file2":
        return extract_from_file2(pdf_bytes)
    else:
        raise ValueError("Invalid method. Choose either 'file1' or 'file2'.")
