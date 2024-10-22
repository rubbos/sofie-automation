import pandas as pd


def create_main_report(df: pd.DataFrame, df2: pd.DataFrame) -> str:
    with open("temp_files/report.txt", "r") as file:
        report = file.read()
    
    replacements = {
        "[naam werkgever]": get_value(df2, "Name employer"),
        "&lt;naam werkgever&gt;": get_value(df2, "Name employer"),
        "&lt;datum aanvang dienstbetrekking&gt;": get_value(df2, "Date of entry into service"),
        "&lt;datum indiensttreding&gt;": get_value(df2, "Date of entry into service"),
        "&lt;datum aanvang tewerkstelling&gt;": get_value(df2, "Date of entry into service"),
        "&lt;datum aankomst NL&gt;": get_value(df, "Arrival date"),
        "&lt;datum kwalificatie als werknemer&gt;": get_value(df, "Arrival date"),
        "&lt;datum eerste werkdag in Nederland&gt;": get_value(df, "Arrival date"),
        "&lt;naam functie&gt;": get_value(df2, "Job title"),
        "&lt;eventueel functiecode vermelden&gt;": f"({get_value(df2, "UFO code")})",
    }

    # signed = df.loc[df["KEY"] == "Arrival date", "VALUE"].values[0]
    # report = report.replace("ADD SIGNED DATE ON AO", signed)

    report = replace_values(replacements, report)
    return report

def create_email_report(df: pd.DataFrame, df2: pd.DataFrame) -> str:
    with open("temp_files/email.txt", "r") as file:
        report = file.read()

    replacements = {
        "{name}": get_value(df, "Full name"),
        "{bsn}": get_value(df2, "BSN number"),
        "{birth}": get_value(df2, "Date of birth"),
        "{employer}": get_value(df2, "Name employer"),
        "{lhm}": get_value(df2, "Loonheffing number"),
        # "{start_date}": get_value(df, ""),
        # "{end_date}": get_value(df, ""),
        "{job_name}": get_value(df2, "Job title"),
        # "{salarynorm}": get_value(df, "salarynorm")
    }
    report = replace_values(replacements, report)
    return report


def get_value(df: pd.DataFrame, key: str) -> str:
    """Retrieve a value from the DataFrame based on the given key."""
    return df.loc[df["KEY"] == key, "VALUE"].values[0]


def replace_values(replacements: dict, report: str):
    for key, value in replacements.items():
        report = report.replace(key, value)
    return report
