import time
import pandas as pd
from methods import extract_methods as em
from methods import transform_methods as tm


def get_raw_data() -> str:
    files = ["clean", "img", "date", "4", "5"]
    file_path = f"pdf_examples/sofie_form_{files[4]}.pdf"
    return em.file_to_raw_data(file_path)


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

    # TODO fix this garbage
    # Make new df with all list[date] to transform to amount of months:
    df_list_dates = df[(df["TYPE"] == "list[date]")]
    df_list_dates = df_list_dates.dropna(subset="VALUE")

    for row_index, row in df_list_dates.iterrows():
        durations = []
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

        print(durations)
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
