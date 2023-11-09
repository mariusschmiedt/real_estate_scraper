from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.item-wrap js-serp-item',
            "sortByDateParam": 's=most_recently_updated_first',
            "paginate": 'page=',
            "crawlFields": {
                "provider_id": '@id',
                "price": 'div.item__spec.item-spec-price',
                "size": 'div.item__spec.item-spec-area',
                "title": 'a.js-item-title-link@title',
                "address_detected": 'div.item__locality',
                "rooms": 'div.item__spec.item-spec-rooms',
            },
            "num_listings": 'li.breadcrumb-item active:1s',
            "maxPageResults": '2000',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immo Suedwest Presse',
            "baseUrl": 'https://immo.swp.de/',
            "id": 'immoswp_de',
        }

    def normalize(self, o):
        
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        address = o['address_detected']
        if ',' in o['address_detected']:
            address = o['address_detected'].split(',')[1]
       

        if o['postalcode'] != "":
            city = address.replace(o['postalcode'], '').strip()
            o['city'] = city
        
        provider_id = o["provider_id"].replace(o["provider_id"][0:o["provider_id"].index("-")+1], '')


        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])

        o['provider_id'] = provider_id
        o['price'] = numConvert_de(o['price'])
        o['size'] = numConvert_de(o['size'])
        o['rooms'] = numConvert_de(o['rooms'])
        o['url'] = self.metaInformation['baseUrl'] + "immobilien/" + provider_id

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass
        
        return o
    
    def numConvert(self, value):
        comma_count = value.count(',')
        dot_count = value.count('.')

        if comma_count == 1 and dot_count == 0:
            value = value.replace(',', '.')
        elif dot_count >= 1 and comma_count == 1:
            value = value.replace('.', '').replace(',', '.')
        elif dot_count >= 1 and comma_count == 0:
            value = value.replace('.', '')
        return value