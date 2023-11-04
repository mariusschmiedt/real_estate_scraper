import os
import json
from lib.provider import getProvider
from lib.preescr import PReEsCr
from lib.services.get_jobs import getJobs
import time

current_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_path, 'jobs/jobs.json')) as f:
    jobs = json.load(f)

maxPageNum = 2
provider_list = jobs.keys()
for prov in provider_list:
    provider = getProvider(prov)
    joblist = getJobs(jobs, prov)
    for job in joblist:
        if job["house_type"] is not None and job["table_name"] is not None and job["url"] is not None:
            start_time = time.time()
            crawler = PReEsCr(provider.config, provider.metaInformation, job["url"], job["house_type"], job["table_name"], job["country"], current_path, update_prices=False)
            print('Initialisiere: ' + str(time.time() - start_time))
            response = crawler._getPagination()
            url_idx = 0
            problem_string = ''
            if type(response) == list:
                urls = response
                print('gefundene urls: ' + str(len(urls)))
                for url_idx in range(len(urls))[0:maxPageNum]:
                    start_time = time.time()
                    response = crawler.exe(urls[url_idx])

                    if response is not None:
                        if type(response) == str:
                            problem_string = 'Scraper seems to got blocked. ' + (url_idx + 1) + ' pages could get analyzed before being blocked\n\n'
                        elif type(response) == dict:
                            problem_keys = ', '.join(['listing[' + key + '] = ' + str(response[key]) for key in response.keys()])
                            problem_string = 'Some crawlFields needs to be adjusted: ' + problem_keys
                        break

                    if crawler.finishJob:
                        break
                    print('scraping: ' + str(time.time() - start_time))
            else:
                problem_string = 'Proxy needs to be defined or crawlcontainer changed.\n\n'
            
            if problem_string != '':
                issue = "Problem occured while scraping " + provider.metaInformation['name'] + ':\n'
                issue = issue + problem_string
                if type(response) == str:
                    log_path = os.path.join(current_path, 'logs/bad_request_' + provider.metaInformation['id']  + '.html')
                    issue = issue + 'Bad request. The following response from the request have been detected:\n'
                    issue = issue + log_path
                    with open(log_path, 'w') as file:
                        file.write(response)
                raise Exception(issue)