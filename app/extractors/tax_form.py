import pandas as pd
from extractors.methods import extract_methods as em
from extractors.methods import transform_methods as tm


def get_raw_data(pdf_path) -> str:
    return em.file_to_raw_data(pdf_path, 11)


def extract(text: str) -> dict:
    type_data = ["str", "list[str]", "date", "list[date]"]

    extracted_data = {
        "Full name": [
            type_data[0],
            em.extract_between_keywords(text, "Initials", "Has agreed"),
        ],
        "Arrival date": [
            type_data[2],
            em.extract_dates(text, "Date of arrival", "My address"),
        ],
        "Start work date": [
            type_data[2],
            em.extract_dates(text, "working day", "Place"),
        ],
        "Residence dates": [
            type_data[3],
            em.extract_dates(text, "Date from", "Have you"),
        ],
        "Residence locations": [
            type_data[1],
            em.extract_multiple_between_keywords(
                text, "upload it again.", "Have you", "Date from", "Place"
            ),
        ],
        "NL lived dates": [
            type_data[3],
            em.extract_dates(text, "in the Netherlands?", "Were you registered"),
        ],
        "NL deregister date": [
            type_data[2],
            em.extract_dates(text, "deregister", "Have you"),
        ],
        "NL worked dates": [
            type_data[3],
            em.extract_dates(text, "Have you previously worked", "private"),
        ],
        "NL private dates": [
            type_data[3],
            em.extract_dates(text, "holiday", "outside"),
        ],
        "NL dutch employer dates": [
            type_data[3],
            em.extract_dates(text, "outside", "undersigned"),
        ],
        "Signature name": [
            type_data[0],
            em.extract_between_keywords(text, "Name:", "Date"),
        ],
        "Signature date": [
            type_data[2],
            em.extract_dates(text, "undersigned", "Signature"),
        ],
        "Signature": [
            type_data[0],
            em.extract_after_keyword(text, "Signature:"),
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
        df.at[4, "VALUE"] = [item.replace("Country:", "") for item in df.at[4, "VALUE"]]
        df.at[4, "VALUE"] = [item.replace("  ", " ") for item in df.at[4, "VALUE"]]
        df.at[4, "VALUE"] = [item.replace(":", "") for item in df.at[4, "VALUE"]]
        df.at[4, "VALUE"] = [item.lstrip() for item in df.at[4, "VALUE"]]
        df.at[4, "VALUE"] = [item for item in df.at[4, "VALUE"] if item]
    except TypeError:
        pass

    # Make new df with all list[date] to transform to amount of months:
    df_list_dates = df[(df["TYPE"] == "list[date]")]
    df_list_dates = df_list_dates.dropna(subset="VALUE")

    # Get all rows with list[date]
    durations = []
    for row_index, row in df_list_dates.iterrows():
        # Get all the values from the list[date]
        for index, date in enumerate(row["VALUE"]):
            if index % 2 == 0:
                first_date = date
            else:
                last_date = date
                if row_index == 3:
                    durations.append(
                        df.at[4, "VALUE"][index // 2]
                        + " "
                        + tm.months_and_days_between_dates(first_date, last_date, False)
                    )
                else:
                    durations.append(
                        tm.months_and_days_between_dates(first_date, last_date)
                    )
    df2 = pd.DataFrame(durations, columns=["Values"])
    return df, df2


def main(raw_data, dev_mode=False) -> pd.DataFrame:
    if not dev_mode:
        raw_data = get_raw_data(raw_data)
        em.save_text(raw_data, "tax_form")
    extracted_data = extract(raw_data)
    clean_data = transform(extracted_data)
    return clean_data


if __name__ == "__main__":
    main()
