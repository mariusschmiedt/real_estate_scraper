import re
from ...utils import findPostalCodeInAddress

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'script@type=application/json',
            "jsonContainer": 'props.pageProps.searchData.ads',
            "sortByDateParam": '',
            "paginate": 'page=',
            "crawlFields": {
                "provider_id": 'list_id',
                "price": 'price',
                "size": 'attributes',
                "rooms": 'attributes',
                "title": 'subject',
                "url": 'url',
                "address_detected": 'location',
                "in_db_since": 'first_publication_date',
            },
            "num_listings": 'props.pageProps.searchData.total',
            "maxPageNum": 'props.pageProps.searchData.max_pages',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Leboncoin FR',
            "baseUrl": 'https://www.leboncoin.fr/',
            "id": 'leboncoin_fr',
        }

    def normalize(self, o):
        address = o['address_detected']
        if 'city_label' in address:
            o['address_detected'] = address['city_label']
        else:
            if 'zipcode' in address:
                o['address_detected'] = address['zipcode']
        
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['currency'] = 'EUR'

        size_information = o['size']
        for s in size_information:
            if 'key' in s:
                if s['key'] == 'rooms':
                    o['rooms'] = s['value']
                if s['key'] == 'square':
                    o['size'] = s['value']

        if type(o['rooms']) == list:
            o['rooms'] = ''
        
        if type(o['size']) == list:
            o['size'] = ''

        o['size_unit'] = 'm^2'

        if type(o['price']) == list:
            o['price'] = o['price'][0]
        
        # remove time from date string
        if o['in_db_since'] != '':
            o['in_db_since'] = o['in_db_since'].split(' ')[0]
        else:
            o['in_db_since'] = ''

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o