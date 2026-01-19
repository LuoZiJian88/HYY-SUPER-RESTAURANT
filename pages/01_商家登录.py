import streamlit as st
from services.auth import login_user
from services.layout_merchant import init_session, hide_pages

init_session()
hide_pages()

st.title("🔐 商家登录")

username = st.text_input("商家账号")
password = st.text_input("密码", type="password")

if st.button("登录", use_container_width=True):
    user = login_user(username, password)
    if user and user["role"] == "merchant":
        st.session_state.user = user
        st.success("登录成功")
        st.switch_page("pages/02_菜品管理.py")
    else:
        st.error("账号或密码错误，或非商家账号")
