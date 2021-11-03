"""
simulation.py
"""
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta
import json
import FinanceDataReader as fdr
from transaction import _transaction
from Balance import _Balance
from analyze_results import _analyze_results, _save_balance
import time
import os

"""
Functions
"""
def save_stock_code_list(stock_data_dir):
    """
    :return:
    오늘 기준 상장 기업 리스트
    """
    ref_date = datetime.strftime(datetime.now().date(), "%Y%m%d")
    code_set = set([])
    tickers1 = stock.get_market_ticker_list(ref_date, market="KOSPI")
    code_set.update(tickers1)
    tickers2 = stock.get_market_ticker_list(ref_date, market="KOSDAQ")
    code_set.update(tickers2)
    code_list = list(code_set)

    file_code_list = os.listdir(stock_data_dir)
    for i in range(len(file_code_list)):
        file_code_list[i] = file_code_list[i][1:]

    code_list = [code for code in code_list if code in file_code_list]
    with open('krx_codes.json', 'w') as f:
        json.dump(code_list, f)

def save_ETF_code_list(ETF_data_dir):
    """
    :return:
    오늘 기준 상장 ETF 리스트
    """
    ref_date = datetime.strftime(datetime.now().date(), "%Y%m%d")
    tickers = stock.get_etf_ticker_list(ref_date)

    file_code_list = os.listdir(ETF_data_dir)
    for i in range(len(file_code_list)):
        file_code_list[i] = file_code_list[i][1:]

    tickers = [ticker for ticker in tickers if ticker in file_code_list]
    with open('ETF_codes.json', 'w') as f:
        json.dump(tickers, f)

def get_MAD_and_IBS(code: str, date:str):
    """
    :param code: 종목 코드 (e.g. '005930')
    :param date: 기준 일자 (e.g. '20210602')
    :return:
    이격도 값, IBS 값
    """
    temp = stock.get_market_ohlcv_by_date(datetime.strftime(datetime.strptime(date, "%Y%m%d") - timedelta(days=15), "%Y%m%d"), date, code)
    temp['MA5'] = temp['종가'].rolling(window=5).mean()
    MAD = temp.iloc[-1]['종가'] / temp.iloc[-1]['MA5'] * 100
    IBS = (temp.iloc[-1]['종가'] - temp.iloc[-1]['저가']) / (temp.iloc[-1]['고가'] - temp.iloc[-1]['저가'] + 1e-4)
    return MAD, IBS

def get_ranking(code_list, date: str, MAD_lower_limit=100, MAD_upper_limit=120):
    """
    :param code_list: 후보군 리스트
    :param date: 기준 일자 (e.g. "20210602")
    :param MAD_lower_limit: MAD 하한 (e.g. 100)
    :param MAD_upper_limit: MAD 상한 (e.g. 120)
    :return:
    df
    ['종목 코드', 'MAD', 'IBS', 'MAD순위', 'IBS순위', '종합순위']]
    1) 후보군 리스트 중 MAD 조건을 만족하는 종목 리스트를 추림
    2) 조건1을 만족하는 리스트의 MAD 및 IBS 종합 순위 반환
    * MAD 값 클수록, IBS 작을수록 종합순위 1에 가까움
    """
    c_list = []
    m_list = []
    i_list = []
    for code in code_list:
        MAD, IBS = get_MAD_and_IBS(code, date)
        if MAD > MAD_lower_limit and MAD < MAD_upper_limit:
            c_list.append(code)
            m_list.append(MAD)
            i_list.append(IBS)
    data = {'종목 코드': c_list, 'MAD': m_list, 'IBS': i_list}
    df = pd.DataFrame(data=data)
    df = df.set_index('종목 코드')
    df['MAD순위'] = df['MAD'].rank(ascending=False)
    df['IBS순위'] = df['IBS'].rank(ascending=True)
    df['종합순위'] = (df['MAD순위'] + df['IBS순위']) / 2
    df = df.sort_values(by='종합순위', ascending=True)
    return df

def simulation(**all_params):
    """
    :param all_params:
    <Input Example>
    'strategy': '단타-이격도-최대20개',
    'stock_data_dir': 'C:/Git/Data/수정/minute_Data/',
    'ETF_data_dir': 'C:/Git/Data/수정/ETF_minute_Data/',
    'start_date': '20210716',
    'end_date': '20210729',
    'MAD_lower_limit': 100,
    'MAD_upper_limit': 120,
    'asset': 10000000,
    'max_stock_num': 20,
    'tax_rate': 0.003,
    'fee_rate': 0.000088,
    'is_stock': True,
    '매수 가격 기준': ['지정가', '전일 종가', '-1.5%'],
    '재 매수 허용': False,
    '목표가': '4.5%',
    '손절가': [False, '-10%'],
    '종목 최소 보유일': [False, 0],
    '종목 최대 보유일': [True, 3],
    '조건 부합 시 매도 가격 기준': ['지정가', '전일 종가', '-3%'],
    '보유일 만기 매도 가격 기준': ['지정가', '전일 종가', '-3%'],
    :return:
    """
    """
    Params
    """
    strategy = all_params['strategy']
    stock_data_dir = all_params['stock_data_dir']
    ETF_data_dir = all_params['ETF_data_dir']
    start_date = all_params['start_date']
    end_date = all_params['end_date']
    MAD_lower_limit = all_params['MAD_lower_limit']
    MAD_upper_limit = all_params['MAD_upper_limit']
    asset = all_params['asset']
    max_stock_num = all_params['max_stock_num']
    tax_rate = all_params['tax_rate']
    fee_rate = all_params['fee_rate']
    is_stock = all_params['is_stock']

    data_dir = stock_data_dir if is_stock else ETF_data_dir

    """
    Dates
    """
    while True:
        try:
            dates_df = stock.get_index_ohlcv_by_date(start_date, end_date, "1001")
            break
        except json.decoder.JSONDecodeError:
            pass
    dates_list = dates_df.index.to_list()
    for i, date in enumerate(dates_list):
        dates_list[i] = datetime.strftime(date, "%Y%m%d")

    """
    KOSDAQ
    """
    df_start_date = datetime.strftime(datetime.strptime(start_date, "%Y%m%d") - timedelta(days=20), "%Y%m%d")
    df_start_date = stock.get_nearest_business_day_in_a_week(date=df_start_date, prev=True)
    kosdaq_df = fdr.DataReader('KQ11', df_start_date)
    kosdaq_df = kosdaq_df[['Close']]
    kosdaq_df['MA3'] = kosdaq_df['Close'].rolling(window=3).mean()
    kosdaq_df['MA5'] = kosdaq_df['Close'].rolling(window=5).mean()
    kosdaq_df['MA10'] = kosdaq_df['Close'].rolling(window=10).mean()
    new_index_list = []
    for i in range(len(kosdaq_df)):
        new_index_list.append(datetime.strftime(kosdaq_df.index[i], "%Y%m%d"))
    kosdaq_df.index = new_index_list

    """
    계좌 생성
    """
    balance = _Balance(asset=asset, max_stock_num=max_stock_num, tax_rate=tax_rate, fee_rate=fee_rate)

    """
    Outputs
    """
    asset_list = [[dates_list[0], asset]]
    yield_list = []
    sold_stock_list = []
    num_bought_list = []
    num_sold_list = []
    num_hold_list = []
    all_sold_stock_list = []
    result_params = {
        'strategy': strategy,
        'tax_rate': tax_rate,
        'fee_rate': fee_rate,
        'dates_list': dates_list[1:],
        'asset_list': asset_list,
        'yield_list': yield_list,
        'sold_stock_list': sold_stock_list,
        'num_bought_list': num_bought_list,
        'num_sold_list': num_sold_list,
        'num_hold_list': num_hold_list,
        'all_sold_stock_list': all_sold_stock_list,
    }
    result_dir = './results/'
    if not os.path.isdir(result_dir):
        os.mkdir(result_dir)
    strategy_dir = result_dir + strategy + '/'
    if not os.path.isdir(strategy_dir):
        os.mkdir(strategy_dir)
    graph_dir = strategy_dir + 'graphs/'
    if not os.path.isdir(graph_dir):
        os.mkdir(graph_dir)
    balance_dir = strategy_dir + 'balance/'
    if not os.path.isdir(balance_dir):
        os.mkdir(balance_dir)

    """
    Code List Update
    """
    save_stock_code_list(stock_data_dir=stock_data_dir)
    save_ETF_code_list(ETF_data_dir=ETF_data_dir)

    """
    BackTesting
    """
    for i in range(1, len(dates_list)):
        start_time = time.time()
        """
        전일 데이터 기반으로 후보 종목 리스트 산출
        - Kosdaq Moving Average Condition
        - Volume Condition
        - Moving Average Distance & IBS Condition
        """
        yesterday = dates_list[i - 1]
        today = dates_list[i]

        """
        Kosdaq Moving Average Condition
        """
        buy_flag = False
        if kosdaq_df.loc[yesterday]['Close'] >= kosdaq_df.loc[yesterday]['MA3'] or \
                kosdaq_df.loc[yesterday]['Close'] >= kosdaq_df.loc[yesterday]['MA5'] or \
                kosdaq_df.loc[yesterday]['Close'] >= kosdaq_df.loc[yesterday]['MA10']:
            buy_flag = True
        all_params['buy_flag'] = buy_flag

        """
        청산 Condition
        """
        all_params['sell_all_flag'] = False

        """
        Volume Condition
        """
        while True:
            try:
                temp1 = stock.get_market_ohlcv_by_ticker(yesterday, market="KOSPI")
                temp2 = stock.get_market_ohlcv_by_ticker(yesterday, market='KOSDAQ')
                break
            except json.decoder.JSONDecodeError:
                pass
        all_df = pd.concat([temp1, temp2])
        all_df = all_df.sort_values(by='거래량', ascending=False)
        volume_list = all_df.index.to_list()[:100]

        """
        Moving Average Distance & IBS Condition
        """
        df = get_ranking(code_list=volume_list, date=yesterday, MAD_lower_limit=MAD_lower_limit,
                         MAD_upper_limit=MAD_upper_limit)

        """
        candidate_basket: 후보 종목 리스트 (우선순위 순)
        """
        candidate_basket = df.index.to_list()

        """
        Day-to-Day Transaction
        """
        day_stock_list, day_sold_stock_list, day_transaction_history, asset_change, _yield, asset = \
            _transaction(today, candidate_basket, balance, **all_params)

        """
        :param result_params:
        asset_list = result_params['asset_list']
        [['20210701', 1000], ...]
        yield_list = result_params['yield_list']
        [['20210701', 0.03], ...]
        sold_stock_list = result_params['sold_stock_list']
        [[코드, 수익률, 손익, 보유일수, 실현일], ...]
        num_bought_list = result_params['num_bought_list']
        [3, 4, 5, 6, ...]
        num_sold_list = result_params['num_sold_list']
        [1, 1, 1, ...]
        num_hold_list = result_params['num_hold_list']
        [10, 10, 9, ...]
        all_sold_stock_list = result_params['all_sold_stock_list']
        [[sold_stock_list1], ...]
        """
        asset_list.append([today, asset])
        yield_list.append([today, _yield])
        for sold_stock in day_sold_stock_list:
            new_sold_stock = [sold_stock['코드'], sold_stock['수익률'], sold_stock['손익'],
                              sold_stock['보유일수'], today]
            sold_stock_list.append(new_sold_stock)
        num_bought = 0
        num_sold = 0
        for transaction in day_transaction_history:
            bought_codes = []
            sold_codes = []
            if transaction[0] == '매입' and transaction[3] not in bought_codes:
                num_bought += 1
                bought_codes.append(transaction[3])
            elif transaction[0] == '매도' and transaction[3] not in sold_codes:
                num_sold += 1
                sold_codes.append(transaction[3])
        num_bought_list.append(num_bought)
        num_sold_list.append(num_sold)
        num_hold_list.append(len(day_stock_list))
        all_sold_stock_list.append(day_sold_stock_list)

        # print('=========================================================')
        # print(today)
        # print()
        # print(day_stock_list)
        # print()
        # print(day_sold_stock_list)
        # print()
        # print(day_transaction_history)
        # print()
        # print(asset_change, _yield, asset)
        # print('=========================================================')

        """
        계좌 정보
        """
        _save_balance(today, day_stock_list, day_sold_stock_list, is_stock=is_stock, save_dir=balance_dir)

        print(today + " Simulation 완료 [" + str(round(i/(len(dates_list)-1)*100, 2)) + "%]")
        print("* 소요 시간: " + str(round(time.time() - start_time, 2)) + "초")


    """
    Generate Outputs
    """
    _analyze_results(**result_params)







"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
*** Only need to modify Parameters Below ***
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


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
all_params = test_params.copy()
all_params.update(transaction_params)

"""
Execution
"""
simulation(**all_params)

