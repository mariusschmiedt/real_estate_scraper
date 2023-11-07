from scrapingant_client import ScrapingAntClient
from .services.scrapingAnt import needScrapingAnt, isScrapingAntApiKeySet, transformUrlForScrapingAnt
from .services.scraper import Scraper
from .services.queryStringMutator import queryStringMutator
from .services.sqlConnection import sqlConnection
from .services.writeListing import writeListing
from .services.getAddress import getAddress
from .utils import getDatabaseScheme

class PReEsCr():
    def __init__(self, providerConfig, metaConfig, url, house_type, table_name, country, base_path, update_prices=False):
        
        # initialize provider information
        self._providerConfig = providerConfig
        self._metaConfig = metaConfig
        self._providerConfig['search_url'] = url
        self._providerConfig['provider'] = self._metaConfig["id"]

        self.update_prices = update_prices
        # set country based on search url
        self._country = country
        # get database scheme
        self._base_path = base_path
        self._database_scheme = getDatabaseScheme(self._base_path)
        # create sql connection to listing table
        self.listing_sql = sqlConnection(table_name, self._base_path, self._database_scheme['listing_scheme'])
        # set indices of listing table
        self.listing_sql.preProcessDbTables()
        if self.update_prices:
            # check every active listing if it is still available
            self.listing_sql.getActiveTableElements()
        # create instance to write listings to database
        self.list_write = writeListing(self.listing_sql, update_prices)
        self.finishJob = self.list_write.finish
        # create sql connection to address table
        self.address_sql = sqlConnection('address_table', self._base_path, self._database_scheme['address_scheme'])
        self.address_sql.preProcessDbTables()
        # determine if a scraping ant is required
        self.ant_required = needScrapingAnt(self._providerConfig['provider'])
        # initialize scraper
        self.scraper = Scraper(self._providerConfig, self.ant_required, self._base_path, country, house_type)
    
    def exe(self, url):
        # scrape listings
        listingResponse = self._getListings(url)
        if type(listingResponse) == list:
            # normalize listings
            listings = self._normalize(listingResponse)
            # validate listings
            fault_listing = self._validation(listings)
            
            if fault_listing is None:
                # normalize address
                listings = self._normalize_address(listings)
                
                # save listings to database
                self._saveListing(listings)
                return None
            else:
                return fault_listing
        else:
            return listingResponse

    def _getPagination(self):
        mutateUrl = queryStringMutator(self._providerConfig['sortByDateParam'], self._providerConfig['provider'], self._providerConfig['paginate'])
        url = mutateUrl.urlSortParamModifier(self._providerConfig['search_url'])
        id = self._providerConfig['provider']
        if self.ant_required and not isScrapingAntApiKeySet(self._base_path):
            print('Immoscout or Immonet can only be used with if you have set an apikey for scrapingAnt.')
            return
        u = url
        if self.ant_required:
            u = transformUrlForScrapingAnt(url, id)
        paginationResponse = self.scraper.scrape(u, get_paginate = True)
        if paginationResponse is None:
            maxPageNum = self.scraper.maxPageNum
            listings_per_page = self.scraper.listings_per_page

            urls = list()
            for page in range(1, int(maxPageNum)+1):
                u = mutateUrl.paginationModifier(url, str(page), str(listings_per_page))
                if self.ant_required:
                    u = transformUrlForScrapingAnt(url, id)
                urls.append(u)

            if self._providerConfig['provider'] == 'immodirekt_at':
                search_url = urls[-1]
                urls = list()
                urls.append(search_url)

            return urls
        else:
            return paginationResponse

    def _getListings(self, url):
        return self.scraper.scrape(url)
    
    def _normalize(self, listings):
        return list(map(self._providerConfig['normalize'], listings))
    
    def _validation(self, listings):
        fault_listing = {}
        for listing in listings:
            if listing['price'] is None:
                fault_listing['price'] = None
            
            if listing['size'] is None:
                fault_listing['size'] = None

            if listing['rooms'] is None:
                fault_listing['rooms'] = None
            
            if listing['url'] is not None:
                if listing['url'] == '' or not listing['url'].startswith('http'):
                    fault_listing['url'] = listing['url']
            else:
                fault_listing['url'] = None
            
            if listing['provider_id'] is not None:
                if listing['provider_id'] == '':
                    fault_listing['provider_id'] = listing['provider_id']
            else:
                fault_listing['provider_id'] = None

            if bool(fault_listing):
                break
        
        if bool(fault_listing):
            return fault_listing
        else:
            return None
    
    def _normalize_address(self, listings):
        self.address_sql.openMySQL()
        for listing in listings:
            listing = getAddress(listing, self._country, self.address_sql)
        self.address_sql.closeMySQL()
        return listings

    def _saveListing(self, listings):
        self.listing_sql.openMySQL()
        for listing in listings:
            self.list_write.writeListingToDb(listing)
            self.finishJob = self.list_write.finish
            if self.finishJob:
                break
        self.listing_sql.closeMySQL()