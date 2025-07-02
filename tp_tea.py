import requests
from bs4 import BeautifulSoup




# 目標網址（使用繁體菜單）
url = 'https://tw.tp-tea.com/menu/'

# 模擬瀏覽器 header，避免被封鎖
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
}

resp = requests.get(url, headers=headers)
resp.encoding = resp.apparent_encoding  # 避免亂碼
soup = BeautifulSoup(resp.text, 'html.parser')

store_name = soup.title.text
store_name = store_name[5:8]
# 獲取每一組品項區塊（每個 table）
tables = soup.select('li div table')

results = []

for table in tables:
    rows = table.select('tbody tr')
    for row in rows:    
        cols = [td.get_text(strip=True) for td in row.select('td')]
        ## 判斷是否為熱飲
        hot = row.select('td i')
        hot_available = '是' if hot else '否'

        if len(cols) >= 3:
            name = cols[1]
            price = cols[2]
            
            # 過濾掉空列或標題列
            if name and price.isdigit():
                results.append({
                    '品名': name, 
                    '價格': price,
                    '可熱飲': hot_available,
                    '大小': '大杯',
                    '商家': store_name
                    })
                

# print(results)

import psycopg2
from dotenv import load_dotenv
import os

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

# # 3️⃣ 建立表格（如果還沒建立）
# cur.execute("""
#     CREATE TABLE menu (
#     product_id SERIAL PRIMARY KEY,
#     store_name TEXT NOT NULL,
#     product_name TEXT NOT NULL,
#     price NUMERIC(10, 2) NOT NULL,
#     size TEXT,
#     is_hot BOOLEAN, 
#     UNIQUE(store_name, product_name, size, is_hot)
#     )
# """)

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