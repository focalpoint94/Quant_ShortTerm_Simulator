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

def simulation(**all_params):
    """
    :param all_params:
    <Input Example>
    'strategy': '단타-이격도-최대20개',
    'stock_data_dir': 'C:/Git/Data/수정/minute_Data/',
    'ETF_data_dir': 'C:/Git/Data/수정/ETF_minute_Data/',
    'start_date': '20210716',
    'end_date': '20210729',
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
    transaction_short_code_list = []
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
        'transaction_short_code_list': transaction_short_code_list,
        'is_stock': is_stock,
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
        yesterday = dates_list[i - 1]
        today = dates_list[i]

        """
        매수 Condition
        """
        all_params['buy_flag'] = True

        """
        청산 Condition
        """
        all_params['sell_all_flag'] = False

        """
        candidate_basket: 후보 종목 리스트 (우선순위 순)
        """
        df = pd.read_csv('ETFs.txt')
        code_list = list(df['codes'])
        for j in range(len(code_list)):
            code_list[j] = code_list[j][1:]
        candidate_basket = code_list

        """
        Day-to-Day Transaction
        """
        day_stock_list, day_sold_stock_list, day_transaction_history, asset_change, _yield, asset, day_transaction_short_code_list = \
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
        for transaction_short_code in day_transaction_short_code_list:
            transaction_short_code_list.append(transaction_short_code)

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
    'strategy': 'ETF-VBS-Mixed12-Basket8-Year2',
    'stock_data_dir': 'C:/Git/Data/수정/minute_Data/',
    'ETF_data_dir': 'C:/Git/Data/무수정/ETF_minute_Data/',
    'start_date': '20190801',
    'end_date': '20210731',
    'asset': 10000000,
    'max_stock_num': 8,
    'tax_rate': 0.003,
    'fee_rate': 0.000088,
    'is_stock': False,
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
    '매수 가격 기준': ['변동성 돌파', 0.4],
    '재 매수 허용': False,
    '목표가': '33%',
    '손절가': [False, '-10%'],
    '종목 최소 보유일': [False, 0],
    '종목 최대 보유일': [True, 1],
    '조건 부합 시 매도 가격 기준': ['지정가', '전일 종가', '33%'],
    # '보유일 만기 매도 가격 기준': ['지정가', '피벗 기준선', '0%'],
    '보유일 만기 매도 가격 기준': ['익일 시가'],
    '매수 및 매도 허용 시간 (단위: 분)': 8,
}
all_params = test_params.copy()
all_params.update(transaction_params)

"""
Execution
"""
simulation(**all_params)

