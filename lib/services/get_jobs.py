import os
import json

def getJob(provider_name, search_type, base_path):
    with open(os.path.join(base_path, 'jobs/jobs.json')) as f:
        jobs = json.load(f)

    house_type = None
    table_name = None
    if search_type.endswith('rent'):
        table_name = 'rentals'
    if search_type.endswith('buy'):
        table_name = 'sales'
    
    house_type = search_type.replace('_rent', '').replace('_buy', '')

    if house_type == 'townhouse' or house_type == 'bungalow':
        house_type = 'house'
    if house_type == 'duplex_buy' or house_type == 'floor' or house_type == 'half_floor' or house_type == 'bulk_unit':
        house_type = 'apartement_building'
    
    if house_type is None or table_name is None:
        raise Exception('Job search criteria not defined correctly.')


    country = jobs[provider_name][search_type]['country']
    url = jobs[provider_name][search_type]['url']

    job = {
        "url": url,
        "house_type": house_type,
        "table_name": table_name,
        "country": country,
    }
    return job
        
        