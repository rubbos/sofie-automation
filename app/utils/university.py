import pandas as pd
import difflib

def get_universities() -> pd.DataFrame:
    with open("temp_files/universities.csv", "r") as file:
        return pd.read_csv(file)

def find_university(data: dict) -> list | None:
    universities = get_universities()

    # Check if the university is in the data
    university = data.get("employer")
    if not university:
        return None

    # Check if the university is in the list of universities
    uni_names = universities["university"].tolist()
    closest_match = difflib.get_close_matches(university, uni_names, n=1)
    if closest_match:
        return (
            universities[universities["university"] == closest_match[0]]
            .iloc[0]
            .tolist()
        )
    return None
