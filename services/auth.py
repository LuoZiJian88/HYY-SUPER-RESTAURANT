from services.db import get_conn

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, role FROM users WHERE username=? AND password=?",
        (username, password)
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
