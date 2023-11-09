
import re
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'li.result-list__listing',
            "sortByDateParam": 'sorting=2',
            "paginate": 'pagenumber=',
            "crawlFields": {
                "provider_id": 'article.result-list-entry@data-obid',
                "price": 'dd.font-highlight font-tabular:1c',
                "size": 'dd.font-highlight font-tabular:2c',
                "rooms": 'span.onlySmall',
                "title": 'a.result-list-entry__brand-title-container',
                "url": 'a.result-list-entry__brand-title-container@href',
                "address_detected": 'button.result-list-entry__map-link',
            },
            "num_listings": 'span.resultlist-resultCount',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immoscout',
            "baseUrl": 'https://www.immobilienscout24.de',
            "id": 'immoscout_de',
        }

    def normalize(self, o):
        url = self.metaInformation['baseUrl'] + o["url"].replace(o["url"][0:o["url"].index("/expose")+1], '')

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if ',' in o['address_detected']:
            o['city'] = o['address_detected'].split(',')[-1]
            o['district'] = o['address_detected'].split(',')[-2]
        else:
            o['city'] = o['address_detected']

        if 'city' in o:
            if 'Kreis' in o['city'] and 'district' in o:
                o['city'] = o['district']
                o['district'] = ''
        
        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])


        o['price'] = numConvert_de(o['price'])
        o['size'] = numConvert_de(o['size'])
        o['rooms'] = numConvert_de(o['rooms'])
        o['url'] = url
        return o
    
    def numConvert(self, value):
        comma_count = value.count(',')
        dot_count = value.count('.')

        if comma_count == 1 and dot_count == 0:
            value = value.replace(',', '.')
        elif dot_count >= 1 and comma_count == 1:
            value = value.replace('.', '').replace(',', '.')
        elif dot_count >= 1 and comma_count == 0:
            value = value.replace('.', '')
        return value