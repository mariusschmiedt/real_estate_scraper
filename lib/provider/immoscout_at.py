
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'li.Item-item-J04',
            "sortByDateParam": 'aktualitaet',
            "crawlFields": {
                "provider_id": 'a.Item-item__link-pTS@href',
                "price": 'li.Text-color-gray-dark-wi_ Text-size-s-KGp Text-bold-t5X',
                "size": 'li.w-full mb-0 mt-0 mr-0*:1c',
                "rooms": 'li.w-full mb-0 mt-0 mr-0*:2c',
                "title": 'h2.Text-color-gray-dark-wi_ Text-size-standard-X2v Text-clamp-lines-1-SVo',
                "url": 'a.Item-item__link-pTS@href',
                "address_detected": 'address.Item-item__address*',
            },
            "num_listings": 'h2.Headline-sub-headline-N14',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Immoscout AT',
            "baseUrl": 'https://www.immobilienscout24.at/',
            "id": 'immoscout_at',
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

        if ',' in o['address_detected']:
            o['city'] = o['address_detected'].split(',')[-1].strip()
        else:
            o['city'] = o['address_detected']
        
        if o['postalcode'] != '':
            o['city'] = o['city'].replace(o['postalcode'], '').strip()
                
        o['url'] = self.metaInformation['baseUrl'][0:-1] + o["url"]
        
        o['provider_id'] = o['provider_id'].replace('expose', '').replace('/', '')
        
        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])


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