import pandas as pd
from dataclasses import dataclass
from typing import Optional
from utils import locations_table, locations_timeline
from utils import calculations as calc


@dataclass
class WorkerData:
    """Represents data related to the worker."""

    full_name: str
    bsn: str
    date_of_birth: str
    first_work_date: str
    arrival_date: str
    recent_locations: str
    nl_dates: Optional[str] = None
    nl_reason: Optional[str] = None
    nl_reason_doc: Optional[str] = None
    cv_data: Optional[str] = None


@dataclass
class EmployerData:
    """Represents data related to the employer."""

    employer: str
    employer_type: str
    lhn: str


@dataclass
class ContractData:
    """Represents contract-specific data."""

    job_title: str
    ufo_code: str
    wage_type: str
    ao_start_date: str
    ao_signed_date: str
    application_date: str
    wo_signed_date: Optional[str] = None
    explain_wo: Optional[str] = None
    income: Optional[str] = None

    def __post_init__(self):
        if self.income and not self.income.isdigit():
            raise ValueError("Income must be numeric.")


@dataclass
class CalculationData:
    """Represents calculated data"""

    application_type: str
    start_date: str
    true_start_date: str
    end_date: str
    signed_location: str


def extracted_data(
    tax_form,
    application_form,
    employment_contract,
):

    full_name = get_value(tax_form, "full_name")
    first_work_date = get_value(tax_form, "first_work_date")
    place_of_residence = get_value(tax_form, "place_of_residence")
    arrival_date = get_value(tax_form, "arrival_date")
    employer = get_value(application_form, "employer")
    lhn = get_value(application_form, "lhn")
    bsn = get_value(application_form, "bsn")
    date_of_birth = get_value(application_form, "date_of_birth")
    ao_start_date = get_value(application_form, "ao_start_date")
    employer_type = get_value(application_form, "employer_type")
    job_title = get_value(application_form, "job_title")
    ufo_code = get_value(application_form, "ufo_code")
    wage_type = calc.salarynorm(get_value(application_form, "ufo_code"))
    application_date = get_value(application_form, "application_date")
    wo_signed_date = get_value(employment_contract, "wo_signed_date")
    explain_wo = get_value(employment_contract, "explain_wo")
    ao_signed_date = get_value(employment_contract, "ao_signed_date")
    cv_data = get_value(employment_contract, "previous_jobs")
    application_type = get_value(tax_form, "application_type")
    nl_dates = get_value(tax_form, "nl_residence_dates")
    start_date = calc.start_date(ao_start_date, first_work_date, employer_type)
    true_start_date = calc.true_start_date(application_date, start_date)
    end_date = calc.end_date(true_start_date)

    # creating timeline_image
    locations_timeline.create_timeline(
        locations_table.convert_string_to_data(place_of_residence), arrival_date
    )

    worker_info = WorkerData(
        full_name=full_name,
        bsn=bsn,
        date_of_birth=date_of_birth,
        first_work_date=first_work_date,
        arrival_date=arrival_date,
        recent_locations=locations_table.create_table(
            locations_table.convert_string_to_data(place_of_residence)
        ),
        nl_dates=nl_dates,
        nl_reason="Work",
        nl_reason_doc="Contract",
        cv_data=cv_data,
    )

    employer_info = EmployerData(
        employer=employer, employer_type=employer_type, lhn=lhn
    )

    contract_info = ContractData(
        job_title=job_title,
        ufo_code=ufo_code,
        wage_type=wage_type,
        ao_start_date=ao_start_date,
        ao_signed_date=ao_signed_date,
        application_date=application_date,
        wo_signed_date=wo_signed_date,
        explain_wo=explain_wo,
    )

    calculation_info = CalculationData(
        application_type=application_type,
        start_date=start_date,
        true_start_date=true_start_date,
        end_date=end_date,
        signed_location=calc.signed_location(
            ao_signed_date,
            locations_table.convert_string_to_data(place_of_residence),
            arrival_date,
        ),
    )
    return worker_info, employer_info, contract_info, calculation_info


def check_application_type(
    worker_info,
    employer_info,
    contract_info,
    calculation_info,
):
    """Figure out what type of report we are dealing with. There are only 4 options: regular, change of employer, returning expat or promovendus exception"""
    if calculation_info.application_type == "Reguliere aanvraag":
        return regular_application(
            worker_info,
            employer_info,
            contract_info,
            calculation_info,
        )
    return "Oeps deze aanvraag type bestaat nog niet in SOFIEbot!"


def regular_application(
    worker_info,
    employer_info,
    contract_info,
    calculation_info,
):

    header = formatting_header("Verslag regulier")
    werknemer = verslag_werknemer(
        employer_info.employer,
        contract_info.ao_start_date,
        employer_info.employer_type,
        worker_info.first_work_date,
        calculation_info.start_date,
    )
    aanwerving = verslag_aanwerving(
        contract_info.ao_start_date,
        contract_info.ao_signed_date,
        worker_info.arrival_date,
        contract_info.wo_signed_date,
        contract_info.explain_wo,
        calculation_info.signed_location,
    )
    buitenland = verslag_buitenland(
        worker_info.recent_locations,
        worker_info.cv_data,
    )
    woonplaats_radius = verslag_woonplaats_radius()
    deskundigheid = verslag_deskundigheid(
        contract_info.job_title,
        contract_info.ufo_code,
        employer_info.employer,
        contract_info.income,
    )
    looptijd = verslag_looptijd(
        contract_info.application_date,
        contract_info.ao_start_date,
        worker_info.nl_dates,
        worker_info.nl_reason,
        worker_info.nl_reason_doc,
        calculation_info.start_date,
        calculation_info.true_start_date,
        calculation_info.end_date,
    )

    return (
        header
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


def verslag_werknemer(
    employer, ao_start_date, employer_type, first_work_date, start_date
):
    title = "Verslag werknemer"
    text = f"De werkgever {employer} is een {employer_type.lower()}rechtelijk lichaam. "
    # Check for public or private employer_type
    if employer_type == "Publiek":
        text += f"Aangezien de werkgever een publiekrechtelijk lichaam is en de werknemer in dienstbetrekking staat tot deze werkgever per {start_date}, kwalificeert werknemer vanaf die datum ook als werknemer in de zin van artikel 2 Wet LB 1964."
    else:
        # Check for the correct text for private employer_type
        if calc.get_most_recent_date(ao_start_date, first_work_date) != ao_start_date:
            text += f" Werknemer is per {start_date} (deels) werkzaam vanuit Nederland of in ieder geval voor meer dan 10% van de werktijd. Daarmee kwalificeert werknemer als werknemer in de zin van artikel 2 van de wet op de Loonbelasting 1964 per {start_date}."
        text += f"Werknemer staat in dienstbetrekking tot werkgever per {start_date} en verricht de werkzaamheden ook vanuit Nederland (of in ieder geval meer dan 10%). Vanaf die datum kwalificeert werknemer als werknemer in de zin van artikel 2 van de Wet op de loonbelasting 1964."
    return formatting_text(title, text)


def verslag_aanwerving(
    ao_start_date,
    ao_signed_date,
    arrival_date,
    wo_signed_date,
    explain_wo,
    signed_location,
):
    title = "Verslag aanwerving"
    text = f"Het betreft een dienstverband met een startdatum van {ao_start_date}. De arbeidsovereenkomst is door de werknemer getekend op {ao_signed_date}. "
    # Check if its signed outside NL
    if calc.get_most_recent_date(ao_signed_date, arrival_date) != arrival_date:
        text += f"Eerder is er al een wilsovereenkomst tot stand gekomen op {wo_signed_date}. Dit blijkt uit: {explain_wo}."
    text += f"Op dat moment woonde de werknemer, naar omstandigheden beoordeeld, in {signed_location}. Dit is aannemelijk o.a. op basis van het cv, de adressering op de arbeidsovereenkomst en de informatie in het werknemersformulier. Werknemer is op {arrival_date} Nederland ingereisd."
    return formatting_text(title, text)


# NOTE: need something to fix the text if the country in under 150km from nl
def verslag_buitenland(recent_locations, cv_data):
    title = "Verslag 150 km criterium 16/24 maanden criterium"
    text = f"24 maanden voorafgaand aan de tewerkstelling woonde werknemer in: {recent_locations}<br>"
    text += "Deze woonplaats(en) liggen op meer dan 150 km van de Nederlandse grens. Het CV en de informatie op het aanvraagformulier geven geen aanleiding om iets anders te concluderen.<br><br>"
    text += f"Volgens het CV werkte/studeerde de werknemer als: {cv_data}<br><br>"
    text += "Conclusie: het is aannemelijk dat werknemer op meer dan 150 km van de Nederlandse grens woonde gedurende meer dan 2/3 van de 24 maanden direct voorafgaand aan de eerste dag van tewerkstelling."
    text += '<img src="/static/images/timeline_image.png" alt="Timeline Image">'
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
    # NOTE: Still needs more attention!
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
    true_start_date,
    end_date,
):
    title = "Verslag looptijd"

    # Check if the difference between start_date and application_date is less than 4 months.
    if calc.is_within_4_months(ao_start_date, application_date):
        text = f"Het verzoek is tijdig ingediend op {application_date}. Dat is binnen de 4 maanden na de aanvang van de tewerkstelling op {true_start_date}.<br><br>"
    else:
        text = f"Het verzoek is niet tijdig ingediend op {application_date}. Dat is 4 maanden na de aanvang van de tewerkstelling op {start_date}.<br><br>"
    text += f"- De startdatum is daarom {true_start_date}.<br><br>"

    # If worker has been in NL before, we have to remove these months if its more than 6 weeks a year.
    # NOTE: Fix the garbage variables types :(
    if nl_dates == "None":
        text += "Betrokkene geeft aan niet eerder in Nederland verblijf te hebben gehad wat in aanmerking genomen moet worden voor een korting. De regeling kan voor de maximale duur worden toegekend (5 jaar). De inhoud van het bijgevoegde cv en het aanvraagformulier, geven geen aanleiding om anders te concluderen.<br><br>"
    else:
        text += f"Er is eerder verblijf in NL wat gekort wordt op de looptijd. Betrokkene heeft in Nederland gewoond van {nl_dates} Dit verblijf was in het kader van {nl_reason}. Dit blijkt o.a. uit {nl_reason_doc}.<br><br>"
    text += f"- De einddatum van de looptijd is daarmee {end_date}."
    return formatting_text(title, text)


def create_main_report(
    worker_info,
    employer_info,
    contract_info,
    calculation_info,
) -> str:

    main_report = check_application_type(
        worker_info,
        employer_info,
        contract_info,
        calculation_info,
    )
    return main_report


def create_email_report(
    worker_info,
    employer_info,
    contract_info,
    calculation_info,
) -> str:
    data = {
        "Naam": worker_info.full_name,
        "BSnr": worker_info.bsn,
        "Geboortedatum": worker_info.date_of_birth,
        "Werkgever": employer_info.employer,
        "Loonheffingsnummer": employer_info.lhn,
        "Gewenste ingangsdatum": calculation_info.true_start_date,
        "Looptijd tot en met": calculation_info.end_date,
        "Functienaam": contract_info.job_title,
        "Loonnorm": contract_info.wage_type,
        "Sectorcode": "61",
    }

    # Build the HTML using a list comprehension
    report = "<br>".join(f"{key}: {value}" for key, value in data.items())
    return report


def get_value(df: pd.DataFrame, key: str) -> str:
    """Retrieve a value from the DataFrame based on the given key."""
    return df.loc[df["VAR"] == key, "VALUE"].values[0]


def formatting_header(header: str) -> str:
    return "<b style='font-size:20px'>" + header + "</b><br><br>"


def formatting_text(subheader: str, text: str) -> str:
    return "<b>" + subheader + "</b><br>" + text + "<br><br><br>"


def replace_values(replacements: dict, report: str):
    for key, value in replacements.items():
        report = report.replace(key, value)
    return report
