import requests
from ..utils import getProviderConfig
from .scrapingAnt import makeUrlResidential

class makeDriver():
    def __init__(self, headers = {}):
        self.cookies = ''
        self.headers = headers
        BLOCKED_HTTP_STATUS = 423
        NOT_FOUND_HTTP_STATUS = 404
        self.MAX_RETRIES_SCRAPING_ANT = 10
        self.EXPECTED_STATUS_CODES = [BLOCKED_HTTP_STATUS, NOT_FOUND_HTTP_STATUS]

    def scrapingAntDriver(self, url, retryCounter = 0):
        result = None
        while retryCounter <= self.MAX_RETRIES_SCRAPING_ANT:
            proxyType = 'datacenter'
            config = getProviderConfig()
            if 'scrapingAnt' in config:
                if 'proxy' in config['scrapingAnt']:
                    proxyType = config['scrapingAnt']['proxy']
            
            try:
                url = url
                if proxyType == 'residential':
                    url =  makeUrlResidential(url)
                
                session = requests.Session()
                response = session.get(url, headers=self.headers)
                result = response.text
                if (len(self.cookies) == 0):
                    self.cookies = session.cookies.get_dict()

                
                break
            except requests.exceptions.HTTPError as err:
                print(err)
                break
            except Exception as e:
                if retryCounter <= self.MAX_RETRIES_SCRAPING_ANT:
                    retryCounter = retryCounter + 1
                    print("ScrapingAnt got blocked. Retrying " + str(retryCounter) + " / " + str(self.MAX_RETRIES_SCRAPING_ANT))
                else:
                    print("Error while trying to scrape data from scraping ant. Received error: " + str(e.message))
        
        return result
    
    def driver(self, url):
        if not 'scrapingant' in url.lower():
            return self.scrapingAntDriver(url)
        
        try:
            session = requests.Session()
            response = session.get(url, headers=self.headers, cookies=self.cookies)
            result = response.text()
            return result
        except Exception as e:
            print("Error while trying to scrape data. Received error: " + str(e.message))
            return None
