from select_menu import connect_db
"""
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(20),
    customer_id TEXT NOT NULL,
    payer_id TEXT,
    product_id INTEGER REFERENCES menu(product_id),
    sweetness TEXT,             -- 半糖、微糖
    temperature TEXT,           -- 去冰、熱、常溫
    size TEXT,                  -- 中杯、大杯
    quantity INTEGER NOT NULL,
    unit_price NUMERIC NOT NULL,   -- 保留當時價格快照
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# ✅ 查 menu 表中的單價
def get_unit_price(product_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT price FROM menu WHERE product_id = %s", (product_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

# ✅ 寫入 order_items 表
def insert_order_item(data):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO order_items (
            order_id, customer_id, payer_id, product_id,
            sweetness, temperature, size, quantity, unit_price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['order_id'],
        data['customer_id'],
        data['payer_id'],
        data['product_id'],
        data['sweetness'],
        data['temperature'],
        data['size'],
        data['quantity'],
        data['unit_price']
    ))
    conn.commit()
    cur.close()
    conn.close()

# ✅ 主邏輯函式：處理使用者輸入文字
def handle_order_input(msg, user_id):
    lines = msg.strip().splitlines()

    if len(lines) != 7 or lines[0] != "訂購":
        return "❌ 輸入格式錯誤，請依照以下格式輸入：\n訂購\n訂單編號\n產品編號\n甜度\n冰熱\n大小\n數量"

    try:
        order_id = lines[1].strip()
        product_id = int(lines[2].strip())
        sweetness = lines[3].strip()
        temperature = lines[4].strip()
        size = lines[5].strip()
        quantity = int(lines[6].strip())

        unit_price = get_unit_price(product_id)
        if unit_price is None:
            return f"❌ 查無商品編號 {product_id} 的價格"

        order_item_data = {
            "order_id": order_id,
            "customer_id": user_id,
            "payer_id": user_id,
            "product_id": product_id,
            "sweetness": sweetness,
            "temperature": temperature,
            "size": size,
            "quantity": quantity,
            "unit_price": unit_price
        }

        insert_order_item(order_item_data)
        return f"✅ 已加入訂單：{order_id}\n商品ID：{product_id} 數量：{quantity}"

    except Exception as e:
        return "請使用「訂購」開頭，依格式輸入訂單資訊。"
