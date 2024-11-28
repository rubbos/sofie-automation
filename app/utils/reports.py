from utils import calculations as calc
import pandas as pd
from extractors.methods import extract_methods as em


def check_application_type(tax_form, application_form, employment_contract):
    """Figure out what type of report we are dealing with. There are only 4 options: regular, change of employer, returning expat or promovendus exception"""
    return regular_application(tax_form, application_form, employment_contract)


def regular_application(tax_form, application_form, employment_contract):
    employer = get_valuex(application_form, "employer")
    ao_start_date = get_valuex(application_form, "ao_start_date")
    employer_type = get_valuex(application_form, "employer_type")
    first_work_date = get_valuex(tax_form, "first_work_date")
    ao_signed_date = get_valuex(employment_contract, "ao_signed_date")
    arrival_date = (get_valuex(tax_form, "arrival_date"),)
    wo_signed_date = get_valuex(employment_contract, "wo_signed_date")

    recent_location = "need text"
    explain_wo = "need text"
    recent_location_months = "need text"

    title = formatting_text("Verslag regulier")
    werknemer = verslag_werknemer(
        employer, ao_start_date, employer_type, first_work_date
    )
    aanwerving = verslag_aanwerving(
        ao_start_date,
        ao_signed_date,
        recent_location,
        arrival_date,
        wo_signed_date,
        explain_wo,
    )
    buitenland = verslag_buitenland(recent_location, recent_location_months)
    woonplaats_radius = verslag_woonplaats_radius()
    return title + werknemer + aanwerving + buitenland + woonplaats_radius


def exception_change_of_employer(): ...


def exception_returning_expat(): ...


def exception_promovendus(): ...


# FIX optional text
def verslag_werknemer(employer, ao_start_date, employer_type, start_work_date=False):
    title = "Verslag werknemer"
    if employer_type == "Publiek":
        main_text = f"De werkgever {employer} is een publiekrechtelijk lichaam. Aangezien de werkgever een publiekrechtelijk lichaam is en de werknemer in dienstbetrekking staat tot deze werkgever per {ao_start_date}, kwalificeert werknemer vanaf die datum ook als werknemer in de zin van artikel 2 Wet LB 1964."
    else:
        private_text_optional = f"Werknemer is per {first_work_date} (deels) werkzaam vanuit Nederland of in ieder geval voor meer dan 10% van de werktijd. Daarmee kwalificeert werknemer als werknemer in de zin van artikel 2 van de wet op de Loonbelasting 1964 per {first_work_date}."
        main_text = f"De werkgever is {employer}. Dit is een privaatrechtelijke werkgever. Werknemer staat in dienstbetrekking tot werkgever per {ao_start_date} en verricht de werkzaamheden ook vanuit Nederland (of in ieder geval meer dan 10%). Vanaf die datum kwalificeert werknemer als werknemer in de zin van artikel 2 van de Wet op de loonbelasting 1964."
    return formatting_text(title, main_text)


# FIX optional text
def verslag_aanwerving(
    ao_start_date,
    ao_signed_date,
    recent_location,
    arrival_date,
    wo_signed_date,
    explain_wo,
):
    title = "Verslag aanwerving"
    optional_text = f"Eerder is er al een wilsovereenkomst tot stand gekomen op {wo_signed_date}. Dit blijkt uit: {explain_wo}."
    main_text = f"Het betreft een dienstverband met een startdatum van {ao_start_date}. De arbeidsovereenkomst is door de werknemer getekend op {ao_signed_date}. {optional_text} Op dat moment woonde de werknemer, naar omstandigheden beoordeeld, in het buitenland in {recent_location}. Dit is aannemelijk o.a. op basis van het cv, de adressering op de arbeidsovereenkomst en de informatie in het werknemersformulier. Werknemer is op {arrival_date} Nederland ingereisd."
    return formatting_text(title, main_text)


def verslag_buitenland(recent_location, recent_location_months):
    title = "Verslag 150 km criterium 16/24 maanden criterium"
    text1 = f"Bij de aanwerving woonde werknemer in {recent_location}. De werknemer woonde daar ook gedurende {recent_location_months} van de 24 maanden voorafgaand aan de tewerkstelling. Deze woonplaats ligt op meer dan 150 km van de Nederlandse grens. Het CV en de informatie op het aanvraagformulier geven geen aanleiding om iets anders te concluderen."
    text2 = f"Volgens het cv werkte/studeerde werknemer als ...&nbsp; in &lt;plaats/land&gt; voor de start van de tewerkstelling van &lt;datum&gt; tot &lt;datum&gt;. &lt;Geef indien mogelijk informatie over de activiteiten en plaats voor aankomst in Nederland"
    text3 = f"Conclusie: het is aannemelijk dat werknemer op meer dan 150 km van de Nederlandse grens woonde gedurende meer dan 2/3 van de 24 maanden direct voorafgaand aan de eerste dag van tewerkstelling."
    text = text1 + text2 + text3
    return formatting_text(title, text)


def verslag_woonplaats_radius():
    title = "Foto woonplaats radius 150km"
    return formatting_text(title)


def verslag_deskundigheid():
    title = ""
    text = f""


def verslag_looptijd():
    title = ""
    text = f""


def formatting_text(title, text=False):
    if text:
        return title + "<br>" + text + "<br><br>"
    return title + "<br><br>"


def create_main_report(
    tax_form: pd.DataFrame,
    application_form: pd.DataFrame,
    employment_contract: pd.DataFrame,
) -> str:

    new_text = check_application_type(tax_form, application_form, employment_contract)
    return new_text

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
    if calc.signed_outside_nl(
        get_value(employment_contract, "Arbeidsovereenkomst datum getekend"),
        get_value(tax_form, "Arrival date"),
    ):
        report = em.remove_text_around_keywords(
            report, "[wilsovereenkomst]", "[wilsovereenkomst]"
        )
    else:
        report = report.replace("[wilsovereenkomst]", "")

    # More needed evidence
    report = em.remove_text_around_keywords(
        report, "[Aanvullend bewijs]", "[Aanvullend bewijs]"
    )

    # UFO job
    report = em.remove_text_around_keywords(
        report,
        "[Indien schaarse deskundigheid op basis van inkomen]",
        "[Indien schaarse deskundigheid op basis van inkomen]",
    )

    # Start date
    if calc.is_within_4_months(
        get_value(tax_form, "Start work date"),
        get_value(application_form, "Application upload date"),
    ):
        report = report.replace("&lt;niet&gt;", "")
        report = report.replace("&lt;buiten&gt;", "")
        report = report.replace(
            "&lt;ingangsdatum&gt;", get_value(tax_form, "Start work date")
        )
    else:
        report = report.replace("&lt;niet&gt;", "niet")
        report = report.replace("binnen &lt;buiten&gt;", "buiten")
        report = report.replace("&lt;ingangsdatum&gt;", calc.next_first_of_month())

    replacements = {
        "[naam werkgever]": get_value(application_form, "Name employer"),
        "&lt;naam werkgever&gt;": get_value(application_form, "Name employer"),
        "&lt;datum aanvang dienstbetrekking&gt;": get_value(
            application_form, "Date of entry into service"
        ),
        "&lt;datum indiensttreding&gt;": get_value(
            application_form, "Date of entry into service"
        ),
        "&lt;datum aanvang tewerkstelling&gt;": get_value(
            application_form, "Date of entry into service"
        ),
        "&lt;datum start kwalificatie als werknemer art. 2 Wet LB 1964&gt;": get_value(
            application_form, "Date of entry into service"
        ),
        "&lt;datum aankomst NL&gt;": get_value(tax_form, "Arrival date"),
        "&lt;datum kwalificatie als werknemer&gt;": get_value(tax_form, "Arrival date"),
        "&lt;datum eerste werkdag in Nederland&gt;": get_value(
            tax_form, "Arrival date"
        ),
        "&lt;naam functie&gt;": get_value(application_form, "Job title"),
        "&lt;eventueel functiecode vermelden&gt;": f"({get_value(application_form, "UFO code")})",
        "&lt;datum ondertekening werknemer&gt;": get_value(
            employment_contract, "Arbeidsovereenkomst datum getekend"
        ),
        "&lt;datum ontstaan wilsovereenkomst&gt;": get_value(
            employment_contract, "Wilsovereenkomst datum getekend"
        ),
        "&lt;datum melding SOFI-expertise&gt;": get_value(
            application_form, "Application upload date"
        ),
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
        "{start_date}": calc.start_date(
            get_value(application_form, "Application upload date"),
            get_value(tax_form, "Start work date"),
        ),
        # "{end_date}": get_value(df, ""),
        "{job_name}": get_value(application_form, "Job title"),
        "{salarynorm}": salarynorm,
    }
    report = replace_values(replacements, report)
    return report


def get_value(df: pd.DataFrame, key: str) -> str:
    """Retrieve a value from the DataFrame based on the given key."""
    return df.loc[df["KEY"] == key, "VALUE"].values[0]


def get_valuex(df: pd.DataFrame, key: str) -> str:
    """Retrieve a value from the DataFrame based on the given key."""
    return df.loc[df["VAR"] == key, "VALUE"].values[0]


def replace_values(replacements: dict, report: str):
    for key, value in replacements.items():
        report = report.replace(key, value)
    return report
