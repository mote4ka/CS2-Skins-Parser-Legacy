from bs4 import BeautifulSoup
import json
import requests
import cloudscraper
import time
import io
import random
import sys

import xlrd
import xlwt
from xlutils.copy import copy

from data import *

from config import *

if '-full' in sys.argv:
    from dataworker import *

rb = xlrd.open_workbook('output.xls')

wb = copy(rb)

ws = wb.get_sheet(0)

ws.write(0,0, "Name")
ws.write(0,1, "Buy Price")
ws.write(0,2, "Sell Price")
ws.write(0,3, "Profit")
ws.write(0,4, "%")
ws.write(0,5, "Volume")

xlwt.add_palette_colour("custom_link", 0x21) 
wb.set_colour_RGB(0x21, 155, 194, 230) 
style_bg_link = xlwt.easyxf('pattern: pattern solid, fore_colour custom_link')

lsk_data = get_lsk_data()
csm_data = get_csm_data()

i=0
for item in csm_data:
    

    if lsk_data.get(item) != None:
        lsk_price = float(lsk_data.get(item))*usdrub

        csm_price = csm_data.get(item).get('price')
        csm_volume = csm_data.get(item).get('volume')

        profit = float(csm_price)*0.95 - float(lsk_price)*1.05

        #print(item, lsk_price, csm_price, profit)

        csm_hashname = item.replace('|', "%7C").replace("(", "%28").replace(")", "%29").replace(" ", "%20")
        lsk_hashname = item.lower().replace(' | ', "-").replace(" (", "-").replace(")", "").replace(" ", "-").replace("'", '%27')

        lsk_url = f"https://lis-skins.com/market/csgo/{lsk_hashname}"
        csm_url = f"https://market.csgo.com/en/{csm_hashname}"

        ws.write(i+1,0, item)
        ws.write(i+1,1, xlwt.Formula(f'HYPERLINK("{lsk_url}", "{float(lsk_price)}")'), style_bg_link)
        ws.write(i+1,2, xlwt.Formula(f'HYPERLINK("{csm_url}", "{float(csm_price)}")'),style_bg_link)
        ws.write(i+1,3, profit)
        ws.write(i+1,4, profit/float(lsk_price)*1.05*100)
        ws.write(i+1,5, float(csm_volume))

        i+=1


wb.save('output.xls')


wb.save('output.xls')