from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


def create_table(data, ao_start_date):
    def calculate_time_of_stay(start_date, end_date, ao_start_date):
        fmt = "%d-%m-%Y"
        start = datetime.strptime(start_date, fmt)
        contract_start = datetime.strptime(ao_start_date, fmt)
        two_year_prior_contract_start = contract_start - relativedelta(years=2)
        
        if start < two_year_prior_contract_start:
            start = two_year_prior_contract_start

        end = datetime.strptime(end_date, fmt)
        delta = relativedelta(end, start)
        return f"{delta.years * 12 + delta.months} maanden + {delta.days} dagen"

    rows = []
    for entry in data:
        if isinstance(entry, list) and len(entry) >= 4:
            start_date, end_date, city, country = entry[:4]
            time_of_stay = calculate_time_of_stay(start_date, end_date, ao_start_date)
            row = f"<br> - {start_date} t/m {end_date} in {city}, {country} ({time_of_stay})."
            rows.append(row)
        else:
            return
    return "\n".join(rows)

