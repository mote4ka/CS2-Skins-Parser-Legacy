import json

def get_csm_data():
    with open("temp/csm_data.json", "r", encoding='utf-8') as file:
        data = json.loads(file.read())
    return data

def get_lsk_data():
    with open("temp/lsk_data.json", "r", encoding='utf-8') as file:
        data = json.loads(file.read())
    return data