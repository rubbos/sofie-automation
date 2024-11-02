from datetime import datetime


def signed_outside_nl(signed_date: str, arrival_date: str) -> bool:
    """If user signed the contract in the Netherlands, a wilsovereenkomst is needed"""
    date_format = "%d-%m-%Y"
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


def start_date(application_upload_date: str, start_date, str) -> bool:
    """If the difference between dates is less than 4 months, its an exception"""
    ...
