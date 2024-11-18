from utils import calculations as calc
import pandas as pd
from extractors.methods import extract_methods as em


def create_main_report(tax_form: pd.DataFrame, application_form: pd.DataFrame, employment_contract: pd.DataFrame) -> str:
    with open("temp_files/report.txt", "r") as file:
        report = file.read()

    # Remove either public or private text. 
    if get_value(application_form, "University type") == "Privaat":
        report = em.remove_text_around_keywords(report, "[Publiek]", "[Publiek]")
        report = report.replace("[Privaat]", "")
    elif get_value(application_form, "University type") == "Publiek":
        report = em.remove_text_around_keywords(report, "[Privaat]", "[Privaat]")
        report = report.replace("[Publiek]", "")
    
    # Check for wilsovereenkomst
    if calc.signed_outside_nl(get_value(employment_contract, "Arbeidsovereenkomst datum getekend"),get_value(tax_form, "Arrival date")):
         report = em.remove_text_around_keywords(report, "[wilsovereenkomst]", "[wilsovereenkomst]")
    else:
         report = report.replace("[wilsovereenkomst]", "")

    # More needed evidence
    report = em.remove_text_around_keywords(report, "[Aanvullend bewijs]", "[Aanvullend bewijs]")

    # UFO job
    report = em.remove_text_around_keywords(report, "[Indien schaarse deskundigheid op basis van inkomen]" , "[Indien schaarse deskundigheid op basis van inkomen]")

    # Start date
    if calc.is_within_4_months(get_value(tax_form, "Start work date"),get_value(application_form, "Application upload date")):
        report = report.replace("&lt;niet&gt;", "")
        report = report.replace("&lt;buiten&gt;", "")
        report = report.replace("&lt;ingangsdatum&gt;", get_value(tax_form, "Start work date"))
    else:
        report = report.replace("&lt;niet&gt;", "niet")
        report = report.replace("binnen &lt;buiten&gt;", "buiten")
        report = report.replace("&lt;ingangsdatum&gt;", calc.next_first_of_month()) 

    replacements = {
        "[naam werkgever]": get_value(application_form, "Name employer"),
        "&lt;naam werkgever&gt;": get_value(application_form, "Name employer"),
        "&lt;datum aanvang dienstbetrekking&gt;": get_value(application_form, "Date of entry into service"),
        "&lt;datum indiensttreding&gt;": get_value(application_form, "Date of entry into service"),
        "&lt;datum aanvang tewerkstelling&gt;": get_value(application_form, "Date of entry into service"),
        "&lt;datum start kwalificatie als werknemer art. 2 Wet LB 1964&gt;": get_value(application_form, "Date of entry into service"),
        "&lt;datum aankomst NL&gt;": get_value(tax_form, "Arrival date"),
        "&lt;datum kwalificatie als werknemer&gt;": get_value(tax_form, "Arrival date"),
        "&lt;datum eerste werkdag in Nederland&gt;": get_value(tax_form, "Arrival date"),
        "&lt;naam functie&gt;": get_value(application_form, "Job title"),
        "&lt;eventueel functiecode vermelden&gt;": f"({get_value(application_form, "UFO code")})",
        "&lt;datum ondertekening werknemer&gt;": get_value(employment_contract, "Arbeidsovereenkomst datum getekend"),
        "&lt;datum ontstaan wilsovereenkomst&gt;": get_value(employment_contract, "Wilsovereenkomst datum getekend"),
        "&lt;datum melding SOFI-expertise&gt;": get_value(application_form, "Application upload date"),
    }

    report = replace_values(replacements, report)
    return report

def create_email_report(tax_form: pd.DataFrame, application_form: pd.DataFrame) -> str:
    with open("temp_files/email.txt", "r") as file:
        report = file.read()

    salarynorm = calc.salarynorm(get_value(application_form, "UFO code"))

    replacements = {
        "{name}": get_value(tax_form, "Full name"),
        "{bsn}": get_value(application_form, "BSN number"),
        "{birth}": get_value(application_form, "Date of birth"),
        "{employer}": get_value(application_form, "Name employer"),
        "{lhm}": get_value(application_form, "Loonheffing number"),
        "{start_date}": calc.start_date(get_value(application_form, "Application upload date"), get_value(tax_form, "Start work date")),
        # "{end_date}": get_value(df, ""),
        "{job_name}": get_value(application_form, "Job title"),
        "{salarynorm}": salarynorm,
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
