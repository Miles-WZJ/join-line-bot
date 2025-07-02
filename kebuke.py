import requests
from bs4 import BeautifulSoup
import re

import psycopg2
from dotenv import load_dotenv
import os

def fetch_kebuke_menu(url="https://kebuke.com/menu/"):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    menu = []
    # 每項飲料資訊是這個區塊
    for item in soup.select("div.menu-item__head"):
        name = item.select_one("p.menu-item__name")
        price = item.select_one("p.menu-item__price")
        
        store_name = soup.title.text
        store_name = store_name[5:12]
        if not name or not price:
            continue

        # 品名（例如：Black Tea with Lemon Juice）
        drink_name = name.get_text(strip=True)

        # # 價格形式是 "M：45 / L：55"
        price_text = price.get_text(strip=True)
        match = re.search(r'大：(\d+)', price_text)
        price = int(match.group(1))

                     

        # 接下來判斷是否支援熱飲：若下方有 "Hot 方案" 出現 hot 字眼
        hot_icon = name.select_one('icon[name="hot"]')
        hot_available = hot_icon is not None


        menu.append({
            '品名': drink_name, 
            '價格': price,
            '可熱飲': hot_available,
            '大小': '大杯',
            '商家': store_name
        })

    return menu


def write_to_db(menu):
    #開始寫入資料庫
    load_dotenv()

    # 1️⃣ 資料庫連線參數
    conn = psycopg2.connect(
    dbname = os.getenv('database_name'),
    user = os.getenv('user'),
    password = os.getenv('password'),
    host = os.getenv('host'),
    port = os.getenv('port')
    )

    # 2️⃣ 建立 cursor（指標）
    cur = conn.cursor()

    #寫入資料庫

    for item in results:
        product_name = item['品名']
        price = float(item['價格'])
        size = item['大小']
        # is_hot = True if item['可熱飲'] == '是' else False
        is_hot = item['可熱飲']
        store_name = item['商家']

        cur.execute('''
            INSERT INTO menu (store_name, product_name, price, size, is_hot)
            VALUES (%s, %s, %s, %s, %s)
        ''', (store_name, product_name, price, size, is_hot))


    conn.commit()
    cur.close()
    conn.close()
    print("完成")



if __name__ == "__main__":
    results = fetch_kebuke_menu()
    write_to_db(results)
    # for d in results:
    #     print(d)
