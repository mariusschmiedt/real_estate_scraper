import os
import json

def getJob(provider_name, search_type, base_path):
    with open(os.path.join(base_path, 'jobs/jobs.json')) as f:
        jobs = json.load(f)

    house_type = None
    table_name = None
    if search_type == 'apartement_rent':
        house_type = 'apartment'
        table_name = 'rentals'
    if search_type == 'house_rent':
        house_type = 'house'
        table_name = 'rentals'
    if search_type == 'apartement_buy':
        house_type = 'apartment'
        table_name = 'sales'
    if search_type == 'house_buy':
        house_type = 'house'
        table_name = 'sales'
    if search_type == 'apartement_building_rent':
        house_type = 'apartement_building'
        table_name = 'sales'
    
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
        
        