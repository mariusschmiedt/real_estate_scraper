from bs4 import BeautifulSoup
import re
import json
import math
import html5lib
import os

def getAttr(value):
    tag = None
    class_name = None
    attr_name = None
    attr_val_des = None
    child = None
    split = None
    tag_split = None
    attr_val_des_start = False
    class_name_start = False
    raw = False
    if '@' in value:
        tag = value.split('@')[0]
        if tag == '':
            tag = None
        attr_name = value.split('@')[1]
        if '=' in attr_name:
            attr_name_split = attr_name.split('=')
            attr_name = attr_name_split[0]
            attr_val_des = attr_name_split[1]
    
    if '.' in value:
        value_split = value.split('.')
        if tag is not None:
            value_split = tag.split('.')
        tag = value_split[0]
        class_name = ' '.join([value_split[v] for v in range(1, len(value_split))])
    
    colon_split = None
    if class_name is not None:
        if ':' in class_name:
            colon_split = class_name.split(':')
            class_name = colon_split[0]
    if attr_val_des is not None:
        if ':' in attr_val_des:
            colon_split = attr_val_des.split(':')
            attr_val_des = colon_split[0]
    if colon_split is not None:
        for c in range(1, len(colon_split)):
            if colon_split[c].endswith('c'):
                child = int(colon_split[c].replace('c', ''))-1
            if colon_split[c].endswith('s'):
                split = int(colon_split[c].replace('s', ''))-1
            if colon_split[c].endswith('t'):
                tag_split = int(colon_split[c].replace('t', ''))-1
            if colon_split[c].endswith('raw'):
                raw = True
    
    if class_name is not None:
        if class_name.endswith('*'):
            class_name = class_name.replace('*', '')
            class_name_start = True
    if attr_val_des is not None:
        if attr_val_des.endswith('*'):
            attr_val_des = attr_val_des.replace('*', '')
            attr_val_des_start = True
    
    if '@' not in value and '=' not in value and '.' not in value and ':' not in value and '*' not in value:
        tag = value
    
    attr_dict = {
        "tag": tag,
        "class_name": class_name,
        "attr_name": attr_name,
        "attr_val_des": attr_val_des,
        "class_name_start": class_name_start,
        "attr_val_des_start": attr_val_des_start,
        "child": child,
        "split": split,
        "tag_split": tag_split,
        "raw": raw
    }
    return attr_dict

def getContent(container, attr_dict, get_container = False):
    result = None
    if attr_dict['child'] is None:
        attr_dict['child'] = 0
    if attr_dict['tag'] is not None:
        tag_find = container.find_all(attr_dict['tag'])
        if attr_dict['class_name'] is not None:
            tag_find = container.find_all(attr_dict['tag'], {"class": attr_dict['class_name']})
        if attr_dict['class_name_start']:
            tag_find = container.find_all(attr_dict['tag'], {"class": lambda v: v and v.startswith(attr_dict['class_name'])})
        result = [r for r in tag_find]
        if attr_dict['attr_name'] is not None:
            result = [r for r in result if attr_dict['attr_name'] in r.attrs]
        if len(result) == 0:
            result = None
    if not get_container:
        get_tag_content = False
        if attr_dict['attr_name'] is not None:
            if attr_dict['attr_val_des'] is not None:
                if attr_dict['attr_val_des_start']:
                    result = [r for r in result if r.attrs[attr_dict['attr_name']].startswith(attr_dict['attr_val_des'])]
                else:
                    result = [r for r in result if r.attrs[attr_dict['attr_name']] == attr_dict['attr_val_des']]
                get_tag_content = True
            else:
                if attr_dict['tag'] is not None and result is not None:
                    result = result[attr_dict['child']].get(attr_dict['attr_name'])
                else:
                    result = container.get(attr_dict['attr_name'])
        elif attr_dict['attr_name'] is None and result is not None:
            get_tag_content = True
        if get_tag_content:
            result = result[attr_dict['child']]
            if attr_dict['split'] is not None and not attr_dict['raw']:
                result = re.sub('\<(.*?)>', ' ', str(result)).replace('\n', '').strip()
                # result = result.text.replace('\n', '').strip()
                result = [i for i in result.split(' ') if i != ''][attr_dict['split']]
            elif attr_dict['tag_split'] is not None and not attr_dict['raw']:
                result = result.find_all()[attr_dict['tag_split']]
                result = re.sub('\<(.*?)>', ' ', str(result)).replace('\n', '').strip()
                # result = result.text.replace('\n', '').strip()
                result = [i for i in result.split(' ') if i != ''][attr_dict['split']]
            elif attr_dict['raw']:
                result = str(result)
            else:
                result = re.sub('\<(.*?)>', ' ', str(result)).replace('\n', '').strip()
                # result = result.text.replace('\n', '').strip()
                result = ' '.join([i for i in result.split(' ') if i != ''])
    else:
        if attr_dict['attr_val_des'] is not None and attr_dict['tag'] is not None:
            if 'json' in attr_dict['attr_val_des'] and attr_dict['tag'] == 'script':
                if attr_dict['attr_val_des_start']:
                    result = [r for r in result if r.attrs[attr_dict['attr_name']].startswith(attr_dict['attr_val_des'])]
                else:
                    result = [r for r in result if r.attrs[attr_dict['attr_name']] == attr_dict['attr_val_des']]
                result = json.loads(result[attr_dict['child']].string)
        else:
            if 'top_field' in config:
                attr_dict_top = getAttr(config['top_field'])
                result1 = result
                result = list()
                for con in result1:
                    tag_find = con.find_all(attr_dict_top['tag'], {"class": attr_dict_top['class_name']})
                    top_find = [r for r in tag_find]
                    if len(top_find) == 0:
                        result.append(con)
    return result

def getListings(containers, config):
    found_listings = 0
    if 'num_listings' in config:
        if type(containers) == dict:
            found_listings = int(getJsonResult(containers, config['num_listings']))
        else:
            attr_dict = getAttr(config['num_listings'])
            found_listings_num = getContent(soup, attr_dict)
            found_listings_num = re.sub('[^0-9]','', found_listings_num)
            found_listings = int(found_listings_num)
    listings_per_page = 1
    if type(containers) == dict:
        if 'listings_per_page' in config:
            listings_per_page = int(getJsonResult(containers, config['listings_per_page']))
        else:
            listings_per_page = len(getJsonResult(containers, config['jsonContainer']))
    else:
        if 'listings_per_page' in config:
            if config['listings_per_page'] != '':
                try:
                    listings_per_page = int(config['listings_per_page'])
                except:
                    raise Exception('Parameter "listings_per_page" of config ' + config['provider'] + ' must be a number')
        else:
            listings_per_page = len(containers)
    if 'maxPageResults' in config:
        if config['maxPageResults'] != '':
            try:
                found_listings = min(int(config['maxPageResults']), found_listings)
            except:
                raise Exception('Parameter "maxPageResults" of config ' + config['provider'] + ' must be a number')
    if 'maxPageNum' in config:
        if type(containers) == dict:
            maxPageNum = int(getJsonResult(containers, config['maxPageNum']))
    else:
        maxPageNum  = str(math.ceil(int(found_listings) / int(listings_per_page)))
    return found_listings, listings_per_page, maxPageNum

def getJsonResult(container, value):
    keys = value.split('.')
    for key in keys:
        if key in container:
            container = container[key]
    return container

def numConvert(value):
    comma_count = value.count(',')
    dot_count = value.count('.')
    if comma_count == 1 and dot_count == 0:
        value = value.replace(',', '.')
    elif dot_count >= 1 and comma_count == 1:
        value = value.replace('.', '').replace(',', '.')
    elif dot_count >= 1 and comma_count == 0:
        value = value.replace('.', '')
    return value

def getNum(value):
    val_split = value.split(' ')
    new_value = ''
    for v in val_split:
        num = False
        try:
            float(v)
            num = True
        except:
            pass
        if num:
            new_value = v
    return new_value


def normalize(o):
        if type(o['price']) == dict:
            price = ''
            if 'value' in o['price']:
                price = o['price']['value']
            if 'period' in o['price']:
                num = False
                try:
                    float(price)
                    num = True
                except:
                    pass
                if num:
                    price = float(price)
                    if o['price']['period'] == 'yearly':
                        price = price / 12
                    if o['price']['period'] == 'weekly':
                        price = price* 52 / 12
                    if o['price']['period'] == 'daily':
                        price = price * 365 / 12
                    price = str(round(price, 2))
            o['currency'] = o['price']['currency']
            o['price'] = price
        else:
            o['price'] = ''
        if 'type' in o:
            o['type'] = o['type'].lower()
        if 'sqft' in o['size_unit'] or 'SQFT' in o['size_unit']:
            o['size_unit'] = 'sqft'
        o['size'] = str(o['size'])
        if o['size_unit'] == 'sqft':
            o['size'] = str(round(float(o['size']) / 10.764, 2))
            o['size_unit'] = 'm^2'
        o['rooms'] = o['rooms'].replace(',', '')
        address = o['address_detected']
        lat = str(address['coordinates']['lat'])
        lon = str(address['coordinates']['lon'])
        address_string = ''
        if 'full_name' in address:
            address_string = ', ' + address['full_name']
        o['address_detected'] = 'lat: ' + lat + ', ' + 'lon: ' + lon + address_string
        try:
            o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
        except:
            pass
        return o

# def normalize(o):
#     o['postalcode'] = ''
#     for add in o['address_detected'].split(' '):
#         num = False
#         try:
#             int(add)
#             num = True
#         except:
#             pass
#         if num and len(add) >=4:
#             o['postalcode'] = add
#     if ',' in o['address_detected']:
#         o['city'] = o['address_detected'].split(',')[-1].strip()
#     else:
#         o['city'] = o['address_detected']
#     if o['postalcode'] != '':
#         o['city'] = o['city'].replace(o['postalcode'], '').strip() 
#     o['url'] = 'https://www.immobilienscout24.at/'[0:-1] + o["url"]
#     o['provider_id'] = o['provider_id'].replace('expose', '').replace('/', '')
#     if '&euro;' in o['price'] or '€' in o['price']:
#         o['currency'] = 'EUR'
#     o['price'] = o['price'].replace('&euro;', '').replace('€', '').replace(',-', '').strip()
#     if 'm²' in o['size'] or 'm2' in o['size']:
#         o['size_unit'] ='m^2'
#     o['size'] = o['size'].replace('m²', '').replace('m2', '').strip()
#     o['rooms'] = o['rooms'].replace('Zimmer', '').replace('Zi', '').strip()
#     o['price'] = numConvert(o['price'])
#     o['size'] = numConvert(o['size'])
#     o['rooms'] = numConvert(o['rooms'])
#     try:
#         o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
#     except:
#         pass
#     return o

config = {
    "search_url": None,
    "crawlContainer": 'script@type=application/json',
    "jsonContainer": 'props.pageProps.searchResult.properties',
    "sortByDateParam": 'ob=nd',
    "paginate": 'page=',
    "crawlFields": {
        "provider_id": 'id',
        "price": 'price',
        "currency": 'price.currency',
        "size": 'size.value',
        "size_unit": 'size.unit',
        "rooms": 'bedrooms',
        "title": 'title',
        "url": 'share_url',
        "address_detected": 'location',
        "type": 'property_type'
    },
    "num_listings": 'props.pageProps.searchResult.meta.total_count',
    "listings_per_page": 'props.pageProps.searchResult.meta.per_page',
    "maxPageNum": 'props.pageProps.searchResult.meta.page_count',
}

# soup = BeautifulSoup(page_content,'html5lib')

with open("/Users/mariusschmiedt/github/fredy_python/lib/provider/example_pages/propertyfinder_uae.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')

attr_dict = getAttr(config['crawlContainer'])
containers = getContent(soup, attr_dict, get_container=True)

found_listings, listings_per_page, maxPageNum = getListings(containers, config)

if type(containers) == dict:
    containers = getJsonResult(containers, config['jsonContainer'])    

con = containers[0]

listings = list()
for con in containers:
    listing = {}
    for key in config['crawlFields'].keys():
        listing[key] = ''
    for key in config['crawlFields'].keys():
        result = None
        if type(con) == dict:
            if not '.' in config['crawlFields'][key]:
                if config['crawlFields'][key] in con:
                    result = con[config['crawlFields'][key]]
            else:
                result = getJsonResult(con, config['crawlFields'][key])
        else:
            attr_dict = getAttr(config['crawlFields'][key])
            result = getContent(con, attr_dict)
        if result is not None:
            listing[key] = result
    # for key in listing.keys():
    #     print(key + ': ' + str(listing[key]))
    listing_norm = normalize(listing)
    # for key in listing_norm.keys():
    #     print(key + ': ' + str(listing_norm[key]))
    if 'price_per_space' in listing_norm:
        listings.append(listing_norm)

print(len(listings))