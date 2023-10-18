from ..provider.immoscout import provider as immoScoutInfo
from ..provider.immonet import provider as immoNetInfo
from ..utils import getProviderConfig

def needScrapingAnt(id):
    return id.lower() == immoScoutInfo().metaInformation['id'] or id.lower() == immoNetInfo().metaInformation['id']

def transformUrlForScrapingAnt(url, id):
    urlParams = ''
    if needScrapingAnt(id):
        # if id.lower() == immoNetInfo().metaInformation['id']:
        #     urlParams = "&wait_for_selector=.content-wrapper-tiles&js_snippet="  + Buffer.from('window.scrollTo(0,document.body.scrollHeight);').toString('base64')}
        url = "https://api.scrapingant.com/v2/general?url=" + encodeURIComponent(url) + "&proxy_type=datacenter" + urlParams
    return url

def isScrapingAntApiKeySet(base_path):
    apiKeySet = False
    config = getProviderConfig(base_path)
    if 'scrapingAnt' in config:
        if 'apiKey' in config['scrapingAnt']:
            if len(config['scrapingAnt']['apiKey']) > 0:
                apiKeySet = True
    return apiKeySet

def makeUrlResidential(url):
    return url.replace('datacenter', 'residential')