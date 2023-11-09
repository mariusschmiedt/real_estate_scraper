import re
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.Box-sc-wfmb7k-0 ResultListAdRowLayout*',
            "sortByDateParam": 'sort=1',
            "paginate": 'page=',
            "crawlFields": {
                "provider_id": '@id',
                "price": 'span@data-testid=search-result-entry-price*',
                "size": 'div@data-testid=search-result-entry-teaser*:2c',
                "rooms": 'div@data-testid=search-result-entry-teaser*:3c',
                "title": 'h3.Text-sc-10o2fdq-0 cAEnXu',
                "url": 'a@href',
                "address_detected": 'span.Text-sc-10o2fdq-0 gJVhIs@aria-label',
            },
            "num_listings": 'h1.Text-sc-10o2fdq-0 djhjqk:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Willhaben AT',
            "baseUrl": 'https://www.willhaben.at/',
            "id": 'willhaben_at',
        }

    def normalize(self, o):
        o['address_detected'] = o['address_detected'].replace('Ort', '').strip()
        if ',' in o['address_detected']:
            o['address_detected'] = o['address_detected'].split(',')[0]
        
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        else:
            o['city'] = o['address_detected']
        

        o['url'] = self.metaInformation['baseUrl'][0:-1] + o["url"]

        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = numConvert_de(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = numConvert_de(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])
        o['rooms'] = numConvert_de(o['rooms'])

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o