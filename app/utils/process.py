def date_ranges(raw_data):
    if not raw_data:
        return None

    processed = []
    for date_pair in raw_data:
        if isinstance(date_pair, list) and len(date_pair) == 2:
            start = date_pair[0].date() if hasattr(date_pair[0], 'date') else date_pair[0]
            end = date_pair[1].date() if hasattr(date_pair[1], 'date') else date_pair[1]
            processed.append({'start_date': start, 'end_date': end})
    return processed

def residences(raw_data):
    if not raw_data:
        return None
    
    processed = []
    for group in raw_data:
        if isinstance(group, list) and len(group) == 4:
            start = group[0].date() if hasattr(group[0], 'date') else group[0]
            end = group[1].date() if hasattr(group[1], 'date') else group[1]
            city = group[2] if isinstance(group[2], str) else str(group[2])
            country = group[3] if isinstance(group[3], str) else str(group[3])
            processed.append({'start_date': start, 'end_date': end, 'city': city, 'country': country})
    return processed

