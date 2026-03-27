
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "quality_model.pkl"
TEST_PATH = BASE_DIR / "test_quality_data.csv"

FEATURES = ["temperature", "pressure", "vibration", "process_time", "humidity"]
LABEL_ORDER = ["정상", "주의", "불량"]

SCENARIOS = {
    "습도 영향 케이스": {"temperature": 70.0, "pressure": 53.0, "vibration": 6.0, "process_time": 72.0, "humidity": 74.0},
    "복합 패턴 케이스": {"temperature": 78.0, "pressure": 54.0, "vibration": 6.9, "process_time": 69.0, "humidity": 72.0},
    "임계값 살짝 벗어난 케이스": {"temperature": 82.0, "pressure": 50.0, "vibration": 6.7, "process_time": 75.0, "humidity": 68.0},
    "명확한 정상 케이스": {"temperature": 60.0, "pressure": 40.0, "vibration": 3.2, "process_time": 50.0, "humidity": 45.0},
    "명확한 불량 케이스": {"temperature": 88.0, "pressure": 62.0, "vibration": 8.5, "process_time": 80.0, "humidity": 76.0},
}

def rule_based_decision(row):
    t = row["temperature"]
    p = row["pressure"]
    v = row["vibration"]
    pt = row["process_time"]

    if t >= 82 and p >= 58:
        return "불량", "온도 >= 82 이고 압력 >= 58 이므로 불량"
    elif v >= 8.0:
        return "주의", "진동 >= 8.0 이므로 주의"
    elif t <= 65 and p <= 45 and v <= 4.0 and pt <= 55:
        return "정상", "정상 기준(온도/압력/진동/가공시간)을 모두 만족"
    else:
        return "판단못함", "현재 입력은 정의된 규칙 범위에 없음"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_test_data():
    return pd.read_csv(TEST_PATH)

def predict_ai(row_dict):
    model = load_model()
    X = pd.DataFrame([row_dict])[FEATURES]
    pred = model.predict(X)[0]

    probs = None
    if hasattr(model, "predict_proba"):
        raw = model.predict_proba(X)[0]
        classes = list(model.classes_)
        probs = {cls: float(raw[classes.index(cls)]) for cls in classes}
    return pred, probs

def difference_explanation(row_dict, rule_result, ai_result):
    messages = []

    if rule_result == "판단못함":
        messages.append("Rule-based는 현재 입력 조합에 해당하는 규칙이 없어 판단을 멈췄습니다.")
    if row_dict["humidity"] >= 70 or row_dict["humidity"] <= 30:
        messages.append("현재 케이스는 습도 영향이 큽니다. 하지만 Rule-based 규칙에는 습도 조건이 없습니다.")
    if 74 <= row_dict["temperature"] <= 82 and row_dict["vibration"] >= 6.2:
        messages.append("온도와 진동이 동시에 높아지는 복합 패턴입니다.")
    if row_dict["pressure"] >= 54 and row_dict["process_time"] >= 70:
        messages.append("압력과 가공시간이 함께 높아지는 패턴은 품질 리스크를 높일 수 있습니다.")

    if rule_result == ai_result:
        messages.append("이 케이스는 두 방식이 같은 결론을 내렸습니다. 명확한 영역에서는 Rule-based도 충분히 유효합니다.")
    else:
        messages.append(f"두 방식의 결과가 다릅니다. AI는 학습 데이터의 패턴을 바탕으로 '{ai_result}' 판정을 시도했습니다.")

    return messages

def style_result(result):
    if result == "정상":
        return "✅ 정상"
    elif result == "주의":
        return "🟡 주의"
    elif result == "불량":
        return "🔴 불량"
    return "⚪ 판단못함"
