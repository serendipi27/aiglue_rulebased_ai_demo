
import pandas as pd
import streamlit as st
from utils import load_test_data, rule_based_decision, predict_ai, difference_explanation, style_result, FEATURES

st.set_page_config(page_title="CSV 비교", page_icon="📄", layout="wide")

st.title("📄 1. CSV 테스트 데이터 기반 비교")
st.caption("테스트 CSV 파일의 각 샘플에 대해 Rule-based와 AI-based 결과를 동시에 비교합니다.")

df = load_test_data().copy()

rule_results = []
rule_reasons = []
ai_results = []
for _, row in df.iterrows():
    rule_result, rule_reason = rule_based_decision(row.to_dict())
    ai_result, _ = predict_ai(row.to_dict())

    rule_results.append(rule_result)
    rule_reasons.append(rule_reason)
    ai_results.append(ai_result)

df["rule_based_result"] = rule_results
df["rule_reason"] = rule_reasons
df["ai_based_result"] = ai_results
df["same_or_diff"] = df.apply(
    lambda x: "같음" if x["rule_based_result"] == x["ai_based_result"] else "다름",
    axis=1
)

left, right = st.columns(2)

with left:
    st.subheader("Rule-based 결과")
    st.dataframe(
        df[FEATURES + ["rule_based_result", "rule_reason"]],
        use_container_width=True,
        hide_index=True
    )

with right:
    st.subheader("AI-based 결과")
    st.dataframe(
        df[FEATURES + ["ai_based_result"]],
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.subheader("전체 비교 테이블")
st.dataframe(
    df[FEATURES + ["rule_based_result", "ai_based_result", "same_or_diff"]],
    use_container_width=True,
    hide_index=True
)

unknown_df = df[df["rule_based_result"] == "판단못함"]
if not unknown_df.empty:
    st.warning("아래 샘플들은 Rule-based 규칙 범위 밖이라 '판단못함'으로 처리되었습니다.")
    for idx, row in unknown_df.iterrows():
        with st.expander(f"샘플 {idx + 1}: Rule-based는 판단못함, AI는 {row['ai_based_result']}"):
            st.write("입력값:", row[FEATURES].to_dict())
            messages = difference_explanation(
                row[FEATURES].to_dict(),
                row["rule_based_result"],
                row["ai_based_result"]
            )
            for m in messages:
                st.write("- " + m)

st.markdown("---")
st.subheader("샘플 상세 확인")
selected_idx = st.selectbox("확인할 샘플 선택", options=list(range(len(df))), format_func=lambda x: f"샘플 {x+1}")
selected = df.iloc[selected_idx]
row_dict = selected[FEATURES].to_dict()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Rule-based")
    st.metric("판정", style_result(selected["rule_based_result"]))
    st.write(selected["rule_reason"])

with col2:
    st.markdown("### AI-based")
    st.metric("판정", style_result(selected["ai_based_result"]))
    pred, probs = predict_ai(row_dict)
    if probs:
        prob_df = pd.DataFrame({"class": list(probs.keys()), "probability": list(probs.values())})
        st.bar_chart(prob_df.set_index("class"))

st.markdown("### 해설")
for msg in difference_explanation(row_dict, selected["rule_based_result"], selected["ai_based_result"]):
    st.write("- " + msg)
