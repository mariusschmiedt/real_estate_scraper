from bs4 import BeautifulSoup
import re
import json
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
        class_name = value.split('@')[0]
        if class_name == '':
            class_name = None
        attr_name = value.split('@')[1]
        if '=' in attr_name:
            attr_name_split = attr_name.split('=')
            attr_name = attr_name_split[0]
            attr_val_des = attr_name_split[1]
    
    if '.' in value:
        value_split = value.split('.')
        if class_name is not None:
            value_split = class_name.split('.')
        tag = value_split[0]
        class_name = ' '.join([value_split[v] for v in range(1, len(value_split))])
    
    if class_name is not None:
        if ':' in class_name:
            class_split = class_name.split(':')
            class_name = class_split[0]
            for c in range(1, len(class_split)):
                if class_split[c].endswith('c'):
                    child = int(class_split[c].replace('c', ''))-1
                if class_split[c].endswith('s'):
                    split = int(class_split[c].replace('s', ''))-1
                if class_split[c].endswith('t'):
                    tag_split = int(class_split[c].replace('t', ''))-1
                if class_split[c].endswith('raw'):
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
    
    return tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw


def getContent(container, tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw, get_container = False):
    result = None
    if child is None:
        child = 0
    if tag is not None:
        tag_find = container.find_all(tag, {"class": class_name})
        if class_name_start:
            tag_find = container.find_all(tag, {"class": lambda v: v and v.startswith(class_name)})
        result = [r for r in tag_find]
        if attr_name is not None:
            result = [r for r in result if attr_name in r.attrs]
        if len(result) == 0:
            result = None
    if not get_container:
        get_tag_content = False
        if attr_name is not None:
            if attr_val_des is not None:
                result = [r for r in result if r.attrs[attr_name] == attr_val_des]
                if attr_val_des_start:
                    result = [r for r in result if r.attrs[attr_name].startswith(attr_val_des)]
                get_tag_content = True
            else:
                if tag is not None and result is not None:
                    result = result[child].get(attr_name)
                else:
                    result = container.get(attr_name)
        elif attr_name is None and result is not None:
            get_tag_content = True
        if get_tag_content:
            result = result[child]
            if split is not None and not raw:
                result = result.text.replace('\n', '').strip()
                result = result.split(' ')[split]
            elif tag_split is not None and not raw:
                result = result.find_all()[tag_split]
                result = result.text.replace('\n', '').strip()
            elif raw:
                result = str(result)
            else:
                result = result.text.replace('\n', '').strip()
    if attr_val_des is not None and tag is not None:
        if 'json' in attr_val_des and tag == 'script':
            result = json.loads(result[child].text)
    return result

def getJsonResult(container, value):
    keys = value.split('.')
    for key in keys:
        if key in container:
            container = container[key]
    return container

def normalize(o):
    o['size_unit'] = 'm'
    o['size'] = o['size'].replace('m', '').strip()
    size_split = o['size'].split(' ')
    if type(size_split) == list:
        if len(size_split) > 1:
            o['size'] = size_split[0]
    o['rooms'] = o['rooms'].replace('Rooms', '').strip()
    o['price'] = o['price'].replace("'", '')
    o['size'] = o['size'].replace("'", '')
    o['rooms'] = o['rooms'].replace("'", '')
    o['provider_id'] = o['provider_id'].split('ad-link-')[1]
    url = ''
    if o['price'] is not None:
        if o['price'] != '':
            if int(o['price']) < 20000:
                url = 'https://www.homegate.ch/rent/' + o['provider_id']
            else:
                url = 'https://www.homegate.ch/buy/' + o['provider_id']
    
    o['url'] = url
    if url == '':
        o['price'] = ''
    for add in o['address_detected'].split(' '):
        num = False
        try:
            int(add)
            num = True
        except:
            pass
        if num and len(add) >=4:
            o['postalcode'] = add
    
    o['city'] = o['address_detected'].replace(o['postalcode'], '').strip()
    
    try:
        o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
    except:
        pass
    return o

config = {
    "search_url": None,
    "crawlContainer": 'a.row search-results__list__item*',
    "sortByDateParam": 'sort=dd',
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
}

# soup = BeautifulSoup(page_content,'html5lib')

with open("/Users/mariusschmiedt/github/fredy_python/lib/provider/example_pages/homech.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')

tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw = getAttr(config['crawlContainer'])
containers = getContent(soup, tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw, get_container=True)

found_listings = 0
if 'num_listings' in config:
    if type(containers) == dict:
        found_listings = int(getJsonResult(containers, config['num_listings']))
    else:
        tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw = getAttr(config['num_listings'])
        found_listings_num = getContent(soup, tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw)
        found_listings_num = re.sub('[^0-9]','', found_listings_num)
        found_listings = int(found_listings_num)

if type(containers) == dict:
    containers = getJsonResult(containers, config['jsonContainer'])    

con = containers[0]

listing = {}
for key in config['crawlFields'].keys():
    listing[key] = ''

for key in config['crawlFields'].keys():
    result = None
    if type(con) == dict:
        if config['crawlFields'][key] in con:
            result = con[config['crawlFields'][key]]
    else:
        tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw = getAttr(config['crawlFields'][key])
        result = getContent(con, tag, class_name, attr_name, attr_val_des, class_name_start, attr_val_des_start, child, split, tag_split, raw)
    if result is not None:
        listing[key] = result

listing = normalize(listing)

for key in listing.keys():
    print(key + ': ' + str(listing[key]))
