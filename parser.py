from bs4 import BeautifulSoup
import json
import requests
import cloudscraper
import time
import io
import random

import xlrd
import xlwt
from xlutils.copy import copy

from data_min import *

from config import *

def find_price(i , item):
    print(i, end = ' ')
    #geneation hashnames
    csm_hashname = item.replace('|', "%7C").replace("(", "%28").replace(")", "%29").replace(" ", "%20")
    lsk_hashname = item.lower().replace(' | ', "-").replace(" (", "-").replace(")", "").replace(" ", "-").replace("'", '%27')
    ws.write(i+1, 0, item)

    #request
    csm_url = "https://market.csgo.com/ru/" + csm_hashname
    lsk_url = "https://lis-skins.com/market/csgo/" + lsk_hashname

    #lsk scrapping
    scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
    req = scraper.get(lsk_url)
    print(req.status_code)

    attempts = 1
    while req.status_code != 200 and attempts <= 5:
        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
        req = scraper.get(lsk_url)
        print("Attempt ", attempts)
        attempts += 1
        time.sleep(1)
    if req.status_code == 200:
        print(item,end=' ')
        soup = BeautifulSoup(req.content, 'html.parser')
        price = soup.find('div', class_='min-price-value').get_text(separator='|',strip=True)
        lsk_price = price[:price.find('|')].replace(' ', '')
        ws.write(i+1, 1, float(lsk_price))
        print(lsk_price,end=' ')

        #csm scrapping
        csm_price = data.get(item).get('price')
        csm_volume = data.get(item).get('volume')
        print(csm_price, csm_volume)
        profit = float(csm_price)*0.95 - float(lsk_price)*1.05
        ws.write(i+1,2, csm_price)
        ws.write(i+1,3, profit)
        ws.write(i+1,4, profit/float(lsk_price)*1.05*100)
        ws.write(i+1,5, csm_volume)

    elif req.status_code == 429:
        print('Too much request, changing proxy..')
        #proxy = getproxy()
        raise Exception('429 Too much request')
    else:
        print(req.status_code)
        print('Skip ' + item)
    wb.save('output.xls')
    time.sleep(0.2)


rb = xlrd.open_workbook('output.xls')

wb = copy(rb)

ws = wb.get_sheet(0)

ws.write(0,0, "Name")
ws.write(0,1, "Buy Price")
ws.write(0,2, "Sell Price")
ws.write(0,3, "Profit")
ws.write(0,4, "%")
ws.write(0,5, "Volume")

wb.save('output.xls')

indexf = open('index.txt', 'w')

#rotator = pr(proxy_list=PROXIES, change_every = 250)

for i, item in enumerate(data):
    try:
        #print(i, item)
        if 'AWP' in item:
            find_price(i, item)
        else:
            wb.save('output.xls')
            exit()
    except KeyboardInterrupt as e:
        print("Closing...")
        indexf.write(str(i))
        wb.save('output.xls')
        exit()

    except BaseException as e:
        print(e)
        print("Restarting...")
        
        #find_price(i, data[i])

        indexf.write(str(i))
        wb.save('output.xls')

wb.save('output.xls')
indexf.close()