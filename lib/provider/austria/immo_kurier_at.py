import re
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.item-wrap js-serp-item',
            "sortByDateParam": 's=most_recently_updated_first',
            "paginate": 'page=',
            "crawlFields": {
                "provider_id": '@data-id',
                "price": 'div.item__spec item-spec-price',
                "size": 'div.item__spec item-spec-area',
                "rooms": 'div.item__spec item-spec-rooms',
                "title": 'a.js-item-title-link:1c',
                "url": 'a.js-item-title-link@href',
                "address_detected": 'div.item__locality',
            },
            "num_listings": 'li.breadcrumb-item active:1s',
            "maxPageResults": '2000',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immo Kurier AT',
            "baseUrl": 'https://immo.kurier.at/',
            "id": 'immo_kurier_at',
        }

    def normalize(self, o):
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])
        if o['postalcode'] != '':
            if ',' in o['address_detected']:
                o['city'] = o['address_detected'].split(',')[-1].strip().replace(o['postalcode'], '').strip()
            else:
                o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['url'] = self.metaInformation['baseUrl'] + 'immobilien/' + o["provider_id"]
        
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