import pandas as pd
from utils import locations_timeline, total_months_nl, map_location_radius
from utils import calculations as calc

class Applicant:
    def __init__(self, **kwargs):
        # Initialize the applicant with default values 
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Do some calculations
        self.calculate()
        self.timeline()

    def calculate(self):
        # Do calculations and set new attributes
        self.wage_type = calc.salarynorm(self.ufo_code)
        self.start_date = calc.start_date(self.contract_start_date, self.first_work_date, self.employer_type)
        self.signed_location = calc.signed_location(self.contract_signed_date, self.places_of_residence, self.arrival_date)
        
        self.true_start_date = calc.true_start_date(self.application_date, self.start_date)
        self.nl_arrival_till_start = calc.get_arrival_date_to_start_date_range(self.arrival_date, self.start_date)
        self.nl_combined = total_months_nl.combine_periods(self.nl_residence_dates, self.nl_worked_dates, self.nl_private_dates, self.nl_arrival_till_start)
        
        self.nl_combined_table = total_months_nl.show_date_ranges_table(self.nl_combined)
        self.cut_months = total_months_nl.calc(self.nl_combined)

        self.end_date = calc.end_date(self.true_start_date, self.cut_months)
    
    #temp fix
    def prepare_places_of_residence(self, data):
        return pd.DataFrame(data).rename(columns={
            'start_date': 'Startdatum',
            'end_date': 'Einddatum',
            'city': 'Stad',
            'country': 'Land'
        })
    
    def timeline(self):
        # Create a timeline of the last 24 months
        timeline = locations_timeline.TimelineVisualizer()
        timeline_end = pd.to_datetime(self.true_start_date, format="%d-%m-%Y")
        timeline_start = timeline_end - pd.DateOffset(years=2)

        # temp fix or else it will break
        places_df = pd.DataFrame(self.places_of_residence)
        
        self.recent_locations = timeline.location_table_24_months(places_df, timeline_start, timeline_end, self.arrival_date)

        # Create timeline_image
        timeline.create_timeline(
            data=places_df,
            ao_start_date_str=self.contract_start_date,
            arrival_date_str=self.arrival_date,
            output_file="static/images/timeline_image.png",
        )

        # Create map with locations near the Netherlands
        map_location_radius.create_map(places_df)

def regular_application(applicant: Applicant) -> str:
    """Create the report for a regular application."""

    header = formatting_header("Verslag regulier")
    werknemer = verslag_werknemer(
        applicant.employer,
        applicant.contract_start_date,
        applicant.employer_type,
        applicant.first_work_date,
        applicant.start_date,
    )
    aanwerving = verslag_aanwerving(
        applicant.contract_start_date,
        applicant.contract_signed_date,
        applicant.arrival_date,
        applicant.willagreement_signed_date, 
        applicant.willagreement_info,
        applicant.signed_location,
    )

    buitenland = verslag_buitenland(
        applicant.recent_locations,
        applicant.previous_jobs,
    )
    woonplaats_radius = verslag_woonplaats_radius()
    deskundigheid = verslag_deskundigheid(
        applicant.job_title,
        applicant.ufo_code,
        applicant.employer,
        "0" ## TODO: add income 
    )
    looptijd = verslag_looptijd(
        applicant.application_date,
        applicant.contract_start_date,
        applicant.nl_combined_table,
        applicant.nl_info,
        applicant.start_date,
        applicant.true_start_date,
        applicant.end_date,
        applicant.cut_months,
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


def exception_change_of_employer(): 
    return "Oeps deze aanvraag type bestaat nog niet in SOFIEbot!"

def exception_returning_expat(): 
    return "Oeps deze aanvraag type bestaat nog niet in SOFIEbot!"

def exception_promovendus(): 
    return "Oeps deze aanvraag type bestaat nog niet in SOFIEbot!"


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
    text = f"24 maanden voorafgaand aan de tewerkstelling woonde werknemer in: <br>{recent_locations}<br><br>"
    text += f"Volgens het CV werkte/studeerde de werknemer als: {cv_data}<br><br>"
    text += "Conclusie: het is aannemelijk dat werknemer op meer dan 150 km van de Nederlandse grens woonde gedurende meer dan 2/3 van de 24 maanden direct voorafgaand aan de eerste dag van tewerkstelling."
    text += '<img src="/static/images/timeline_image.png" alt="Timeline Image">'
    return formatting_text(title, text)


def verslag_woonplaats_radius():
    title = "Foto woonplaats radius 150km"
    text = '<img src="/static/images/geojson_map.png" alt="Map Image">'
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
    nl_combined_table,
    explain_nl,
    start_date,
    true_start_date,
    end_date,
    cut_months,
):
    title = "Verslag looptijd"

    # Check if the difference between start_date and application_date is less than 4 months.
    if calc.is_within_4_months(ao_start_date, application_date):
        text = f"Het verzoek is tijdig ingediend op {application_date}. Dat is binnen de 4 maanden na de aanvang van de tewerkstelling op {true_start_date}.<br><br>"
    else:
        text = f"Het verzoek is niet tijdig ingediend op {application_date}. Dat is 4 maanden na de aanvang van de tewerkstelling op {start_date}.<br><br>"
    text += f"- De startdatum is daarom {true_start_date}.<br><br>"

    # If worker has been in NL before, we have to remove these months if its more than 6 weeks a year.
    if cut_months == 0:
        text += "Betrokkene geeft aan niet eerder in Nederland verblijf te hebben gehad wat in aanmerking genomen moet worden voor een korting. De regeling kan voor de maximale duur worden toegekend (5 jaar). De inhoud van het bijgevoegde cv en het aanvraagformulier, geven geen aanleiding om anders te concluderen.<br><br>"
    else:
        text += f"Er is eerder verblijf in NL wat gekort wordt op de looptijd. Betrokkene heeft in Nederland gewoond van:<br>{nl_combined_table}<br>({cut_months} maand(en) totaal).<br>" 
        text += f"Dit verblijf was in het kader van {explain_nl}.<br><br>"

    text += f"- De einddatum van de looptijd is daarmee {end_date}."
    return formatting_text(title, text)

def create_main_report(applicant: Applicant) -> str:
    """Create the report based on the application type."""
    if applicant.request_type == "regular":
        return regular_application(applicant)
    elif applicant.request_type == "change_of_employer":
        return exception_change_of_employer()
    elif applicant.request_type == "returning_expat":   
        return exception_returning_expat()
    elif applicant.request_type == "promovendus":
        return exception_promovendus()
    else:
        return "Oeps deze aanvraag type bestaat nog niet in SOFIEbot!"


def create_email_report(applicant: Applicant) -> str:
    data = {
        "Naam": applicant.name,
        "BSnr": applicant.bsn,
        "Geboortedatum": applicant.date_of_birth,
        "Werkgever": applicant.employer,
        "Loonheffingsnummer": applicant.payroll_tax_number,
        "Gewenste ingangsdatum": applicant.true_start_date,
        "Looptijd tot en met": applicant.end_date,
        "Functienaam": applicant.job_title,
        "Loonnorm": applicant.wage_type,
        "Sectorcode": "61",
    }

    # Build the HTML using a list comprehension
    report = "<br>".join(f"{key}: {value}" for key, value in data.items())
    return report


def formatting_header(header: str) -> str:
    return "<b style='font-size:20px'>" + header + "</b><br><br>"


def formatting_text(subheader: str, text: str) -> str:
    return "<b>" + subheader + "</b><br>" + text + "<br><br><br>"


def replace_values(replacements: dict, report: str):
    for key, value in replacements.items():
        report = report.replace(key, value)
    return report
