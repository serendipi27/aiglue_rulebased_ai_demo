
import pandas as pd
import streamlit as st
from utils import (
    SCENARIOS, FEATURES, rule_based_decision, predict_ai,
    difference_explanation, style_result
)

st.set_page_config(page_title="직접 입력 비교", page_icon="🎛️", layout="wide")

st.title("🎛️ 2. 직접 입력 비교")
st.caption("슬라이더로 입력값을 바꾸며 Rule-based와 AI-based 결과를 실시간으로 비교합니다.")

scenario_name = st.selectbox("추천 예시 불러오기", ["직접 입력"] + list(SCENARIOS.keys()))
defaults = {"temperature": 70.0, "pressure": 50.0, "vibration": 5.0, "process_time": 60.0, "humidity": 50.0}
if scenario_name != "직접 입력":
    defaults = SCENARIOS[scenario_name].copy()

with st.sidebar:
    st.header("입력값 조정")
    temperature = st.slider("온도", 55.0, 90.0, float(defaults["temperature"]), 0.1)
    pressure = st.slider("압력", 35.0, 65.0, float(defaults["pressure"]), 0.1)
    vibration = st.slider("진동", 2.0, 9.5, float(defaults["vibration"]), 0.1)
    process_time = st.slider("가공시간", 40.0, 85.0, float(defaults["process_time"]), 0.1)
    humidity = st.slider("습도", 25.0, 80.0, float(defaults["humidity"]), 0.1)

row_dict = {
    "temperature": temperature,
    "pressure": pressure,
    "vibration": vibration,
    "process_time": process_time,
    "humidity": humidity,
}

st.subheader("현재 입력값")
input_df = pd.DataFrame([row_dict])[FEATURES]
st.dataframe(input_df, use_container_width=True, hide_index=True)

rule_result, rule_reason = rule_based_decision(row_dict)
ai_result, probs = predict_ai(row_dict)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Rule-based 결과")
    st.metric("판정", style_result(rule_result))
    st.write(rule_reason)

    st.markdown("#### Rule-based 특징")
    st.write("- 사람이 정의한 규칙만 적용합니다.")
    st.write("- 규칙에 없는 조합은 '판단못함'입니다.")
    st.write("- 현재 데모에서는 습도 조건을 보지 않습니다.")

with col2:
    st.markdown("### AI-based 결과")
    st.metric("판정", style_result(ai_result))
    st.write("학습된 패턴을 바탕으로 현재 입력의 품질 상태를 예측합니다.")

    if probs:
        prob_df = pd.DataFrame({"class": list(probs.keys()), "probability": list(probs.values())})
        st.bar_chart(prob_df.set_index("class"))

st.markdown("---")
st.subheader("자동 해설")
for msg in difference_explanation(row_dict, rule_result, ai_result):
    st.write("- " + msg)

st.markdown("---")
st.subheader("강의용 설명 포인트")
if rule_result == "판단못함":
    st.info("이 케이스는 Rule-based가 정의한 조건 바깥에 있으므로 판단을 내리지 못합니다. AI는 과거 데이터 패턴을 기반으로 판정을 시도합니다.")
elif rule_result == ai_result:
    st.success("이 케이스는 Rule-based와 AI-based가 같은 결론을 내렸습니다. 명확한 상황에서는 Rule-based도 충분히 효과적입니다.")
else:
    st.warning("두 방식의 결과가 다릅니다. 규칙의 단순성과 AI의 패턴 학습 차이를 설명하기 좋은 사례입니다.")
