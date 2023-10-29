import re
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.col-lg-4*',
            "sortByDateParam": '',
            "crawlFields": {
                "provider_id": 'a@href',
                "price": 'div.property-box-pricev',
                "size": 'div.property-box-meta-itemv col-lg-3*:2c',
                "rooms": 'div.property-box-meta-itemv col-lg-3*:1c',
                "title": 'h3.property-titlev g_d_none*',
                "url": 'a@href',
                "address_detected": 'table.table sp_tbl:3t',
            },
            "num_listings": 'div.countProperty:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Flatbee AT',
            "baseUrl": 'https://www.flatbee.at/',
            "id": 'flatbee_at',
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

        if '|' in o['address_detected']:
            o['city'] = o['address_detected'].split('|')[0].replace('Bezirk:', '').replace('-Umgebung', '').strip()
            o['city'] = re.sub('\(.*\)', '', o['city']).strip()
            o['city'] = re.sub('[0-9].*', '', o['city']).strip()

        o['provider_id'] = o['provider_id'].split('/')[-1].split('-')[0].strip()

        o['url'] = self.metaInformation['baseUrl'] + 'properties/searchengine_property_detail/' + o["provider_id"]


        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = self.numConvert(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = self.numConvert(o['size'])
        o['size'] = getNum(o['size'])

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