import pandas as pd
import difflib


def get_universities() -> pd.DataFrame:
    with open("temp_files/universities.csv", "r") as file:
        return pd.read_csv(file)


def find_university(df) -> list | None:
    universities = get_universities()
    university = df.loc[df["KEY"] == "Name employer", "VALUE"].values[0]
    if university is None:
        return None

    uni_names = universities["university"].tolist()
    closest_match = difflib.get_close_matches(university, uni_names, n=1)
    if closest_match:
        return (
            universities[universities["university"] == closest_match[0]]
            .iloc[0]
            .tolist()
        )
    return None
