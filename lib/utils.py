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