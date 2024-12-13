from datetime import datetime
from dateutil.relativedelta import relativedelta


def create_table(data):
    headers = [
        "Start Date",
        "End Date",
        "City",
        "Country",
        "Time of Stay (months, days)",
    ]

    def calculate_time_of_stay(start_date, end_date):
        fmt = "%d-%m-%Y"
        start = datetime.strptime(start_date, fmt)
        end = datetime.strptime(end_date, fmt)
        delta = relativedelta(end, start)
        return f"{delta.years * 12 + delta.months} months, {delta.days} days"

    html = '<table border="1" style="border-collapse: collapse; text-align: left;">\n'
    html += "  <tr>\n"
    for header in headers:
        html += f"    <th>{header}</th>\n"
    html += "  </tr>\n"

    for entry in data:
        print("Processing entry:", entry)  # Debugging
        if isinstance(entry, list) and len(entry) >= 4:
            start_date, end_date, city, country = entry[:4]
            time_of_stay = calculate_time_of_stay(start_date, end_date)
            html += "  <tr>\n"
            html += f"    <td>{start_date}</td>\n"
            html += f"    <td>{end_date}</td>\n"
            html += f"    <td>{city}</td>\n"
            html += f"    <td>{country}</td>\n"
            html += f"    <td>{time_of_stay}</td>\n"
            html += "  </tr>\n"
        else:
            print("Invalid entry:", entry)  # Debugging

    html += "</table>"
    return html


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
