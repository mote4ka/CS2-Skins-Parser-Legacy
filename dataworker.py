import json
import re
import requests

import sys
import os

from config import *

# json stuuf made by deepseek
def pre_process_json(content, remove_tags):

    if content.startswith("b'") or content.startswith('b"'):
        content = content[2:-1]

    content = re.sub(r"\\'", "'", content)

    for field in remove_tags:
        patterns = [
            f'"{field}"\\s*:\\s*[^,}}]*,?',  # простые значения
            f'"{field}"\\s*:\\s*"[^"]*",?',   # строковые значения
            f'"{field}"\\s*:\\s*\\d+,?',      # числовые значения
            f'"{field}"\\s*:\\s*null,?',      # null значения
            f'"{field}"\\s*:\\s*\\[.*?\\],?'  # массивы
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    content = re.sub(r'\"\]\}(\s*,)?', '"}\1', content)  # "]} -> "}
    content = re.sub(r'\"\}\](\s*,)?', '"}\1', content)  # "}] -> "}

    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)

    content = re.sub(r'(\"items\"\s*:\s*\[)[^]]*$', r'\1]}', content)

    p = re.compile('(?<!\\\\)\'')
    content = p.sub('\"', content)

    return content

def fix_json(content, output_file):
    try:
        objects = re.findall(r'\{[^{}]*\}', content)
        items = []
        
        for obj in objects:
            try:
                item_data = json.loads(obj)
                if 'name' in item_data and 'price' in item_data:
                    items.append({"name": item_data['name'].replace("\\u2122", "™").replace("\\u2605","★"), "price": item_data['price']})
            except:
                continue
        
        new_json = {"status": "success", "items": items}
        
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(new_json, file, ensure_ascii=False, indent=2)
        return True
        
    except Exception as e:
        print(f"JSON file broken: {e}")

def FileWrite(file, content):
    with open(file, 'w',encoding='utf-8') as file:
        file.write(content)

def FileRead(file):
    with open(file, 'r',encoding='utf-8') as file:
        content = file.read().splitlines()
    return content

def JsonDump(file, content):
    with open(file, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=2)

def JsonRead(file):
    with open(file, 'r',encoding='utf-8') as file:
        content = file.read()
    return json.loads(content)

def getwhitelist():
    return FileRead('whitelist.txt')

def GetCSMDb():
    req = requests.get("https://market.csgo.com/api/v2/full-history/all.json")
    items = req.json().get('history')
    db = {}
    for item in items:
        if any(word in item for word in getwhitelist()):
            db[item] = items.get(item)
    JsonDump("temp/csm_items_db.json", db)
    return db

def GetItemData(id):
    req = requests.get(f"https://market.csgo.com/api/v2/full-history/{id}.json", timeout=5)
    data = req.json().get('data')
    
    return data

def GetHistoryByName(name):
    db = GetCSMDb()
    req = requests.get(f"https://market.csgo.com/api/v2/full-history/{db.get(name)}.json")
    return req.json().get('data').get('history')

# 
def csm_data_preprocess(output_file):
    
    ## get whitelist
    whitelist = getwhitelist()

    # Get Price and Volume

    # request to csm api
    req = requests.get("https://market.csgo.com/api/v2/prices/RUB.json")
    items = req.json().get('items')
    # collect and save to dict ask price & volume
    skins_list = {}
    for item in items:
        name = item.get('market_hash_name')
        skins_list[name] = {'price' : item.get('price'),
                            'volume': item.get('volume')}
        
    # save dict to file
    JsonDump("temp/csm_data.json", skins_list)

# process previous data and make final dict that will be used in parser.py
def csm_data_process(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        items = json.loads(file.read()).get('items')
    
    counter = 0
    result_dict = {}
    names = []
    for item in items:
        name = item.get('name')
        price = float(item.get('price'))
        if name in names:
            if price < result_dict[name].get('price'):
                result_dict[name]['price'] = price
            if item.get('avg_price') < result_dict[name].get('avg_price'):
                result_dict[name]['avg_price'] = item.get('avg_price')
            if item.get('buy_order') > result_dict[name].get('buy_order'):
                result_dict[name]['buy_order'] = item.get('buy_order')
        else:
            counter += 1
            result_dict[name] = {"price": price, "avg_price": float(item.get('avg_price')), "buy_order": item.get('buy_order'), "volume": float(item.get('volume'))}

    with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(result_dict, file, ensure_ascii=False, indent=2)

    print(f"CSM saved {len(result_dict)} items")
# just collecting raw data from lis skins api
def lsk_get_data(output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        req = requests.get("https://lis-skins.com/market_export_json/api_csgo_full.json")
        file.write(str(req.content))
    print("lsk data collected!")

# preparing lsk data for parsing in next step
def lsk_process_data(input_file, output_file):

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read().strip()
    
    objects = re.findall(r'\{[^{}]*\}', content)
    
    unique_objects = {}
    duplicate_count = 0
    
    for obj in objects:
        name_match = re.search(r'"name"\s*:\s*"([^"]*)"', obj)
        
        if name_match:
            key = f"{name_match.group(1)}"
            
            if key not in unique_objects:
                unique_objects[key] = obj
            else:
                duplicate_count += 1
        else:
            if obj not in unique_objects:
                unique_objects[obj] = obj
            else:
                duplicate_count += 1
    
    items_start = content.find('"items":[') + 8
    items_end = content.rfind(']')
    
    if items_start > 0 and items_end > items_start:
        before_items = content[:items_start]
        after_items = content[items_end:]
        new_content = before_items + ','.join(unique_objects.values()) + after_items
    else:
        new_content = '{"status":"success","items":[' + ','.join(unique_objects.values()) + ']}'
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"Deleted {duplicate_count} repeating items")
    print(f"Saved {len(unique_objects)} unique items")




    with open(output_file, "r", encoding="utf-8") as file:
        content = file.read()
   
    content = re.sub(r'"name":"([^"]*)\"}\]\},', r'"name":"\1"},', content)

    content = re.sub(r'"name":"([^"]*)\"}\],', r'"name":"\1"},', content)
    content = re.sub(r'"name":"([^"]*)\"}\]', r'"name":"\1"}', content)

    remove_tags = [
        
        'id',
        'stickers',
        'item_paint_seed',
        'item_paint_index', 
        'item_float',
        'unlock_at',
        'created_at',
        'game_id',
        'name_tag',
        'item_class_id',
        'item_asset_id',
        'image',
        'wear',
        'slot'
    ]
    
    content = pre_process_json(content, remove_tags)

    # save
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)


    # fix json file
    fix_json(content, output_file)

    print("lsk data processed!")

# lsk final step. output is pure data that wil be used in parser.py
def lsk_data_parse(input_file, output_file):
    
    result_dict = {}

    # get blacklist
    # with open('blacklist.txt', 'r',encoding='utf-8') as file:
    #     blacklist = file.read().splitlines()
    with open('whitelist.txt', 'r',encoding='utf-8') as file:
        whitelist = file.read().splitlines()

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
        items = json.loads(file.read()).get('items')
        
        for item in items:
            try:
                if isinstance(item, dict) and 'name' in item and 'price' in item:
                    name = str(item['name'])
                    if any(word in name for word in whitelist):
                        price = item['price']
                        
                        if name not in result_dict:
                            result_dict[name] = price
                        else:
                            continue
            except:
                continue


    # save the result in output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(result_dict, file, ensure_ascii=False, indent=2)
    
    # print items amount
    print(f"Lsk saved {len(result_dict)} items")

# args handler
if '-csm' in sys.argv:
    csm_data_preprocess('temp/csm_cache.json')
    #csm_data_process('temp/csm_cache.json', 'temp/csm_data.json')
if '-lskgetdata' in sys.argv:
    lsk_get_data('temp/lsk_rawdata.json')
if '-lskprocessdata' in sys.argv:
    lsk_process_data('temp/lsk_rawdata.json','temp/lsk_processed.json')
if '-lskparse' in sys.argv:
    lsk_data_parse('temp/lsk_processed.json', 'temp/lsk_data.json')
if '-lsk' in sys.argv:
    lsk_process_data('temp/lsk_rawdata.json','temp/lsk_processed.json')
    lsk_data_parse('temp/lsk_processed.json', 'temp/lsk_data.json')
if '-full' in sys.argv:
    csm_data_preprocess('temp/csm_cache.json')
    #csm_data_process('temp/csm_cache.json', 'temp/csm_data.json')
    lsk_get_data('temp/lsk_rawdata.json')
    lsk_process_data('temp/lsk_rawdata.json','temp/lsk_processed.json')
    lsk_data_parse('temp/lsk_processed.json', 'temp/lsk_data.json')