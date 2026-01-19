import streamlit as st

from services.repo_orders import list_orders_by_customer, get_order_items
from services.layout_customer import init_session, hide_pages, render_sidebar

init_session()
hide_pages()
render_sidebar()




if st.session_state.user["role"] != "customer":
    st.error("仅客户可访问")
    st.stop()

st.title("📦 我的订单")

STATUS_CN = {
    "ORDERED": "已下单",
    "ACCEPTED": "商家已接单",
    "PAID": "已支付"
}

orders = list_orders_by_customer(st.session_state.user["id"])


if not orders:
    st.info("你还没有订单")
    st.stop()

for o in orders:
    with st.expander(
        f"订单 #{o['id']} | 状态：{STATUS_CN[o['status']]} | ¥{float(o['total_amount']):.2f}",
        expanded=False
    ):
        st.write(f"用餐人数：{o['party_size'] or '-'}")
        if o["note"]:
            st.write(f"备注：{o['note']}")

        st.write("**菜品明细**")
        for it in get_order_items(o["id"]):
            st.write(f"- {it['product_name']} × {it['quantity']}")

        if o["status"] == "ORDERED":
            st.info("已下单，等待商家接单")
        elif o["status"] == "ACCEPTED":
            st.info("商家已接单，正在处理，买单请至前台")
        else:
            st.success("订单已支付完成")
