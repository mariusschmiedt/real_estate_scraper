from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'sd-card.tile card',
            "sortByDateParam": 'sortby=19',
            "paginate": 'page=',
            "crawlFields": {
                "provider_id": 'a@href',
                "price": 'span.is-bold ng-star-inserted',
                "size": 'span.ml-100 ng-star-inserted:1c',
                "rooms": 'span.ml-100 ng-star-inserted:2c',
                "title": 'h3.is-bold mb-75*',
                "url": 'a@href',
                "address_detected": 'span.text-overflow ng-star-inserted:1c',
            },
            "num_listings": 'h1.is-bold:1s',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immonet',
            "baseUrl": 'https://www.immonet.de/',
            "id": 'immonet_de',
        }

    def normalize(self, o):
        
        o['provider_id'] = o["provider_id"].replace(o["provider_id"][0:o["provider_id"].index("/")]+1, '')

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