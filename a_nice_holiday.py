import requests
from bs4 import BeautifulSoup

import psycopg2
from dotenv import load_dotenv
import os

url = "https://www.aniceholiday.com.tw/beverages/store/6"
res = requests.get(url)
Soup = BeautifulSoup(res.text,'html.parser')

# 假設你已經有 HTML 存在於 html_content 變數中
soup = BeautifulSoup(res.text, 'html.parser')

items = soup.find_all(class_='row faic')
results = []

# 商店名稱
#這裡多一個空白
store_name = Soup.title.text
store_name = store_name[0:4]

for item in items:
    # 避免處理加料專區
    if item.name != 'li':
        continue

    name_tag = item.find('h4')
    price_tag = item.find('span')

    # 確保這是飲料項目，並且有名字和價格
    if name_tag and price_tag:
        name = name_tag.text.strip()
        price = price_tag.text.strip()
        hot_available = '是' if 'on' in price_tag.get('class', []) else '否'
        
        results.append({
            '品名': name,
            '價格': price,
            '可熱飲': hot_available,
            '大小': '大杯',
            '商家': store_name

        })

print(results)

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

# 3️⃣ 建立表格（如果還沒建立）
cur.execute("""
    CREATE TABLE menu (
    product_id SERIAL PRIMARY KEY,
    store_name TEXT NOT NULL,
    product_name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    size TEXT,
    is_hot BOOLEAN, 
    UNIQUE(store_name, product_name, size, is_hot)
    )
""")

#寫入資料庫

for item in results:
    product_name = item['品名']
    price = float(item['價格'])
    size = item['大小']
    is_hot = True if item['可熱飲'] == '是' else False
    store_name = item['商家']

    cur.execute('''
        INSERT INTO menu (store_name, product_name, price, size, is_hot)
        VALUES (%s, %s, %s, %s, %s)
    ''', (store_name, product_name, price, size, is_hot))


conn.commit()
cur.close()
conn.close()
print("完成")