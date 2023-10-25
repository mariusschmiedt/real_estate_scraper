from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.EstateItem*',
            "sortByDateParam": 'sd=DESC&sf=TIMESTAMP',
            "crawlFields": {
                "provider_id": 'a.mainSection*@id',
                "price": 'div.@data-test=price',
                "size": 'div.@data-test=area',
                "title": 'h2',
                "address_detected": 'div.IconFact*:1c:2t',
                "rooms": 'div.@data-test=rooms',
            },
            "num_listings": 'h1.MatchNumber-a225f:1s',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Immowelt',
            "baseUrl": 'https://www.immowelt.de/',
            "id": 'immowelt',
            "paginate": '&sp=',
        }

    def init(self, sourceConfig, blacklist=None):
        self.config["enabled"] = sourceConfig["enabled"]
        self.config["search_url"] = sourceConfig["search_url"]
        if blacklist is None:
            blacklist = []
        self.appliedBlackList = blacklist

    def normalize(self, o):
        
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if '(' in o['address_detected'] and ')' in o['address_detected']:
            o['district'] = o['address_detected'].split('(')[1].replace('(', '').replace(')', '').strip()
            o['city'] = o['address_detected'].split('(')[0].strip()
        else:
            o['city'] = o['address_detected']
        
        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])

        
        o['price'] = self.numConvert(o['price'].replace('.', ''))
        o['size'] = self.numConvert(o['size'])
        o['rooms'] = self.numConvert(o['rooms'])
        o['url'] = "https://www.immowelt.de/expose/" + o['provider_id']

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass
        return o

    def applyBlacklist(self, o):
      titleNotBlacklisted = not isOneOf(o['title'], self.appliedBlackList)
      return titleNotBlacklisted
    
    def numConvert(self, value):
        comma_count = value.count(',')
        dot_count = value.count('.')

        if comma_count == 1 and dot_count == 0:
            value = value.replace(',', '.')
        elif dot_count == 1 and comma_count == 1:
            value = value.replace('.', '').replace(',', '.')
        return value
