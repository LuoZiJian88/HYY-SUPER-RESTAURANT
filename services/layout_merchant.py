import streamlit as st

def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None

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


def require_merchant():
    if st.session_state.user is None or st.session_state.user["role"] != "merchant":
        st.warning("请先以商家身份登录")
        st.switch_page("pages/01_商家登录.py")

def render_sidebar():
    with st.sidebar:
        st.title("🧑‍🍳 HYY超级大饭店 商家后台")

        if st.button("🧾 菜品管理", use_container_width=True):
            st.switch_page("pages/02_菜品管理.py")

        if st.button("📋 订单管理", use_container_width=True):
            st.switch_page("pages/03_订单管理.py")

        if st.button("📊 数据看板", use_container_width=True):
            st.switch_page("pages/04_数据看板.py")

        st.divider()

        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.user = None
            st.switch_page("pages/01_商家登录.py")
