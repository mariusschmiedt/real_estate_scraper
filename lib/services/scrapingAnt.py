from ..provider.germany.immoscout_de import provider as immoScoutInfo
from ..provider.germany.immonet_de import provider as immoNetInfo
from ..provider.united_states.zillow_us import provider as zillowInfo
from ..provider.switzerland.homegate_ch import provider as homegateInfo
from ..provider.switzerland.immoscout_ch import provider as immoscoutChInfo
from ..utils import getAntConfig

def needScrapingAnt(base_path, id):
    config = getAntConfig(base_path)
    return id.lower() in config['antRequired']

def transformUrlForScrapingAnt(url, id):
    urlParams = ''
    if needScrapingAnt(id):
        # if id.lower() == immoNetInfo().metaInformation['id']:
        #     urlParams = "&wait_for_selector=.content-wrapper-tiles&js_snippet="  + Buffer.from('window.scrollTo(0,document.body.scrollHeight);').toString('base64')}
        url = "https://api.scrapingant.com/v2/general?url=" + encodeURIComponent(url) + "&proxy_type=datacenter" + urlParams
    return url

def isScrapingAntApiKeySet(base_path):
    apiKeySet = False
    config = getAntConfig(base_path)
    if 'scrapingAnt' in config:
        if 'apiKey' in config['scrapingAnt']:
            if len(config['scrapingAnt']['apiKey']) > 0:
                apiKeySet = True
    return apiKeySet

def makeUrlResidential(url):
    return url.replace('datacenter', 'residential')