from .immonet import provider as immonet
from .immoscout import provider as immoscout
from .immoswp import provider as immoswp
from .immowelt import provider as immowelt
from .kleinanzeigen import provider as kleinanzeigen

def getProvider(provider):
    if provider == 'immoswp':
        return immoswp()
    if provider == 'immoscout':
        return immoscout()
    if provider == 'immonet':
        return immonet()
    if provider == 'immowelt':
        return immowelt()
    if provider == 'kleinanzeigen':
        return kleinanzeigen()