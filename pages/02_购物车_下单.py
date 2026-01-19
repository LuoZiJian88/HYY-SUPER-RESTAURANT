import streamlit as st
from services.repo_orders import create_order
from services.layout_customer import init_session, hide_pages, render_sidebar

init_session()
hide_pages()
render_sidebar()




if st.session_state.user["role"] != "customer":
    st.error("仅客户可访问")
    st.stop()

st.title("🛒 购物车 / 下单")

cart = st.session_state.cart
if not cart:
    st.info("购物车为空，去菜单页添加吧。")
    st.stop()

if st.session_state.party_size is None:
    st.warning("请先在菜单页选择用餐人数。")
    st.stop()

total = 0.0

for pid, v in list(cart.items()):
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1:
            st.write(f"**{v['name']}**")
        with c2:
            st.write(f"¥{float(v['price']):.2f}")
        with c3:
            new_qty = st.number_input("数量", min_value=0, max_value=999, value=int(v["qty"]), step=1, key=f"cart_{pid}")
            v["qty"] = int(new_qty)
        with c4:
            if st.button("删除", key=f"del_{pid}"):
                cart.pop(pid, None)
                st.rerun()

# 清理 qty=0
for pid in list(cart.keys()):
    if int(cart[pid]["qty"]) <= 0:
        cart.pop(pid, None)

if not cart:
    st.info("已清空购物车。")
    st.stop()

for pid, v in cart.items():
    total += float(v["price"]) * int(v["qty"])

st.subheader(f"合计：¥{total:.2f}")

note = st.text_input("备注（可选）", "")

if st.session_state.user["id"] is None:
    st.warning("请先登录后再下单")
    st.stop()


if st.button("✅ 提交订单", type="primary", use_container_width=True):
    try:
        order_id = create_order(
            customer_id=st.session_state.user["id"],
            party_size=int(st.session_state.party_size),
            cart=cart,
            note=note.strip()
        )

        st.session_state.cart = {}
        st.success(f"下单成功！订单号：{order_id}")
        st.switch_page("pages/03_我的订单.py")
    except Exception as e:
        st.error(f"下单失败：{e}")
