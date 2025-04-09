from datetime import datetime, timedelta
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


def signed_location(signed_date: str, place_of_residence: list, arrival_date: str):
    """Finds the location where the given signed date falls within the start and end date ranges"""
    query_date = datetime.strptime(signed_date, "%d-%m-%Y")
    arrival_nl = datetime.strptime(arrival_date, "%d-%m-%Y")
 
    for entry in place_of_residence:
        start_date = datetime.strptime(entry[0], "%d-%m-%Y")
        end_date = datetime.strptime(entry[1], "%d-%m-%Y")

        if start_date <= query_date <= end_date:
            return f"{entry[2]}, {entry[3]}"
        elif query_date >= arrival_nl:
            return "Nederland"
    
    return "Onbekend"


def salarynorm(ufo_code: str) -> str:
    """If the users job position is an academic position, its an exception"""
    if ufo_code.startswith("01"):
        return "Wetenschappelijk O&O"
    return "Regulier"


def is_within_4_months(date1_str, date2_str, date_format="%d-%m-%Y") -> bool:
    """Compare 2 dates and see if the time between is less than 4 months"""
    date1 = datetime.strptime(date1_str, date_format)
    date2 = datetime.strptime(date2_str, date_format)

    # Calculate the exact cutoff date
    four_months_later = date1 + relativedelta(months=4)
    cutoff_date = four_months_later - relativedelta(days=1)

    # Check if date2 is within the 4-month range
    return date2 <= cutoff_date


def next_first_of_month(date: str) -> str:
    """Gets the first day of the next month based of input"""
    try:
        # Parse the input date
        date_obj = datetime.strptime(date, "%d-%m-%Y")

        # Determine the first date of the next month
        if date_obj.month == 12:
            next_month = datetime(date_obj.year + 1, 1, 1)
        else:
            next_month = datetime(date_obj.year, date_obj.month + 1, 1)

        return next_month.strftime("%d-%m-%Y")
    except ValueError:
        return "Invalid date format. Please use dd-mm-yyyy."


def start_date(ao_start_date: str, first_work_date: str, employer_type: str):
    """Figure out the start date for the user"""
    if employer_type == "Publiek":
        return ao_start_date
    return first_work_date


def true_start_date(application_date: str, start_date: str) -> str:
    """If the difference between dates is more than 4 months, we return the first of the next month"""
    if is_within_4_months(start_date, application_date):
        return start_date
    return next_first_of_month(application_date)


def end_date(true_start_date: str, months_nl: Optional[int] = None) -> str:
    """ Calculates end date based on adding 5 years to the starting date, then subtracting the months minus 1 day"""
    start_date = datetime.strptime(true_start_date, "%d-%m-%Y") - timedelta(days=1)
    end_date = start_date + relativedelta(years=5)

    # if any months are given, subtract them from the end date
    if months_nl is not None:
        end_date = end_date - relativedelta(months=months_nl)

    return end_date.strftime("%d-%m-%Y")


def get_most_recent_date(date1: str, date2: str) -> str:
    """
    Returns the most recent date from two given dates.

    Args:
        date1 (str): First date in the format dd-mm-yyyy.
        date2 (str): Second date in the format dd-mm-yyyy.

    Returns:
        str: The most recent date.
    """
    date_format = "%d-%m-%Y"
    date1_parsed = datetime.strptime(date1, date_format)
    date2_parsed = datetime.strptime(date2, date_format)

    return date1 if date1_parsed > date2_parsed else date2

def calculate_time_of_stay(start: pd.DataFrame, end: pd.DataFrame) -> str:
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