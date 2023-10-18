
import re
from ..utils import isOneOf

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'li.result-list__listing',
            "sortByDateParam": 'sorting=2',
            "crawlFields": {
                "provider_id": 'article.result-list-entry@data-obid',
                "price": 'dd.font-highlight font-tabular:1c',
                "size": 'dd.font-highlight font-tabular:2c',
                "rooms": 'span.onlySmall',
                "title": 'a.result-list-entry__brand-title-container',
                "url": 'a.result-list-entry__brand-title-container@href',
                "address_detected": 'button.result-list-entry__map-link',
            },
            "num_listings": 'span.resultlist-resultCount',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Immoscout',
            "baseUrl": 'https://www.immobilienscout24.de/',
            "id": 'immoscout',
            "paginate": '?pagenumber=',
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
        url = "https://www.immobilienscout24.de" + o["url"].replace(o["url"][0:o["url"].index("/expose")+1], '')

        o['price'] = self.numConvert(o['price'])
        o['size'] = self.numConvert(o['size'])
        o['rooms'] = self.numConvert(o['rooms'])
        o['url'] = url
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