from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from select_menu import *
from user_join import *
from order import *
from create_order import *
from join_drink import *
from order_item import *
# from main_meun import *
from query_info import *
import re
from urllib.parse import parse_qs
from dotenv import load_dotenv
import os

app = Flask(__name__)

# # Load environment variables
load_dotenv()
channel_access_token = os.getenv('channel_access_token')
channel_secret = os.getenv('channel_secret')


# # Initialize LINE Bot API
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)



def send_message(reply_token: str, text: str):
    line_bot_api.reply_message(
        reply_token,
        [
        TextSendMessage(text=text)
        ]
    )

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="大家好，我是點餐機器人～請輸入『菜單』開始點餐！")
            ]
        )
    )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    parsed_data = parse_qs(data)  # {'action': ['join'], 'order_id': ['abc123']}

    action = parsed_data.get('action', [None])[0]
    order_id = parsed_data.get('order_id', [None])[0]

    if data == 'action=tp_tea':
      send_message(event.reply_token,get_menu_by_store('茶湯會'))
    elif data == 'action=a_nice_holiday_menu':
      send_message(event.reply_token,get_menu_by_store('一沐日 '))
    elif data == 'action=kebuke':
      send_message(event.reply_token,get_menu_by_store('可不可熟成紅茶'))
    elif action == "join" and order_id:
      # 按下訂單參加時，回傳訂單編號！
      send_message(event.reply_token,f"你參加的揪團單號為: {order_id}")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    # 依據來源取得使用者名稱
    try:
        if isinstance(event.source, SourceGroup):
            group_id = event.source.group_id
            profile = line_bot_api.get_group_member_profile(group_id, user_id)
        elif isinstance(event.source, SourceRoom):
            room_id = event.source.room_id
            profile = line_bot_api.get_room_member_profile(room_id, user_id)
        else:
            profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception as e:
        print(f"取得名稱失敗: {e}")
        display_name = "unknown"
    if 'jo!n' in msg:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=upsert_user(user_id, display_name))
        )
    elif '菜單' in msg:
      line_bot_api.reply_message(
          event.reply_token, 
          get_main_menu()
      )    
    elif '訂飲料' in msg:
      order_id,created_at = insert_order(display_name,user_id,status=False)
      line_bot_api.reply_message(
          event.reply_token, 
          join_drink_message(order_id,display_name)
      )
    # 使用者 訂購
    elif '訂購' in msg:
      reply = handle_order_input(msg, user_id)
      send_message(event.reply_token,reply)

    # 結單
    elif '結單' in msg:
      try:
          order_id = msg.replace("結單", "").strip()
          reply = update_order_status(order_id)
          send_message(event.reply_token,reply)
      except Exception as e:
          reply = f"❌ 結單 + 訂單編號"
          send_message(event.reply_token,reply)

    # 查詢訂單
    elif msg.startswith("查詢訂單"):
      order_id = msg.replace("查詢訂單", "").strip()
      reply = query_order_detail(order_id)
      send_message(event.reply_token,reply)

    # 查詢我的飲料
    elif msg.strip() == "我的飲料":
      user_id = event.source.user_id
      reply = query_my_drinks(user_id)
      send_message(event.reply_token,reply)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

