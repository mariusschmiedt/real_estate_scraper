from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.item-wrap js-serp-item',
            "sortByDateParam": 's=most_recently_updated_first',
            "crawlFields": {
                "provider_id": '@id',
                "price": 'div.item__spec.item-spec-price',
                "size": 'div.item__spec.item-spec-area',
                "title": 'a.js-item-title-link@title',
                "address_detected": 'div.item__locality',
                "rooms": 'div.item__spec.item-spec-rooms',
            },
            "num_listings": 'li.breadcrumb-item active:1s',
            "maxPageResults": '2000',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Immo Suedwest Presse',
            "baseUrl": 'https://immo.swp.de/',
            "id": 'immoswp',
            "paginate": '&page=',
        }

    def init(self, sourceConfig, blacklist=None):
        self.config["enabled"] = sourceConfig["enabled"]
        self.config["search_url"] = sourceConfig["search_url"]
        if blacklist is None:
            blacklist = []
        self.appliedBlackList = blacklist

    def normalize(self, o):
        
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        address = o['address_detected']
        if ',' in o['address_detected']:
            address = o['address_detected'].split(',')[1]
       

        if o['postalcode'] != "":
            city = address.replace(o['postalcode'], '').strip()
            o['city'] = city
        
        provider_id = o["provider_id"].replace(o["provider_id"][0:o["provider_id"].index("-")+1], '')


        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])

        o['provider_id'] = provider_id
        o['price'] = self.numConvert(o['price'])
        o['size'] = self.numConvert(o['size'])
        o['rooms'] = self.numConvert(o['rooms'])
        o['url'] = "https://immo.swp.de/immobilien/" + provider_id

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
        elif dot_count == 1 and comma_count == 0:
            value = value.replace('.', '')
        return value