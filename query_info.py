from select_menu import connect_db

def query_order_detail(order_id):
    conn = connect_db()
    cur = conn.cursor()

    # Step 1：確認該訂單已結單
    cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
    result = cur.fetchone()

    if not result:
        cur.close()
        conn.close()
        return f"❌ 查無訂單編號 {order_id}"
    elif result[0] is not True:
        cur.close()
        conn.close()
        return f"❌ 訂單 {order_id} 尚未結單，無法查詢明細。"

    # Step 2：查詢訂單細項與品名、使用者名稱
    query = """
    SELECT
        oi.product_id,
        m.product_name,
        oi.sweetness,
        oi.temperature,
        oi.size,
        oi.unit_price,
        u.display_name
    FROM order_items oi
    JOIN menu m ON oi.product_id = m.product_id
    LEFT JOIN users u ON oi.customer_id = u.user_id
    WHERE oi.order_id = %s
    ORDER BY oi.item_id;
    """
    cur.execute(query, (order_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return f"⚠️ 訂單 {order_id} 無任何訂購品項。"

    # Step 3：整理格式
    reply = [f"📦 訂單號碼 {order_id}"]
    for i, row in enumerate(rows, start=1):
        pid, pname, sweet, temp, size, price, name = row
        display_name = name or "未知使用者"
        reply.append(f"{i}. 品項編號:{pid}，品項名稱:{pname}，甜度：{sweet}，溫度：{temp}，大小：{size}，價錢:{price}，訂購者:{display_name}")

    return "\n".join(reply)


def query_my_drinks(user_id):
    conn = connect_db()
    cur = conn.cursor()

    # 取得此 user_id 所參與的、已結單的訂單細項
    query = """
    SELECT
        oi.order_id,
        oi.product_id,
        m.product_name,
        oi.sweetness,
        oi.temperature,
        oi.size,
        oi.unit_price,
        u.display_name
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN menu m ON oi.product_id = m.product_id
    LEFT JOIN users u ON oi.customer_id = u.user_id
    WHERE o.status = TRUE AND oi.customer_id = %s
    ORDER BY oi.order_id, oi.item_id;
    """
    cur.execute(query, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return "❌ 查無您已結單的飲料訂單記錄。"

    # 整理結果：依 order_id 分群
    from collections import defaultdict
    grouped = defaultdict(list)

    for row in rows:
        order_id, pid, pname, sweet, temp, size, price, name = row
        display_name = name or "未知使用者"
        grouped[order_id].append(
            f"品項編號:{pid}，品項名稱:{pname}，甜度：{sweet}，溫度：{temp}，大小：{size}，價錢:{price}，訂購者:{display_name}"
        )

    # 輸出
    output = []
    for idx, (oid, items) in enumerate(grouped.items(), start=1):
        output.append(f"{idx}. 訂單編號 {oid}")
        for i, item in enumerate(items, start=1):
            output.append(f"　{idx}.{i} {item}")  # 全形空白作為縮排

    return "\n".join(output)
