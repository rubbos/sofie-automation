from datetime import datetime
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
