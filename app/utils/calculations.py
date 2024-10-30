from datetime import datetime


def signed_outside_nl(signed_date: str, arrival_date: str) -> bool:
    date_format = "%d-%m-%Y"
    date1 = datetime.strptime(signed_date, date_format)
    date2 = datetime.strptime(arrival_date, date_format)

    if date1 >= date2:
        return False
    return True


def salarynorm(ufo_code: str) -> str:
    if ufo_code.startswith("01"):
        return "Wetenschappelijk O&O"
    return "Regulier"
