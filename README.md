
# Rule-based vs AI-based 의사결정 비교 실습

## 1. 데이터 생성
```bash
python generate_data.py
```

## 2. 모델 학습 및 저장
```bash
python train_model.py
```

## 3. Streamlit 실행
```bash
streamlit run app.py
```

## 파일 구성
- `generate_data.py`: 학습용 / 테스트용 CSV 생성
- `train_model.py`: RandomForest 모델 학습 및 저장
- `quality_model.pkl`: 저장된 모델 파일
- `app.py`: 메인 홈
- `pages/1_CSV_비교.py`: 테스트 CSV 기반 비교 페이지
- `pages/2_직접_입력_비교.py`: 슬라이더 기반 실시간 비교 페이지
- `utils.py`: 공통 함수 모음

## 교육 의도
- Rule-based는 사람이 정의한 규칙만 적용
- 규칙에 없는 조합은 `판단못함`
- AI-based는 학습 데이터의 패턴을 바탕으로 판정 시도
- AI가 무조건 더 낫다는 메시지가 아니라, **규칙 기반을 보완하는 역할**을 체험하도록 설계
