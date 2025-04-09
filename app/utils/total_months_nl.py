import pandas as pd
import ast
from collections import defaultdict

def parse_date(date_str):
    """Parses a date string in the format 'dd-mm-yyyy' and returns a datetime object"""
    return pd.to_datetime(date_str, format="%d-%m-%Y")

def pair_dates(flat_list: list, stay_type: str) -> list[tuple]:
    """Pairs the dates in the list and gives them a type"""
    pairs = []    
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

#NOTE Does not check the period from the arrival date to start of work. 
def combine_periods(nl_lived: list, nl_worked: list, nl_visited: list) -> list:
    """Combines the periods into a single sorted list"""
    #FIXME this string to list isnt good but works for now
    nl_lived = string_to_literal_list(nl_lived)
    nl_worked = string_to_literal_list(nl_worked)
    nl_visited = string_to_literal_list(nl_visited)

    all_periods = pair_dates((nl_lived), "private") + pair_dates(nl_worked, "work") + pair_dates(nl_visited, "private")
    return sorted(all_periods)  

#NOTE This still needs refinement for the period between arrival date and start of work. 
def calc(nl_list: list[tuple]) -> int:
    """
    Calculates the total months in the Netherlands in the last 25 years,
    applying specific filtering rules:
    1. For private stays:
       a. Count all days in periods of at least 6 weeks (42 days)
       b. If total days in a year exceed 6 weeks, count all private stay days in that year
    2. Allow one period of less than 3 months (90 days) in the entire 25-year span
       if it doesn't meet the above criteria
    3. For work stays: Count only years with at least 20 days of work
    
    Args:
        nl_list: List of tuples containing (start_date, end_date, stay_type) for periods in NL
        
    Returns:
        int: Total number of valid months in NL (if there are atleast than 6 weeks, and the user 
         has been in the Netherlands for 1 day in 1 single month, we count that month as a whole.
    """
    
    # Separate private and work stays
    private_stays = [stay for stay in nl_list if stay[2] == 'private']
    work_stays = [stay for stay in nl_list if stay[2] == 'work']
    
    # First, process long private stays (≥ 6 weeks)
    valid_private_days = set()
    all_private_days_by_year = defaultdict(set)
    
    # Collect all private stay days by year
    for start, end, _ in private_stays:
        days = pd.date_range(start, end)
        
        # Track days by year for consolidation
        for day in days:
            all_private_days_by_year[day.year].add(day)
        
        # Rule 1a: If individual period is at least 6 weeks (42 days), count all days
        if len(days) >= 42:
            valid_private_days.update(days)
    
    # Rule 1b: If total days in a year exceed 6 weeks, count all days in that year
    for year, days in all_private_days_by_year.items():
        if len(days) >= 42:
            valid_private_days.update(days)
    
    # Find candidate for short period exemption from remaining days
    remaining_private_days = set()
    for start, end, _ in private_stays:
        days = pd.date_range(start, end)
        for day in days:
            if day not in valid_private_days:
                remaining_private_days.add(day)
    
    # Rule 2: Apply short period exemption if available
    if len(remaining_private_days) > 0 and len(remaining_private_days) < 90:
        # Group remaining days into consecutive periods
        sorted_days = sorted(remaining_private_days)
        periods = []
        current_period = []
        
        for i, day in enumerate(sorted_days):
            if i == 0 or (day - sorted_days[i-1]).days == 1:
                current_period.append(day)
            else:
                periods.append(current_period)
                current_period = [day]
                
        if current_period:
            periods.append(current_period)
        
        # Find the longest period under 90 days
        longest_period = max(periods, key=len, default=[])
        if len(longest_period) > 0 and len(longest_period) < 90:
            valid_private_days.update(longest_period)
    
    # Process work stays by year
    work_days_by_year = defaultdict(set)
    for start, end, _ in work_stays:
        days = pd.date_range(start, end)
        for day in days:
            work_days_by_year[day.year].add(day)
    
    # Rule 3: Add work days for years with at least 20 days
    valid_work_days = set()
    for year, days in work_days_by_year.items():
        if len(days) >= 20:
            valid_work_days.update(days)
    
    # Combine all valid days
    all_valid_days = valid_private_days.union(valid_work_days)
    
    # Count unique months
    unique_months = {day.strftime('%Y-%m') for day in all_valid_days}
    total_months = len(unique_months)
    
    return total_months