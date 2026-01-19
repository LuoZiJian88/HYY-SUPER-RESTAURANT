import streamlit as st
import plotly.express as px

from services.analytics import daily_orders_last_n_days, top_products
from services.layout_merchant import (
    init_session,
    hide_pages,
    require_merchant,
    render_sidebar
)

# ======================
# 页面初始化
# ======================
init_session()
hide_pages()
require_merchant()
render_sidebar()

st.title("📊 数据看板（交互式）")

# =================================================
# 1️⃣ 近 7 日订单数 & 营收趋势
# =================================================
df = daily_orders_last_n_days(7)

if df.empty:
    st.info("暂无订单数据")
else:
    st.subheader("📅 近 7 日订单与营收趋势")

    fig_orders = px.bar(
        df,
        x="day",
        y="orders_cnt",
        labels={"day": "日期", "orders_cnt": "订单数"},
        title="近 7 日订单量",
        text="orders_cnt"
    )
    fig_orders.update_traces(textposition="outside")
    fig_orders.update_layout(hovermode="x unified")
    st.plotly_chart(fig_orders, use_container_width=True)

    fig_revenue = px.line(
        df,
        x="day",
        y="revenue",
        labels={"day": "日期", "revenue": "营收（¥）"},
        title="近 7 日营收趋势",
        markers=True
    )
    fig_revenue.update_layout(hovermode="x unified")
    st.plotly_chart(fig_revenue, use_container_width=True)

# =================================================
# 2️⃣ 各菜品销量占比 & 销售额占比（两张饼图）
# =================================================
# 使用较大的 n，确保覆盖全部菜品
tp = top_products(1000)

if tp.empty:
    st.info("暂无菜品销售数据")
else:
    st.subheader("🍽 各菜品销售结构分析")

    col1, col2 = st.columns(2)

    # ---------- 饼图 1：销量占比 ----------
    with col1:
        fig_qty = px.pie(
            tp,
            names="product_name",
            values="qty_sold",
            title="各菜品销量占比",
            hole=0.35
        )
        fig_qty.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "%{label}<br>"
                "销量：%{value} 份<br>"
                "占比：%{percent}"
            )
        )
        st.plotly_chart(fig_qty, use_container_width=True)

    # ---------- 饼图 2：销售额占比 ----------
    with col2:
        fig_sales = px.pie(
            tp,
            names="product_name",
            values="sales",
            title="各菜品销售额占比",
            hole=0.35
        )
        fig_sales.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "%{label}<br>"
                "销售额：¥%{value:.2f}<br>"
                "占比：%{percent}"
            )
        )
        st.plotly_chart(fig_sales, use_container_width=True)
