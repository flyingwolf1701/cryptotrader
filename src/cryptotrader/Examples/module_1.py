import logging
import requests

logger = logging.getLogger()

def get_contracts_binance():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response_object = requests.get(url)

    contracts = []

    response_object = requests.get(url)
    for contract in response_object.json()['symbols']:
        contracts.append(contract['pair'])
    return contracts

def get_contracts_bitmex():
    contracts = []
    url = "https://www.bitmex.com/api/v1/instrament/active"
    response_object = requests.get(url)
    for contract in response_object.json():
        contracts.append(contract['symbol'])
    return contracts