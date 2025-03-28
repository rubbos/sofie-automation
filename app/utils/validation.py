import pandas as pd
from utils.university import find_university
"""This module contains validation functions that are used in the results.html before it gets loaded"""

def validate_df(df, df2):
    validations = []
    df_name, df2_name = "Tax Form 30%", "Application Form"
    #validations.append(check_standard_request(df2))
    #validations.append(check_missing_fields(df, df_name, ignore_index=[5, 6, 7, 8, 9]))
    #validations.append(check_missing_fields(df2, df2_name))
    #validations.append(check_missing_dates(df, df_name))
    validations = [item for item in validations if item is not None]
    pd.set_option("display.max_colwidth", None)
    return pd.DataFrame(validations, columns=["VALUE"])


def check_missing_fields(df, df_name: str, ignore_index=[]) -> str:
    """Return keys of missing values in df and ignore specific optional values"""
    errors = [
        row["KEY"]
        for index, row in df.iterrows()
        if row["VALUE"] is None and index not in ignore_index
    ]
    if errors:
        return f"{df_name} - Missing values: {errors}"


def check_missing_dates(df, df_name: str):
    """Return where missing dates in a list, they are always in pairs"""
    errors = [
        row["KEY"]
        for index, row in df.iterrows()
        if row["TYPE"] == "list[date]"
        and row["VALUE"] is not None
        and len(row["VALUE"]) % 2 != 0
    ]
    if errors:
        return f"{df_name} - Missing dates: {errors}"


def check_standard_request(df):
    """Return warning if not a standard request"""
    if (
        df.loc[df["KEY"] == "Returning expat", "VALUE"].values == "No"
        and df.loc[df["KEY"] == "Changing Dutch employer", "VALUE"].values == "No"
        and df.loc[df["KEY"] == "Contract signed outside NL", "VALUE"].values == "Yes"
        and df.loc[df["KEY"] == "16/24 Months outside NL", "VALUE"].values == "Yes"
        and df.loc[df["KEY"] == "UFO 01 type", "VALUE"].values == "Yes"
    ):
        return
    return "This request might be an exception!"


def validate_uni(df):
    """Validate university data and update the values in the DataFrame."""
    uni = find_university(df)

    def update_value(var, value):
        """Helper function to update a row in the DataFrame."""
        df.loc[df["VAR"] == var, "VALUE"] = value

    if isinstance(uni, (list, tuple)) and len(uni) >= 3:
        # Update DataFrame with university data
        update_value("employer", uni[0])
        update_value("lhn", uni[1])
        update_value("employer_type", uni[2])
    else:
        # Log error and set default values
        print("Error: Invalid university data")
        for var in ["employer", "lhn", "employer_type"]:
            update_value(var, None)

    return df
