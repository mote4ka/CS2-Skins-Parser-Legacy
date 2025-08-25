import io
import json
import ijson
import re
import requests

import sys

#from data_full import *



def csm_data_process(output_file):

    # collect data from api
    req = requests.get("https://market.csgo.com/api/v2/prices/RUB.json")
    items = req.json().get('items')
    
    counter = 0
    skipped_counter = 0
    result_dict = {}

    # get ignore names
    with open('ignorelist.txt', 'r',encoding='utf-8') as file:
        ignorelist = file.read().splitlines()

    # loop for each item in collected items
    for item in items:
        
        name = item.get('market_hash_name')
        # check if item in ignore list
        if any(ignore_word in name for ignore_word in ignorelist):
            skipped_counter +=1
        else:
            # add item in dict with volume and price
            result_dict[name] = {'price' : item.get('price'),
                             'volume': item.get('volume')}
       
            # increment counter
            counter += 1

    # save dict to file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(result_dict, file, ensure_ascii=False, indent=2)

    # print items amount
    print(f"CSM saved {counter} items, skipped {skipped_counter} items")



def lsk_collect_data(output_file):
    f = io.open(output_file, 'w',encoding="utf-8")

    req = requests.get("https://lis-skins.com/market_export_json/api_csgo_full.json")
    
    f.write(str(req.content))
    f.close()
    print("Lsk data collected!")



def lsk_data_process(input_file, output_file):
    
    # open input file with raw data
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # seek for all names and price in file
    name_pattern = r'"name"\s*:\s*"([^"]*)"'
    price_pattern = r'"price"\s*:\s*([0-9.]+)'
    
    names = re.findall(name_pattern, content)
    prices = re.findall(price_pattern, content)
    
    # set price to equal name (same oreder)
    result_dict = {}
    min_len = min(len(names), len(prices))

    # get names to ignore
    with open('ignorelist.txt', 'r',encoding='utf-8') as file:
        ignorelist = file.read().splitlines()
    skipped_counter = 0
    

    for i in range(min_len):
        # get name and fix stattrack and knifes symbols
        name = names[i].replace('\\\\u2122','™').replace('\\\\u2605','★')
        price = prices[i]
        
        # check if item in ignore list
        if any(ignore_word in name for ignore_word in ignorelist):
            skipped_counter +=1
        else:
            if name not in result_dict:
                try:
                    result_dict[name] = float(price)
                except ValueError:
                    result_dict[name] = price
    
    # save the result in output file
    import json
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(result_dict, file, ensure_ascii=False, indent=2)
    
    # print items amount
    print(f"Lsk saved {len(result_dict)} items, skipped {skipped_counter} items")

# args handler
if 'csm' in sys.argv:
    csm_data_process('temp/csm_data.json')
if 'lskdata' in sys.argv:
    lsk_collect_data('temp/lsk_rawdata.json')
if 'lsk' in sys.argv:
    lsk_data_process('temp/lsk_rawdata.json', 'temp/lsk_data.json')