import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.drawing.image import Image
from openpyxl import load_workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter


import os

from data import *

from config import *

if '-full' in sys.argv:
    from dataworker import *
elif '-csm' in sys.argv:
    from dataworker import *
else:
    from dataworker import GetCSMDb, GetItemData

from rsi import *

import traceback
import time
from time import sleep
import io

from datetime import date

# excel preparations
wb = Workbook()
ws = wb.active
ws.title = "Data"


headers = ["Name", "Buy", "Sell", "Avg", "Deviation", "%", "Avg %", "RSI SM", "Volume", "Profit", "Max", "Min"]
column_widths = [49] + [10]*12

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

skip_file = open('skipped.txt', 'w',encoding='utf-8')

for item in db:
    try:
        # check if item doesn match
        if lsk_data.get(item)  is None:
            skip_file.write(f'{i_w} | {item} lsk miss\n')
            raise ValueError('lsk price none')
        lsk_price = float(lsk_data.get(item)*usdrub)
        if not(lsk_price > low_filter and lsk_price < high_filter):
            skip_file.write(f'{i_w} | {item} filter\n')
            raise ValueError('filter skip')
        csm_price = float(csm_data.get(item).get('price'))
        profit = round(csm_price*0.95 - lsk_price*1.02,2)

        if profit <= 0:
            skip_file.write(f'{i_w} | {item} unprofitable ({lsk_price} ! {csm_price}\n')
            raise ValueError('unprofitable')

        o_item = str(item).replace('Battle-Scarred', 'BS').replace('Well-Worn', 'WW').replace('Field-Tested', 'FT').replace('Minimal Wear', 'MW').replace('Factory New', 'FN')
        print(f"\r{i_w-1}/{len(db)} | {str(o_item).rjust(len(str(o_item))+(30-len(str(o_item))//2),' ').ljust(60,' ')} | {round(time.time()-time_start)//60}m {round(time.time()-time_start)%60}s ")
        item_data = GetItemData(db.get(item))

        avg_price = float(item_data.get('average30d').get('RUB'))
        price_deviation = round(csm_price / avg_price * 100 - 100,2)
        # history data
        history_data = item_data.get('history')
        
        profit_avg = round(avg_price*0.95 - lsk_price*1.05,2)
        # get values from data
        final_data = {
            'name': item,
            'price_lis':lsk_price,
            'price_csm':csm_price,
            'price_avg30': avg_price,
            'price_deviation': price_deviation,
            'profit_percent': round(profit / (lsk_price*1.05) *100,2),
            'avg_percent': round(profit_avg / (lsk_price*1.05)*100,2),
            'rsi-sm':get_last_rsi_smoothed(history_data),
            'volume30': float(item_data.get('sales30d').get('RUB')),
            'profit': profit,
            'price_max': float(item_data.get('max').get('RUB')),
            'price_min': float(item_data.get('min').get('RUB')),
            #'rsi':get_rsi(history_data),
            
        }


        # make hyperllink
        csm_hashname = item.replace('|', "%7C").replace("(", "%28").replace(")", "%29").replace(" ", "%20")
        lsk_hashname = item.lower().replace(' | ', "-").replace(" (", "-").replace(")", "").replace(" ", "-").replace("'", '%27').replace("™", "")

        lsk_url = f"https://lis-skins.com/market/csgo/{lsk_hashname}"
        csm_url = f"https://market.csgo.com/en/{csm_hashname}"

        # writing values to cell
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


        # cell size
        for row in range(1, i + 2):
            ws.row_dimensions[row].height = 25
        wb.save(f'output {str(date.today())}.xlsx')

        i+=1
        i_w +=1  

    except Exception as e:
        #skip_file.write(f'{i_w} | {item} uknwn\n')
        print(f"\r{i_w-1}/{len(db)} | ## {str(e)[:45].rjust(len(str(e))+(27-len(str(e))//2),' ').ljust(54,' ')} ## | {round(time.time()-time_start)//60}m {round(time.time()-time_start)%60}s ")
        i_w +=1
        continue

wb.save(f'output {str(date.today())}.xlsx')