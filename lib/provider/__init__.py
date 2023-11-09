from .germany.immonet_not_done import provider as immonet
from .germany.immoscout_de import provider as immoscout_de
from .germany.immoswp_de import provider as immoswp_de
from .germany.immowelt_de import provider as immowelt_de
from .germany.kleinanzeigen_de import provider as kleinanzeigen_de
from .switzerland.immoscout_ch import provider as immoscout_ch
from .united_states.zillow_us import provider as zillow_us
from .switzerland.homegate_ch import provider as homegate_ch
from .switzerland.comparis_ch import provider as comparis_ch
from .switzerland.home_ch import provider as home_ch
from .austria.findmyhome_at import provider as findmyhome_at
from .austria.immoscout_at import provider as immoscout_at
from .austria.derstandard_at import provider as derstandard_at
from .austria.flatbee_at import provider as flatbee_at
from .austria.immo_kurier_at import provider as immo_kurier_at
from .austria.willhaben_at import provider as willhaben_at
from .austria.wohnnet_at import provider as wohnnet_at
from .austria.immodirekt_at import provider as immodirekt_at

def getProvider(provider):
    if provider == 'immoswp_de':
        return immoswp_de()
    if provider == 'immoscout_de':
        return immoscout_de()
    if provider == 'immoscout_ch':
        return immoscout_ch()
    if provider == 'immonet':
        return immonet()
    if provider == 'immowelt_de':
        return immowelt_de()
    if provider == 'kleinanzeigen_de':
        return kleinanzeigen_de()
    if provider == 'zillow_us':
        return zillow_us()
    if provider == 'homegate_ch':
        return homegate_ch()
    if provider == 'comparis_ch':
        return comparis_ch()
    if provider == 'home_ch':
        return home_ch()
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
    if provider == 'immodirekt_at':
        return immodirekt_at()