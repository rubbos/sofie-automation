from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


def dict_to_table(data: dict):
    df = pd.DataFrame(
        {
            "KEY": list(data.keys()),
            "TYPE": [item[0] if len(item[0]) > 0 else None for item in data.values()],
            "VALUE": [
                item[1] if item[1] is not None and len(item[1]) > 0 else None
                for item in data.values()
            ],
        }
    )
    return df


def transform_date(date: str) -> str:
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


def clean_locations(dates: list[str], locations: list[str]) -> list[str]:
    """
    Every location has a start date and end date.
    This cleans up the excess locations list while extracting.
    """
    if len(dates) % 2 == 0:
        if len(dates) <= 2:
            return locations[:1]
        return locations[: -len(dates) // 2]


def months_and_days_between_dates(first_date: str, last_date: str, round=False) -> str:
    date_format = "%d-%m-%Y"
    try:
        date1 = datetime.strptime(first_date, date_format)
        date2 = datetime.strptime(last_date, date_format)
    except ValueError:
        return "{date1}, {date2}: Error"
    months = (date2.year - date1.year) * 12 + (date2.month - date1.month)

    # If date2's day is less than date1's day, we subtract one month and calculate the day difference
    if date2.day < date1.day:
        months -= 1
        # Calculate the adjusted date by subtracting 1 month from date2
        adjusted_date = date2 - relativedelta(months=1)
        days = (date2 - adjusted_date.replace(day=date1.day)).days
    else:
        # If date2's day is greater than or equal to date1's day, calculate day difference directly
        adjusted_date = date1 + relativedelta(months=months)
        days = (date2 - adjusted_date).days

    month_str = check_string_plural("maand", months)
    day_str = check_string_plural("dag", days)

    if not round:
        if months == 0:
            return f"{days} {day_str}"
        return f"{months} {month_str} + {days} {day_str}"
    return f"{round_months(months, days)} {month_str}"


def check_string_plural(string: str, amount: int) -> str:
    if amount > 1:
        return f"{string}en"
    return string


def round_months(months: int, days: int) -> int:
    if days > 0:
        return months + 1
    return months
