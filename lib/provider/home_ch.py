
import re
from ..utils import replaceSizeUnit, replaceRoomAbbr, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'a.row search-results__list__item*',
            "sortByDateParam": 'sort=dd',
            "paginate": 'pageNum=',
            "crawlFields": {
                "provider_id": 'a.row search-results__list__item@data-gtm-id',
                "price": 'span.price-tag__amount',
                "currency": 'span.price-tag__currency',
                "size": 'span.tags__tag:3c',
                "rooms": 'span.tags__tag:2c',
                "title": 'h2.search-results__list__item__meta__title',
                "url": 'a.row search-results__list__item@href',
                "address_detected": 'div.search-results__list__item__meta__description*',
            },
            "num_listings": 'h2.h4 search-results__subheadline*',
            # "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Home.ch',
            "baseUrl": 'https://www.home.ch',
            "id": 'home_ch',
        }

    def nullOrEmpty(self, val):
        nullVal = False
        if val == None:
            nullVal = True
        else:
            if len(val) == 0:
                nullVal = True
        return nullVal

    def normalize(self, o):
        o['size_unit'] = getSizeUnit(size = o['size'])
        o['size'] = replaceSizeUnit(o['size'])
        size_split = o['size'].split(' ')
        if type(size_split) == list:
            if len(size_split) > 1:
                o['size'] = size_split[0]
        o['rooms'] = replaceRoomAbbr(o['rooms'])

        o['price'] = self.numConvert(o['price'])
        o['size'] = self.numConvert(o['size'])
        o['rooms'] = self.numConvert(o['rooms'])

        o['provider_id'] = o['provider_id'].split('ad-link-')[1]

        url = ''
        if o['price'] is not None:
            if o['price'] != '':
                url = self.metaInformation['baseUrl'] 
                if int(o['price']) < 20000:
                    url = '/rent/' + o['provider_id']
                else:
                    url = '/buy/' + o['provider_id']
        
        o['url'] = url

        if url == '':
            o['price'] = ''

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])
        
        o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o

    def numConvert(self, value):

        value = value.replace("'", '')
        value = value.replace(",", '')


        return value