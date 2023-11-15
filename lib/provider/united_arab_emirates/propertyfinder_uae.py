import re
from ...utils import getSizeUnit

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'script@type=application/json',
            "jsonContainer": 'props.pageProps.searchResult.properties',
            "sortByDateParam": 'ob=nd',
            "paginate": 'page=',
            "crawlFields": {
                "provider_id": 'id',
                "price": 'price',
                "currency": 'price.currency',
                "size": 'size.value',
                "size_unit": 'size.unit',
                "rooms": 'bedrooms',
                "title": 'title',
                "url": 'share_url',
                "address_detected": 'location',
                "in_db_since": 'listed_date'
            },
            "num_listings": 'props.pageProps.searchResult.meta.total_count',
            "listings_per_page": 'props.pageProps.searchResult.meta.per_page',
            "maxPageNum": 'props.pageProps.searchResult.meta.page_count',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Property Finder UAE',
            "baseUrl": 'https://www.propertyfinder.ae/',
            "id": 'propertyfinder_uae',
        }

    def normalize(self, o):

        if type(o['price']) == dict:
            price = ''
            if 'value' in o['price']:
                price = o['price']['value']
            if 'period' in o['price']:
                num = False
                try:
                    float(price)
                    num = True
                except:
                    pass
                if num:
                    price = float(price)
                    if o['price']['period'] == 'yearly':
                        price = price / 12
                    if o['price']['period'] == 'weekly':
                        price = price* 52 / 12
                    if o['price']['period'] == 'daily':
                        price = price * 365 / 12
                    price = str(round(price, 2))
            o['currency'] = o['price']['currency']
            o['price'] = price
        else:
            o['price'] = ''

        o['size_unit'] = getSizeUnit(o['size_unit'])

        o['size'] = str(o['size'])

        if o['size_unit'] == 'sqft':
            o['size'] = str(round(float(o['size']) / 10.764, 2))
            o['size_unit'] = 'm^2'

        o['rooms'] = o['rooms'].replace(',', '')
        try:
            float(o['rooms'])
        except:
            o['rooms'] = '1'

        # remove time from date string
        if o['in_db_since'] != '':
            o['in_db_since'] = o['in_db_since'].split('T')[0]
        
        address = o['address_detected']

        lat = str(address['coordinates']['lat'])
        lon = str(address['coordinates']['lon'])

        address_string = ''
        if 'full_name' in address:
            address_string = ', ' + address['full_name']

        o['address_detected'] = 'lat: ' + lat + ', ' + 'lon: ' + lon + address_string
        
        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o