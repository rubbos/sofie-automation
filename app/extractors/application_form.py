import pandas as pd
from extractors.methods import extract_methods as em
from extractors.methods import transform_methods as tm
from utils.validation import validate_uni


def get_raw_data(pdf_path) -> str:
    return em.file_to_raw_data(pdf_path, 4)


def extract(text: str) -> dict:
    type_string = "str"
    type_date = "date"
    
    extracted_data = {
        "Naam werkgever": [
            type_string,
            em.extract_between_keywords(text, "Name of employer", "\n"),
            "employer",
        ],
        "Loonheffingsnummer": [
            type_string,
            em.extract_between_keywords(text, "LH number", "\n"),
            "lhn",
        ],
        "Publiek/Privaat universiteit": [type_string, "None", "employer_type"],
        "Geboortedatum": [
            type_date,
            em.extract_dates(text, "Birth", "\n"),
            "date_of_birth",
        ],
        "BSN": [
            type_string,
            em.extract_between_keywords(text, "BSN Number", "\n"),
            "bsn",
        ],
        "Functietitel": [
            type_string,
            em.extract_between_keywords(text, "Title", "\n"),
            "job_title",
        ],
        "Startdatum arbeidsovereenkomst": [
            type_date,
            em.extract_dates(text, "into service", "\n"),
            "ao_start_date",
        ],
        "UFO code": [
            type_string,
            em.extract_between_keywords(text, "UFO code", "\n"),
            "ufo_code",
        ],
        "SOFIE Aanvraagdatum": [
            type_date,
            em.extract_dates(text, "Created at", "by"),
            "application_date",
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


def validate(transformed_data):
    transformed_data = validate_uni(transformed_data)  # validates uni, lhn and uni type
    return transformed_data


def main(raw_data, dev_mode=False) -> pd.DataFrame:
    if not dev_mode:
        raw_data = get_raw_data(raw_data)
        em.save_text(raw_data, "application_form")
    extracted_data = extract(raw_data)
    transformed_data = transform(extracted_data)
    clean_data = validate(transformed_data)
    return clean_data
