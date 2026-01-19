from services.db import get_conn

def list_active_products(keyword=None, category=None):
    conn = get_conn()
    cur = conn.cursor()

    sql = "SELECT * FROM products WHERE is_active=1"
    params = []

    if keyword:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        k = f"%{keyword}%"
        params += [k, k]


    if category and category != "全部":
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY id DESC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def list_all_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def list_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''"
    )
    cats = [r["category"] for r in cur.fetchall()]
    conn.close()
    return ["全部"] + sorted(cats)

def add_product(name, category, price, description="", is_active=1, image_path=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO products
        (name, category, price, is_active, description, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            str(name),
            str(category),
            float(price),
            int(is_active),
            str(description),
            image_path
        )
    )
    conn.commit()
    conn.close()


def update_product(pid, name, category, price, is_active, description="", image_path=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE products
        SET name=?, category=?, price=?, is_active=?, description=?, image_path=?
        WHERE id=?
        """,
        (
            str(name),
            str(category),
            float(price),
            int(is_active),
            str(description),
            image_path,
            int(pid)
        )
    )
    conn.commit()
    conn.close()


def delete_product(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (int(pid),))
    conn.commit()
    conn.close()

def get_product(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=?", (int(pid),))
    row = cur.fetchone()
    conn.close()
    return row
