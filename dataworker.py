import io
import json
import ijson
import re
import requests

import sys

from config import *



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
            if float(item.get('price')) >= low_filter and float(item.get('price')) <= high_filter:
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

def lsk_get_data(output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        req = requests.get("https://lis-skins.com/market_export_json/api_csgo_full.json")
        file.write(str(req.content))
    print("lsk data collected!")

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

    if content.startswith("b'") or content.startswith('b"'):
        content = content[2:-1]
    
    content = re.sub(r'"name":"([^"]*)\"}\]\},', r'"name":"\1"},', content)

    content = re.sub(r'"name":"([^"]*)\"}\],', r'"name":"\1"},', content)
    content = re.sub(r'"name":"([^"]*)\"}\]', r'"name":"\1"}', content)

    content = re.sub(r"\\'", "'", content)
    fields_to_remove = [
        
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
    
    for field in fields_to_remove:
        patterns = [
            f'"{field}"\\s*:\\s*[^,}}]*,?',  # простые значения
            f'"{field}"\\s*:\\s*"[^"]*",?',   # строковые значения
            f'"{field}"\\s*:\\s*\\d+,?',      # числовые значения
            f'"{field}"\\s*:\\s*null,?',      # null значения
            f'"{field}"\\s*:\\s*\\[.*?\\],?'  # массивы
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # cleaning json file
    content = re.sub(r'\"\]\}(\s*,)?', '"}\1', content)  # "]} -> "}
    content = re.sub(r'\"\}\](\s*,)?', '"}\1', content)  # "}] -> "}

    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)

    content = re.sub(r'(\"items\"\s*:\s*\[)[^]]*$', r'\1]}', content)

    p = re.compile('(?<!\\\\)\'')
    content = p.sub('\"', content)

    # save
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)


    # fix json file
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

    print("lsk data processed!")



def lsk_data_parse(input_file, output_file):
    
    result_dict = {}

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
        items = json.loads(file.read()).get('items')
        
        for item in items:
            try:
                if isinstance(item, dict) and 'name' in item and 'price' in item:
                    name = str(item['name'])
                    price = item['price']
                    
                    if name not in result_dict:
                        result_dict[name] = price
                    else:
                        print("skip")
            except:
                continue


    # save the result in output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(result_dict, file, ensure_ascii=False, indent=2)
    
    # print items amount
    print(f"Lsk saved {len(result_dict)} items")

# args handler
if 'csm' in sys.argv:
    csm_data_process('temp/csm_data.json')
if 'lskgetdata' in sys.argv:
    lsk_get_data('temp/lsk_rawdata.json')
if 'lskprocessdata' in sys.argv:
    lsk_process_data('temp/lsk_rawdata.json','temp/lsk_processed.json')
if 'lskparse' in sys.argv:
    lsk_data_parse('temp/lsk_processed.json', 'temp/lsk_data.json')
if 'lsk' in sys.argv:
    lsk_process_data('temp/lsk_rawdata.json','temp/lsk_processed.json')
    lsk_data_parse('temp/lsk_processed.json', 'temp/lsk_data.json')
if '-full' in sys.argv:
    csm_data_process('temp/csm_data.json')
    lsk_get_data('temp/lsk_rawdata.json')
    lsk_process_data('temp/lsk_rawdata.json','temp/lsk_processed.json')
    lsk_data_parse('temp/lsk_processed.json', 'temp/lsk_data.json')