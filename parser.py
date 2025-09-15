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

xlwt.add_palette_colour("custom_link", 0x21) 
wb.set_colour_RGB(0x21, 155, 194, 230) 
style_bg_link = xlwt.easyxf('pattern: pattern solid, fore_colour custom_link; align: horiz center, vert center, wrap on; font: italic on')
style_name= xlwt.easyxf('align: horiz center, vert centre')
style_value = xlwt.easyxf('align: horiz center, vert centre; font: italic on')
style_header = xlwt.easyxf('align: horiz center, vert centre; font: bold on, italic on')


ws.write(0,0, "Name",style_header)
ws.col(0).width = 256*50
ws.write(0,1, "Buy Price",style_header)
ws.col(1).width = 256*10
ws.write(0,2, "Ask Price",style_header)
ws.col(2).width = 256*10
ws.write(0,3, "Avg Price",style_header)
ws.col(3).width = 256*10
ws.write(0,4, "Buy Order",style_header)
ws.col(4).width = 256*10
ws.write(0,5, "Profit",style_header)
ws.col(5).width = 256*10
ws.write(0,6, "%",style_header)
ws.col(6).width = 256*10
ws.write(0,7, "Avg Profit",style_header)
ws.col(7).width = 256*10
ws.write(0,8, "%",style_header)
ws.col(8).width = 256*10
ws.write(0,9, "Volume",style_header)
ws.col(9).width = 256*8

lsk_data = get_lsk_data()
csm_data = get_csm_data()
print(len(csm_data), len(lsk_data))
i=0
for item in csm_data:
    

    if lsk_data.get(item) != None:
        lsk_price = float(lsk_data.get(item))*usdrub

        ask_price = float(csm_data.get(item).get('price'))
        avg_price = float(csm_data.get(item).get('avg_price'))
        buy_order_price = float(csm_data.get(item).get('buy_order'))
        csm_volume = float(csm_data.get(item).get('volume'))

        profit = float(ask_price)*0.95 - float(lsk_price)*1.05
        avg_profit = float(avg_price)*0.95 - float(lsk_price)*1.05

        csm_hashname = item.replace('|', "%7C").replace("(", "%28").replace(")", "%29").replace(" ", "%20")
        lsk_hashname = item.lower().replace(' | ', "-").replace(" (", "-").replace(")", "").replace(" ", "-").replace("'", '%27').replace("™", "")

        lsk_url = f"https://lis-skins.com/market/csgo/{lsk_hashname}"
        csm_url = f"https://market.csgo.com/en/{csm_hashname}"

        ws.write(i+1,0, item, style_name)
        ws.write(i+1,1, xlwt.Formula(f'HYPERLINK("{lsk_url}", {round(lsk_price,1)})'),style_bg_link)
        ws.write(i+1,2, xlwt.Formula(f'HYPERLINK("{csm_url}", {round(ask_price,1)})'),style_bg_link)
        ws.write(i+1,3, avg_price, style_value)
        ws.write(i+1,4, buy_order_price, style_value)
        ws.write(i+1,5, round(profit,1),style_value)
        ws.write(i+1,6, round(profit/lsk_price*1.05*100,2),style_value)
        ws.write(i+1,7, round(avg_profit,1),style_value)
        ws.write(i+1,8, round(avg_profit/lsk_price*1.05*100,2),style_value)
        ws.write(i+1,9, csm_volume,style_value)

        i+=1


wb.save('output.xls')