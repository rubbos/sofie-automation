import pandas as pd
from extractors.methods import extract_methods as em
from extractors.methods import transform_methods as tm

def get_raw_data(pdf_path) -> str:
    return em.file_to_raw_data(pdf_path, 11)

def extract_specific_data(sofie_raw_data, topdesk_raw_data) -> dict:
    request_type = ""
    name = em.extract_between_keywords(sofie_raw_data, "Initials", "Has agreed")
    arrival_date = em.extract_dates(sofie_raw_data, "Date of arrival", "My address")
    first_work_date = em.extract_dates(sofie_raw_data, "working day", "Place")
    places_of_residence = em.extract_place_of_residences(sofie_raw_data)
    nl_residence_dates = em.extract_multiple_dates(sofie_raw_data, "Have you previously", "Were you registered")
    nl_deregister_date = em.extract_dates(sofie_raw_data, "deregister", "Have you")
    nl_worked_dates = em.extract_multiple_dates(sofie_raw_data, "Have you previously worked", "private")
    nl_private_dates = em.extract_multiple_dates(sofie_raw_data, "holiday", "outside")
    nl_dutch_employer_dates= em.extract_multiple_dates(sofie_raw_data, "outside", "undersigned")

    print("NL RESIDENCE DATES", nl_residence_dates)
    print("NL DEREGISTER DATE", nl_deregister_date)
    print("NL PRIVATE DATES", nl_private_dates)         
    print("NL DUTCH EMPLOYER DATES", nl_dutch_employer_dates)
    print("NL WORKED DATES", nl_worked_dates)
    return []


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


def extract(sofie_data, topdesk_data, dev_mode=False) -> dict:
    if not dev_mode:
        sofie_raw_data = get_raw_data(sofie_data)
        topdesk_raw_data = get_raw_data(topdesk_data)
        em.save_text(topdesk_data, "sofie_data")
        em.save_text(topdesk_data, "topdesk_data")
    extracted_data = extract_specific_data(sofie_raw_data, topdesk_raw_data)
    return extracted_data

