

def getJobs(jobs, provider_name):
    job_list = list()
    for job in jobs[provider_name].keys():
        provider_types = jobs[provider_name][job]
        house_type = None
        table_name = None
        country = None
        url = None
        number_format = None
        if job == 'apartement_rent':
            house_type = 'apartement'
            table_name = 'rent_homes'
        if job == 'house_rent':
            house_type = 'house'
            table_name = 'rent_homes'
        if job == 'apartement_buy':
            house_type = 'apartement'
            table_name = 'buy_homes'
        if job == 'house_buy':
            house_type = 'house'
            table_name = 'buy_homes'
        if 'url' in provider_types.keys():
            url = provider_types['url']
        if 'country' in provider_types.keys():
            country = provider_types['country']
        if 'number_format' in provider_types.keys():
            number_format = provider_types['number_format']
        job_dict = {
            "url": url,
            "house_type": house_type,
            "table_name": table_name,
            "country": country,
            "number_format": number_format
        }
        job_list.append(job_dict)
    return job_list
        
        