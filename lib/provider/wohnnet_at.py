import re
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.col-12 col-md-6 col-lg-12*',
            "sortByDateParam": 'sortierung=neueste-zuerst',
            "crawlFields": {
                "provider_id": 'a@data-id',
                "price": 'div.col text-right text-nowrap',
                "size": 'div.col col-lg-2:1c',
                "rooms": 'div.col col-lg-2:2c',
                "title": 'a@title',
                "url": 'a@href',
                "address_detected": 'div.col-10 col-lg-11',
            },
            "num_listings": 'p.mt-1 bigger sticky-hide:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Wohnnet AT',
            "baseUrl": 'https://www.wohnnet.at/',
            "id": 'wohnnet_at',
            "paginate": 'seite=',
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
        o['address_detected'] = o['address_detected'].replace(o['title'], '').strip()

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['url'] = self.metaInformation['baseUrl'][0:-1] + o["url"]

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