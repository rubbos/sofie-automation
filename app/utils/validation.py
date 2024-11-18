# check for name
# check for date
# check for valid location
# check for 24m before starting date
# check if less than 6 weeks in a year
# signed date must be before arrival date
# check for valid date of birth
# valid bsn number
# valid 01 ufo code
# check for yes, no values
# check for 16/24 months
# check job title with ufo code
# if promovendus, returning, changing dutch employer skip.
# add calc for income
import pandas as pd
from utils.university import find_university


def validate_df(df, df2):
    validations = []
    df_name, df2_name = "Tax Form 30%", "Application Form"
    validations.append(check_standard_request(df2))
    validations.append(check_missing_fields(df, df_name, ignore_index=[5, 6, 7, 8, 9]))
    validations.append(check_missing_fields(df2, df2_name))
    validations.append(check_missing_dates(df, df_name))
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
    """Validate university and update the values from a csv"""
    uni = find_university(df)
    df.loc[df["KEY"] == "Name employer", "VALUE"] = uni[0]
    df.loc[df["KEY"] == "Loonheffing number", "VALUE"] = uni[1]
    df.loc[df["KEY"] == "University type", "VALUE"] = uni[2]
    return df
