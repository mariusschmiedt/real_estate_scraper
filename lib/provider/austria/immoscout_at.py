
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'li.Item-item-J04',
            "crawlContainer2": 'li.Item-item-S33',
            "sortByDateParam": 'aktualitaet',
            "paginate": 'seite-',
            "crawlFields": {
                "provider_id": 'a.Item-item__link*@href',
                "price": 'li.Text-color-gray-dark-wi_*',
                "size": 'li.w-full mb-0 mt-0 mr-0*:1c',
                "rooms": 'li.w-full mb-0 mt-0 mr-0*:2c',
                "title": 'h2.Text-color-gray-dark-wi_*',
                "url": 'a.Item-item__link*@href',
                "address_detected": 'address.Item-item__address*',
            },
            "num_listings": 'h2.Headline-sub-headline-N14',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immoscout AT',
            "baseUrl": 'https://www.immobilienscout24.at/',
            "id": 'immoscout_at',
        }

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


        o['price'] = numConvert_de(o['price'])
        o['size'] = numConvert_de(o['size'])
        o['rooms'] = numConvert_de(o['rooms'])

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o