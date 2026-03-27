
import streamlit as st

st.set_page_config(page_title="Rule-based vs AI 의사결정 비교", page_icon="🏭", layout="wide")

st.title("🏭 Rule-based vs AI-based 의사결정 비교 실습")
st.markdown("""
이 웹앱은 **규칙 기반 의사결정**과 **AI 기반 의사결정**이 어떻게 다른지 체험하기 위한 교육용 데모입니다.

### 구성
- **페이지 1:** CSV 테스트 데이터를 불러와 Rule-based와 AI-based 결과를 비교
- **페이지 2:** 사용자가 슬라이더로 값을 조정하며 두 방식의 차이를 즉시 확인
""")

st.info("왼쪽 사이드바에서 페이지를 선택하세요.")
