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
    arrival_date = get_valuex(tax_form, "arrival_date")
    wo_signed_date = get_valuex(employment_contract, "wo_signed_date")
    job_name = get_valuex(application_form, "job_title")
    ufo_code = get_valuex(application_form, "ufo_code")
    application_date = get_valuex(application_form, "application_date")
    recent_location = "need text"
    explain_wo = "need text"
    recent_location_months = "need text"
    start_date = "need text"
    end_date = "need text"
    nl_dates = "need text"
    nl_reason = "need text"
    nl_reason_doc = "need text"
    cv_data = "need text"
    income = "need text"

    title = formatting_text("Verslag regulier", "")
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
    buitenland = verslag_buitenland(recent_location, recent_location_months, cv_data)
    woonplaats_radius = verslag_woonplaats_radius()
    deskundigheid = verslag_deskundigheid(job_name, ufo_code, employer, income)
    looptijd = verslag_looptijd(
        application_date,
        ao_start_date,
        nl_dates,
        nl_reason,
        nl_reason_doc,
        start_date,
        end_date,
    )

    return (
        title
        + werknemer
        + aanwerving
        + buitenland
        + woonplaats_radius
        + deskundigheid
        + looptijd
    )


def exception_change_of_employer(): ...


def exception_returning_expat(): ...


def exception_promovendus(): ...


def verslag_werknemer(employer, ao_start_date, employer_type, first_work_date):
    title = "Verslag werknemer"
    # Check for public or private university
    if employer_type == "Publiek":
        text = f"De werkgever {employer} is een publiekrechtelijk lichaam. Aangezien de werkgever een publiekrechtelijk lichaam is en de werknemer in dienstbetrekking staat tot deze werkgever per {ao_start_date}, kwalificeert werknemer vanaf die datum ook als werknemer in de zin van artikel 2 Wet LB 1964."
    else:
        # This is the private text with first_work_date.
        if calc.get_most_recent_date(ao_start_date, first_work_date) != ao_start_date:
            text = f"De werkgever is {employer}. Dit is een privaatrechtelijke werkgever. Werknemer is per {first_work_date} (deels) werkzaam vanuit Nederland of in ieder geval voor meer dan 10% van de werktijd. Daarmee kwalificeert werknemer als werknemer in de zin van artikel 2 van de wet op de Loonbelasting 1964 per {first_work_date}."
        # This is the private text with ao_start_date.
        else:
            text = f"De werkgever is {employer}. Dit is een privaatrechtelijke werkgever. Werknemer staat in dienstbetrekking tot werkgever per {ao_start_date} en verricht de werkzaamheden ook vanuit Nederland (of in ieder geval meer dan 10%). Vanaf die datum kwalificeert werknemer als werknemer in de zin van artikel 2 van de Wet op de loonbelasting 1964."
    return formatting_text(title, text)


def verslag_aanwerving(
    ao_start_date,
    ao_signed_date,
    recent_location,
    arrival_date,
    wo_signed_date,
    explain_wo,
):
    title = "Verslag aanwerving"
    text = f"Het betreft een dienstverband met een startdatum van {ao_start_date}. De arbeidsovereenkomst is door de werknemer getekend op {ao_signed_date}. "
    # Check if its signed outside NL
    if calc.get_most_recent_date(ao_signed_date, arrival_date) != arrival_date:
        text += f"Eerder is er al een wilsovereenkomst tot stand gekomen op {wo_signed_date}. Dit blijkt uit: {explain_wo}."
    text += f"Op dat moment woonde de werknemer, naar omstandigheden beoordeeld, in het buitenland in {recent_location}. Dit is aannemelijk o.a. op basis van het cv, de adressering op de arbeidsovereenkomst en de informatie in het werknemersformulier. Werknemer is op {arrival_date} Nederland ingereisd."
    return formatting_text(title, text)


def verslag_buitenland(recent_location, recent_location_months, cv_data):
    title = "Verslag 150 km criterium 16/24 maanden criterium"
    text = f"Bij de aanwerving woonde werknemer in {recent_location}. De werknemer woonde daar ook gedurende {recent_location_months} van de 24 maanden voorafgaand aan de tewerkstelling. Deze woonplaats ligt op meer dan 150 km van de Nederlandse grens. Het CV en de informatie op het aanvraagformulier geven geen aanleiding om iets anders te concluderen.<br><br>"
    text += f"Volgens het CV werkte/studeerde de werknemer als: {cv_data}<br><br>"
    text += "Conclusie: het is aannemelijk dat werknemer op meer dan 150 km van de Nederlandse grens woonde gedurende meer dan 2/3 van de 24 maanden direct voorafgaand aan de eerste dag van tewerkstelling."
    return formatting_text(title, text)


# NOTE: need to make something that makes a picture of the location on a map with a radius
def verslag_woonplaats_radius():
    title = "Foto woonplaats radius 150km"
    text = "Enter picture"
    return formatting_text(title, text)


def verslag_deskundigheid(job_name, ufo_code, employer, income):
    title = "Verslag specifieke deskundigheid"
    # Regular academic position
    if ufo_code.startswith("01"):
        text = f"De functie van {job_name} ({ufo_code}) is een functie binnen de UFO functiefamilie «onderzoek en onderwijs» en de werknemer is tewerkgesteld bij {employer} welke een werkgever is zoals bedoeld in artikel 1.11, onderdelen a, van het Vreemdelingenbesluit 2000. Daarmee kwalificeert de werknemer als schaars specifiek deskundig."
    # Non-academic position
    else:
        # High-income position
        text = f"Uit de pro forma loonstrook, jaaropgaaf, salarisbedrag uit de arbeidsovereenkomst, addendum, blijkt dat voldaan wordt aan de loonnorm. Het loon omgerekend op jaarbasis bedraagt {income} EUR. <br><br>"
        # High-income position and MSc
        text += "In de Excel lijst staat de master genoemd van de specifieke onderwijsinstelling in het buitenland alsmede de studierichting.<br><br>"
        # Not high enough income to receive the full 30%
        text += "Omdat het salaris na toepassing van een korting van 30% van het loon onder de norm dreigt te komen, hebben we het belang van het addendum benadrukt.<br><br>"
        # Special cases
        text += "Er is een diplomawaardering opgevraagd bij Nuffic/IDW. Deze wijst uit dat de Master kwalificeert als: <naam kwalificatie>"
    return formatting_text(title, text)


def verslag_looptijd(
    application_date,
    ao_start_date,
    nl_dates,
    nl_reason,
    nl_reason_doc,
    start_date,
    end_date,
):
    title = "Verslag looptijd"

    # Check if the difference between start_date and application_date is less than 4 months.
    if calc.is_within_4_months(ao_start_date, application_date):
        text = f"Het verzoek is tijdig ingediend op {application_date}. Dat is binnen de 4 maanden na de aanvang van de tewerkstelling op {start_date}.<br><br>"
    else:
        text = f"Het verzoek is niet tijdig ingediend op {application_date}. Dat is 4 maanden na de aanvang van de tewerkstelling op {start_date}.<br><br>"
    text += f"- De startdatum is daarom {start_date}.<br><br>"

    # If worker has been in NL before, we have to remove these months if its more than 6 weeks a year.
    if nl_dates:
        text += f"Er is eerder verblijf in NL wat gekort wordt op de looptijd. Betrokkene heeft in Nederland gewoond van {nl_dates} Dit verblijf was in het kader van {nl_reason}. Dit blijkt o.a. uit {nl_reason_doc}.<br><br>"
    else:
        text += "Betrokkene geeft aan niet eerder in Nederland verblijf te hebben gehad wat in aanmerking genomen moet worden voor een korting. De regeling kan voor de maximale duur worden toegekend (5 jaar). De inhoud van het bijgevoegde cv en het aanvraagformulier, geven geen aanleiding om anders te concluderen.<br><br>"
    text += f"- De einddatum van de looptijd is daarmee {end_date}."
    return formatting_text(title, text)


def create_main_report(
    tax_form: pd.DataFrame,
    application_form: pd.DataFrame,
    employment_contract: pd.DataFrame,
) -> str:

    main_report = check_application_type(
        tax_form, application_form, employment_contract
    )
    return main_report


def create_email_report(tax_form: pd.DataFrame, application_form: pd.DataFrame) -> str:

    # FIX: and make use of the variables from the regular one
    text = f"Naam: {get_valuex(tax_form, "full_name")}<br>"
    text += f"BSnr: {get_value(application_form, "BSN number")}<br>"
    text += f"Geboortedatum: {get_value(application_form, "Date of birth")}<br>"
    text += f"Werkgever: {get_value(application_form, "Name employer")}<br>"
    text += f"Loonheffingsnummer: {get_value(application_form, "Loonheffing number")}<br>"
    text += f"Gewenste ingangsdatum: {calc.start_date(get_value(application_form, "Application upload date"), get_value(tax_form, "Start work date")}<br>"
    text += f"Looptijd tot en met: {"need data"}<br>"
    text += f"Functienaam: {get_value(application_form, "Job title")}<br>"
    text += f"Loonnorm: {calc.salarynorm(get_value(application_form, "UFO code"))}<br>"
    text += "Sectorcode: 61"

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


def formatting_text(title: str, text: str) -> str:
    return title + "<br>" + text + "<br><br>"


def replace_values(replacements: dict, report: str):
    for key, value in replacements.items():
        report = report.replace(key, value)
    return report
