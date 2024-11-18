from datetime import datetime
from dateutil.relativedelta import relativedelta


def signed_outside_nl(signed_date: str, arrival_date: str) -> bool:
    """If user signed the contract in the Netherlands, a wilsovereenkomst is needed"""
    date_format = "%d-%m-%Y"
    print(arrival_date)
    date1 = datetime.strptime(signed_date, date_format)
    date2 = datetime.strptime(arrival_date, date_format)

    if date1 >= date2:
        return False
    return True


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


def next_first_of_month() -> str:
    """Gets the first date of the next month"""
    today = datetime.today()
    if today.month == 12:
        next_month = datetime(today.year + 1, 1, 1)
    else:
        next_month = datetime(today.year, today.month + 1, 1)
    return next_month.strftime("%d-%m-%Y")


def start_date(application_upload_date: str, start_date: str) -> str:
    """If the difference between dates is more than 4 months, we return the first of the next mont h"""
    if is_within_4_months(start_date, application_upload_date):
        return start_date
    return next_first_of_month()
