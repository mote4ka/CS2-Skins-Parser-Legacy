import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter

import pandas as pd
import matplotlib.pyplot as plt

import os

from data import *

from config import *

if '-full' in sys.argv:
    from dataworker import *
elif '-csm' in sys.argv:
    from dataworker import *
else:
    from dataworker import GetCSMDb, GetItemData


import traceback
import time
from time import sleep


# excel preparations
wb = Workbook()
ws = wb.active
ws.title = "Data"

headers = ["Name", "Buy", "Sell", "Avg", "Profit", "%", "Avg %", "Volume", "Max", "Min", "Chart"]
column_widths = [49] + [10]*9 +  [90]

center_alignment = Alignment(horizontal='center', vertical='center')
blue_fill = PatternFill(start_color="9BC2E6", end_color="9BC2E6", fill_type="solid")
font_header = Font(name='Arial',bold=True, italic=True, size=10)
font_name = Font(name='Arial', size=10)
font_value = Font(name='Arial', italic=True, size=10)

for col_num, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_num, value=header)
    cell.font = font_header
    cell.alignment = center_alignment
    ws.column_dimensions[get_column_letter(col_num)].width = column_widths[col_num-1]

time_start = time.time()

# get data from dataworker
lsk_data = get_lsk_data()
csm_data = get_csm_data()
i=2
i_w =i

db = GetCSMDb()

for item in db:
    try:
        lsk_price = float(lsk_data.get(item)*usdrub)
        csm_price = float(csm_data.get(item).get('price'))
        profit = round(csm_price*0.95 - lsk_price*1.05,2)

        if profit <= 0:
            raise ValueError('shit')

        o_item = str(item).replace('Battle-Scarred', 'BS').replace('Well-Worn', 'WW').replace('Field-Tested', 'FT').replace('Minimal Wear', 'MW').replace('Factory New', 'FN')
        print(f"\r{i-1}/{len(db)} | {str(o_item).rjust(len(str(o_item))+(30-len(str(o_item))//2),' ').ljust(60,' ')} | {round(time.time()-time_start)//60}m {round(time.time()-time_start)%60}s ")
        item_data = GetItemData(db.get(item))

        
        avg_price = float(item_data.get('average30d').get('RUB'))

        
        profit_avg = round(avg_price*0.95 - lsk_price*1.05,2)
        # get values from data
        final_data = {
            'name': item,
            'price_lis':lsk_price,
            'price_csm':csm_price,
            'price_avg30': avg_price,
            'profit': profit,
            'profit_percent': round(profit / (lsk_price*1.05) *100,2),
            'avg_percent': round(profit_avg / (lsk_price*1.05)*100,2),
            'volume30': float(item_data.get('sales30d').get('RUB')),
            'price_max': float(item_data.get('max').get('RUB')),
            'price_min': float(item_data.get('min').get('RUB')),
            
        }
        history = item_data.get('history')

        # make hyperllink
        csm_hashname = item.replace('|', "%7C").replace("(", "%28").replace(")", "%29").replace(" ", "%20")
        lsk_hashname = item.lower().replace(' | ', "-").replace(" (", "-").replace(")", "").replace(" ", "-").replace("'", '%27').replace("™", "")

        lsk_url = f"https://lis-skins.com/market/csgo/{lsk_hashname}"
        csm_url = f"https://market.csgo.com/en/{csm_hashname}"

        for index,value in enumerate(final_data,1):
            cell = ws.cell(i, index, final_data.get(value))
            cell.alignment = center_alignment
            if index != 1:
                cell.font = font_value
            else:
                cell.font = font_name
            if index == 2:
                cell.hyperlink = lsk_url
                cell.fill = blue_fill
            elif index == 3:
                cell.hyperlink = csm_url
                cell.fill = blue_fill


        wb.save('output.xlsx')
        i+=1
        i_w +=1

    except Exception as e:
        print(f"\r{i_w-1}/{len(db)} | ## {str(e).rjust(len(str(e))+(27-len(str(e))//2),' ').ljust(54,' ')} ## | {round(time.time()-time_start)//60}m {round(time.time()-time_start)%60}s ")
        i_w +=1
        sleep(0.1)
        continue

wb.save('output.xlsx')