import streamlit as st
import pymysql
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as mticker

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams["axes.unicode_minus"] = False

# main.py의 데이터 가져오기
name = st.session_state.get("name", "이름")
age = int(st.session_state.get("age", 0))
sex = st.session_state.get("sex", "성별")
df = st.session_state.get("loaded_data", None)
data = st.session_state.get("loaded_data2", None)
benefit = int(st.session_state.get("benefit", "0"))
formatted_benefit = f"{benefit:,}"

if df is None:
    st.error("❌ 데이터가 없습니다. 먼저 로딩 페이지에서 데이터를 불러와 주세요.")
else:
    st.success("✅ 데이터 로딩 완료! 아래 표에서 확인하세요.")

st.header(f"안녕하세요 {name}님 👋🏻")
st.subheader(f"당신의 예상 보험 수령액은 :red[**{formatted_benefit}원**]입니다!")
st.markdown("<br>", unsafe_allow_html=True)

df["나이대"] = pd.cut(
    df["AGE"],
    bins=range(0, 101, 10), 
    right=False,         
    labels=[f"{i}대" for i in range(0, 100, 10)]
)

df['PHI_BENEFIT'] = np.exp(df['PHI_BENEFIT']) - 1
df['PHI_PREMIUM'] = np.exp(df['PHI_PREMIUM']) - 1
df['H_OOP'] = np.exp(df['H_OOP']) - 1

data['PHI_BENEFIT'] = np.exp(data['PHI_BENEFIT']) - 1
data['PHI_PREMIUM'] = np.exp(data['PHI_PREMIUM']) - 1
data['H_OOP'] = np.exp(data['H_OOP']) - 1

inmed_col = ['INMED_CVD','INMED_ETC','INMED_HPT','INMED_HTN','INMED_LIV','INMED_LRI','INMED_MSD','INMED_OBG', "INMED_CNR"]

data['INMED'] = data[inmed_col].apply(lambda row: ', '.join([col for col in inmed_col if row[col] == 1]), axis=1)
data.drop(inmed_col, axis=1, inplace=True)

age_grouped = df.groupby("나이대").agg({
    "PHI_BENEFIT": "mean",
    "PHI_PREMIUM": "mean",
    "H_OOP": "mean"
}).reset_index()

age_bins = range(0, 101, 10)
age_labels = [f"{i}대" for i in range(0, 100, 10)]
user_age_group = pd.cut([age], bins=age_bins, right=False, labels=age_labels)[0]

conditions = ["CVD", "ETC", "HPT", "HTN", "LIV", "LRI", "MSD", "OBG", "CNR"]

benefit_dict = {cond: [] for cond in conditions}
for index, row in data.iterrows():
    for cond in conditions:
        if f"INMED_{cond}" in row['INMED']:
            benefit_dict[cond].append(row['PHI_BENEFIT'])

premium_dict = {cond: [] for cond in conditions}
for index, row in data.iterrows():
    for cond in conditions:
        if f"INMED_{cond}" in row['INMED']:
            premium_dict[cond].append(row['PHI_PREMIUM'])

hoop_dict = {cond: [] for cond in conditions}
for index, row in data.iterrows():
    for cond in conditions:
        if f"INMED_{cond}" in row['INMED']:
            hoop_dict[cond].append(row['H_OOP'])

data2 = {
    "INMED" : conditions,
}
data2 = pd.DataFrame(data2)

average_benefits = {key: (sum(values) / len(values) if values else None) for key, values in benefit_dict.items()}
average_premium = {key: (sum(values) / len(values) if values else None) for key, values in premium_dict.items()}
average_hoop = {key: (sum(values) / len(values) if values else None) for key, values in hoop_dict.items()}

def get_benefit(inmed):
    for cond in average_benefits.keys():
        if f"{cond}" in inmed:
            return average_benefits[cond]
    return None

data2["BENEFIT"] = data2["INMED"].apply(get_benefit)

def get_premium(inmed):
    for cond in average_premium.keys():
        if f"{cond}" in inmed:
            return average_premium[cond]
    return None

data2["PREMIUM"] = data2["INMED"].apply(get_premium)

def get_hoop(inmed):
    for cond in average_hoop.keys():
        if f"{cond}" in inmed:
            return average_hoop[cond]
    return None

data2["H_OOP"] = data2["INMED"].apply(get_hoop)

# average_benefits = {key: (sum(values) / len(values) if values else None) for key, values in benefit_dict.items()}
# average_premium = {key: (sum(values) / len(values) if values else None) for key, values in premium_dict.items()}
# average_hoop = {key: (sum(values) / len(values) if values else None) for key, values in hoop_dict.items()}

x = age_grouped["나이대"]
y_bar = age_grouped["PHI_BENEFIT"]     
y_line = age_grouped["PHI_PREMIUM"]       
y_line2 = age_grouped["H_OOP"]

bar_colors = ["red" if label == user_age_group else "lightgray" for label in x]
highlight_idx = list(x).index(user_age_group)

fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.bar(x, y_bar, color=bar_colors, label="평균 보험금 수령액", zorder=1)
ax1.plot(highlight_idx, benefit, marker='*', color='black', markersize=10, label="예상 보험금", zorder=5)
ax1.set_ylabel("평균 보험금 수령액 / 연간 의료비 지출", color="black")
ax1.tick_params(axis='y', labelcolor="red")

ax1.plot(x, y_line2, color="red", marker="o", label="연간 의료비 지출", zorder=2)

ax2 = ax1.twinx()

ax2.plot(x, y_line, color="green", marker="s", linestyle="--", label="평균 월 보험료", zorder=3)

ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))

ax2.set_ylabel("평균 월 보험료", color="black")
ax2.tick_params(axis='y', labelcolor="green")

plt.title("연령대 별 연간 의료비 지출, 보험금 수령액, 보험료 + 나의 예측 보험금 수령액", fontsize=14, pad=20)

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right")

plt.tight_layout()

st.pyplot(fig)

x2 = data2["INMED"]
y2_bar = data2["BENEFIT"]
y2_line2 = data2["H_OOP"]
y2_line = data2["PREMIUM"]

new_x_labels = ['심뇌혈관', '기타', '갑상선기능장애', '고혈압당뇨', '간', 
                '만성하기도', '근골격계', '산부인과', '암']

highlight_labels = ['간', '산부인과']
bar_colors2 = ['steelblue' if label in highlight_labels else 'lightgray' for label in new_x_labels]

fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.bar(x2, y2_bar, color=bar_colors2, label="평균 보험금")
ax1.set_ylabel("평균 보험금", color="black")
ax1.tick_params(axis='y', labelcolor="steelblue")

ax1.plot(x2, y2_line2, color="steelblue", marker="o", label="평균 의료비")

ax2 = ax1.twinx()

ax2.plot(x2, y2_line, color="green", marker="s", linestyle="--", label="평균 보험료")

ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))

ax2.set_ylabel("평균 의료비 / 평균 보험료", color="black")
ax2.tick_params(axis='y', labelcolor="green")

plt.title("주질환 별 평균 보험금 및 의료비, 보험료")
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right")

ax1.set_xticks(range(len(new_x_labels)))
ax1.set_xticklabels(new_x_labels)

plt.tight_layout()

st.pyplot(fig)