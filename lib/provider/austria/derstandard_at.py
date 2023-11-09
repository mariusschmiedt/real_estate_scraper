
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.result-data-container',
            "sortByDateParam": 'SortType=1',
            "paginate": 'seite-',
            "crawlFields": {
                "provider_id": 'a@href',
                "price": 'span.result-data:3c',
                "size": 'span.result-data:1c',
                "rooms": 'span.result-data:2c',
                "title": 'a@title',
                "url": 'a@href',
                "address_detected": 'span.adress',
            },
            "num_listings": 'h1.headerImmoSearch:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Der Standard AT',
            "baseUrl": 'https://immobilien.derstandard.at/',
            "id": 'derstandard_at',
        }

    def normalize(self, o):

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['provider_id'] = o['provider_id'].replace('/immobiliensuche/detail/', '').split('/')[0]

        o['url'] = self.metaInformation['baseUrl'] + 'immobiliensuche/detail/' + o["provider_id"]


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