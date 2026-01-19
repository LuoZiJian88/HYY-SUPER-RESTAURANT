import streamlit as st
from services.db import init_db

# ===== 启动时初始化数据库 =====
init_db()
st.switch_page("pages/01_商家登录.py")
