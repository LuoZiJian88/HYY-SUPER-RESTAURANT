import streamlit as st
import uuid

def init_session():
    if "user" not in st.session_state:
        st.session_state.user = {
            "id": f"guest_{uuid.uuid4().hex}",  # ⭐ 自动游客ID
            "username": "游客",
            "role": "customer"
        }

    if "cart" not in st.session_state:
        st.session_state.cart = {}
    if "party_size" not in st.session_state:
        st.session_state.party_size = None

import streamlit as st

def hide_pages():
    st.markdown(
        """
        <style>
        /* 隐藏左侧 Pages 自动导航 */
        section[data-testid="stSidebarNav"] {
            display: none !important;
        }
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }
        ul[data-testid="stSidebarNavItems"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_sidebar():
    with st.sidebar:
        st.title("🍜 HYY超级大饭店 点餐系统")

        if st.button("🍽 菜单", use_container_width=True):
            st.switch_page("pages/01_菜单浏览.py")

        if st.button("🛒 购物车", use_container_width=True):
            st.switch_page("pages/02_购物车_下单.py")

        if st.button("📦 我的订单", use_container_width=True):
            st.switch_page("pages/03_我的订单.py")
            
        if st.button("🤖 AI 点餐推荐", use_container_width=True):
            st.switch_page("pages/04_AI点餐推荐.py")


