from select_menu import connect_db
"""
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,     -- LINE user ID
    display_name TEXT,            -- 使用者目前顯示名稱（可更新）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
"""

def upsert_user(user_id, display_name):
    conn = connect_db()
    cur = conn.cursor()
    
    sql = """
    INSERT INTO users (user_id, display_name)
    VALUES (%s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET
        display_name = EXCLUDED.display_name,
        updated_at = CURRENT_TIMESTAMP
    """
    cur.execute(sql, (user_id, display_name))
    conn.commit()
    finish_user = '使用者 {} , id {} \n 已更新/建立成功'.format(display_name, user_id)
    return finish_user
