import os
from lib.provider import getProvider
from lib.utils import getDatabaseScheme
from lib.services.sqlConnection import sqlConnection
from lib.preescr import PReEsCr
from lib.services.get_jobs import getJob
import time


def main_control(provider_name, search_type, maxPageNum = None):
    timeout = 14.25 # minutes
    process_start_time = time.time()

    current_path = os.path.dirname(os.path.abspath(__file__))

    database_scheme = getDatabaseScheme(current_path)
    resume_sql = sqlConnection('resume_table', current_path, database_scheme['resume_scheme'])
    resume_sql.preProcessDbTables()

    provider = getProvider(provider_name)
    job = getJob(provider_name, search_type, current_path)

    url_idx_start = 0
    resume_sql.openMySQL()
    found_ids = resume_sql.querySql("SELECT resume_id FROM resume_table WHERE job='" + provider_name + '_' + search_type + "'")
    if len(found_ids) > 0:
        url_idx_start = found_ids[0][0]
    resume_sql.closeMySQL()
    
    start_time = time.time()
    crawler = PReEsCr(provider.config, provider.metaInformation, job["url"], job["house_type"], job["table_name"], job["country"], current_path, update_prices=False)
    print('Initialisiere: ' + str(time.time() - start_time))
    response = crawler._getPagination()

    problem_string = ''
    if type(response) == list:
        urls = response
        if maxPageNum is None:
            maxPageNum = len(urls)
        print('gefundene urls: ' + str(len(urls)))
        
        for url_idx in range(url_idx_start, len(urls))[0:maxPageNum]:
            start_time = time.time()
            response = crawler.exe(urls[url_idx])
            if response is not None:
                if type(response) == str:
                    problem_string = 'Scraper seems to got blocked. ' + str(url_idx + 1) + ' pages could get analyzed before being blocked\n\n'
                elif type(response) == dict:
                    problem_keys = ', '.join(['listing[' + key + '] = ' + str(response[key]) for key in response.keys()])
                    problem_string = 'Some crawlFields needs to be adjusted: ' + problem_keys
                break
            if (time.time() - process_start_time) >= (timeout * 60) or crawler.finishJob:
                resume_sql.openMySQL()
                if not crawler.finishJob:
                    if url_idx_start == 0:
                        resume_sql.querySql("INSERT INTO resume_table (job, resume_id) VALUES ('" + provider_name + '_' + search_type + "'," + str(url_idx + 1) + "); ")
                    else:
                        resume_sql.querySql("UPDATE resume_table SET resume_id = " + str(url_idx + 1) + " WHERE job = '" + provider_name + '_' + search_type + "'")
                else:
                    if url_idx_start != 0:
                        resume_sql.querySql("DELETE FROM resume_table WHERE job = '" + provider_name + '_' + search_type + "';")
                resume_sql.closeMySQL()
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
        return issue
    else:
        return 'Success'

provider_name = 'bayut_uae'
search_type = 'apartement_buy'
maxPageNum = 2

result = main_control(provider_name, search_type, maxPageNum)
print(result)