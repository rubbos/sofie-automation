import pandas as pd
from extractors.methods import transform_methods as tm


def empty_info():
    type_data = ["str", "list[str]", "date", "list[date]"]
    type_string = "str"
    type_date = "date"

    extracted_data = {
        "Arbeidsovereenkomst datum getekend": [
            type_string,
            "",
            "ao_signed_date",
        ],
        "Wilsovereenkomst datum getekend": [type_date, "", "wo_signed_date"],
        "De wilsovereenkomst blijkt uit: ": [
            type_string,
            "",
            "explain_wo",
        ],
        "Volgens het cv werkte/studeerde werknemer als ...": [
            type_string,
            "",
            "previous_jobs",
        ],
        "Het verblijf in Nederland was in het kader van ... Dit blijkt o.a. uit Contract ...": [
            type_string,
            "",
            "explain_nl",
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
