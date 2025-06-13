from bs4 import BeautifulSoup
import json
import requests
from colors import bcolors

class steamInfo:
    weapon = ""
    name = ""
    quality = ""

    def __init__(self,weapon, name, quality):
        self.weapon = weapon
        self.name = name
        self.quality = quality

        weaponTag = weapon
        nameTag= name
        qualityTag= quality
        if(weapon.find(" ") != -1):
            weaponTag = weapon.replace(' ','%20')
        if(name.find(" ") != -1):
            nameTag = name.replace(' ','%20')
        if(quality.find(" ") != -1):
            qualityTag = quality.replace(' ','%20')

        url = 'https://steamcommunity.com/market/listings/730/' + weaponTag + f'%20%7C%20' + nameTag + f'%20%28' + qualityTag + '%29'
        "AK-47%20%7C%20Vulcan%20%28Field-Tested%29"
        "%E2%98%85%20Driver%20Gloves%20%7C%20King%20Snake%20%28Minimal%20Wear%29"

        #print(url)
        req = requests.get(url).text
        soup = BeautifulSoup(req, 'lxml')
        #name_div = soup.find('div', class_='market_listing_item_name_block')
        #name = steam_best_name_div.find('span').text
        price_div = soup.find('div', class_='market_listing_right_cell market_listing_their_price')
        self.price = price_div.find('span')
        self.price = self.price.find('span').text

        self.price = self.price[self.price.find('$'):]

weapon = "M4A1-S"
name = "Stratosphere"
quality = "Minimal Wear"


kerambit = steamInfo(weapon, name, quality)
print('\033[95m' ,kerambit.weapon,"|", kerambit.name, '\033[97m', "(", kerambit.quality, ")", bcolors.OKGREEN, kerambit.price, bcolors.ENDC)
# except Exception:
#     print("smth gone wrong")



