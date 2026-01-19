import streamlit as st


from services.repo_orders import (
    list_all_orders,
    get_order_items,
    merchant_accept_order,
    merchant_mark_paid
)

from services.layout_merchant import (
    init_session, hide_pages, require_merchant, render_sidebar
)

init_session()
hide_pages()
require_merchant()
render_sidebar()



if st.session_state.user["role"] != "merchant":
    st.error("仅商家可访问")
    st.stop()

st.title("📋 订单管理")

STATUS_CN = {
    "ORDERED": "已下单",
    "ACCEPTED": "商家已接单",
    "PAID": "已支付"
}

status_filter = st.selectbox(
    "筛选订单状态",
    ["全部", "ORDERED", "ACCEPTED", "PAID"]
)

orders = list_all_orders(status_filter)

if not orders:
    st.info("暂无订单")
    st.stop()

for o in orders:
    with st.expander(
        f"订单 #{o['id']} | {STATUS_CN[o['status']]} | ¥{float(o['total_amount']):.2f}",
        expanded=False
    ):
        st.write(f"客户ID：{o['customer_id']}")
        st.write(f"用餐人数：{o['party_size'] or '-'}")
        if o["note"]:
            st.write(f"备注：{o['note']}")

        st.write("**菜品明细**")
        for it in get_order_items(o["id"]):
            st.write(f"- {it['product_name']} × {it['quantity']}")

        st.divider()

        if o["status"] == "ORDERED":
            if st.button(
                "🧑‍🍳 接单",
                key=f"accept_{o['id']}",
                use_container_width=True
            ):
                merchant_accept_order(o["id"])
                st.success("已接单")
                st.rerun()

        elif o["status"] == "ACCEPTED":
            if st.button(
                "💰 确认已支付",
                key=f"paid_{o['id']}",
                use_container_width=True
            ):
                merchant_mark_paid(o["id"])
                st.success("已标记为已支付")
                st.rerun()

        else:
            st.success("订单已完成")
