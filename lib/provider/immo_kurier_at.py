import re
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.item-wrap js-serp-item',
            "sortByDateParam": 's=most_recently_updated_first',
            "crawlFields": {
                "provider_id": '@data-id',
                "price": 'div.item__spec item-spec-price',
                "size": 'div.item__spec item-spec-area',
                "rooms": 'div.item__spec item-spec-rooms',
                "title": 'a.js-item-title-link:1c',
                "url": 'a.js-item-title-link@href',
                "address_detected": 'div.item__locality',
            },
            "num_listings": 'li.breadcrumb-item active:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Immo Kurier AT',
            "baseUrl": 'https://immo.kurier.at/',
            "id": 'immo_kurier_at',
            "paginate": 'page=',
        }

    def init(self, sourceConfig, blacklist=None):
        self.config["enabled"] = sourceConfig["enabled"]
        self.config["search_url"] = sourceConfig["search_url"]
        if blacklist is None:
            blacklist = []
        self.appliedBlackList = blacklist
    
    def nullOrEmpty(self, val):
        nullVal = False
        if val == None:
            nullVal = True
        else:
            if len(val) == 0:
                nullVal = True
        return nullVal

    def normalize(self, o):
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])
        if o['postalcode'] != '':
            if ',' in o['address_detected']:
                o['city'] = o['address_detected'].split(',')[-1].strip().replace(o['postalcode'], '').strip()
            else:
                o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['url'] = self.metaInformation['baseUrl'] + 'immobilien/' + o["provider_id"]
        
        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = self.numConvert(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = self.numConvert(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])
        o['rooms'] = self.numConvert(o['rooms'])

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o

    def applyBlacklist(self, o):
        return not isOneOf(o['title'], self.appliedBlackList)
    
    def numConvert(self, value):
        comma_count = value.count(',')
        dot_count = value.count('.')

        if comma_count == 1 and dot_count == 0:
            value = value.replace(',', '.')
        elif dot_count == 1 and comma_count == 1:
            value = value.replace('.', '').replace(',', '.')
        elif dot_count == 1 and comma_count == 0:
            value = value.replace('.', '')
        return value