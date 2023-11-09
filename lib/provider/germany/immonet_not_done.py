from ...utils import replaceCurrency, replaceSizeUnit, replaceRoomAbbr, getCurrency, getSizeUnit, findPostalCodeInAddress, numConvert_de

class provider():
    def __init__(self):

        self.config = {
            "search_url": None,
            "crawlContainer": '.content-wrapper-tiles .ng-star-inserted',
            "sortByDateParam": 'sortby=19',
            "paginate": '',
            "crawlFields": {
                "provider_id": '.card a@href',
                "price": '.card .has-font-300 .is-bold | trim',
                "size": '.card .has-font-300 .ml-100 | trim',
                "title": '.card h3 |trim',
                "address_detected": '.card span:nth-child(2) | trim',
            },
            "paginate": '#idResultList .margin-bottom-6.margin-bottom-sm-12 .panel a.pull-right@href',
            "normalize": self.normalize,
        }

        self.metaInformation = {
            "name": 'Immonet',
            "baseUrl": 'https://www.immonet.de/',
            "id": 'immonet',
        }

    def normalize(self, o):
        
        if '(' in o['address_detected'] and ')' in o['address_detected']:
            o['district'] = o['address_detected'].split('(')[1].replace('(', '').replace(')', '').strip()
            o['city'] = o['address_detected'].split('(')[0].strip()
        else:
            o['city'] = o['address_detected']
        
        o['postalcode'] = findPostalCodeInAddress(o['address_detected'])

        provider_id = o["provider_id"].replace(o["provider_id"][0:o["provider_id"].index("/")]+1, '')

        url = o["provider_id"]

        o['currency'] = getCurrency(o['price'])
        o['price'] = replaceCurrency(o['price'])

        o['size_unit'] = getSizeUnit(o['size'])
        o['size'] = replaceSizeUnit(o['size'])

        o['rooms'] = replaceRoomAbbr(o['rooms'])

        o['price'] = numConvert_de(o['price'])
        o['size'] = numConvert_de(o['size'])
        o['rooms'] = numConvert_de(o['rooms'])



        o['provider_id'] = provider_id
        o['url'] = url
        return o