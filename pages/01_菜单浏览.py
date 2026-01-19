import streamlit as st
from collections import defaultdict

from services.repo_products import list_active_products, list_categories
from services.layout_customer import init_session, hide_pages, render_sidebar

init_session()
hide_pages()
render_sidebar()




if st.session_state.user["role"] != "customer":
    st.error("仅客户可访问")
    st.stop()

st.title("🍽 菜单浏览")

# ===== 用餐人数确认 =====
if st.session_state.party_size is None:
    st.info("请先选择用餐人数并点击确认")

    if "party_size_input" not in st.session_state:
        st.session_state.party_size_input = 1

    c1, c2 = st.columns([2, 1])
    with c1:
        st.number_input(
            "用餐人数",
            min_value=1,
            max_value=20,
            step=1,
            key="party_size_input",
        )
    with c2:
        st.write("")
        if st.button("✅ 确认人数", use_container_width=True):
            st.session_state.party_size = int(st.session_state.party_size_input)
            st.rerun()

    st.stop()

st.success(f"当前用餐人数：{st.session_state.party_size}")

# ===== 搜索（分类选择仍保留，用于筛选）=====
col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("搜索（菜名 / 描述）", "")
with col2:
    category_filter = st.selectbox("只看某一分类（可选）", list_categories())

rows = list_active_products(
    keyword=keyword.strip() or None,
    category=category_filter
)

if not rows:
    st.info("没有符合条件的菜品")
    st.stop()

# ===== 按分类分组 =====
grouped = defaultdict(list)
for p in rows:
    cat = p["category"] or "未分类"
    grouped[cat].append(p)

# ===== 分类顺序：按分类名排序 =====
sorted_categories = sorted(grouped.keys())

st.caption(f"共 {len(rows)} 个菜品，按分类展示")

# ===== 分类 → 菜品 =====
for cat in sorted_categories:
    st.subheader(f"📂 {cat}")

    for p in grouped[cat]:
        with st.container(border=True):
            c0, c1, c2, c3 = st.columns([1.3, 2.7, 1, 1])

            with c0:
                if p["image_path"]:
                    st.image(p["image_path"], use_container_width=True)
                else:
                    st.caption("无图")

            with c1:
                st.subheader(p["name"])
                if p["description"]:
                    st.write(p["description"])

            with c2:
                st.metric("价格", f"¥{float(p['price']):.2f}")

            with c3:
                qty = st.number_input(
                    "数量",
                    min_value=1,
                    max_value=20,
                    value=1,
                    key=f"qty_{p['id']}"
                )
                if st.button("加入购物车", key=f"add_{p['id']}", use_container_width=True):
                    pid = int(p["id"])
                    if pid not in st.session_state.cart:
                        st.session_state.cart[pid] = {
                            "name": p["name"],
                            "price": float(p["price"]),
                            "qty": 0
                        }
                    st.session_state.cart[pid]["qty"] += int(qty)
                    st.success("已加入购物车")
