# Quant_ShortTerm_Simulator
단타 시뮬레이터입니다.

# Setup
- 주식 / ETF 분 단위 데이터가 필요합니다. (참고 https://github.com/focalpoint94/Quant_Price_Data_Crawling)

# 실행
simulation.py를 실행합니다.

# 참고 사항
simulation.py는 단타 시뮬레이터입니다.

# 시뮬레이터
시뮬리에터 동작은 아래와 같습니다.
```
1. 상장 기업 / ETF List Update
2. MAD, IBS 등의 지표를 통한 매수 우선순위 리스트 생성
3. 분 단위 데이터를 통한 알고리즘 매매 백테스트
```

# 사용방법
simulation.py 가장 하단의 Parameter를 수정하여 매매 전략을 백테스트할 수 있습니다.
```
"""
* TEST PARAM *
Stock BackTesting Dates AVAILABLE: 20190801 ~ 20210731
ETF BackTesting Dates AVAILABLE: 20190801 ~ 20210731
"""
test_params = {
    'strategy': '단타-이격도-최대20개',
    'stock_data_dir': 'C:/Git/Data/수정/minute_Data/',
    'ETF_data_dir': 'C:/Git/Data/무수정/ETF_minute_Data/',
    'start_date': '20210701',
    'end_date': '20210731',
    'MAD_lower_limit': 100,
    'MAD_upper_limit': 120,
    'asset': 10000000,
    'max_stock_num': 20,
    'tax_rate': 0.003,
    'fee_rate': 0.000088,
    'is_stock': True,
}
"""
* TRANSACTION PARAMS *
매수 가격 기준 options:
['지정가', '전일 종가', '-1.5%']
['변동성 돌파', 0.4]
조건 부합 시 매도 가격 기준 options:
['지정가', '전일 종가'/피벗 기준선'/'피벗 1차지지선'/'피벗 2차지지선'/'피벗 1차저항선'/'피벗 2차저항선', '-3%']
보유일 만기 매도 가격 기준 options:
['지정가', '전일 종가'/피벗 기준선'/'피벗 1차지지선'/'피벗 2차지지선'/'피벗 1차저항선'/'피벗 2차저항선', '-3%']
['당일 종가'/익일 시가']
"""
transaction_params = {
    '매수 가격 기준': ['지정가', '전일 종가', '-1.5%'],
    '재 매수 허용': False,
    '목표가': '4.5%',
    '손절가': [False, '-10%'],
    '종목 최소 보유일': [False, 0],
    '종목 최대 보유일': [True, 3],
    '조건 부합 시 매도 가격 기준': ['지정가', '피벗 기준선', '0%'],
    '보유일 만기 매도 가격 기준': ['지정가', '피벗 기준선', '0%'],
    # '보유일 만기 매도 가격 기준': ['익일 시가'],
}
```

# 실행 결과
실행 결과는 /results/ 하위 폴더에 저장됩니다.

## balance
각 일자별 장 종료시 계좌 잔고 및 당일 실현 내역을 jpeg 파일로 저장합니다.
- 계좌 잔고

![계좌 잔고](https://user-images.githubusercontent.com/55021961/140011866-17fadefc-7113-4cf8-b319-66306631cb3f.png)

- 실현 내역

![실현 내역](https://user-images.githubusercontent.com/55021961/140011868-f48622e7-bb99-4744-a551-d8cd9acdae8f.png)

## graphs
전체 매매 결과를 그래프로 요약합니다.

- 월간 수익률 그래프
<img src = "https://github.com/focalpoint94/Quant_ShortTerm_Simulator/blob/main/V5/results/ETF-VBS-Mixed12-Basket8-Year2/graphs/%EC%9B%94%EA%B0%84%20%EC%88%98%EC%9D%B5%EB%A5%A0%20%EA%B7%B8%EB%9E%98%ED%94%84.png?raw=true" width="50%" height="50%">

- 일 평균 수익률
<img src = "https://github.com/focalpoint94/Quant_ShortTerm_Simulator/blob/main/V5/results/ETF-VBS-Mixed12-Basket8-Year2/graphs/%EC%9D%BC%20%ED%8F%89%EA%B7%A0%20%EC%88%98%EC%9D%B5%EB%A5%A0.png?raw=true" width="50%" height="50%">

- 코스피/매매 수익률 Scatter Plot
<img src = "https://github.com/focalpoint94/Quant_ShortTerm_Simulator/blob/main/V5/results/ETF-VBS-Mixed12-Basket8-Year2/graphs/%EC%BD%94%EC%8A%A4%ED%94%BC%20%EC%88%98%EC%9D%B5%EB%A5%A0%20-%20%EC%A0%84%EB%9E%B5%20%EC%88%98%EC%9D%B5%EB%A5%A0%20Scatter%20Plot.png?raw=true" width="50%" height="50%">

- 누적 수익률
<img src = "https://raw.githubusercontent.com/focalpoint94/Quant_ShortTerm_Simulator/main/V5/results/ETF-VBS-Mixed12-Basket8-Year2/graphs/%EB%88%84%EC%A0%81%20%EC%88%98%EC%9D%B5%EB%A5%A0%20%EA%B7%B8%EB%9E%98%ED%94%84.png" width="50%" height="50%">


## 매매 결과
results.txt에 저장됩니다.
```
전략: ETF-VBS-Mixed12-Basket8-Year2 (세율: 0.003, 수수료율: 8.8e-05)
투자기간: 20190802~20210730

총 거래일: 494
총 매매횟수: 8266

누적 수익률: 1.91
CAGR: 0.38
MDD: 37.21
투자 원금: 10000000 총 손익: 9090902.74175942 총 자산: 19090902.74175942

일 평균 수익률: 0.15
일 수익률 표준편차: 1.99

마지막 거래일 수익률: -0.02
최근 주 수익률: 0.97
최근 월 수익률: 1.0
최근 3개월 수익률: 1.04
최근 6개월 수익률: 1.0
최근 1년 수익률: 1.52

승률: 52.35
평균 보유일수: 1.0
수익 종목 평균 수익률: 2.0
손실 종목 평균 수익률: -1.89
코스피 상관계수: 0.88
코스닥 상관계수: 0.89
```

## 거래량 부족 종목 리스트.xlsx
거래량 부족 종목 리스트의 종목은 말 그대로 거래량이 부족한 종목들입니다.

이 종목들을 포함하여 백테스트할 경우, 실제 매매와 결과가 달라질 가능성이 커집니다.

## 기타
일단위 데이터.xlsx, 월별 데이터.png, 수익률_내림차순.xlsx 파일이 생성됩니다.

