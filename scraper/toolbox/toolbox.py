from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from itertools import tee, islice, chain
import re

def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

def replace_query_param(url, param, new_value):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Update or add the query parameter
    query_params[param] = [new_value]
    
    # Rebuild the query string
    new_query_string = urlencode(query_params, doseq=True)
    
    # Construct the new URL
    new_url = urlunparse(parsed_url._replace(query=new_query_string))
    
    return new_url

def parse_sizes(text):
    # Normalize whitespace and remove "Size:" if present
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^Size:\s*', '', text, flags=re.I)

    # Define valid size patterns (numbers & letter sizes like S, M, L, XL, XXL, etc.)
    size_pattern = r'(?:(?:\d{2})|(?:XXL|XL|L|M|S))'

    # Extract sizes at the **start** of the string
    match = re.match(rf'^({size_pattern}(?:,\s*{size_pattern})*)(.*)', text)

    if match:
        size_text = match.group(1).strip()  # Extract size part
        extra_info = match.group(2).strip() if match.group(2) else None  # Extract remaining details

        # Split sizes properly while avoiding merging issues
        sizes = [s.strip() for s in size_text.split(',') if s]

        return {
            "sizes": sizes,
            "value": extra_info if extra_info else None
        }

    return {"sizes": [], "value": None}  # Default if no match

def extract_price(price_str):
    # Remove the dollar sign and commas
    price_cleaned = re.sub(r'[^\d.]', '', price_str)
    return float(price_cleaned)

def find_brand_in_component(component_string, bike_brands):
    # Loop through each brand object and check if the name exists in the component string
    for brand in bike_brands:
        # Check if the brand name (case-insensitive) is present in the component string
        if re.search(r'\b' + re.escape(brand['name']) + r'\b', component_string, re.IGNORECASE):
            return brand  # Return the full brand object
    return None  # If no brand is found