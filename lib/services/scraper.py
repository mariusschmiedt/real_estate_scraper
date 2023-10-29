import re
import requests
import math
import datetime
import json
from bs4 import BeautifulSoup
import html5lib
import locale
from scrapingant_client import ScrapingAntClient
import random
from ..utils import getProviderConfig, getLanguageId, getDatabaseScheme, replaceChrs
from .requestDriver import makeDriver

class Scraper():
    def __init__(self, providerConfig, needScrapingAnt, base_path, country, house_type):
        
        self.needScrapingAnt = needScrapingAnt
        self.providerConfig = providerConfig
        self.languageId = getLanguageId(base_path, country)
        self.database_schemes = getDatabaseScheme(base_path)
        self.table_columns = self.database_schemes['listing_scheme']
        self.house_type = house_type

        user_agents_list = [
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        ]

        self.headers={'User-Agent': random.choice(user_agents_list)}

        self.config = getProviderConfig(base_path)
        
        if 'scrapingAnt' in self.config:
            if 'apiKey' in self.config['scrapingAnt']:
                self.headers['x-api-key'] = self.config['scrapingAnt']['apiKey']
        
        self.driver = makeDriver(self.headers)

        self.maxPageNum = '1'
    
    def scrape(self, url, get_paginate = False):
        page_content = None

        if self.needScrapingAnt:
            if self.driver.cookies != '':
                cookies = '&cookies=' + '%3B'.join([cookie + '%3D' + self.driver.cookies[cookie] for cookie in self.driver.cookies.keys()])
                url = url + cookies
            client = ScrapingAntClient(token=self.config.scrapingAnt.apiKey)
            page_content = client.general_request(url).content
        else:
            session = requests.Session()
            response = session.get(url, headers=self.headers, cookies=self.driver.cookies)
            page_content = response.text
        
        soup = BeautifulSoup(page_content,'html5lib')
        attr_dict = self.getAttr(self.providerConfig['crawlContainer'])
        containers = self.getContent(soup, attr_dict, get_container=True)
        
        

        if get_paginate:
            found_listings = 0
            if 'num_listings' in self.providerConfig:
                if type(containers) == dict:
                    found_listings = int(self.getJsonResult(containers, self.providerConfig['num_listings']))
                else:
                    attr_dict = self.getAttr(self.providerConfig['num_listings'])
                    found_listings_num = self.stringToNumber(self.getContent(soup, attr_dict), self.languageId)
                    found_listings_num = re.sub('[^0-9]','', found_listings_num)
                    found_listings = int(found_listings_num)
            
            if type(containers) == dict:
                containers = self.getJsonResult(containers, self.providerConfig['jsonContainer'])    
            
            listings_per_page = len(containers)
            if 'listings_per_page' in self.providerConfig:
                if self.providerConfig['listings_per_page'] != '':
                    try:
                        listings_per_page = int(self.providerConfig['listings_per_page'])
                    except:
                        raise Exception('Parameter "listings_per_page" of config ' + self.providerConfig['provider'] + ' must be a number')
            if 'maxPageResults' in self.providerConfig:
                if self.providerConfig['maxPageResults'] != '':
                    try:
                        found_listings = min(int(self.providerConfig['maxPageResults']), found_listings)
                    except:
                        raise Exception('Parameter "maxPageResults" of config ' + self.providerConfig['provider'] + ' must be a number')
            self.listings_per_page = listings_per_page
            self.maxPageNum  = str(math.ceil(int(found_listings) / int(listings_per_page)))
        else:
            return self.readListings(containers)
        
    def readListings(self, containers):        
        listings = list()

        for con in containers:

            listing = {}
            for key in self.table_columns.keys():
                listing[key] = ''

            listing['provider'] = self.providerConfig['provider']
            listing['type'] = self.house_type
            listing['active'] = '1'

            for key in self.providerConfig['crawlFields'].keys():
                result = None
                if type(con) == dict:
                    if self.providerConfig['crawlFields'][key] in con:
                        result = con[self.providerConfig['crawlFields'][key]]
                else:
                    attr_dict = self.getAttr(self.providerConfig['crawlFields'][key])
                    result = self.getContent(con, attr_dict)
                if result is not None:
                    listing[key] = replaceChrs(result)
            
            if listing['in_db_since'] == '':
                listing['in_db_since'] = str(datetime.datetime.now().strftime("%Y-%m-%d"))

            try:
                listing['price_per_space'] = str(round((float(listing['price']) / float(listing['size'])), 2))
            except:
                pass
            listings.append(listing)
        return listings
                
    def getAttr(self, value):
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
    
    def getContent(self, container, attr_dict, get_container = False):
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
                if 'top_field' in self.providerConfig:
                    attr_dict_top = self.getAttr(self.providerConfig['top_field'])
                    result1 = result
                    result = list()
                    for con in result1:
                        tag_find = con.find_all(attr_dict_top['tag'], {"class": attr_dict_top['class_name']})
                        top_find = [r for r in tag_find]
                        if len(top_find) == 0:
                            result.append(con)
        return result
    
    def getJsonResult(self, container, value):
        keys = value.split('.')
        for key in keys:
            if key in container:
                container = container[key]
            else:
                raise Exception('Dictionary key "' + key + '" is not part of the json result of ' + self.providerConfig['provider'] + '.')
        return container
    
    def stringToNumber(self, value, languageId):
        if languageId.startswith('de') or languageId.startswith('es') or languageId.startswith('it') or languageId.startswith('fr'):
            value = value.replace('.', '')
            value = value.replace(' ', '')
            value = value.replace(',', '.')
        elif languageId.startswith('en'):
            value = value.replace(',', '')
            value = value.replace(' ', '')
        
        return value
