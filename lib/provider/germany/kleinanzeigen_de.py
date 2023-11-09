
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'li.ad-listitem*',
            "sortByDateParam": 'sortierung:neueste',
            "paginate": 'seite:',
            "crawlFields": {
                "provider_id": 'article.aditem@data-adid',
                "price": 'p.aditem-main--middle--price-shipping--price',
                "size": 'span.simpletag:1c',
                "rooms": 'span.simpletag:2c',
                "title": 'a.ellipsis',
                "url": 'a.ellipsis@href',
                "address_detected": 'div.aditem-main--top--left',
            },
            "num_listings": 'span.breadcrump-summary:5s',
            "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Kleinanzeigen',
            "baseUrl": 'https://www.kleinanzeigen.de/',
            "id": 'kleinanzeigen_de',
        }

    def normalize(self, o):

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
            o['district'] = o['city']
        
        url = self.metaInformation['baseUrl'] + o["url"]


        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])


        o['price'] = numConvert_de(o['price'])
        o['size'] = numConvert_de(o['size'])
        o['rooms'] = numConvert_de(o['rooms'])
        o['url'] = url

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o