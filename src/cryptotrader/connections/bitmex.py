import requests

def get_contracts():
    contracts = []
    url = "https://www.bitmex.com/api/v1/instrament/active"
    response_object = requests.get(url)
    for contract in response_object.json():
        contracts.append(contract['symbol'])
    return contracts
