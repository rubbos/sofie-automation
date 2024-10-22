import pandas as pd


def create_main_report(tax_form: pd.DataFrame, application_form: pd.DataFrame, employment_contract: pd.DataFrame) -> str:
    with open("temp_files/report.txt", "r") as file:
        report = file.read()
    
    replacements = {
        "[naam werkgever]": get_value(application_form, "Name employer"),
        "&lt;naam werkgever&gt;": get_value(application_form, "Name employer"),
        "&lt;datum aanvang dienstbetrekking&gt;": get_value(application_form, "Date of entry into service"),
        "&lt;datum indiensttreding&gt;": get_value(application_form, "Date of entry into service"),
        "&lt;datum aanvang tewerkstelling&gt;": get_value(application_form, "Date of entry into service"),
        "&lt;datum aankomst NL&gt;": get_value(tax_form, "Arrival date"),
        "&lt;datum kwalificatie als werknemer&gt;": get_value(tax_form, "Arrival date"),
        "&lt;datum eerste werkdag in Nederland&gt;": get_value(tax_form, "Arrival date"),
        "&lt;naam functie&gt;": get_value(application_form, "Job title"),
        "&lt;eventueel functiecode vermelden&gt;": f"({get_value(application_form, "UFO code")})",
        "&lt;datum ondertekening werknemer&gt;": get_value(employment_contract, "Datum getekend"),
    }

    report = replace_values(replacements, report)
    return report

def create_email_report(tax_form: pd.DataFrame, application_form: pd.DataFrame) -> str:
    with open("temp_files/email.txt", "r") as file:
        report = file.read()

    replacements = {
        "{name}": get_value(tax_form, "Full name"),
        "{bsn}": get_value(application_form, "BSN number"),
        "{birth}": get_value(application_form, "Date of birth"),
        "{employer}": get_value(application_form, "Name employer"),
        "{lhm}": get_value(application_form, "Loonheffing number"),
        # "{start_date}": get_value(df, ""),
        # "{end_date}": get_value(df, ""),
        "{job_name}": get_value(application_form, "Job title"),
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
