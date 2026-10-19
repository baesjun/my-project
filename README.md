# 딥러닝 기반 일단위 토양수분 예측

부경대학교 배성준

## 연구 목적
관측 자료를 입력으로 받아 0.25° 격자의 일단위 토양수분을 예측하는 딥러닝 모델을 만든다.
모델 구조는 Aardvark Weather(Allen et al., 2025)의 end-to-end 구조를 참고한다.

## 대상 영역
- 격자 해상도: 0.25°, 일단위
- 영역: 전지구(남극 제외), 위도 60S–90N, 경도 0–360 (0–360 표기)
- 격자 크기: [확인 필요]

## 자료
- 격자 자료: ERA5-Land, MERRA2, ESA-CCI, GLEAM v4.3a, SMAP
- 지점 관측: ISMN(International Soil Moisture Network) 관측소 일자료

### ISMN 일자료 형식
- 파일 1개 = 관측소(센서) 1개, CSV
- 열: `date_time`, `latitude`, `longitude`, `sm_corrected`
- 단위: 체적함수율 m³/m³
- 생성: 시간 자료에서 결측을 빼고, 하루 유효 시간이 8시간 이상인 날만 일평균한다 (`ismn_daily.py`).
- 학습 전 처리: `compute_stats.py`가 ISMN 값 전체로 평균·표준편차를 구해 정규화에 쓴다. `dataset.py`는 경도를 0–360으로 바꿔 날짜별로 묶는다.

## 학습 절차
1. ERA5 자료로 1일 예측 모델 사전학습
2. lead 1부터 lead 10까지 단계별 미세조정. 각 단계는 앞 단계 가중치를 이어받는다.
3. 관측(ISMN) 기반 end-to-end 미세조정

## 데이터 분할
- train 1980–2019 / val 2020–2023 / test 2024–2025 [확인 필요: 서버 코드 기준]

## 평가
- 주 지표: 관측소 기준 35일 anomaly correlation
- 비교 대상: SoMo.ml(O & Orth, 2021), persistence, ERA5-Land
- SoMo.ml은 학습 기간이 평가 기간과 겹치고 nowcast(lag 0)라서, 이 모델과 조건이 다르다. 비교할 때 이 차이를 함께 적는다.

## 용어
- lead: 예측 시점부터 며칠 뒤를 예측하는지 (lead 1 = 다음 날)
- anomaly correlation: 기후값(계절 변동)을 뺀 편차끼리의 상관계수
- persistence: 마지막 관측값이 그대로 유지된다고 보는 기준 예측

## 참고문헌
- Allen, A., Markou, S., Tebbutt, W., et al. (2025). End-to-end data-driven weather prediction. *Nature*. https://doi.org/10.1038/s41586-025-08897-0
- O, S., & Orth, R. (2021). Global soil moisture data derived through machine learning trained with in-situ measurements. *Scientific Data*, 8, 170. https://doi.org/10.1038/s41597-021-00964-1
- Benechehab, A., Thomas, A., Paolo, G., Filippone, M., & Kégl, B. (2024). A multi-step loss function for robust learning of the dynamics in model-based reinforcement learning. arXiv:2402.03146.
