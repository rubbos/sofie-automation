from datetime import datetime
from dateutil.relativedelta import relativedelta


def create_table(data):
    def calculate_time_of_stay(start_date, end_date):
        fmt = "%d-%m-%Y"
        start = datetime.strptime(start_date, fmt)
        end = datetime.strptime(end_date, fmt)
        delta = relativedelta(end, start)
        return f"{delta.years * 12 + delta.months}m + {delta.days}d"

    rows = []
    for entry in data:
        if isinstance(entry, list) and len(entry) >= 4:
            start_date, end_date, city, country = entry[:4]
            time_of_stay = calculate_time_of_stay(start_date, end_date)
            row = f"<br>{city}, {country} van {start_date} t/m {end_date}({time_of_stay})."
            rows.append(row)
        else:
            print("Invalid entry:", entry)  # Debugging
    return "\n".join(rows)


def convert_string_to_data(string_data):
    # Remove surrounding brackets and split by rows
    string_data = string_data.strip("[]")
    rows = string_data.split("], [")

    # Convert each row into a list
    data = []
    for row in rows:
        row = row.strip("[]")
        entries = row.split(", ")
        data.append([entry.strip("'\"") for entry in entries])
    return data
