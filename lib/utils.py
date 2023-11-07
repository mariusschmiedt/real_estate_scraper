import json
import os

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
    return replaceArray(value, ['€', 'EURO', '\x82', 'â\x82¬', 'â¬', 'CHF', '$', 'Dollar', 'USD', '/mo', '.—', ',-', '&euro;'])

def replaceSizeUnit(value):
    return replaceArray(value, ['m&#178;', 'm&sup2;', 'm²', 'm2', 'm^2', 'sqft', 'mÂ²', 'm'])

def replaceRoomAbbr(value):
    return replaceArray(value, ['Zimmer', 'Zi.', 'Zi', 'Rooms', 'Ro'])

def replaceArray(value, array):
    if array is not None:
        for arr in array:
            if arr in value:
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
    if '€' in value or 'EUR' in value or '\x82' in value or '&euro;' in value:
        currency = 'EUR'
    if 'CHF' in value:
        currency = 'CHF'
    if '$' in value or 'Dollar' in value or 'USD' in value :
        currency = 'USD'
    return currency

def getSizeUnit(value):
    unit = 'm^2'
    if 'm²' in value or 'm2' in value or 'm^2' in value or 'mÂ²' in value or 'm' in value or 'm&sup2;' in value or 'm&#178;' in value:
        unit = 'm^2'
    if 'sqft' in value:
        unit = 'sqft'
    return unit

def findPostalCodeInAddress(address):
    postalcode = ''
    if address is not None:
        # split found address
        address_split = address.split(' ')
        # find post code in address
        for add in address_split:
            # check if address part is number
            num = False
            try:
                int(add)
                num = True
            except:
                pass
            # if number has more than 4 digits it is propably a postalcode
            if len(add) >= 4 and num:
                postalcode = add

    return postalcode

def getNum(value):
    val_split = value.split(' ')
    new_value = ''
    for v in val_split:
        num = False
        try:
            float(v)
            num = True
        except:
            pass
        if num:
            new_value = str(float(v))
            if new_value.endswith('.0'):
                new_value = new_value.replace('.0', '')
            if new_value.endswith('.'):
                new_value = new_value.replace('.', '')
    return new_value

def numConvert_de(value):
        comma_count = value.count(',')
        dot_count = value.count('.')

        if comma_count == 1 and dot_count == 0:
            value = value.replace(',', '.')
        elif dot_count >= 1 and comma_count == 1:
            value = value.replace('.', '').replace(',', '.')
        elif dot_count >= 1 and comma_count == 0:
            value = value.replace('.', '')
        return value