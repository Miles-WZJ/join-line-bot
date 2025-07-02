from datetime import datetime
from select_menu import connect_db

'''
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(20) REFERENCES orders(order_id),
    customer_id TEXT NOT NULL,
    product_id INTEGER REFERENCES menu(product_id),
    sweetness TEXT,
    is_hot TEXT,
    size TEXT,
    quantity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

'''
# def insert_order_items(items,order_id):
#     conn = connect_db()
#     cur = conn.cursor()
    
#     try:

#         for item in items:
#             cur.execute("""
#                 INSERT INTO order_items (
#                     order_id, customer_id, product_id, sweetness, is_hot,
#                     size, quantity, unit_price, created_at
#                 )
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
#             """, (
#                 order_id,
#                 item["customer_id"],
#                 item["product_id"],
#                 item["sweetness"],
#                 item["is_hot"],
#                 item["size"],
#                 item["quantity"],
#                 item["unit_price"]
#             ))

#         conn.commit()
#         info = "訂購成功 ✅"

#     except Exception as e:
#         conn.rollback()
#         print("發生錯誤 ❌:", e)

#     finally:
#         cur.close()
#         conn.close()
#     return info

def update_order_status(order_id):
    conn = connect_db()
    cur = conn.cursor()

    # 先檢查是否存在此訂單
    cur.execute("SELECT 1 FROM orders WHERE order_id = %s", (order_id,))
    exists = cur.fetchone()

    if not exists:
        cur.close()
        conn.close()
        return f"❌ 沒有此 訂單號碼 {order_id}"

    # 如果有，就更新 status = TRUE
    cur.execute("UPDATE orders SET status = TRUE WHERE order_id = %s", (order_id,))
    conn.commit()

    cur.close()
    conn.close()

    return f"✅ 訂單 {order_id} 已結單成功！"
