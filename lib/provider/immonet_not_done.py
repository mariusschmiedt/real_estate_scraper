from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": '.content-wrapper-tiles .ng-star-inserted',
            "sortByDateParam": 'sortby=19',
            "crawlFields": {
                "provider_id": '.card a@href',
                "price": '.card .has-font-300 .is-bold | trim',
                "size": '.card .has-font-300 .ml-100 | trim',
                "title": '.card h3 |trim',
                "address_detected": '.card span:nth-child(2) | trim',
            },
            "paginate": '#idResultList .margin-bottom-6.margin-bottom-sm-12 .panel a.pull-right@href',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Immonet',
            "baseUrl": 'https://www.immonet.de/',
            "id": 'immonet',
        }

    def init(self, sourceConfig, blacklist=None):
        self.config["enabled"] = sourceConfig["enabled"]
        self.config["search_url"] = sourceConfig["search_url"]
        if blacklist is None:
            blacklist = []
        self.appliedBlackList = blacklist

    def normalize(self, o):
        
        if '(' in o['address_detected'] and ')' in o['address_detected']:
            o['district'] = o['address_detected'].split('(')[1].replace('(', '').replace(')', '').strip()
            o['city'] = o['address_detected'].split('(')[0].strip()
        else:
            o['city'] = o['address_detected']
        
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        provider_id = o["provider_id"].replace(o["provider_id"][0:o["provider_id"].index("/")]+1, '')

        url = o["provider_id"]

        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])

        o['price'] = self.numConvert(o['price'])
        o['size'] = self.numConvert(o['size'])
        o['rooms'] = self.numConvert(o['rooms'])



        o['provider_id'] = provider_id
        o['url'] = url
        return o

    def applyBlacklist(self, o):
        titleNotBlacklisted = not isOneOf(o['title'], self.appliedBlackList)
        descNotBlacklisted = not isOneOf(o['description'], self.appliedBlackList)
        return titleNotBlacklisted and descNotBlacklisted
    
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