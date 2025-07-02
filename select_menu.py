import psycopg2
from dotenv import load_dotenv
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

load_dotenv()

# 建立資料庫連線的函式
def connect_db():
    return psycopg2.connect(
        host = os.getenv('host'),       # 主機位置
        dbname = os.getenv('database_name'), # 資料庫名稱
        user = os.getenv('user'),    # 使用者名稱
        password = os.getenv('password') # 使用者密碼
    )

# 查詢特定店家的商品
def get_menu_by_store(store_name):
    conn = connect_db()
    cur = conn.cursor()

    query = """
        SELECT product_id, product_name, price, size, is_hot
        FROM menu
        WHERE store_name = %s;
    """
    cur.execute(query, (store_name,))
    rows = cur.fetchall()

    get_menu_list = ""

    for m in rows:
        get_menu_list += '品項編號:{} 品項名稱:{} 價錢:{} 大小杯{} 熱飲{} \n ----------------------------------- \n'.format(m[0],m[1],int(m[2]),m[3],m[4])

    # 關閉連線
    cur.close()
    conn.close()
    return get_menu_list


def get_main_menu():
    return FlexSendMessage(
        alt_text="菜單",
        contents={
          "type": "bubble",
          "hero": {
            "type": "image",
            "url": "https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
              "type": "uri",
              "uri": "https://line.me/"
            }
          },
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "🍹 菜單",
                "weight": "bold",
                "size": "xl"
              },
              {
                "type": "box",
                "layout": "baseline",
                "margin": "md",
                "contents": [
                  {
                    "type": "icon",
                    "size": "sm",
                    "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "size": "sm",
                    "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "size": "sm",
                    "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "size": "sm",
                    "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "size": "sm",
                    "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                  },
                  {
                    "type": "text",
                    "text": "5.0",
                    "size": "sm",
                    "color": "#999999",
                    "margin": "md",
                    "flex": 0
                  }
                ]
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "一沐日",
                  "data": "action=a_nice_holiday_menu"
                }
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "茶湯會",
                  "data": "action=tp_tea"
                }
              },
              {
                "type": "button",
                "action": {
                  "type": "postback",
                  "label": "可不可熟成紅茶",
                  "data": "action=kebuke"
                }
              }
            ]
          }
        }
        
  )
