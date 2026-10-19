---
name: ismn-qc-report
description: ismn_daily.py가 만든 ISMN 관측소 일자료 CSV(date_time, latitude, longitude, sm_corrected)를 받아 관측소별 결측·단위·이상값 점검표를 만든다. 일자료를 새로 만들었거나 관측소 집합·기간을 바꾼 뒤, 학습(compute_stats.py, build_ismn_index) 전에 쓴다. 시간 단위 원자료 보정, 격자 자료(ERA5-Land, SMAP 등) 점검, 모델 평가 결과 정리, 값 수정·삭제에는 쓰지 않는다.
---

# ISMN 일자료 점검표

## 규칙
- 값을 고치거나 파일을 지우지 않는다. 플래그만 단다.
- 입력 경로, 점검 기간, 임계값 중 정보가 없으면 추정하지 말고 묻는다.
- 원인을 단정하지 않는다. "센서 고장", "단위 오류"가 아니라 "~ 의심"으로 쓴다.
- 배경과 기준은 references/research.md를 따른다.

## 절차
1. 입력 확인: 디렉터리 경로, 점검 기간(start, end), 임계값(sm-max, flat-days, jump)을 확인한다. 임계값을 사용자가 주지 않았으면 기본값을 쓴다고 알리고 진행 여부를 묻는다.
2. 실행: `python .claude/skills/ismn-qc-report/scripts/check_ismn.py <dir> --start <start> --end <end> --out qc_table.csv`
3. 스크립트 출력(파일 수, 오류 수, 플래그별 개수)을 그대로 옮긴다. 숫자를 다시 계산하거나 반올림을 바꾸지 않는다.
4. 플래그가 있는 관측소만 골라 아래 형식으로 정리한다.

## 출력 형식
1. 요약: 전체 파일 수 / 오류·빈 파일 수 / 플래그별 관측소 수 / 같은 좌표를 공유하는 파일 수
2. 사용한 설정: 경로, 기간, 임계값
3. 플래그 관측소 표: file | lat | lon | first–last | 결측률(%) | sm 범위 | flags
4. 확인 필요 항목: 사람이 판단해야 할 것만 (예: 같은 좌표 파일이 깊이가 다른 센서인지)
