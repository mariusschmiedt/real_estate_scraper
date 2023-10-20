from ..utils import isOneOf

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
        provider_id = o["provider_id"].replace(o["provider_id"][0:o["provider_id"].index("/")]+1, '')
        size = 'N/A m²'
        if o['size'] != '':
            size = o['size'].replace('Wohnfläche ', '')
        price = '--- €'
        if o['price'] != '':
            price =  o['price'].replace('Kaufpreis ', '')
        address_detected = 'No address available'
        if o['address_detected'] != '':
            address_detected = o['address_detected'].split(' • ')[-2]
        title = 'No title available'
        if o['title'] != '':
            title = o['title']
        url = o["provider_id"]

        o['provider_id'] = provider_id
        o['address_detected'] = address_detected
        o['price'] = price
        o['size'] = size
        o['title'] = title
        o['url'] = url
        return o

    def applyBlacklist(self, o):
        titleNotBlacklisted = not isOneOf(o['title'], self.appliedBlackList)
        descNotBlacklisted = not isOneOf(o['description'], self.appliedBlackList)
        return titleNotBlacklisted and descNotBlacklisted