from datetime import datetime
from select_menu import connect_db

"""
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(20) PRIMARY KEY,
    created_by TEXT,
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status BOOLEAN DEFAULT FALSE
);
"""

def generate_order_id(conn):
    today_str = datetime.now().strftime("%Y%m%d")  # 例如：20250618
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM orders
            WHERE to_char(created_at, 'YYYYMMDD') = %s
        """, (today_str,))
        count = cur.fetchone()[0] + 1  # 當天訂單數 +1
    return today_str + str(count).zfill(3)  # 補零成三位數，例如 001、002

def insert_order(created_by, user_id, status=False):
    conn = connect_db()
    cur = conn.cursor()

    # 產生自訂 order_id
    order_id = generate_order_id(conn)

    insert_sql = """
    INSERT INTO orders (order_id, created_by, user_id, status)
    VALUES (%s, %s, %s, %s)
    RETURNING created_at;
    """
    cur.execute(insert_sql, (order_id, created_by, user_id, status))

    created_at = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ 訂單建立成功：Order ID = {order_id}")
    return order_id, created_at
