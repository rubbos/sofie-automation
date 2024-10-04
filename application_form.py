import time
import pandas as pd
from methods import extract_methods as em
from methods import transform_methods as tm


# TODO Change parsing to something more efficient since its always a pdf
def get_raw_data() -> str:
    files = [0]
    file_path = f"pdf_examples/Oorspronkelijke aanvraag {files[0]}.pdf"
    return em.file_to_raw_data(file_path)


def extract(text: str) -> dict:
    type_data = ["str", "list[str]", "date", "list[date]"]
    yes_no = ["Yes", "No"]

    extracted_data = {
        "Name employer": [
            type_data[0],
            em.extract_between_keywords(text, "Name of employer", "LH number"),
        ],
        "Loonheffing number": [
            type_data[0],
            em.extract_between_keywords(text, "LH number", "Employee"),
        ],
        "Last name, Initials": [
            type_data[0],
            em.extract_between_keywords(text, "Initials", "Date"),
        ],
        "Date of birth": [
            type_data[2],
            em.extract_dates(text, "Birth", "BSN"),
        ],
        "BSN number": [
            type_data[0],
            em.extract_between_keywords(text, "BSN Number", "Job"),
        ],
        "Job title": [
            type_data[0],
            em.extract_between_keywords(text, "Job Title", "Date of entry"),
        ],
        "Date of entry into service": [
            type_data[2],
            em.extract_dates(text, "into service", "PDF"),
        ],
        "Returning expat": [
            type_data[0],
            em.extract_specific_words(text, "Expat", "employment?", yes_no),
        ],
        "Changing Dutch employer": [
            type_data[0],
            em.extract_specific_words(text, "employee eligible for", "the 30%", yes_no),
        ],
        "Contract signed outside NL": [
            type_data[0],
            em.extract_specific_words(
                text, "Was the employee living outside", "the Netherlands", yes_no
            ),
        ],
        "16/24 Months outside NL": [
            type_data[0],
            em.extract_specific_words(
                text, "employee living outside", "the Netherlands", yes_no
            ),
        ],
        "Promovendus exception": [
            type_data[0],
            em.extract_specific_words(
                text, "Did the employee live or stay", "PhD", yes_no
            ),
        ],
        "UFO 01 type": [
            type_data[0],
            em.extract_specific_words(text, "Specific Expertise", "UFO", yes_no),
        ],
        "UFO code": [
            type_data[0],
            em.extract_between_keywords(text, "UFO code", "Upload"),
        ],
        "Application tax": [
            type_data[0],
            em.extract_specific_words(text, "to employment contract", "Note", yes_no),
        ],
        "Agreement": [
            type_data[0],
            em.extract_specific_words(
                text, "On behalf of the employer", "confirm that", yes_no
            ),
        ],
    }

    return extracted_data


def transform(extracted_data: dict) -> pd.DataFrame:
    df = tm.dict_to_table(extracted_data)

    # Clean excess \n where type str
    df.loc[df["TYPE"] == "str", "VALUE"] = df.loc[df["TYPE"] == "str", "VALUE"].replace(
        "\n", "", regex=True
    )

    # Clean list to string where type date
    df.loc[df["TYPE"] == "date", "VALUE"] = df.loc[df["TYPE"] == "date", "VALUE"].apply(
        lambda x: x[0] if x else None
    )
    return df


def load(transformed_data: dict) -> None:
    print(transformed_data)


def main() -> None:
    start_time = time.time()

    raw_data = get_raw_data()
    extracted_data = extract(raw_data)
    clean_data = transform(extracted_data)
    load(clean_data)

    print("--- %s seconds ---" % round(time.time() - start_time, 2))


if __name__ == "__main__":
    main()
