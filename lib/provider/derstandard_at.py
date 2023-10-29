
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.result-data-container',
            "sortByDateParam": 'SortType=1',
            "crawlFields": {
                "provider_id": 'a@href',
                "price": 'span.result-data:3c',
                "size": 'span.result-data:1c',
                "rooms": 'span.result-data:2c',
                "title": 'a@title',
                "url": 'a@href',
                "address_detected": 'span.adress',
            },
            "num_listings": 'h1.headerImmoSearch:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Der Standard AT',
            "baseUrl": 'https://immobilien.derstandard.at/',
            "id": 'derstandard_at',
            "paginate": 'seite-',
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
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['provider_id'] = o['provider_id'].replace('/immobiliensuche/detail/', '').split('/')[0]

        o['url'] = self.metaInformation['baseUrl'] + 'immobiliensuche/detail/' + o["provider_id"]


        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = self.numConvert(o['price'])
        o['price'] = getNum(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = self.numConvert(o['size'])
        o['size'] = getNum(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])
        o['rooms'] = self.numConvert(o['rooms'])
        o['rooms'] = getNum(o['rooms'])

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