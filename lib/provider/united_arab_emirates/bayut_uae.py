import re
from ...utils import getSizeUnit

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'script@type=application/ld+json',
            "jsonContainer": 'itemListElement',
            "sortByDateParam": 'sort=date_desc',
            "paginate": 'page-',
            "crawlFields": {
                "provider_id": 'mainEntity.url',
                "price": 'mainEntity.offers',
                "size": 'mainEntity.floorSize.value',
                "size_unit": 'mainEntity.floorSize.unitText',
                "rooms": 'mainEntity.numberOfRooms.value',
                "title": 'mainEntity.name',
                "url": 'mainEntity.url',
                "address_detected": 'mainEntity.geo',
                "type": 'mainEntity.@type'
            },
            "num_listings": 'numberOfItems',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Bayut',
            "baseUrl": 'https://www.bayut.com/',
            "id": 'bayut_uae',
        }

    def normalize(self, o):
        o['provider_id'] = o['provider_id'].split('/')[-1].replace('.html', '').replace('details-', '')

        if type(o['price']) == list:
            o['price'] = o['price'][0]
            if type(o['price']) == dict:
                o['price'] = o['price']['priceSpecification']
                price = ''
                if 'price' in o['price']:
                    price = o['price']['price']
                if 'unitText' in o['price']:
                    num = False
                    try:
                        float(price)
                        num = True
                    except:
                        pass
                    if num:
                        price = float(price)
                        if o['price']['unitText'] == 'yearly':
                            price = price / 12
                        if o['price']['unitText'] == 'weekly':
                            price = price* 52 / 12
                        if o['price']['unitText'] == 'daily':
                            price = price * 365 / 12
                        price = str(round(price, 2))
                o['currency'] = o['price']['priceCurrency']
                o['price'] = price
            else:
                o['price'] = ''
        else:
            o['price'] = ''

        if 'type' in o:
            if type(o['type']) == list:
                o['type'] = o['type'][-1].lower()
                if 'residence' == o['type']:
                    o['type'] = 'apartment'

        o['size_unit'] = getSizeUnit(o['size_unit'])

        o['size'] = o['size'].replace(',', '')

        if o['size_unit'] == 'sqft':
            o['size'] = str(round(float(o['size']) / 10.764, 2))
            o['size_unit'] = 'm^2'

        o['rooms'] = o['rooms'].replace(',', '')

        address = o['address_detected']

        lat = str(address['latitude'])
        lon = str(address['longitude'])

        o['address_detected'] = 'lat: ' + lat + ', ' + 'lon: ' + lon
        
        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o