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
                result = [r for r in result if r.attrs[attr_dict['attr_name']] == attr_dict['attr_val_des']]
                if attr_dict['attr_val_des_start']:
                    result = [r for r in result if r.attrs[attr_dict['attr_name']].startswith(attr_dict['attr_val_des'])]
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
                result = result.text.replace('\n', '').strip()
                result = [i for i in result.split(' ') if i != ''][attr_dict['split']]
            elif attr_dict['tag_split'] is not None and not attr_dict['raw']:
                result = result.find_all()[attr_dict['tag_split']]
                result = result.text.replace('\n', '').strip()
            elif attr_dict['raw']:
                result = str(result)
            else:
                result = result.text.replace('\n', '').strip()
                result = ' '.join([i for i in result.split(' ') if i != ''])
    else:
        if attr_dict['attr_val_des'] is not None and attr_dict['tag'] is not None:
            if 'json' in attr_dict['attr_val_des'] and attr_dict['tag'] == 'script':
                result = json.loads(result[attr_dict['child']].text)
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

def getJsonResult(container, value):
    keys = value.split('.')
    for key in keys:
        if key in container:
            container = container[key]
    return container

def normalize(o):
    o['postalcode'] = ''
    for add in o['address_detected'].split(' '):
        num = False
        try:
            int(add)
            num = True
        except:
            pass
        if num and len(add) >=4:
            o['postalcode'] = add
    if '|' in o['address_detected']:
        o['city'] = o['address_detected'].split('|')[0].replace('Bezirk:', '').replace('-Umgebung', '').strip()
        o['city'] = re.sub('\(.*\)', '', o['city']).strip()
        o['city'] = re.sub('[0-9].*', '', o['city']).strip()
    o['provider_id'] = o['provider_id'].split('/')[-1].split('-')[0].strip()
    o['url'] = 'https://www.flatbee.at/' + 'properties/searchengine_property_detail/' + o["provider_id"]
    if '&euro;' in o['price'] or '€' in o['price']:
        o['currency'] = 'EUR'
    o['price'] = o['price'].replace('&euro;', '').replace('€', '').replace(',-', '').strip()
    o['price'] = numConvert(o['price'])
    if 'm²' in o['size']:
        o['size_unit'] ='m^2'
    o['size'] = o['size'].replace('m²', '').strip()
    o['size'] = numConvert(o['size'])
    o['size'] = getNum(o['size'])
    o['rooms'] = o['rooms'].replace('Zimmer', '').strip()
    o['rooms'] = numConvert(o['rooms'])
    try:
        o['price_per_space'] = str(round((float(o['price']) / float(o['size'])), 2))
    except:
        pass
    return o

def numConvert(value):
    comma_count = value.count(',')
    dot_count = value.count('.')
    if comma_count == 1 and dot_count == 0:
        value = value.replace(',', '.')
    elif dot_count == 1 and comma_count == 1:
        value = value.replace('.', '').replace(',', '.')
    elif dot_count == 1 and comma_count == 0:
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

config = {
    "search_url": None,
    "crawlContainer": 'div.col-lg-4*',
    "sortByDateParam": '',
    "crawlFields": {
        "provider_id": 'a@href',
        "price": 'div.property-box-pricev',
        "size": 'div.property-box-meta-itemv col-lg-3*:2c',
        "rooms": 'div.property-box-meta-itemv col-lg-3*:1c',
        "title": 'h3.property-titlev g_d_none*',
        "url": 'a@href',
        "address_detected": 'table.table sp_tbl:3t',
    },
    "num_listings": 'div.countProperty:1s',
}

# soup = BeautifulSoup(page_content,'html5lib')

with open("/Users/mariusschmiedt/github/fredy_python/lib/provider/example_pages/flatbee_at.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')

attr_dict = getAttr(config['crawlContainer'])
containers = getContent(soup, attr_dict, get_container=True)

found_listings = 0
if 'num_listings' in config:
    if type(containers) == dict:
        found_listings = int(getJsonResult(containers, config['num_listings']))
    else:
        attr_dict = getAttr(config['num_listings'])
        found_listings_num = getContent(soup, attr_dict)
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
        attr_dict = getAttr(config['crawlFields'][key])
        result = getContent(con, attr_dict)
    if result is not None:
        listing[key] = result

listing = normalize(listing)

for key in listing.keys():
    print(key + ': ' + str(listing[key]))
