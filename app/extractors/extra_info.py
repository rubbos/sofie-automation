import pandas as pd
from extractors.methods import transform_methods as tm


def empty_info():
    type_data = ["str", "list[str]", "date", "list[date]"]

    extracted_data = {
        "Arbeidsovereenkomst datum getekend": [
            type_data[2],
            "01-01-2024",
            "ao_signed_date",
        ],
        "Wilsovereenkomst datum getekend": [type_data[2], "", "wo_signed_date"],
        "De wilsovereenkomst blijkt uit: ": [
            type_data[0],
            "",
            "explain_wo",
        ],
        "Volgens het cv werkte/studeerde werknemer als ...": [
            type_data[0],
            "",
            "previous_jobs",
        ],
    }

    return extracted_data


def transform(extracted_data: dict) -> pd.DataFrame:
    df = tm.dict_to_table(extracted_data)
    return df


def main() -> pd.DataFrame:
    extracted_data = empty_info()
    clean_data = transform(extracted_data)
    return clean_data
