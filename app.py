import pandas as pd
import streamlit as st

from utils import (
    FEATURES,
    SCENARIOS,
    difference_explanation,
    load_test_data,
    predict_ai,
    rule_based_decision,
    style_result,
)

# -----------------------------------
# 기본 설정
# -----------------------------------
st.set_page_config(
    page_title="Rule-based vs AI-based 의사결정 비교",
    page_icon="🏭",
    layout="wide"
)

# -----------------------------------
# 기본 멀티페이지 사이드바 숨기기
# (pages 폴더가 있어도 상단 app / CSV 비교 / 직접 입력 비교 안 보이게)
# -----------------------------------
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* 사이드바 버튼 간격 조금 정리 */
    section[data-testid="stSidebar"] .stButton {
        width: 100%;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# 세션 상태 초기화
# -----------------------------------
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "intro"

# -----------------------------------
# 공통 스타일
# -----------------------------------
def highlight_unknown_row(row):
    """
    Rule-based 결과가 '판단못함'인 경우
    해당 행 전체를 노란색으로 강조
    """
    if row.get("rule_based_result", "") == "판단못함":
        return ["background-color: #fff3b0"] * len(row)
    return [""] * len(row)


def validate_uploaded_dataframe(df: pd.DataFrame):
    """
    업로드된 파일의 컬럼 구조가 FEATURES와 동일한지 검사
    """
    actual_cols = list(df.columns)
    expected_cols = FEATURES

    if actual_cols != expected_cols:
        return False, (
            "업로드한 파일의 컬럼 구조가 올바르지 않습니다.\n\n"
            f"- 현재 컬럼: {actual_cols}\n"
            f"- 필요한 컬럼: {expected_cols}"
        )
    return True, ""


def run_decision_on_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    입력 데이터프레임에 대해 Rule-based / AI-based 결과 계산
    """
    result_df = df.copy()

    rule_results = []
    rule_reasons = []
    ai_results = []

    for _, row in result_df.iterrows():
        row_dict = row.to_dict()

        rule_result, rule_reason = rule_based_decision(row_dict)
        ai_result, _ = predict_ai(row_dict)

        rule_results.append(rule_result)
        rule_reasons.append(rule_reason)
        ai_results.append(ai_result)

    result_df["rule_based_result"] = rule_results
    result_df["rule_reason"] = rule_reasons
    result_df["ai_based_result"] = ai_results
    result_df["same_or_diff"] = result_df.apply(
        lambda x: "같음" if x["rule_based_result"] == x["ai_based_result"] else "다름",
        axis=1
    )

    return result_df


# -----------------------------------
# 사이드바 페이지 버튼
# -----------------------------------
def render_sidebar_navigation():
    st.sidebar.title("메뉴")
    st.sidebar.markdown("### 페이지 선택")

    intro_type = "primary" if st.session_state.selected_page == "intro" else "secondary"
    test_type = "primary" if st.session_state.selected_page == "test" else "secondary"
    user_type = "primary" if st.session_state.selected_page == "user" else "secondary"
    mfg_type = "primary" if st.session_state.selected_page == "mfg_quality" else "secondary"

    if st.sidebar.button(
        "Rule-based .vs. AI-based 웹앱 소개",
        use_container_width=True,
        type=intro_type,
        key="btn_intro"
    ):
        st.session_state.selected_page = "intro"

    if st.sidebar.button(
        "Test 데이터로 비교해보기",
        use_container_width=True,
        type=test_type,
        key="btn_test"
    ):
        st.session_state.selected_page = "test"

    if st.sidebar.button(
        "사용자 입력으로 비교해보기",
        use_container_width=True,
        type=user_type,
        key="btn_user"
    ):
        st.session_state.selected_page = "user"

    if st.sidebar.button(
        "제조데이터 업로드 & 품질검사",
        use_container_width=True,
        type=mfg_type,
        key="btn_mfg_quality"
    ):
        st.session_state.selected_page = "mfg_quality"


# -----------------------------------
# 소개 페이지
# -----------------------------------
def show_intro_page():
    st.title("🏭 Rule-based .vs. AI-based 웹앱 소개")

    st.markdown("""
이 웹앱은 **Rule-based 의사결정**과 **AI-based 의사결정**의 차이를  
현업 담당자가 직접 체험할 수 있도록 만든 교육용 실습 도구입니다.

### 이 웹앱의 목적
- 사람이 만든 **규칙 기반 판단**이 어떻게 동작하는지 이해
- **AI가 학습 데이터를 기반으로 판단**하는 방식 이해
- 두 방식이 **언제 같고, 언제 달라지는지** 직접 비교
- 현업에서 왜 AI 기반 의사결정이 필요한지 직관적으로 이해

---

### 구성
#### 1) Test 데이터로 비교해보기
- 준비된 CSV 테스트 데이터를 불러옵니다.
- 각 행에 대해 **Rule-based 결과**와 **AI-based 결과**를 동시에 비교합니다.
- 특히 Rule-based에서 **'판단못함'** 인 케이스를 쉽게 확인할 수 있습니다.

#### 2) 사용자 입력으로 비교해보기
- 사용자가 슬라이더로 직접 입력값을 조절합니다.
- Rule-based와 AI-based의 결과를 즉시 비교할 수 있습니다.
- 추천 시나리오를 불러와 차이를 설명할 수 있습니다.

#### 3) 제조데이터 품질검사
- CSV 파일을 업로드합니다.
- 업로드한 제조데이터를 표로 확인합니다.
- 버튼을 눌러 Rule-based와 AI-based 품질검사를 동시에 수행합니다.

---

### 실습에서 전달하고 싶은 핵심 메시지
#### Rule-based의 장점
- 이해하기 쉽습니다.
- 기준이 명확합니다.
- 바로 적용할 수 있습니다.

#### Rule-based의 한계
- 규칙에 없는 상황은 판단하지 못합니다.
- 복합적인 패턴 반영이 어렵습니다.
- 새로운 변수(예: 습도)가 들어오면 다시 규칙을 수정해야 합니다.

#### AI-based의 장점
- 여러 변수의 조합 패턴을 반영할 수 있습니다.
- 사람이 명시적으로 규칙을 쓰지 않은 경우도 판정할 수 있습니다.
- 복잡한 중간 영역을 다룰 수 있습니다.

#### 주의할 점
- AI가 항상 더 낫다는 뜻은 아닙니다.
- 실제 현업에서는 **Rule-based + AI-based 보완 구조**가 현실적입니다.
""")

    st.info("왼쪽 사이드바에서 페이지를 선택해 주세요.")


# -----------------------------------
# Test 데이터 비교 페이지
# -----------------------------------
def show_test_compare_page():
    st.title("📄 Test 데이터로 비교해보기")
    st.caption("CSV 테스트 데이터를 불러와 Rule-based와 AI-based 결과를 비교합니다.")

    df = load_test_data().copy()

    rule_results = []
    rule_reasons = []
    ai_results = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        rule_result, rule_reason = rule_based_decision(row_dict)
        ai_result, _ = predict_ai(row_dict)

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

    st.markdown("## 전체 비교 결과")

    styled_df = df[
        FEATURES + ["rule_based_result", "rule_reason", "ai_based_result", "same_or_diff"]
    ].style.apply(highlight_unknown_row, axis=1)

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=False
    )

    st.warning("노란색으로 표시된 행은 Rule-based에서 '판단못함'으로 처리된 케이스입니다.")

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.subheader("Rule-based 결과")
        styled_rule_df = df[
            FEATURES + ["rule_based_result", "rule_reason"]
        ].style.apply(highlight_unknown_row, axis=1)

        st.dataframe(
            styled_rule_df,
            use_container_width=True,
            hide_index=False
        )

    with right:
        st.subheader("AI-based 결과")
        st.dataframe(
            df[FEATURES + ["ai_based_result"]],
            use_container_width=True,
            hide_index=False
        )

    st.markdown("---")
    st.subheader("Rule-based가 판단못함인 케이스만 보기")

    unknown_df = df[df["rule_based_result"] == "판단못함"].copy()

    if unknown_df.empty:
        st.success("현재 테스트 데이터에는 '판단못함' 케이스가 없습니다.")
    else:
        styled_unknown_df = unknown_df[
            FEATURES + ["rule_based_result", "rule_reason", "ai_based_result"]
        ].style.apply(highlight_unknown_row, axis=1)

        st.dataframe(
            styled_unknown_df,
            use_container_width=True,
            hide_index=False
        )

        for idx, row in unknown_df.iterrows():
            with st.expander(f"샘플 {idx + 1} 상세 해설"):
                row_dict = row[FEATURES].to_dict()

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Rule-based")
                    st.metric("판정", style_result(row["rule_based_result"]))
                    st.write(row["rule_reason"])

                with col2:
                    st.markdown("### AI-based")
                    st.metric("판정", style_result(row["ai_based_result"]))
                    _, probs = predict_ai(row_dict)
                    if probs:
                        prob_df = pd.DataFrame({
                            "class": list(probs.keys()),
                            "probability": list(probs.values())
                        })
                        st.bar_chart(prob_df.set_index("class"))

                st.markdown("### 해설")
                messages = difference_explanation(
                    row_dict,
                    row["rule_based_result"],
                    row["ai_based_result"]
                )
                for msg in messages:
                    st.write("- " + msg)

    st.markdown("---")
    st.subheader("샘플 하나씩 상세 확인")

    selected_idx = st.selectbox(
        "확인할 샘플 선택",
        options=list(range(len(df))),
        format_func=lambda x: f"샘플 {x + 1}"
    )

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
        _, probs = predict_ai(row_dict)
        if probs:
            prob_df = pd.DataFrame({
                "class": list(probs.keys()),
                "probability": list(probs.values())
            })
            st.bar_chart(prob_df.set_index("class"))

    st.markdown("### 자동 해설")
    for msg in difference_explanation(
        row_dict,
        selected["rule_based_result"],
        selected["ai_based_result"]
    ):
        st.write("- " + msg)


# -----------------------------------
# 사용자 입력 비교 페이지
# -----------------------------------
def show_user_input_page():
    st.title("🎛️ 사용자 입력으로 비교해보기")
    st.caption("슬라이더로 값을 조정하며 Rule-based와 AI-based 결과를 즉시 비교합니다.")

    scenario_name = st.selectbox(
        "추천 예시 불러오기",
        ["직접 입력"] + list(SCENARIOS.keys())
    )

    defaults = {
        "temperature": 70.0,
        "pressure": 50.0,
        "vibration": 5.0,
        "process_time": 60.0,
        "humidity": 50.0,
    }

    if scenario_name != "직접 입력":
        defaults = SCENARIOS[scenario_name].copy()

    input_col1, input_col2 = st.columns(2)

    with input_col1:
        temperature = st.slider("온도", 55.0, 90.0, float(defaults["temperature"]), 0.1)
        pressure = st.slider("압력", 35.0, 65.0, float(defaults["pressure"]), 0.1)
        vibration = st.slider("진동", 2.0, 9.5, float(defaults["vibration"]), 0.1)

    with input_col2:
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
    st.dataframe(input_df, use_container_width=True, hide_index=False)

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
            prob_df = pd.DataFrame({
                "class": list(probs.keys()),
                "probability": list(probs.values())
            })
            st.bar_chart(prob_df.set_index("class"))

    st.markdown("---")
    st.subheader("자동 해설")
    for msg in difference_explanation(row_dict, rule_result, ai_result):
        st.write("- " + msg)

    st.markdown("---")
    st.subheader("강의용 설명 포인트")

    if rule_result == "판단못함":
        st.info(
            "이 케이스는 Rule-based가 정의한 조건 바깥에 있으므로 판단을 내리지 못합니다. "
            "AI는 과거 데이터 패턴을 기반으로 판정을 시도합니다."
        )
    elif rule_result == ai_result:
        st.success(
            "이 케이스는 Rule-based와 AI-based가 같은 결론을 내렸습니다. "
            "명확한 상황에서는 Rule-based도 충분히 효과적입니다."
        )
    else:
        st.warning(
            "두 방식의 결과가 다릅니다. "
            "규칙의 단순성과 AI의 패턴 학습 차이를 설명하기 좋은 사례입니다."
        )


# -----------------------------------
# 제조데이터 품질검사 페이지
# -----------------------------------
def show_manufacturing_quality_page():
    st.title("🧪 제조데이터 업로드 & 품질검사")
    st.caption("CSV 파일을 업로드하고 Rule-based와 AI-based 품질검사 결과를 확인합니다.")

    st.markdown("### 1. 제조데이터 업로드")
    st.write("아래 CSV 파일을 업로드해 주세요.")

    uploaded_file = st.file_uploader(
        "CSV 파일 업로드",
        type=["csv"],
        key="manufacturing_quality_upload"
    )

    if uploaded_file is None:
        st.info("품질검사를 진행하려면 CSV 파일을 업로드해 주세요.")
        st.markdown("#### 필요한 컬럼 구조")
        st.code(", ".join(FEATURES))
        return

    try:
        upload_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    is_valid, error_msg = validate_uploaded_dataframe(upload_df)
    if not is_valid:
        st.error(error_msg)
        st.markdown("#### 필요한 컬럼 구조")
        st.code(", ".join(FEATURES))
        return

    st.markdown("### 2. 업로드한 파일 내용")
    st.dataframe(upload_df, use_container_width=True, hide_index=False)

    run_button = st.button(
        "품질검사 실시",
        type="primary",
        use_container_width=False,
        key="run_manufacturing_quality_check"
    )

    if run_button:
        result_df = run_decision_on_dataframe(upload_df)

        st.markdown("---")
        st.markdown("## 3. 품질검사 결과")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Rule-based 결과")
            rule_df = result_df[FEATURES + ["rule_based_result", "rule_reason"]].copy()
            styled_rule_df = rule_df.style.apply(highlight_unknown_row, axis=1)
            st.dataframe(
                styled_rule_df,
                use_container_width=True,
                hide_index=False
            )

        with col2:
            st.subheader("AI-based 결과")
            ai_df = result_df[FEATURES + ["ai_based_result"]].copy()
            st.dataframe(
                ai_df,
                use_container_width=True,
                hide_index=False
            )

        unknown_count = (result_df["rule_based_result"] == "판단못함").sum()
        diff_count = (result_df["same_or_diff"] == "다름").sum()

        st.markdown("---")
        summary_col1, summary_col2, summary_col3 = st.columns(3)

        with summary_col1:
            st.metric("전체 데이터 수", len(result_df))
        with summary_col2:
            st.metric("Rule-based 판단못함", int(unknown_count))
        with summary_col3:
            st.metric("두 방식 결과 다름", int(diff_count))

        if unknown_count > 0:
            st.warning("노란색으로 표시된 행은 Rule-based에서 '판단못함'으로 처리된 케이스입니다.")


# -----------------------------------
# 실행
# -----------------------------------
render_sidebar_navigation()

if st.session_state.selected_page == "intro":
    show_intro_page()
elif st.session_state.selected_page == "test":
    show_test_compare_page()
elif st.session_state.selected_page == "user":
    show_user_input_page()
elif st.session_state.selected_page == "mfg_quality":
    show_manufacturing_quality_page()
else:
    show_intro_page()
