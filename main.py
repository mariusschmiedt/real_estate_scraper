import os
import json
from lib.provider import getProvider
from lib.FredyRuntime import FredyRuntime
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
            fredy = FredyRuntime(provider.config, provider.metaInformation, job["url"], job["house_type"], job["table_name"], job["country"], current_path, update_prices=False)
            print('Initialisiere: ' + str(time.time() - start_time))
            urls = fredy._getPagination()
            print('gefundene urls: ' + str(len(urls)))
            for url in urls[0:maxPageNum]:
                start_time = time.time()
                fredy.exe(url)
                if fredy.finishJob:
                    break
                print('scraping: ' + str(time.time() - start_time))