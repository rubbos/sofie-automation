from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional
import pandas as pd


def signed_outside_nl(signed_date: str, arrival_date: str) -> bool:
    """If user signed the contract in the Netherlands, a wilsovereenkomst is needed"""
    date_format = "%d-%m-%Y"
    print(arrival_date)
    date1 = datetime.strptime(signed_date, date_format)
    date2 = datetime.strptime(arrival_date, date_format)

    if date1 >= date2:
        return False
    return True


def signed_location(signed_date: datetime.date, places_of_residence: list, arrival_date: datetime.date):
    """Finds the location where the given signed date falls within the start and end date ranges"""
 
    for entry in places_of_residence:
        start_date = entry['start_date']
        end_date = entry['end_date']

        if start_date <= signed_date <= end_date:
            return f"{entry['city']}, {entry['country']}"
        elif signed_date >= arrival_date:
            return "Nederland"
    
    return "Onbekend"


def salarynorm(ufo_code: str) -> str:
    """If the users job position is an academic position, its an exception"""
    if ufo_code.startswith("01"):
        return "Wetenschappelijk O&O"
    return "Regulier"


def is_within_4_months(date1, date2) -> bool:
    """Compare 2 dates and see if the time between is less than 4 months"""
    four_months_later = date1 + relativedelta(months=4)
    cutoff_date = four_months_later - relativedelta(days=1)
    return date2 <= cutoff_date


def next_first_of_month(date: datetime.date) -> datetime.date:
    """Gets the first day of the next month based of input"""
    if date.month == 12:
        next_month = datetime(date.year + 1, 1, 1)
    next_month = datetime(date.year, date.month + 1, 1)
    return next_month


def start_date(ao_start_date: str, first_work_date: str, employer_type: str):
    """Figure out the start date for the user"""
    if employer_type == "Publiek":
        return ao_start_date
    return first_work_date


def true_start_date(application_date: datetime.date, start_date: datetime.date) -> datetime.date:
    """If the difference between dates is more than 4 months, we return the first of the next month"""
    if is_within_4_months(start_date, application_date):
        return start_date
    return next_first_of_month(application_date)


def end_date(true_start_date: datetime.date, months_nl: Optional[int] = None) -> str:
    """ Calculates end date based on adding 5 years to the starting date, then subtracting the months minus 1 day"""
    start_date = true_start_date - timedelta(days=1)
    end_date = start_date + relativedelta(years=5)

    # if any months are given, subtract them from the end date
    if months_nl is not None:
        end_date = end_date - relativedelta(months=months_nl)

    return end_date.strftime("%d-%m-%Y")


def get_most_recent_date(date1: datetime.date, date2: datetime.date) -> datetime.date:
    """Returns the most recent date from two given dates."""
    return date1 if date1 > date2 else date2

def calculate_time_of_stay(start: pd.DataFrame, end: pd.DataFrame) -> str:
    """Calculates time between 2 dates"""
    delta = relativedelta(end, start)
    months = delta.years * 12 + delta.months
    days = delta.days

    month_text = "maand" if months == 1 else "maanden"
    day_text = "dag" if days == 1 else "dagen"

    parts = []
    if months:
        parts.append(f"{months} {month_text}")
    if days:
        parts.append(f"{days} {day_text}")

    return " + ".join(parts) if parts else "0 dagen"

def get_arrival_date_to_start_date_range(arrival_date: datetime.date, start_work_date: datetime.date) -> dict:
    """Gets the dates of the 2 variables in a list if the arrival date is before the start date"""
    last_day_before_work = start_work_date - timedelta(days=1) 

    if arrival_date >= last_day_before_work:
        return {}
    return {'start_date': arrival_date, 'end_date': last_day_before_work}