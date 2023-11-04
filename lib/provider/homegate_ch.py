import re
from ..utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": 'div.ResultList_listItem*',
            "sortByDateParam": 'o=dateCreated-desc',
            "paginate": 'ep=',
            "crawlFields": {
                "provider_id": '',
                "price": 'span.HgListingCard_price*',
                "size": 'div.HgListingRoomsLivingSpace_roomsLivingSpace*:raw',
                "rooms": '',
                "title": 'p.HgListingDescription_title*:t1',
                "url": 'a.HgCardElevated_link*@href',
                "address_detected": 'address',
            },
            "num_listings": 'span.ResultsNumber_results_zTgsG:1s',
            # "listings_per_page": '25',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Homegate',
            "baseUrl": 'http://homegate.ch',
            "id": 'homegate_ch',
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

        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        if o['postalcode'] != '':
            rem_address = o['address_detected'].replace(o['postalcode'], '').strip()
            if ',' in rem_address:
                o['city'] = rem_address.split(',')[1].strip()
            else:
                o['city'] = rem_address
        
        size_tag = re.sub('\<(.*?)>', ', ', o['size']).strip()

        size_split = [i.strip() for i in size_tag.split(', ') if i != '' and i != ',']
        # find the number of bedrooms
        for p in range(1, len(size_split)):
            num = False
            try:
                int(size_split[p-1])
                num = True
            except:
                pass
            if num:
                if 'Zimmer' in size_split[p-1]:
                    o['rooms'] = size_split[p-1]
                else:
                    o['size'] = size_split[p-1]
        
        url = self.metaInformation['baseUrl'] + o["url"]

        o['provider_id'] = o["url"].split('/')[-1]

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
        value = value.replace('´', '')
        value = value.replace("'", '')

        comma_count = value.count(',')
        dot_count = value.count('.')

        if comma_count == 1 and dot_count == 0:
            value = value.replace(',', '.')
        return value