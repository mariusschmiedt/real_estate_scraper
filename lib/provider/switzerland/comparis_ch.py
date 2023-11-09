
from ...utils import replaceRoomAbbr, findPostalCodeInAddress, getNum

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'script@type=application/json',
            "jsonContainer": 'props.pageProps.initialResultData.resultItems',
            "sortByDateParam": '',
            "paginate": 'page=',
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
        }

        self.metaInformation = {
            "name": 'Comparis',
            "baseUrl": 'https://www.comparis.ch/',
            "id": 'comparis_ch',
        }

    def normalize(self, o):
        o["provider_id"] = str(o["provider_id"])

        # create url
        url = self.metaInformation['baseUrl'] + "immobilien/marktplatz/details/show/" + o["provider_id"]
        o['url'] = url
        
        # address is a list. get the postal code and the city from the list
        if o['address_detected'] != '':
            o['address_detected'] = o['address_detected'].replace('[', '')
            o['address_detected'] = o['address_detected'].replace(']', '')
            o['postalcode'] = findPostalCodeInAddress(o['address_detected'])
            if ',' in o['address_detected']:
                o['city'] = o['address_detected'].split(',')[-1]
            else:
                o['city'] = o['address_detected']
            o['city'] = o['city'].replace(o['postalcode'], '').strip()
            if type(o['address_detected']) == list:
                o['address_detected'] = ', '.join(o['address_detected'])
        else:
            o['address_detected'] = ''
        
        # find the room from the essential information list
        if o['rooms'] != '':
            o['rooms'] = o['rooms'].replace('[', '')
            o['rooms'] = o['rooms'].replace(']', '')
            room_split = o['rooms'].split(',')
            for r in room_split:
                new_r = replaceRoomAbbr(r)
                if r != new_r:
                    o['rooms'] = new_r.strip()            
            o['rooms'] = getNum(o['rooms'])
        else:
            o['rooms'] = ''
                
        # remove time from date string
        if o['in_db_since'] != '':
            o['in_db_since'] = o['in_db_since'].split('T')[0]
        else:
            o['in_db_since'] = ''
        
        # set size unit
        o['size_unit'] = 'm^2'
        
        
        # if the rooms could not be found reset the value
        if type(o['rooms']) == list:
            o['rooms'] = ''

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o