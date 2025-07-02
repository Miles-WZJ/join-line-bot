# 參加飲料訂單
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

def join_drink_message(order_id,created_at):
    return FlexSendMessage(
        alt_text="是否參加訂飲料",
        contents={
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "是否參加訂飲料",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "訂單ID",
                            "color": "#aaaaaa",
                            "size": "xs",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": order_id,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "發起人",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5,
                            "text": created_at
                        }
                        ]
                    }
                    ]
                },
                {
                    "type": "button",
                    "action": {
                    "type": "postback",
                    "label": "參加",
                    "data": f"action=join&order_id={order_id}"
                    },
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                    "type": "postback",
                    "label": "不參加",
                    "data": "action=not-join"
                    },
                    "height": "sm"
                }
                ]
            }
        }
        
    )