from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    
    try:
        #handles datetime strings
        if 'T' in str(date_str):
            date_str = str(date_str).split('T')[0]
        if '+' in str(date_str):
            date_str = str(date_str).split('+')[0]
        
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
    except ValueError:
        return None

def extract_dates(obj):
    #Extract all date values from an object
    dates = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            # Look for common date field names
            if any(date_key in key.lower() for date_key in ["date", "datetime", "published", "updated", "contextdate"]):
                parsed = parse_date(str(value))
                if parsed:
                    dates.append(parsed)
            # Recursively check nested objects
            dates.extend(extract_dates(value))
    elif isinstance(obj, list):
        for item in obj:
            dates.extend(extract_dates(item))
    elif isinstance(obj, str):
        parsed = parse_date(obj)
        if parsed:
            dates.append(parsed)
    
    return dates

def matches_date_range(obj, before_date, after_date):
    #check if obj matches
    dates = extract_dates(obj)
    
    if not dates:
        return True
    
    for date in dates:
        if before_date and date > before_date:
            continue
        if after_date and date < after_date:
            continue
        return True
    
    return False

def search_in_value(value, query):
    query_lower = query.lower()
    
    if isinstance(value, str):
        return query_lower in value.lower()
    elif isinstance(value, dict):
        return any(search_in_value(v, query) for v in value.values())
    elif isinstance(value, list):
        return any(search_in_value(item, query) for item in value)
    else:
        return query_lower in str(value).lower()

def filter_objects(data, query, before_date, after_date):
    if isinstance(data, dict):
        filtered = {}
        for key, value in data.items():
            if isinstance(value, list):
                #filter list items
                filtered_list = []
                for item in value:
                    matches_query = not query or search_in_value(item, query)
                    matches_dates = matches_date_range(item, before_date, after_date)
                    if matches_query and matches_dates:
                        filtered_list.append(item)
                if filtered_list:
                    filtered[key] = filtered_list
            elif isinstance(value, dict):
                filtered_value = filter_objects(value, query, before_date, after_date)
                if filtered_value:
                    filtered[key] = filtered_value
            else:
                matches_query = not query or search_in_value(value, query)
                matches_dates = matches_date_range(value, before_date, after_date)
                if matches_query and matches_dates:
                    filtered[key] = value
        return filtered
    elif isinstance(data, list): #i do not even remember how all this works
        filtered_list = []
        for item in data:
            matches_query = not query or search_in_value(item, query)
            matches_dates = matches_date_range(item, before_date, after_date)
            if matches_query and matches_dates:
                filtered_list.append(item)
        return filtered_list
    else:
        matches_query = not query or search_in_value(data, query)
        matches_dates = matches_date_range(data, before_date, after_date)
        return data if (matches_query and matches_dates) else None