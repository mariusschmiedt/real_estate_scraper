
import re
from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'article.Wrapper__WrapperStyled*',
            "sortByDateParam": '?se=16',
            "paginate": 'pn=',
            "crawlFields": {
                "provider_id": '.@data-property-id',
                "price": 'h3.Box-cYFBPY*:raw',
                "size": '',
                "rooms": '',
                "title": 'h2.Box-cYFBPY*',
                "url": 'a.Wrapper__A-kVOWTT*@href',
                "address_detected": 'span.AddressLine*',
            },
            "num_listings": 'h1.Box-cYFBPY*:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immoscout CH',
            "baseUrl": 'https://www.immoscout24.ch',
            "id": 'immoscout_ch',
        }

    def normalize(self, o):
        url = self.metaInformation['baseUrl'] + o["provider_id"]

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if ',' in o['address_detected']:
            o['city'] = o['address_detected'].split(',')[-2].replace(o['postalcode'], '').strip()
        
        price_tag = re.sub('\<(.*?)>', ' ', o['price']).strip()

        price_split = [i for i in price_tag.split(', ') if i != '']
        # find the number of bedrooms
        if len(price_split) == 3:
            o['rooms'] = price_split[0]
            o['size'] = price_split[1]
            o['price'] = price_split[2]
        else:
            for p in price_split:
                if 'Zimmer' in p:
                    o['rooms'] = p
                elif 'CHF' in p or 'EUR' in p or '€' in p or '$' in p or 'USD' in p:
                    o['price'] = p
                else:
                    o['size'] = p

        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])


        o['price'] = self.numConvert(o['price'])
        o['size'] = self.numConvert(o['size'])
        o['rooms'] = self.numConvert(o['rooms'])
        o['url'] = url

        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass

        return o

    def numConvert(self, value):
        value = value.replace(' ', '')

        value = numConvert_de(value)
        
        return value