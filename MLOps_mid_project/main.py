import streamlit as st
import pymysql
from sqlalchemy import create_engine
import pandas as pd

# Streamlit UI
st.markdown(
    """
    <style>
    .title-container {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title-container">🌟 건강행태조사 설문지 🌟</h1>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style='font-size:15px; font-weight:bold'>
    이름
</div>
""", unsafe_allow_html=True)
name = st.text_input(
    label="",
    placeholder="이름을 입력하세요"
)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style='font-size:15px; font-weight:bold'>
    나이
</div>
""", unsafe_allow_html=True)
age = st.text_input(
  label="",
  placeholder="나이를 입력하세요"
)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style='font-size:15px; font-weight:bold'>
    성별
</div>
""", unsafe_allow_html=True)
sex = st.radio(
    "",
    ("남성", "여성"),
    horizontal=True
)
st.markdown("<br>", unsafe_allow_html=True)

# if st.button("제출"):
#     st.session_state['name'] = name
#     st.session_state['age'] = age
#     st.session_state['sex'] = sex

#     st.switch_page("pages/loading.py")

col1, col2, col3 = st.columns([1, 2, 1])  # 가운데 칸을 크게
with col2:
    if st.button("제출", use_container_width=True):
        st.session_state['name'] = name
        st.session_state['age'] = age
        st.session_state['sex'] = sex
        st.switch_page("pages/loading.py")