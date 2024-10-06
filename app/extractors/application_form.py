import pandas as pd
from extractors.methods import extract_methods as em
from extractors.methods import transform_methods as tm


def get_raw_data(pdf_path) -> str:
    return em.file_to_raw_data(pdf_path, 4)


def extract(text: str) -> dict:
    type_data = ["str", "list[str]", "date", "list[date]"]
    yes_no = ["Yes", "No"]

    extracted_data = {
        "Name employer": [
            type_data[0],
            em.extract_between_keywords(text, "Name of employer", "\n"),
        ],
        "Loonheffing number": [
            type_data[0],
            em.extract_between_keywords(text, "LH number", "\n"),
        ],
        "Last name, Initials": [
            type_data[0],
            em.extract_between_keywords(text, "Initials", "\n"),
        ],
        "Date of birth": [
            type_data[2],
            em.extract_dates(text, "Birth", "\n"),
        ],
        "BSN number": [
            type_data[0],
            em.extract_between_keywords(text, "BSN Number", "\n"),
        ],
        "Job title": [
            type_data[0],
            em.extract_between_keywords(text, "Job Title", "\n"),
        ],
        "Date of entry into service": [
            type_data[2],
            em.extract_dates(text, "into service", "\n"),
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
            em.extract_between_keywords(text, "UFO code", "\n"),
        ],
        "Application tax": [
            type_data[0],
            em.extract_specific_words(
                text, "Did employer and employee", "Note", yes_no
            ),
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


def main(pdf_path, dev_mode=False) -> pd.DataFrame:
    if dev_mode:
        extracted_data = extract(pdf_path)
        clean_data = transform(extracted_data)
        return clean_data
    raw_data = get_raw_data(pdf_path)
    em.save_text(raw_data, "application_form")
    extracted_data = extract(raw_data)
    clean_data = transform(extracted_data)
    return clean_data


if __name__ == "__main__":
    main()
