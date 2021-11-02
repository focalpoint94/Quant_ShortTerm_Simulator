"""
analyze_results.py
"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math
import matplotlib.dates as mdates
import FinanceDataReader as fdr
import scipy.stats as stats
import pandas as pd
import dataframe_image as dfi
import os
from pykrx import stock

def _get_duration_num_transactions(yield_list, num_bought_list, num_sold_list):
    """
    :param yield_list: [[날짜, 당일 수익률], ...]
    :param all_transaction_history_list: 거래 내역 리스트
    :return:
    총 거래일, 총 매매횟수
    """
    num_transactions = np.sum(num_bought_list) + np.sum(num_sold_list)
    return len(yield_list), num_transactions

def _get_culmulative_yield_CAGR_MDD_investment_results(asset_list):
    """
    :param asset_list: [[날짜, 당일 총 자산], ...]
    [['20210701', 10500000], ...]
    :return:
    누적 수익률, CAGR, MDD, 투자 원금, 총 손익, 총 자산
    """
    culmulative_yield = asset_list[-1][1] / asset_list[0][1]

    investment_td = datetime.strptime(asset_list[-1][0], "%Y%m%d") - datetime.strptime(asset_list[0][0], "%Y%m%d")
    investment_td_yr = investment_td / timedelta(days=365)
    CAGR = math.pow(culmulative_yield, 1/investment_td_yr) - 1

    MDD = 0
    highest_asset = []
    highest_asset.append(asset_list[0][1])
    for i in range(1, len(asset_list)):
        if asset_list[i][1] >= highest_asset[i-1]:
            highest_asset.append(asset_list[i][1])
        else:
            highest_asset.append(highest_asset[i-1])
    for i in range(len(highest_asset)):
        MDD = max(MDD, (highest_asset[i] - asset_list[i][1]) / highest_asset[i] * 100)

    investment_principal = asset_list[0][1]
    total_assets = asset_list[-1][1]
    total_profit = total_assets - investment_principal

    culmulative_yield = round(culmulative_yield, 2)
    CAGR = round(CAGR, 2)
    MDD = round(MDD, 2)

    return culmulative_yield, CAGR, MDD, investment_principal, total_profit, total_assets

def _get_daily_yield(yield_list):
    """
    :param yield_list: [[날짜, 당일 수익률], ...]
    :return:
    일 수익률 평균, 표준편차
    """
    yield_list = [_yield[1] for _yield in yield_list]
    average = np.mean(yield_list)
    std = np.std(yield_list)
    average = round(average, 2)
    std = round(std, 2)
    return average, std

def _get_recent_yield(yield_list):
    """
    :param yield_list: [[날짜, 당일 수익률], ...]
    :return:
    최근 거래일 수익률, 최근 1주 수익률, 최근 1개월 수익률, 최근 3개월 수익률, 최근 6개월 수익률, 최근 1년 수익률
    """
    last_date = datetime.strptime(yield_list[-1][0], "%Y%m%d")
    week_ago = datetime.strftime(last_date - timedelta(days=7), "%Y%m%d")
    month_ago = datetime.strftime(last_date - timedelta(days=30), "%Y%m%d")
    three_months_ago = datetime.strftime(last_date - timedelta(days=91), "%Y%m%d")
    half_year_ago = datetime.strftime(last_date - timedelta(days=182), "%Y%m%d")
    year_ago = datetime.strftime(last_date - timedelta(days=365), "%Y%m%d")

    recent_date_yield = yield_list[-1][1] / 100

    recent_week_yield = 1
    for _yield in yield_list:
        if _yield[0] >= week_ago:
            recent_week_yield *= (1 + _yield[1]/100)

    recent_month_yield = 1
    for _yield in yield_list:
        if _yield[0] >= month_ago:
            recent_month_yield *= (1 + _yield[1]/100)

    recent_three_months_yield = 1
    for _yield in yield_list:
        if _yield[0] >= three_months_ago:
            recent_three_months_yield *= (1 + _yield[1]/100)

    recent_half_year_yield = 1
    for _yield in yield_list:
        if _yield[0] >= half_year_ago:
            recent_half_year_yield *= (1 + _yield[1]/100)

    recent_year_yield = 1
    for _yield in yield_list:
        if _yield[0] >= year_ago:
            recent_year_yield *= (1 + _yield[1]/100)

    recent_date_yield = round(recent_date_yield, 2)
    recent_week_yield = round(recent_week_yield, 2)
    recent_month_yield = round(recent_month_yield, 2)
    recent_three_months_yield = round(recent_three_months_yield, 2)
    recent_half_year_yield = round(recent_half_year_yield, 2)
    recent_year_yield = round(recent_year_yield, 2)

    return recent_date_yield, recent_week_yield, recent_month_yield, recent_three_months_yield, recent_half_year_yield, recent_year_yield

def _get_win_rate_average_holding_days_average_yield(sold_stock_list):
    """
    :param sold_stock_list: 실현 종목 수익률 리스트
    [[코드, 수익률, 손익, 보유일수, 실현일], ...]
    :return:
    승률, 평균 보유일, 수익 종목 평균 수익률, 손실 종목 평균 수익률
    """
    num_stocks = len(sold_stock_list)

    num_win = 0
    for item in sold_stock_list:
        if item[1] >= 0:
            num_win += 1
    win_rate = num_win / num_stocks * 100

    holding_days_sum = 0
    for item in sold_stock_list:
        holding_days_sum += item[3]
    average_holding_days = holding_days_sum / num_stocks

    positive_yield = []
    negative_yield = []
    for item in sold_stock_list:
        if item[1] >= 0:
            positive_yield.append(item[1])
        else:
            negative_yield.append(item[1])
    average_positive_yield = np.mean(positive_yield)
    average_negative_yield = np.mean(negative_yield)

    win_rate = round(win_rate, 2)
    average_holding_days = round(average_holding_days, 2)
    average_positive_yield = round(average_positive_yield, 2)
    average_negative_yield = round(average_negative_yield, 2)

    return win_rate, average_holding_days, average_positive_yield, average_negative_yield

def _get_kospi_kosdaq_correlation(yield_list, save_dir):
    """
    :param yield_list: [[날짜, 당일 수익률], ...]
    :param save_dir: 저장 경로
    :return:
    코스피 상관 계수, 코스닥 상관 계수
    """
    if len(yield_list) <= 30:
        return 0, 0

    # 일자별 수익률
    _yield_list = [_yield[1] for _yield in yield_list]

    # 날짜
    date_list = [item[0] for item in yield_list]
    for i in range(len(date_list)):
        date_list[i] = datetime.strptime(date_list[i], "%Y%m%d")

    # KOSPI
    kospi_yield_list = []
    start_date = datetime.strftime(date_list[0], "%Y-%m-%d")
    kospi_df = fdr.DataReader('KS11', start_date)
    for date in date_list:
        s_date = datetime.strftime(date, "%Y%m%d")
        kospi_yield_list.append([s_date, kospi_df.loc[date]['Change']]*100)
    _kospi_yield_list = [item[1] for item in kospi_yield_list]

    # KOSDAQ
    kosdaq_yield_list = []
    start_date = datetime.strftime(date_list[0], "%Y-%m-%d")
    kosdaq_df = fdr.DataReader('KQ11', start_date)
    for date in date_list:
        s_date = datetime.strftime(date, "%Y%m%d")
        kosdaq_yield_list.append([s_date, kosdaq_df.loc[date]['Change']]*100)
    _kosdaq_yield_list = [item[1] for item in kosdaq_yield_list]

    kospi_corr, kospi_pval = stats.pearsonr(_yield_list, _kospi_yield_list)
    kosdaq_corr, kosdaq_pval = stats.pearsonr(_yield_list, _kosdaq_yield_list)
    kospi_corr = round(kospi_corr, 2)
    kosdaq_corr = round(kosdaq_corr, 2)

    figure = plt.figure(1, figsize=(9, 9))
    plt.rc('axes', unicode_minus=False)
    plt.scatter(_kospi_yield_list, _yield_list, alpha=0.5)
    plt.title('코스피 수익률 - 전략 수익률 Scatter Plot')
    plt.xlabel('코스피 수익률')
    plt.ylabel('전략 수익률')
    figure.savefig(fname=save_dir + '코스피 수익률 - 전략 수익률 Scatter Plot', dpi=300)
    plt.close()

    figure = plt.figure(1, figsize=(9, 9))
    plt.rc('axes', unicode_minus=False)
    plt.scatter(_kosdaq_yield_list, _yield_list, alpha=0.5)
    plt.title('코스닥 수익률 - 전략 수익률 Scatter Plot')
    plt.xlabel('코스닥 수익률')
    plt.ylabel('전략 수익률')
    figure.savefig(fname=save_dir + '코스닥 수익률 - 전략 수익률 Scatter Plot', dpi=300)
    plt.close()

    return kospi_corr, kosdaq_corr

def _get_yield_plots(yield_list, save_dir):
    """
    :param yield_list: [[날짜, 당일 수익률], ...]
    :param save_dir: 저장 경로
    :return:
    일 평균 수익률 분포, 누적 수익률 그래프, 월간 수익률 그래프
    """
    """
    Handle Data
    """
    # 일자별 수익률
    _yield_list = [_yield[1] for _yield in yield_list]

    # 날짜
    date_list = [item[0] for item in yield_list]
    for i in range(len(date_list)):
        date_list[i] = datetime.strptime(date_list[i], "%Y%m%d")

    """
    일 평균 수익률 분포
    """
    figure = plt.figure(1, figsize=(9, 9))
    plt.hist(_yield_list, bins=100, color='black', edgecolor='black', linewidth=1.2)
    plt.xlabel('일 평균 수익률')
    plt.rc('axes', unicode_minus=False)
    plt.xticks(np.arange(1.1*min(_yield_list)//1*1, 1.1*np.max(_yield_list)//1*1, 1.0))
    figure.savefig(fname=save_dir + '일 평균 수익률', dpi=300)
    plt.close()

    """
    누적 수익률 그래프
    """
    # 누적 수익률
    culmulative_yield_list = []
    culmulative_yield = 1
    for i, _yield in enumerate(_yield_list):
        culmulative_yield = culmulative_yield * (1 + _yield/100)
        culmulative_yield_list.append(culmulative_yield)

    # KOSPI
    kospi_index_list = []
    start_date = datetime.strftime(date_list[0], "%Y-%m-%d")
    kospi_df = fdr.DataReader('KS11', start_date)
    for date in date_list:
        s_date = datetime.strftime(date, "%Y%m%d")
        kospi_index_list.append([s_date, kospi_df.loc[date]['Close']])
    kospi_base = kospi_index_list[0][1]
    for i in range(len(kospi_index_list)):
        kospi_index_list[i][1] = kospi_index_list[i][1] / kospi_base
    _kospi_index_list = [item[1] for item in kospi_index_list]

    # KOSDAQ
    kosdaq_index_list = []
    start_date = datetime.strftime(date_list[0], "%Y-%m-%d")
    kosdaq_df = fdr.DataReader('KQ11', start_date)
    for date in date_list:
        s_date = datetime.strftime(date, "%Y%m%d")
        kosdaq_index_list.append([s_date, kosdaq_df.loc[date]['Close']])
    kosdaq_base = kosdaq_index_list[0][1]
    for i in range(len(kosdaq_index_list)):
        kosdaq_index_list[i][1] = kosdaq_index_list[i][1] / kosdaq_base
    _kosdaq_index_list = [item[1] for item in kosdaq_index_list]

    if len(yield_list) >= 2:
        figure = plt.figure(1, figsize=(9, 9))
        p1 = figure.add_subplot()
        p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.plot(date_list, culmulative_yield_list, c='r', label='전략 수익률')
        plt.plot(date_list, _kospi_index_list, c='g', label='KOSPI')
        plt.plot(date_list, _kosdaq_index_list, c='b', label='KOSDAQ')
        plt.legend(loc='best')
        figure.savefig(fname=save_dir + '누적 수익률 그래프', dpi=300)
        plt.close()

    """
    월간 수익률 그래프
    """
    st = datetime.strftime(date_list[0], "%y%m")
    ed = datetime.strftime(date_list[-1], "%y%m")
    start_year = int(st[:2])
    end_year = int(ed[:2])
    start_month = int(st[2:])
    end_month = int(ed[2:])
    if start_year == end_year:
        num_bins = end_month - start_month + 1
    else:
        num_bins = (end_year - start_year - 1) * 12 + (12 - start_month + 1) + end_month
    labels = []
    label = st
    labels.append(label)
    for i in range(num_bins-1):
        if int(label[2:]) == 12:
            label = str(int(label[:2])+1) + "01"
        else:
            label = label[:2] + f"{int(label[2:])+1:02d}"
        labels.append(label)

    monthly_yield_list = [[] for _ in range(num_bins)]
    for item in yield_list:
        label = item[0][2:6]
        to_idx = labels.index(label)
        monthly_yield_list[to_idx].append(item[1])
    new_monthly_yield_list = []
    for i in range(len(monthly_yield_list)):
        new_monthly_yield = 1
        for j in range(len(monthly_yield_list[i])):
            new_monthly_yield *= (1 + monthly_yield_list[i][j]/100)
        new_monthly_yield_list.append(new_monthly_yield - 1)
    monthly_yield_list = new_monthly_yield_list

    new_index_list = []
    for i in range(len(kospi_df)):
        new_index_list.append(datetime.strftime(kospi_df.index[i], "%Y%m%d"))
    kospi_df.index = new_index_list
    new_index_list = []
    for i in range(len(kosdaq_df)):
        new_index_list.append(datetime.strftime(kosdaq_df.index[i], "%Y%m%d"))
    kosdaq_df.index = new_index_list

    monthly_kospi_yield_list = []
    monthly_kosdaq_yield_list = []

    for i in range(num_bins):
        label = labels[i]
        month_idx = []
        for index in kospi_df.index:
            if index[2:6] == label:
                month_idx.append(index)
        start_price = kospi_df.loc[month_idx[0]]['Open']
        end_price = kospi_df.loc[month_idx[-1]]['Close']
        _yield = (end_price - start_price) / start_price
        monthly_kospi_yield_list.append(_yield)
    for i in range(num_bins):
        label = labels[i]
        month_idx = []
        for index in kosdaq_df.index:
            if index[2:6] == label:
                month_idx.append(index)
        start_price = kosdaq_df.loc[month_idx[0]]['Open']
        end_price = kosdaq_df.loc[month_idx[-1]]['Close']
        _yield = (end_price - start_price) / start_price
        monthly_kosdaq_yield_list.append(_yield)

    x = np.arange(len(labels))
    width = 0.15
    figure, ax = plt.subplots()
    rects1 = ax.bar(x - 0.35, monthly_yield_list, width, color='r', label='전략 수익률')
    rects2 = ax.bar(x, monthly_kospi_yield_list, width, color='g', label='KOSPI')
    rects3 = ax.bar(x + 0.35, monthly_kosdaq_yield_list, width, color='b', label='KOSDAQ')
    ax.set_xlabel('기간')
    ax.set_ylabel('Yield')
    ax.set_title('월간 수익률 차트')
    ax.set_xticks(x)
    plt.xticks(rotation=45)
    ax.set_xticklabels(labels)
    ax.legend()
    figure.tight_layout()
    figure.savefig(fname=save_dir + '월간 수익률 그래프', dpi=300)
    plt.close()

def _get_daily_transaction_info(yield_list, num_bought_list, num_sold_list, num_hold_list, save_dir):
    """
    :param yield_list: [[날짜, 당일 수익률], ...]
    :param num_bought_list: 매수 종목수
    :param num_sold_list: 매도 종목수
    :param num_hold_list: 보유 종목수
    :param save_dir: 저장 경로
    :return:
    일단위 df
    """
    # 일자별 수익률
    _yield_list = [_yield[1] for _yield in yield_list]

    # 날짜
    date_list = [item[0] for item in yield_list]

    # 누적 수익률
    culmulative_yield_list = []
    culmulative_yield = 1
    for i, _yield in enumerate(_yield_list):
        culmulative_yield = culmulative_yield * (1 + _yield/100)
        culmulative_yield_list.append(culmulative_yield)

    data = {'날짜': date_list, '매수 종목수': num_bought_list, '매도 종목수': num_sold_list,
            '보유 종목수': num_hold_list, '일일 수익률': _yield_list, '누적 수익률': culmulative_yield_list}
    df = pd.DataFrame(data=data)
    writer = pd.ExcelWriter(save_dir + '일단위 데이터.xlsx', engine='xlsxwriter')
    df.to_excel(writer)
    writer.close()

def _get_monthly_yield(yield_list, sold_stock_list, save_dir):
    """
    :param yield_list: [[날짜, 당일 수익률], ...]
    :param sold_stock_list: 실현 종목 수익률 리스트
    [[코드, 수익률, 손익, 보유일수, 실현일], ...]
    :param save_dir: 저장 경로
    :return:
    월별 수익률 dataframe
    """
    # 날짜
    date_list = [item[0] for item in yield_list]
    for i in range(len(date_list)):
        date_list[i] = datetime.strptime(date_list[i], "%Y%m%d")

    # Load Index Data
    start_date = datetime.strftime(date_list[0], "%Y-%m-%d")
    kospi_df = fdr.DataReader('KS11', start_date)
    kosdaq_df = fdr.DataReader('KQ11', start_date)

    st = datetime.strftime(date_list[0], "%y%m")
    ed = datetime.strftime(date_list[-1], "%y%m")
    start_year = int(st[:2])
    end_year = int(ed[:2])
    start_month = int(st[2:])
    end_month = int(ed[2:])
    if start_year == end_year:
        num_bins = end_month - start_month + 1
    else:
        num_bins = (end_year - start_year - 1) * 12 + (12 - start_month + 1) + end_month
    labels = []
    label = st
    labels.append(label)
    for i in range(num_bins-1):
        if int(label[2:]) == 12:
            label = str(int(label[:2])+1) + "01"
        else:
            label = label[:2] + f"{int(label[2:])+1:02d}"
        labels.append(label)

    monthly_yield_list = [[] for _ in range(num_bins)]
    for item in yield_list:
        label = item[0][2:6]
        to_idx = labels.index(label)
        monthly_yield_list[to_idx].append(item[1])

    # 월간 일평균 수익률
    month_daily_yield_list = [np.mean(item) for item in monthly_yield_list]

    # 월간 수익률
    monthly_culmulative_yield_list = []
    for i, yields in enumerate(monthly_yield_list):
        monthly_culmulative_yield = 1
        for _yield in yields:
            monthly_culmulative_yield *= (1 +_yield/100)
        monthly_culmulative_yield_list.append(monthly_culmulative_yield)

    # 월간 코스피 / 코스닥 수익률
    monthly_kospi_yield_list = []
    monthly_kosdaq_yield_list = []
    new_index_list = []
    for i in range(len(kospi_df)):
        new_index_list.append(datetime.strftime(kospi_df.index[i], "%Y%m%d"))
    kospi_df.index = new_index_list
    new_index_list = []
    for i in range(len(kosdaq_df)):
        new_index_list.append(datetime.strftime(kosdaq_df.index[i], "%Y%m%d"))
    kosdaq_df.index = new_index_list
    for i in range(num_bins):
        label = labels[i]
        month_idx = []
        for index in kospi_df.index:
            if index[2:6] == label:
                month_idx.append(index)
        start_price = kospi_df.loc[month_idx[0]]['Open']
        end_price = kospi_df.loc[month_idx[-1]]['Close']
        _yield = end_price / start_price
        monthly_kospi_yield_list.append(_yield)
    for i in range(num_bins):
        label = labels[i]
        month_idx = []
        for index in kosdaq_df.index:
            if index[2:6] == label:
                month_idx.append(index)
        start_price = kosdaq_df.loc[month_idx[0]]['Open']
        end_price = kosdaq_df.loc[month_idx[-1]]['Close']
        _yield = end_price / start_price
        monthly_kosdaq_yield_list.append(_yield)

    monthly_sold_stock_list = [[] for _ in range(num_bins)]
    for item in sold_stock_list:
        label = item[4][2:6]
        to_idx = labels.index(label)
        monthly_sold_stock_list[to_idx].append(item)

    monthly_average_holding_days = [np.mean([item[3] for item in monthly_sold_stock]) for monthly_sold_stock in monthly_sold_stock_list]
    monthly_num_profit_stock = [len([item for item in monthly_sold_stock if item[1] >= 0]) for monthly_sold_stock in monthly_sold_stock_list]
    monthly_num_loss_stock = [len([item for item in monthly_sold_stock if item[1] < 0]) for monthly_sold_stock in monthly_sold_stock_list]
    monthly_average_positive_yield = [np.mean([item[1] for item in monthly_sold_stock if item[1] >= 0]) for monthly_sold_stock in monthly_sold_stock_list]
    monthly_average_negative_yield = [np.mean([item[1] for item in monthly_sold_stock if item[1] < 0]) for monthly_sold_stock in monthly_sold_stock_list]
    monthly_total_profit = [np.sum([item[2] for item in monthly_sold_stock]) for monthly_sold_stock in monthly_sold_stock_list]
    monthly_total_profit = [str(value) for value in monthly_total_profit]

    data = {'기간': labels, '월수익률': monthly_culmulative_yield_list, '일평균수익률': month_daily_yield_list,
            '코스피수익률': monthly_kospi_yield_list, '코스닥수익률': monthly_kosdaq_yield_list,
            '평균보유일': monthly_average_holding_days, '수익종목': monthly_num_profit_stock,
            '손실종목': monthly_num_loss_stock, '평균수익': monthly_average_positive_yield,
            '평균손실': monthly_average_negative_yield, '총손익': monthly_total_profit}
    df = pd.DataFrame(data=data)
    fname = save_dir + '월별 데이터.png'
    dfi.export(df, fname)

def _get_individual_yield(all_sold_stock_list, is_stock, save_dir, reference='수익률', ascending=False):
    """
    :param all_sold_stock_list: 모든 실현 종목 리스트 (class balance - sold_stock_list)
    :param reference: '코드', '종목명', '매입가', '매도가', '수량', '수익률', '손익', '보유일수'
    :return:
    """
    code_list = []
    name_list = []
    b_price_list = []
    s_price_list = []
    quantity_list = []
    _yield_list = []
    profit_list = []
    num_days_list = []
    for i in range(len(all_sold_stock_list)):
        for sold_stock in all_sold_stock_list[i]:
            code = sold_stock['코드']
            name = stock.get_market_ticker_name(code) if is_stock else stock.get_etf_ticker_name(code)
            b_price = sold_stock['매입가']
            s_price = sold_stock['매도가']
            quantity = sold_stock['수량']
            _yield = sold_stock['수익률']
            profit = sold_stock['손익']
            num_days = sold_stock['보유일수']
            code_list.append(code)
            name_list.append(name)
            b_price_list.append(b_price)
            s_price_list.append(s_price)
            quantity_list.append(quantity)
            _yield_list.append(_yield)
            profit_list.append(profit)
            num_days_list.append(num_days)
    data = {'코드': code_list, '종목': name_list, '매입가': b_price_list, '매도가': s_price_list,
            '수량': quantity_list, '수익률': _yield_list, '손익': profit_list, '보유일수': num_days_list}
    df = pd.DataFrame(data=data)
    df = df.sort_values(by=reference, ascending=ascending)
    fname = save_dir + reference + '_오름차순.xlsx' if ascending else save_dir + reference + '_내림차순.xlsx'
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')
    df.to_excel(writer)
    writer.close()

def _get_transaction_short_frequency_df(code_list, is_stock, save_dir):
    code_list.sort()
    code_list.append('')

    df_code_list = []
    df_name_list = []
    df_freq_list = []

    prev_code = code_list[0]
    prev_idx = 0
    for idx in range(1, len(code_list)):
        code = code_list[idx]
        if code == prev_code:
            continue
        else:
            freq = idx - prev_idx
            df_code_list.append(prev_code)
            df_freq_list.append(freq)
            prev_code = code
            prev_idx = idx

    for code in df_code_list:
        name = stock.get_market_ticker_name(code) if is_stock else stock.get_etf_ticker_name(code)
        df_name_list.append(name)

    data = {'코드': df_code_list, '종목': df_name_list, '거래량 부족 횟수': df_freq_list}
    df = pd.DataFrame(data=data)
    df = df.sort_values(by='거래량 부족 횟수', ascending=False)
    fname = save_dir + '거래량 부족 종목 리스트.xlsx'
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')
    df.to_excel(writer)
    writer.close()

def _save_balance(date, day_stock_list, day_sold_stock_list, is_stock, save_dir):
    """
    :param date: 날짜
    :param day_stock_list: class balance - stock_list type
    :param day_sold_stock_list: class balance - sold_stock_list type
    :param is_stock: True(주식), False(ETF)
    :param save_dir: 저장 경로
    :return:
    종목단위 df
    """
    date_dir = save_dir + date + '/'
    if not os.path.isdir(date_dir):
        os.mkdir(date_dir)
    """
    계좌 잔고
    """
    code_list = []
    name_list = []
    price_list = []
    quantity_list = []
    current_price_list = []
    _yield_list = []
    num_days_list = []
    for date_stock in day_stock_list:
        code = date_stock['코드']
        name = stock.get_market_ticker_name(code) if is_stock else stock.get_etf_ticker_name(code)
        price = date_stock['매입가']
        quantity = date_stock['수량']
        current_price = date_stock['현재가']
        _yield = date_stock['수익률']
        num_days = date_stock['보유일수']
        code_list.append(code)
        name_list.append(name)
        price_list.append(price)
        quantity_list.append(quantity)
        current_price_list.append(current_price)
        _yield_list.append(_yield)
        num_days_list.append(num_days)
    data = {'코드': code_list, '종목': name_list, '매입가': price_list, '수량': quantity_list, '현재가': current_price_list,
            '수익률': _yield_list, '보유일수': num_days_list}
    df = pd.DataFrame(data=data)
    fname = date_dir + '계좌 잔고.png'
    dfi.export(df, fname)

    """
    실현 내역
    """
    code_list = []
    name_list = []
    _yield_list = []
    profit_list = []
    num_days_list = []
    for date_sold_stock in day_sold_stock_list:
        code = date_sold_stock['코드']
        name = stock.get_market_ticker_name(code) if is_stock else stock.get_etf_ticker_name(code)
        _yield = date_sold_stock['수익률']
        profit = date_sold_stock['손익']
        num_days = date_sold_stock['보유일수']
        code_list.append(code)
        name_list.append(name)
        _yield_list.append(_yield)
        profit_list.append(profit)
        num_days_list.append(num_days)
    data = {'코드': code_list, '종목': name_list, '수익률': _yield_list, '손익': profit_list, '보유일수': num_days_list}
    df = pd.DataFrame(data=data)
    fname = date_dir + '실현 내역.png'
    dfi.export(df, fname)

def _analyze_results(**result_params):
    """
    :param result_params:
    strategy = result_params['strategy']
    '이격도-단타'
    tax_rate = result_params['tax_rate']
    0.003
    fee_rate = result_params['fee_rate']
    0.000088
    dates_list = result_params['dates_list']
    ['20210701', ...]
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
    :return:
    """
    strategy = result_params['strategy']
    tax_rate = result_params['tax_rate']
    fee_rate = result_params['fee_rate']
    dates_list = result_params['dates_list']
    asset_list = result_params['asset_list']
    yield_list = result_params['yield_list']
    sold_stock_list = result_params['sold_stock_list']
    num_bought_list = result_params['num_bought_list']
    num_sold_list = result_params['num_sold_list']
    num_hold_list = result_params['num_hold_list']
    all_sold_stock_list = result_params['all_sold_stock_list']
    transaction_short_code_list = result_params['transaction_short_code_list']
    is_stock = result_params['is_stock']

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

    # 결과 Text File 생성
    f = open(strategy_dir + 'result.txt', 'w')
    f.write('전략: ' + strategy + ' (세율: ' + str(tax_rate) + ', 수수료율: ' + str(fee_rate) + ')' + '\n')
    f.write('투자기간: ' + str(dates_list[0]) + '~' + str(dates_list[-1]) + '\n')
    f.write('\n')

    investment_duration, num_transactions = \
        _get_duration_num_transactions(yield_list, num_bought_list, num_sold_list)
    f.write('총 거래일: ' + str(investment_duration) + '\n')
    f.write('총 매매횟수: ' + str(num_transactions) + '\n')
    f.write('\n')

    culmulative_yield, CAGR, MDD, investment_principal, total_profit, total_assets = \
        _get_culmulative_yield_CAGR_MDD_investment_results(asset_list)
    f.write('누적 수익률: ' + str(culmulative_yield) + '\n')
    f.write('CAGR: ' + str(CAGR) + '\n')
    f.write('MDD: ' + str(MDD) + '\n')
    f.write('투자 원금: ' + str(investment_principal) + ' ' + '총 손익: ' + str(total_profit) + ' ' + '총 자산: ' + str(total_assets) + '\n')
    f.write('\n')

    average, std = _get_daily_yield(yield_list)
    f.write('일 평균 수익률: ' + str(average) + '\n')
    f.write('일 수익률 표준편차: ' + str(std) + '\n')
    f.write('\n')

    recent_date_yield, recent_week_yield, recent_month_yield, recent_three_months_yield, \
    recent_half_year_yield, recent_year_yield = _get_recent_yield(yield_list)
    f.write('마지막 거래일 수익률: ' + str(recent_date_yield) + '\n')
    f.write('최근 주 수익률: ' + str(recent_week_yield) + '\n')
    f.write('최근 월 수익률: ' + str(recent_month_yield) + '\n')
    f.write('최근 3개월 수익률: ' + str(recent_three_months_yield) + '\n')
    f.write('최근 6개월 수익률: ' + str(recent_half_year_yield) + '\n')
    f.write('최근 1년 수익률: ' + str(recent_year_yield) + '\n')
    f.write('\n')

    win_rate, average_holding_days, average_positive_yield, average_negative_yield = \
        _get_win_rate_average_holding_days_average_yield(sold_stock_list)
    f.write('승률: ' + str(win_rate) + '\n')
    f.write('평균 보유일수: ' + str(average_holding_days) + '\n')
    f.write('수익 종목 평균 수익률: ' + str(average_positive_yield) + '\n')
    f.write('손실 종목 평균 수익률: ' + str(average_negative_yield) + '\n')
    f.write('')

    kospi_corr, kosdaq_corr = _get_kospi_kosdaq_correlation(yield_list, save_dir=graph_dir)
    f.write('코스피 상관계수: ' + str(kospi_corr) + '\n')
    f.write('코스닥 상관계수: ' + str(kosdaq_corr) + '\n')
    f.write('')
    f.close()

    # 그래프 생성
    _get_yield_plots(yield_list, save_dir=graph_dir)

    # DF 생성
    _get_daily_transaction_info(yield_list, num_bought_list, num_sold_list, num_hold_list, save_dir=strategy_dir)
    _get_monthly_yield(yield_list, sold_stock_list, save_dir=strategy_dir)
    _get_individual_yield(all_sold_stock_list, is_stock=is_stock, save_dir=strategy_dir, reference='수익률', ascending=False)
    _get_transaction_short_frequency_df(code_list=transaction_short_code_list, is_stock=is_stock, save_dir=strategy_dir)