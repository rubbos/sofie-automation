from datetime import datetime

def transform_date(date):
    """Convert different date formats into dd-mm-yyyy"""
    date_formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d-%b-%Y",
        "%d %b %Y",
        "%d-%B-%Y",
        "%d %B %Y",
        "%d-%b-%y",
        "%d %b %y",
        "%d-%m-%y",
        "%d/%m/%y",
        "%d.%m.%y",
    ]

    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date, date_format)
            return parsed_date.strftime("%d-%m-%Y")
        except ValueError:
            pass
    return date


def clean_locations(dates, locations):
    """
    Every location has a start date and end date.
    This cleans up the excess locations list.
    """
    if len(dates) % 2 == 0:
        if len(dates) <= 2:
            return locations[:1]
        return locations[: -len(dates) // 2]
