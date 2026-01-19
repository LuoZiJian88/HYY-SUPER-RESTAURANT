import pandas as pd
from services.db import get_conn

def daily_orders_last_n_days(n=7):
    conn = get_conn()
    df = pd.read_sql_query(
        f"""
        SELECT date(created_at) as day,
               COUNT(*) as orders_cnt,
               SUM(total_amount) as revenue
        FROM orders
        WHERE created_at >= datetime('now', '-{int(n)} days')
        GROUP BY date(created_at)
        ORDER BY day ASC
        """,
        conn
    )
    conn.close()
    return df

def top_products(n=10):
    conn = get_conn()
    df = pd.read_sql_query(
        f"""
        SELECT product_name,
               SUM(quantity) as qty_sold,
               SUM(quantity * unit_price) as sales
        FROM order_items
        GROUP BY product_name
        ORDER BY qty_sold DESC
        LIMIT {int(n)}
        """,
        conn
    )
    conn.close()
    return df
