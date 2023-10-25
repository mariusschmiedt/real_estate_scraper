
import re
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'li.ListItem*',
            "sortByDateParam": '"sort":{"value":"days"}}',
            "crawlFields": {
                "provider_id": 'article.StyledPropertyCard*@id',
                "price": 'span.PropertyCardWrapper*',
                "size": 'ul.StyledPropertyCardHomeDetailsList*:raw',
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
            "id": 'zillow',
            "paginate": ' "pagination":{"currentPage":}',
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
            o['city'] = o['address_detected'].split(',')[-2].strip()
            o['district'] = o['address_detected'].split(',')[-2].strip()
        
        # remove html tags from size
        size = re.sub('\<(.*?)>', ' ', o['size']).strip()
        # split the size string
        size_split = [i for i in size.split(' ') if i != '']
        # find the position of the size unit to get the apartement size (or pick the numeric value wiht more than three digits)
        try:
            o['size'] = size_split[size_split.index('sqft')-1]
        except:
            for s in size_split:
                num = False
                try:
                    int(s)
                    num = True
                except:
                    pass
                if num and len(s) >= 3:
                    o['size'] = s
        
        # find the number of bedrooms
        try:
            o['rooms'] = size_split[size_split.index('bds')-1]
        except:
            o['rooms'] = '1'

        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(size)
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

        value = value.replace(',', '')

        return value