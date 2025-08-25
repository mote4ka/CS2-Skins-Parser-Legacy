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
ws.write(0,2, "Sell Price",style_header)
ws.col(2).width = 256*10
ws.write(0,3, "Profit",style_header)
ws.col(3).width = 256*10
ws.write(0,4, "%",style_header)
ws.col(4).width = 256*10
ws.write(0,5, "Volume",style_header)
ws.col(5).width = 256*8

lsk_data = get_lsk_data()
csm_data = get_csm_data()

i=0
for item in csm_data:
    

    if lsk_data.get(item) != None:
        lsk_price = float(lsk_data.get(item))*usdrub

        csm_price = csm_data.get(item).get('price')
        csm_volume = csm_data.get(item).get('volume')

        profit = float(csm_price)*0.95 - float(lsk_price)*1.05

        csm_hashname = item.replace('|', "%7C").replace("(", "%28").replace(")", "%29").replace(" ", "%20")
        lsk_hashname = item.lower().replace(' | ', "-").replace(" (", "-").replace(")", "").replace(" ", "-").replace("'", '%27').replace("™", "")

        lsk_url = f"https://lis-skins.com/market/csgo/{lsk_hashname}"
        csm_url = f"https://market.csgo.com/en/{csm_hashname}"

        ws.write(i+1,0, item, style_name)
        ws.write(i+1,1, xlwt.Formula(f'HYPERLINK("{lsk_url}", "{round(float(lsk_price),1)}")'),style_bg_link)
        ws.write(i+1,2, xlwt.Formula(f'HYPERLINK("{csm_url}", "{round(float(csm_price),1)}")'),style_bg_link)
        ws.write(i+1,3, round(profit,1),style_value)
        ws.write(i+1,4, round(profit/float(lsk_price)*1.05*100,2),style_value)
        ws.write(i+1,5, float(csm_volume),style_value)

        i+=1


wb.save('output.xls')


wb.save('output.xls')