import pandas as pd

def parse_date(date_str):
    """Parses a date string in the format 'dd-mm-yyyy' and returns a datetime object"""
    return pd.to_datetime(date_str, format="%d-%m-%Y")

def pair_dates(flat_list: list) -> list[tuple]:
    """Pairs the dates in the list and calculates the duration in days"""
    pairs = []    
    for i in range(0, len(flat_list), 2):
        start_date = parse_date(flat_list[i])
        end_date = parse_date(flat_list[i + 1])
        duration = (end_date - start_date).days
        pairs.append((start_date, end_date, duration))
    return pairs

#NOTE Does not check the period from the arrival date to start of work. 
def combine_periods(nl_lived: list, nl_worked: list, nl_visited: list) -> list:
    """Combines the periods into a single sorted list"""
    all_periods = pair_dates(nl_lived) + pair_dates(nl_worked) + pair_dates(nl_visited)
    return sorted(all_periods, key=lambda x: x[2], reverse=True)  # Sort by duration descending

def get_total_months_in_nl(nl_list: list[tuple]) -> int:
    """Calculates the total months in the Netherlands in the last 25 years"""
    return ...

def more_than_6_weeks_in_a_year(nl_list: list[tuple]) -> bool:
    """"Check if the total periods in a year is more than 6 weeks, else ignore the period"""
    return ...

# testvalues
all_periods_range = ['04-03-2020', '11-09-2023']  
work_periods_ranges = ['06-04-2021', '01-11-2021', '12-03-2021', '31-03-2021', '09-03-2020', '30-11-2020']
private_periods_range = ['04-03-2020', '11-09-2023']  
print(combine_periods(all_periods_range, work_periods_ranges, private_periods_range))
    