import re
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.col-12 col-md-6 col-lg-12*',
            "sortByDateParam": 'sort=d_dt_crea',
            "paginate": 'LISTING-LISTpg=',
            "crawlFields": {
                "provider_id": 'a@data-id',
                "price": 'div.col text-right text-nowrap',
                "size": 'div.col col-lg-2:1c',
                "rooms": 'div.col col-lg-2:2c',
                "title": 'a@title',
                "url": 'a@href',
                "address_detected": 'div.col-10 col-lg-11',
            },
            "num_listings": 'p.mt-1 bigger sticky-hide:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Wohnnet AT',
            "baseUrl": 'https://www.wohnnet.at/',
            "id": 'seloger_fr',
        }

    def normalize(self, o):
        o['address_detected'] = o['address_detected'].replace(o['title'], '').strip()

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['url'] = self.metaInformation['baseUrl'][0:-1] + o["url"]

        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = numConvert_de(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = numConvert_de(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])
        o['rooms'] = numConvert_de(o['rooms'])

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o