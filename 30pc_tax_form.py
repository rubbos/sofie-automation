import time
from methods import extract_methods as em
from methods import transform_methods as tm


def get_raw_data() -> str:
    files = ["clean", "img", "date"]
    file_path = f"pdf_examples/sofie_form_{files[2]}.pdf"
    return em.file_to_raw_data(file_path)


def extract(text: str) -> dict:
    extracted_data = {
        "Full name": em.extract_between_keywords(text, "Initials", "Has agreed"),
        "Arrival date": em.extract_dates(text, "Date of arrival", "My address"),
        "First working date": em.extract_dates(text, "working day", "Place"),
        "Places of residence dates": em.extract_dates(text, "Date from", "Have you"),
        "Places of residence locations": em.extract_multiple_between_keywords(
            text, "upload it again.", "Have you", "Date from", "Place"
        ),
        "Residence in NL dates": em.extract_dates(
            text, "in the Netherlands?", "Were you registered"
        ),
        "Deregister NL date": em.extract_dates(text, "deregister", "Have you"),
        "Worked in NL dates": em.extract_dates(
            text, "Have you previously worked", "private"
        ),
        "Private reasons NL dates": em.extract_dates(text, "holiday", "outside"),
        "Dutch employer outside NL dates": em.extract_dates(
            text, "outside", "undersigned"
        ),
        "Signature name": em.extract_between_keywords(text, "Name:", "Date"),
        "Signature date": em.extract_dates(text, "undersigned", "Signature"),
    }

    # print data
    for item in extracted_data.items():
        print(item)

    return extracted_data


def transform(): ...


def load(): ...


def main() -> None:
    raw_data = get_raw_data()
    extracted_data = extract(raw_data)
    clean_data = transform(extracted_data)
    load(clean_data)


if __name__ == "__main__":
    # Calc runtime
    start_time = time.time()

    main()

    print("--- %s seconds ---" % round(time.time() - start_time, 2))
