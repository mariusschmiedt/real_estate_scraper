import urllib.parse as urlparse
from urllib.parse import urlencode

class queryStringMutator():
    def __init__(self, sortByDateParam, provider, paginateParam):
        self.sortByDateParam = sortByDateParam
        self.provider = provider
        self.paginateParam = paginateParam

    def urlSortParamModifier(self, url):
        if self.sortByDateParam == None:
            return url
        
        if self.sortByDateParam == '':
            return url
        
        if self.sortByDateParam in url:
            return url

        # parse url into its parts
        url_parts = urlparse.urlparse(url)
        if self.provider == 'kleinanzeigen':
            # get the path from the url
            old_path = url_parts.path
            # split the existing path
            old_split = old_path.split('/')
            # insert the sorting parameter
            old_split[0] = old_split[1]
            old_split[1] = self.sortByDateParam
            # form the new path
            new_path = '/' + '/'.join(old_split)
            # get the position of the old path
            url_parts = list(url_parts)
            idx = url_parts.index(old_path)
            # replace the old path with the new one
            url_parts[idx] = new_path
            # unparse list to new url
            url = urlparse.urlunparse(list(url_parts))
        elif self.provider == 'immoscout_at':
            # get the path from the url
            old_path = url_parts.path
            # form new path
            new_path = old_path + '/' + self.sortByDateParam
            # get the position of the old path
            url_parts = list(url_parts)
            idx = url_parts.index(old_path)
            # replace the old path with the new one
            url_parts[idx] = new_path
            # unparse list to new url
            url = urlparse.urlunparse(list(url_parts))
        else:
            # parse param to url format
            params = dict(urlparse.parse_qsl(self.sortByDateParam))
            # get the query from the url
            old_query = url_parts.query
            if old_query == '':
                url = url + '?' + self.sortByDateParam
            else:
                # split the existing query into parts
                query = dict(urlparse.parse_qsl(old_query))
                # create a list of the url
                url_parts = list(url_parts)
                # find the index of the old query
                idx = url_parts.index(old_query)
                # update the query with the params
                query.update(params)
                # update the url parts
                url_parts[idx] = urlencode(query)
                # unparse list to new url
                url = urlparse.urlunparse(list(url_parts))
        
        return url
    
    def paginationModifier(self, url, page, listings_per_page):
        if self.provider == 'comparis_ch':
            page = str(int(page) - 1)
        elif self.provider == 'findmyhome_at':
            page = str((int(page) - 1)  * listings_per_page)
        
        if self.provider == 'immoscout_at' or self.provider == 'derstandard_at':
            if int(page) > 1:
                url_parts = urlparse.urlparse(url)
                # get the path from the url
                old_path = url_parts.path
                # form new path
                new_path = old_path + '/' + self.paginateParam + page
                # get the position of the old path
                url_parts = list(url_parts)
                idx = url_parts.index(old_path)
                # replace the old path with the new one
                url_parts[idx] = new_path
                # cretae url
                url = urlparse.urlunparse(list(url_parts))
        elif self.provider == 'kleinanzeigen':
            # get url components
            url_parts = urlparse.urlparse(url)
            # get old path
            old_path = url_parts.path
            # split the existing path
            old_split = old_path.split('/')
            # insert the sorting parameter
            old_split[0] = old_split[1]
            old_split[1] = old_split[2]
            old_split[2] = self.paginateParam + page
            # form the new path
            new_path = '/' + '/'.join(old_split)
            # get the position of the old path
            url_parts = list(url_parts)
            idx = url_parts.index(old_path)
            # replace the old path with the new one
            url_parts[idx] = new_path
            # unparse list to new url
            url = urlparse.urlunparse(list(url_parts))
        else:
            url_parts = urlparse.urlparse(url)
            # parse param to url format
            params = dict(urlparse.parse_qsl(self.paginateParam + page))
            # get the query from the url
            old_query = url_parts.query
            if old_query == '':
                url = url + '?' + self.sortByDateParam
            else:
                # split the existing query into parts
                query = dict(urlparse.parse_qsl(old_query))
                # create a list of the url
                url_parts = list(url_parts)
                # find the index of the old query
                idx = url_parts.index(old_query)
                # update the query with the params
                query.update(params)
                # update the url parts
                url_parts[idx] = urlencode(query)
                # unparse list to new url
                url = urlparse.urlunparse(list(url_parts))
        return url