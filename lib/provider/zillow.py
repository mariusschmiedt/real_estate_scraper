
import re
from ..utils import isOneOf

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'li.ListItem*',
            "sortByDateParam": 'sortierung:neueste',
            "crawlFields": {
                "provider_id": 'article.StyledPropertyCard*@id',
                "price": 'span.PropertyCardWrapper*',
                "size": 'ul.PropertyCardWrapper:3c:2t',
                "rooms": '',
                "title": '',
                "url": 'a.property-card-link@href',
                "address_detected": 'address',
            },
            "num_listings": 'span.result-count',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Zillow',
            "baseUrl": 'https://www.zillow.com',
            "id": 'kleinanzeigen',
            "paginate": 'seite:',
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

        value = value.replace(',', '')

        return value