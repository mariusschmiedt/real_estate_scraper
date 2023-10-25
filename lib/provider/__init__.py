from .immonet_not_done import provider as immonet
from .immoscout import provider as immoscout
from .immoswp import provider as immoswp
from .immowelt import provider as immowelt
from .kleinanzeigen import provider as kleinanzeigen
from .immoscoutch import provider as immoscout_ch
from .zillow import provider as zillow
from .homegate import provider as homegate

def getProvider(provider):
    if provider == 'immoswp':
        return immoswp()
    if provider == 'immoscout':
        return immoscout()
    if provider == 'immoscout_ch':
        return immoscout_ch()
    if provider == 'immonet':
        return immonet()
    if provider == 'immowelt':
        return immowelt()
    if provider == 'kleinanzeigen':
        return kleinanzeigen()
    if provider == 'zillow':
        return zillow()
    if provider == 'homegate':
        return homegate()