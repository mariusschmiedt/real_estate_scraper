import re
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.col-xs-12 col-sm-9 col-md-9 col-lg-9',
            "sortByDateParam": '',
            "top_field": 'div.col-xs-12 col-sm-11 col-md-11 col-lg-11',
            "crawlFields": {
                "provider_id": 'a.btnHeadlineErgebnisliste@href',
                "price": 'div.col-xs-4 col-lg-2:1c',
                "size": 'div.col-xs-4 col-lg-2:2c',
                "rooms": 'div.col-xs-4 col-lg-2:3c',
                "title": 'a.btnHeadlineErgebnisliste',
                "url": 'a.btnHeadlineErgebnisliste@href',
                "address_detected": 'div.col-xs-12 col-sm-12 col-md-12 col-lg-12:2c',
            },
            "num_listings": 'div.hidden-md hidden-lg col-xs-12:3s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Findmyhome',
            "baseUrl": 'https://www.findmyhome.at/',
            "id": 'findmyhome_at',
            "paginate": 'entry=',
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
        o['provider_id'] = re.sub('[^0-9]','', o['provider_id'])
        o['address_detected'] = o['address_detected'].replace('Ort:', '').strip()
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['url'] = self.metaInformation['baseUrl'] + o["provider_id"]


        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = getNum(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = getNum(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])
        o['rooms'] = getNum(o['rooms'])

        o['price'] = self.numConvert(o['price'])
        o['size'] = self.numConvert(o['size'])
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