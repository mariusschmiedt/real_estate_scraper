import os
import json

def getJob(provider_name, search_type, base_path):
    with open(os.path.join(base_path, 'jobs/jobs.json')) as f:
        jobs = json.load(f)

    house_type = None
    table_name = None
    offer_type = None
    if search_type == 'apartement_rent':
        house_type = 'apartement'
        table_name = 'rent_homes'
        offer_type = 'rent'
    if search_type == 'house_rent':
        house_type = 'house'
        table_name = 'rent_homes'
        offer_type = 'rent'
    if search_type == 'apartement_buy':
        house_type = 'apartement'
        table_name = 'buy_homes'
        offer_type = 'buy'
    if search_type == 'house_buy':
        house_type = 'house'
        table_name = 'buy_homes'
        offer_type = 'buy'
    
    if house_type is None or table_name is None or offer_type is None:
        raise Exception('Job search criteria not defined correctly.')


    country = jobs[provider_name][search_type]['country']
    url = jobs[provider_name][search_type]['url']

    job = {
        "url": url,
        "house_type": house_type,
        "table_name": table_name,
        "country": country,
        "offer_type": offer_type
    }
    return job
        
        