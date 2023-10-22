import json
import os

def isOneOf(word, arr):
    if arr is None:
        return False
    else:
        if len(arr) == 0:
            return False
    return word in arr


def getProviderConfig(base_path):
    with open(os.path.join(base_path, 'conf/config.json')) as f:
        providerConfig = json.load(f)
    return providerConfig

def getDataBaseConfig(base_path):
    with open(os.path.join(base_path, 'conf/db_config.json')) as f:
        databaseConfig = json.load(f)
    return databaseConfig

def getDatabaseScheme(base_path):
    with open(os.path.join(base_path, 'conf/database_scheme.json')) as f:
        databaseScheme = json.load(f)
    return databaseScheme

def getLanguageId(base_path, country):
    with open(os.path.join(base_path, 'conf/language_id.json')) as f:
        languageDict = json.load(f)
    languageId = languageDict[country]
    return languageId

def replaceCurrency(value):
    return replaceArray(value, ['€', 'EURO', '\x82', 'â\x82¬', 'â¬', 'CHF', '$', 'Dollar', 'USD', '/mo', '+'])

def replaceSizeUnit(value):
    return replaceArray(value, ['m²', 'm2', 'm^2', 'sqft', 'mÂ²'])

def replaceRoomAbbr(value):
    return replaceArray(value, ['Zimmer', 'Zi.', 'Zi'])

def replaceArray(value, array):
    for arr in array:
        value = value.replace(arr, '').strip()
    return value

def replaceChrs(value):
    replacements = {
        "'": '',
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ü": "Ue",
        "Ö": "Oe",
        "Ä": "Ae",
        "ß": "ss"
    }
    for rep in replacements.keys():
        value = value.replace(rep, replacements[rep]).strip()
    return value

def getCurrency(value):
    currency = 'EUR'
    if '€' in value or 'EUR' in value or '\x82' in value:
        currency = 'EUR'
    if 'CHF' in value:
        currency = 'CHF'
    if '$' in value or 'Dollar' in value or 'USD' in value :
        currency = 'USD'
    return currency

def getSizeUnit(value):
    unit = 'm^2'
    if 'm²' in value or 'm2' in value or 'm^2' in value or 'mÂ²' in value:
        unit = 'm^2'
    if 'sqft' in value:
        unit = 'sqft'
    return unit