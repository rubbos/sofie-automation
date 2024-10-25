import pandas as pd
from extractors.methods import extract_methods as em
from extractors.methods import transform_methods as tm


def empty_info():
    type_data = ["str", "list[str]", "date", "list[date]"]

    extracted_data = {
        "Getekend": [type_data[0], ""],
        "Datum getekend": [type_data[2], ""],
        "Wilsovereenkomst getekend": [type_data[0], ""],
        "Wilsovereenkomst datum getekend": [type_data[2], ""],
    }

    return extracted_data


def transform(extracted_data: dict) -> pd.DataFrame:
    df = tm.dict_to_table(extracted_data)
    return df


def main() -> pd.DataFrame:
    extracted_data = empty_info()
    clean_data = transform(extracted_data)
    return clean_data


if __name__ == "__main__":
    main()
