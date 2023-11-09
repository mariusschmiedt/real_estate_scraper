import re
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'section.VKFkO _3swN3',
            "sortByDateParam": '',
            "paginate": 'page=',
            "crawlFields": {
                "provider_id": 'a@href',
                "price": 'div._1-CSS:3c',
                "size": 'div._1-CSS:2c',
                "rooms": 'div._1-CSS:1c',
                "title": 'h2._2jNcY',
                "url": 'a@href',
                "address_detected": 'p._1FDvH',
            },
            "num_listings": 'h1._3fslm:1s',
            "maxPageResults": '500',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immodirekt AT',
            "baseUrl": 'https://www.immodirekt.at/',
            "id": 'immodirekt_at',
        }

    def normalize(self, o):
        o['provider_id'] =  o['provider_id'].split('-')[-1].replace('/', '').strip()
        o['url'] = self.metaInformation['baseUrl'][0:-1] + o["url"]

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        if ',' in o['city']:
            o['city'] = o['city'].split(',')[0].strip()
        
        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = numConvert_de(o['price'])
        o['price'] = getNum(o['price'])
        
        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = numConvert_de(o['size'])
        o['size'] = getNum(o['size'])
        
        o['rooms'] = replaceRoomAbbr(o['rooms'])
        o['rooms'] = numConvert_de(o['rooms'])
        o['rooms'] = getNum(o['rooms'])

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o