import re
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, getNum, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.col-xs-12 col-sm-9 col-md-9 col-lg-9',
            "sortByDateParam": 'sort=0',
            "paginate": 'entry=',
            "top_field": 'div.col-xs-12 col-sm-11 col-md-11 col-lg-11',
            "crawlFields": {
                "provider_id": 'a.btnHeadlineErgebnisliste@href',
                "price": 'div.col-xs-4 col-lg-2:1c',
                "size": 'div.col-xs-4 col-lg-2:2c',
                "rooms": 'div.col-xs-4 col-lg-2:3c',
                "title": 'a.btnHeadlineErgebnisliste',
                "url": 'a.btnHeadlineErgebnisliste@href',
                "address_detected": 'div.col-xs-12 col-sm-12 col-md-12 col-lg-12:2c',
            },
            "num_listings": 'div.hidden-md hidden-lg col-xs-12:3s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Findmyhome',
            "baseUrl": 'https://www.findmyhome.at/',
            "id": 'findmyhome_at',
        }

    def normalize(self, o):
        
        o['provider_id'] = re.sub('[^0-9]','', o['provider_id'])
        o['address_detected'] = o['address_detected'].replace('Ort:', '').strip()
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
        
        o['url'] = self.metaInformation['baseUrl'] + o["provider_id"]


        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])
        o['price'] = numConvert_de(o['price'])
        o['price'] = getNum(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        o['size'] = numConvert_de(o['size'])
        o['size'] = getNum(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])
        o['rooms'] = getNum(o['rooms'])

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass
        
        return o