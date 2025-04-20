import streamlit as st
import pymysql
import pandas as pd
from sqlalchemy import create_engine
import time
import numpy as np
import pickle

st.title("🔄 데이터 로딩 중...")

# DB 연결 정보
DB_USER = "chaeyun"
DB_PASSWORD = "6149"
DB_HOST = "hk-toss-middle-project.cjkcuqkegqpx.eu-north-1.rds.amazonaws.com"
DB_PORT = "3306"
DB_NAME = "project_db"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

query_for_eda="""
SELECT 
    PHI_BENEFIT,
    PHI_PREMIUM,
    H_OOP,
    AGE,
    SEX,
    OUDENT_DZ_CTN,
    OUORT_DZ_CTN,
    INMED_HTN_CTN,
    INMED_HPT_CTN,
    INMED_CVD_CTN,
    INMED_LIV_CTN,
    INMED_LRI_CTN,
    INMED_MSD_CTN,
    INMED_CNR_CTN,
    INMED_OBG_CTN,
    INMED_ETC_CTN
FROM final_model_data
"""

query = """
SELECT PIDWON, PHI_BENEFIT, PHI_PREMIUM, H_OOP, D_YEAR, INMED_CNR, INMED_CVD, INMED_ETC, INMED_HPT, INMED_HTN, INMED_LIV, INMED_LRI, INMED_MSD, INMED_OBG
FROM final_model_data_encoded
"""

# 프로그레스 바 초기화
progress_bar = st.progress(0)

# 데이터 로딩 시뮬레이션
for i in range(100):
    time.sleep(0.2)  # 데이터 로딩 중 (테스트용)
    progress_bar.progress(i + 1)

# 실제 데이터 로딩
df = pd.read_sql(query_for_eda, engine)
data = pd.read_sql(query, engine)

# 모델 불러오기
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# 사용자 입력값 받아와서 전처리
name = st.session_state.get("name", "이름")
age = float(st.session_state.get("age", 0))
sex = st.session_state.get("sex", "성별")
sex_encoded = 0.0 if sex == "남성" else 1.0
phi_premium = 11.6736062060344
h_inc_tot = 17.9024947825699
debt_ratio = 0.73798357949177
prop = 9.05963375455148
custm_benf_yn = 0.0
p2 = 6.0
p2_2 = 60.0
disa_yn = 0.0
wt_mg = 1
inmed_cnr = 0.0
inmed_cvd = 0.0
inmed_etc = 1.0
inmed_hpt = 0.0
inmed_htn = 1.0
inmed_liv = 0.0
inmed_lri = 0.0
inmed_msd = 0.0
inmed_obg = 0.0
ouoop_2 = 11.8923203453452
med_sum = 30.1919366978379

# 모델 입력값 만들기
X_input = np.array([[
    phi_premium,
    h_inc_tot,
    debt_ratio,
    prop,
    custm_benf_yn,
    p2,
    p2_2,
    sex_encoded,
    disa_yn,
    age,
    wt_mg,
    inmed_cnr,
    inmed_cvd,
    inmed_etc,
    inmed_hpt,
    inmed_htn,
    inmed_liv,
    inmed_lri,
    inmed_msd,
    inmed_obg,
    ouoop_2,
    med_sum
]])

#, 예측 실행
benefit = np.exp(model.predict(X_input)[0]) - 1
# benefit = 300000

# 세션 상태에 데이터 저장
st.session_state["loaded_data"] = df
# 모델을 돌렸다고 가정하고 보험금 정보 보내기
st.session_state['benefit'] = benefit
st.session_state['loaded_data2'] = data

# 성공 메시지
st.success("✅ 데이터 로딩 완료!")

# 자동 페이지 이동
time.sleep(2)  # 2초 대기 후 이동
st.switch_page("pages/result.py")