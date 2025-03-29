from datetime import datetime
from dateutil.relativedelta import relativedelta


def create_table(data):
    def calculate_time_of_stay(start_date, end_date):
        fmt = "%d-%m-%Y"
        start = datetime.strptime(start_date, fmt)
        end = datetime.strptime(end_date, fmt)
        delta = relativedelta(end, start)
        return f"{delta.years * 12 + delta.months} maanden + {delta.days} dagen"

    rows = []
    for entry in data:
        if isinstance(entry, list) and len(entry) >= 4:
            start_date, end_date, city, country = entry[:4]
            time_of_stay = calculate_time_of_stay(start_date, end_date)
            row = f"<br> - {start_date} t/m {end_date} in {city}, {country} ({time_of_stay})."
            rows.append(row)
        else:
            print("Invalid entry:", entry)  # Debugging
    return "\n".join(rows)
