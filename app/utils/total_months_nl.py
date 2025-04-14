import pandas as pd
import ast
from utils import calculations
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import timedelta

def parse_date(date_str):
    """Parses a date string in the format 'dd-mm-yyyy' and returns a datetime object"""
    return pd.to_datetime(date_str, format="%d-%m-%Y")

def pair_dates(flat_list: list, stay_type: str) -> list[tuple]:
    """Pairs the dates in the list and gives them a type"""
    pairs = []    
    if flat_list == None:
        return pairs

    for i in range(0, len(flat_list), 2):
        start_date = parse_date(flat_list[i])
        end_date = parse_date(flat_list[i + 1])
        pairs.append((start_date, end_date, stay_type))
    return pairs

def string_to_literal_list(lst: list) -> bool:
    """Converts a string representation of a list to an actual list"""
    #FIXME need to fix these variable on submit of form, happens in more places
    if lst == "" or lst == None:
        return []
    return ast.literal_eval(lst)

def combine_periods(nl_lived: list, nl_worked: list, nl_visited: list, nl_arrival_till_start: list) -> list:
    """Combines the periods into a single sorted list"""
    #FIXME this string to list isnt good but works for now
    nl_lived = pair_dates(string_to_literal_list(nl_lived), "private")
    nl_worked = pair_dates(string_to_literal_list(nl_worked), "work")
    nl_visited = pair_dates(string_to_literal_list(nl_visited), "private")
    nl_arrival_till_start = pair_dates(nl_arrival_till_start, "private")

    all_periods = nl_lived + nl_worked + nl_visited + nl_arrival_till_start
    return sorted(all_periods)  

def filter_unique_dates(date_list: list[tuple]) -> list[tuple]:
    """
    Filter out unique dates for a list of possible overlapping dates
    
    Parameters:
    date_list (list): List of tuples (start_timestamp, end_timestamp, label)

    Returns:
    list: List of unique dates as datetime objects
    """
    # Extract all unique dates
    unique_dates = set()
    
    for start_timestamp, end_timestamp, _ in date_list:
        start_date = start_timestamp.date()
        end_date = end_timestamp.date()
        
        current_date = start_date
        while current_date <= end_date:
            unique_dates.add(current_date)
            current_date += timedelta(days=1)
    
    # If no dates, return empty list
    if not unique_dates:
        return []
    
    # Sort the unique dates
    sorted_dates = sorted(unique_dates)
    
    # Consolidate into continuous ranges
    consolidated_ranges = []
    range_start = sorted_dates[0]
    range_end = range_start
    
    for i in range(1, len(sorted_dates)):
        current_date = sorted_dates[i]
        
        # If there's a gap (more than 1 day difference), start a new range
        if (current_date - range_end).days > 1:
            consolidated_ranges.append((range_start, range_end))
            range_start = current_date
        
        range_end = current_date
    
    # Add the last range
    consolidated_ranges.append((range_start, range_end))
    
    return consolidated_ranges

def show_date_ranges_table(nl_list: list[tuple]) -> str:
    """Shows the date ranges in a fancy way for the user"""
    lst = []
    filtered_list = filter_unique_dates(nl_list)

    for start, end in filtered_list:
        lst_item = (f"{start.strftime('%d-%m-%Y')} t/m {end.strftime('%d-%m-%Y')} ({calculations.calculate_time_of_stay(start, end)})")
        lst.append(lst_item)
    return "<br>".join(lst)

def calc(nl_list: list[tuple]) -> int:
    """
    Calculates the total months in the Netherlands (excluding duplicate dates) 
    by applying specific filtering rules:
    1. Check if its 1 continous period only (max 3 months), we can ignore this period.
    2. Check for multiple stays that are longer than 42 days (6 weeks)
    3. Check for each year, if the sum of all the days is more than 42 private days OR 20 work days
    
    Args:
        nl_list: List of tuples containing (start_date, end_date, stay_type) for periods in NL
        
    Returns:
        int: Total number of valid months in NL (if there are atleast 6 weeks in a year, and the user 
         has been in the Netherlands for 1 day in one of the months, we count that month as a whole.
    """
    
    # Check if lists are empty
    if len(nl_list) == 0:
        return 0
    
    # An exception is one stay with less than 3 months
    if len(nl_list) == 1:
        start, end, _ = nl_list[0]
        delta = relativedelta(end, start)
        if delta.years == 0 and delta.months < 3:
            return 0
    
    # Separate private and work stays
    private_stays = [stay for stay in nl_list if stay[2] == 'private']
    work_stays = [stay for stay in nl_list if stay[2] == 'work']
    
    # Process private stays by years
    valid_days = set()  
    private_days_by_year = defaultdict(set)
    work_days_by_year = defaultdict(set)
    
    # Collect all private stay days by year
    for start, end, _ in private_stays:
        days = pd.date_range(start, end)
        
        # Track days by each year 
        for day in days:
            private_days_by_year[day.year].add(day)
        
        # If individual period is at least 6 weeks (42 days), count all days
        # This is one of the exceptions that if a period is continuos through multiple years,
        # we dont cut out between the years.
        if len(days) >= 42:
            valid_days.update(days)
    
    # Collect all work stay days by year
    for start, end, _ in work_stays:
        days = pd.date_range(start, end)
        
        # Track days by each year 
        for day in days:
            work_days_by_year[day.year].add(day)
    
    # Check each year to see if it qualifies
    all_years = set(private_days_by_year.keys()).union(set(work_days_by_year.keys()))
    
    for year in all_years:
        # If total private days in a year exceed 42 OR work days exceed 20, count all days in that year
        private_days_count = len(private_days_by_year[year])
        work_days_count = len(work_days_by_year[year])
        
        if private_days_count >= 42 or work_days_count >= 20:
            # Include all days from this year
            valid_days.update(private_days_by_year[year])
            valid_days.update(work_days_by_year[year])
    
    # Count unique months
    unique_months = {day.strftime('%Y-%m') for day in valid_days}
    total_months = len(unique_months)
    
    return total_months
