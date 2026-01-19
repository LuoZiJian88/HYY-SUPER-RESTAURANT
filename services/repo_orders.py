from services.db import get_conn
from services.repo_products import get_product

# 订单状态流
STATUS_FLOW = ["ORDERED", "ACCEPTED", "PAID"]

def create_order(customer_id: str, party_size: int, cart: dict, note: str = "") -> int:
    if not cart:
        raise ValueError("购物车为空")

    items = []
    total = 0.0

    for pid, v in cart.items():
        qty = int(v["qty"])
        if qty <= 0:
            continue

        p = get_product(pid)
        if p is None:
            raise ValueError(f"菜品不存在：{pid}")

        unit_price = float(p["price"])
        items.append({
            "product_id": int(pid),
            "product_name": p["name"],
            "unit_price": unit_price,
            "qty": qty
        })
        total += unit_price * qty

    if not items:
        raise ValueError("购物车数量为0")

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO orders(customer_id, party_size, total_amount, status, note)
               VALUES (?, ?, ?, 'ORDERED', ?)""",
            (customer_id, int(party_size) if party_size else None, float(total), note)
        )
        order_id = cur.lastrowid

        for it in items:
            cur.execute(
                """INSERT INTO order_items(order_id, product_id, product_name, unit_price, quantity)
                   VALUES (?, ?, ?, ?, ?)""",
                (order_id, it["product_id"], it["product_name"], it["unit_price"], it["qty"])
            )

        conn.commit()
        return int(order_id)
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def list_orders_by_customer(customer_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC",
        (customer_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def list_all_orders(status=None):
    conn = get_conn()
    cur = conn.cursor()
    if status and status != "全部":
        cur.execute(
            "SELECT * FROM orders WHERE status=? ORDER BY id DESC",
            (status,)
        )
    else:
        cur.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_order_items(order_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM order_items WHERE order_id=? ORDER BY id",
        (int(order_id),)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

# ===== 商家操作 =====

def merchant_accept_order(order_id: int):
    """已下单 → 商家已接单"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET status='ACCEPTED' WHERE id=? AND status='ORDERED'",
        (int(order_id),)
    )
    conn.commit()
    conn.close()

def merchant_mark_paid(order_id: int):
    """商家已接单 → 已支付"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET status='PAID' WHERE id=? AND status='ACCEPTED'",
        (int(order_id),)
    )
    conn.commit()
    conn.close()
