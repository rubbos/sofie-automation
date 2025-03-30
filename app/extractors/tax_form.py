import pandas as pd
from extractors.methods import extract_methods as em
from extractors.methods import transform_methods as tm


def get_raw_data(pdf_path) -> str:
    return em.file_to_raw_data(pdf_path, 11)


def extract(text: str) -> dict:
    type_data = ["str", "list[str]", "date", "list[date]"]

    extracted_data = {
        "Aanvraag type": [type_data[0], "", "application_type"],
        "Naam": [
            type_data[0],
            em.extract_between_keywords(text, "Initials", "Has agreed"),
            "full_name",
        ],
        "Aankomstdatum in Nederland": [
            type_data[2],
            em.extract_dates(text, "Date of arrival", "My address"),
            "arrival_date",
        ],
        "Eerste werkdag in Nederland": [
            type_data[2],
            em.extract_dates(text, "working day", "Place"),
            "first_work_date",
        ],
        "Recente woonplaats(en)": [
            type_data[1],
            em.extract_place_of_residences(text),
            "place_of_residence",
        ],
        "Alle periodes in Nederland": [
            type_data[3],
            em.extract_dates(text, "in the Netherlands?", "Were you registered"),
            "nl_residence_dates",
        ],
        "Uitschrijvingsdatum Nederland": [
            type_data[2],
            em.extract_dates(text, "deregister", "Have you"),
            "nl_deregister_date",
        ],
        "Periodes gewerkt in Nederland": [
            type_data[3],
            em.extract_dates(text, "Have you previously worked", "private"),
            "nl_worked_dates",
        ],
        "Periodes privezaken in Nederland": [
            type_data[3],
            em.extract_dates(text, "holiday", "outside"),
            "nl_private_visit_dates",
        ],
        "Periodes gewerkt voor een Nederlandse werkgever": [
            type_data[3],
            em.extract_dates(text, "outside", "undersigned"),
            "nl_worked_dutch_employer_dates",
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

    # Clean locations and group
    try:
        df.at[5, "VALUE"] = [item.replace("Country:", "") for item in df.at[5, "VALUE"]]
        df.at[5, "VALUE"] = [item.replace("  ", " ") for item in df.at[5, "VALUE"]]
        df.at[5, "VALUE"] = [item.replace(":", "") for item in df.at[5, "VALUE"]]
        df.at[5, "VALUE"] = [item.lstrip() for item in df.at[5, "VALUE"]]
        df.at[5, "VALUE"] = [item for item in df.at[5, "VALUE"] if item]
    except TypeError:
        pass

    return df


def main(raw_data, dev_mode=False) -> pd.DataFrame:
    if not dev_mode:
        raw_data = get_raw_data(raw_data)
        em.save_text(raw_data, "tax_form")
    extracted_data = extract(raw_data)
    clean_data = transform(extracted_data)
    return clean_data
