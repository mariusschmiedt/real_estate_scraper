
from ..utils import isOneOf, replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):
        self.appliedBlackList = []

        self.config = {
            "search_url": None,
            "crawlContainer": 'script.@type=application/json',
            "jsonContainer": 'props.pageProps.initialResultData.resultItems',
            "sortByDateParam": '',
            "crawlFields": {
                "provider_id": 'AdId',
                "price": 'PriceValue',
                "currency": 'Currency',
                "size": 'AreaValue',
                "rooms": 'EssentialInformation',
                "title": 'Title',
                "address_detected": 'Address',
                "in_db_since": 'Date'
            },
            "num_listings": 'props.pageProps.initialResultData.numberOfResults',
            # "listings_per_page": '25',
            "normalize": self.normalize,
            "filter": self.applyBlacklist,
        }

        self.metaInformation = {
            "name": 'Comparis',
            "baseUrl": 'https://www.comparis.ch/',
            "id": 'comparis',
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
        o["provider_id"] = str(o["provider_id"])

        # create url
        url = "https://www.comparis.ch/immobilien/marktplatz/details/show/" + o["provider_id"]
        o['url'] = url
        
        # address is a list. get the postal code and the city from the list
        if o['address_detected'] is not None:
            for add in o['address_detected']:
                o['postalcode'] = findPostalCodeInAddress(o['address_detected'])
                if o['postalcode'] != '':
                    o['city'] = add.replace(o['postalcode'], '').strip()
                    break
            if type(o['address_detected']) == list:
                o['address_detected'] = ', '.join(o['address_detected'])
        else:
            o['address_detected'] = ''
        
        # find the room from the essential information list
        if o['rooms'] is not None:
            for ei in o['rooms']:
                room = replaceRoomAbbr(ei)
                if room != ei:
                    o['rooms'] = room
                    break
        else:
            o['rooms'] = ''
        
        # remove time from date string
        if o['in_db_since'] is not None:
            o['in_db_since'] = o['in_db_since'].split('T')[0]
        else:
            o['in_db_since'] = ''
        
        # set size unit
        o['size_unit'] = 'm^2'
        
        # normalize values
        if o['size'] is None:
            o['size'] = ''
        else:
            o['size'] = str(o['size'])
        
        if o['price'] is None:
            o['price'] = ''
        else:
            o['price'] = str(o['price'])
        
        if o['currency'] is None:
            o['currency'] = ''
        
        if o['title'] is None:
            o['title'] = ''
        
        
        # if the rooms could not be found reset the value
        if type(o['rooms']) == list:
            o['rooms'] = ''

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