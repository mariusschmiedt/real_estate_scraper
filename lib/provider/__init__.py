from .immonet_not_done import provider as immonet
from .immoscout import provider as immoscout
from .immoswp import provider as immoswp
from .immowelt import provider as immowelt
from .kleinanzeigen import provider as kleinanzeigen
from .immoscoutch import provider as immoscout_ch
from .zillow import provider as zillow
from .homegate import provider as homegate
from .comparis import provider as comparis
from .homech import provider as homech
from .findmyhome_at import provider as findmyhome_at
from .immoscout_at import provider as immoscout_at
from .derstandard_at import provider as derstandard_at
from .flatbee_at import provider as flatbee_at
from .immo_kurier_at import provider as immo_kurier_at
from .willhaben_at import provider as willhaben_at
from .wohnnet_at import provider as wohnnet_at

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
    if provider == 'comparis':
        return comparis()
    if provider == 'homech':
        return homech()
    if provider == 'findmyhome_at':
        return findmyhome_at()
    if provider == 'immoscout_at':
        return immoscout_at()
    if provider == 'derstandard_at':
        return derstandard_at()
    if provider == 'flatbee_at':
        return flatbee_at()
    if provider == 'immo_kurier_at':
        return immo_kurier_at()
    if provider == 'willhaben_at':
        return willhaben_at()
    if provider == 'wohnnet_at':
        return wohnnet_at()