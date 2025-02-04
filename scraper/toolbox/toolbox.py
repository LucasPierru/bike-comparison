from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from itertools import tee, islice, chain

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
