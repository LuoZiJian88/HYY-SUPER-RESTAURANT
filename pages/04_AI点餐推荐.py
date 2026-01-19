import streamlit as st

from services.repo_products import list_active_products
from services.llm_recommender import recommend_with_llm
from services.layout_customer import init_session, hide_pages, render_sidebar

init_session()
hide_pages()
render_sidebar()

if st.session_state.user["role"] != "customer":
    st.error("仅客户可访问")
    st.stop()

st.title("🤖 AI 点餐推荐")

# ===== 输入区 =====
people = st.number_input(
    "用餐人数",
    min_value=1,
    max_value=20,
    value=st.session_state.party_size or 1,
    step=1
)

budget = st.number_input(
    "预算",
    min_value=0.0,
    value=0.0,
    step=10.0
)

prefs = st.text_input(
    "口味偏好（自由描述，例如：辣一点、下饭、肉多）"
)

avoid = st.text_input(
    "忌口（例如：不吃辣、不吃牛肉）"
)

# ===== 用 session_state 记住推荐结果（否则 rerun 会丢）=====
if "ai_last_result" not in st.session_state:
    st.session_state.ai_last_result = None
if "ai_last_menu_rows" not in st.session_state:
    st.session_state.ai_last_menu_rows = None

# ===== 触发推荐 =====
if st.button("✨ 开始 AI 推荐", use_container_width=True):
    menu_rows = list_active_products()

    req = {
        "people": int(people),
        "budget": float(budget),
        "prefs": prefs,
        "avoid": avoid
    }

    try:
        with st.spinner("AI 正在思考点什么菜…"):
            result = recommend_with_llm(req, menu_rows)

        # 保存结果，后续可“一键加入购物车”
        st.session_state.ai_last_result = result
        st.session_state.ai_last_menu_rows = menu_rows

        # 同步用餐人数（可选但更合理）
        st.session_state.party_size = int(people)

        st.success("推荐已生成，可下方一键加入购物车。")
        st.rerun()

    except Exception as e:
        st.error(f"AI 推荐失败：{e}")

# ===== 展示推荐 + 一键加入购物车 =====
result = st.session_state.ai_last_result
menu_rows = st.session_state.ai_last_menu_rows

if result and menu_rows:
    st.subheader("🍽 推荐结果")

    total = 0.0
    for it in result.get("items", []):
        pid = int(it["product_id"])
        qty = int(it["qty"])
        reason = it.get("reason", "")

        # 找到菜品信息（如果菜单变了/菜下架，避免崩）
        p = next((p for p in menu_rows if int(p["id"]) == pid), None)
        if not p:
            st.warning(f"推荐菜品 ID={pid} 当前不在菜单中，已跳过展示。")
            continue

        price = float(p["price"]) * qty
        total += price

        with st.container(border=True):
            if p["image_path"]:
                st.image(p["image_path"], width=160)
            st.write(f"**{p['name']} × {qty}**（¥{price:.2f}）")
            if reason:
                st.caption(reason)

    st.success(f"预计总价：¥{total:.2f}")
    if result.get("note"):
        st.info(result["note"])

    # ===== 一键加入购物车（核心功能）=====
    col_a, col_b = st.columns([2, 1])
    with col_a:
        if st.button("🛒 一键加入购物车", type="primary", use_container_width=True):
            added_cnt = 0
            skipped_cnt = 0

            # 确保 cart 存在
            if "cart" not in st.session_state:
                st.session_state.cart = {}

            for it in result.get("items", []):
                pid = int(it["product_id"])
                qty = int(it["qty"])
                if qty <= 0:
                    skipped_cnt += 1
                    continue

                p = next((p for p in menu_rows if int(p["id"]) == pid), None)
                if not p:
                    skipped_cnt += 1
                    continue

                if pid not in st.session_state.cart:
                    st.session_state.cart[pid] = {
                        "name": p["name"],
                        "price": float(p["price"]),
                        "qty": 0
                    }
                st.session_state.cart[pid]["qty"] += qty
                added_cnt += 1

            st.success(f"已加入购物车：{added_cnt} 个菜品（跳过 {skipped_cnt} 个无效项）")
            # 让用户立刻去结算
            st.switch_page("pages/02_购物车_下单.py")

    with col_b:
        if st.button("🧹 清空本次推荐", use_container_width=True):
            st.session_state.ai_last_result = None
            st.session_state.ai_last_menu_rows = None
            st.rerun()
else:
    st.caption("先点击“开始 AI 推荐”，生成推荐后可一键加入购物车。")
