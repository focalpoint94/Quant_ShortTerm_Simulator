"""
transaction.py
"""
from pykrx import stock
import json
from datetime import datetime, timedelta
import pandas as pd
import os


def _load_minute_series(candidate_basket, date, data_dir):
    """
    :param code_list: 종목 리스트
    :param date: 일자
    :return:
    timestamp
    minute_data
    [[(종목1, 가격1, volume1), (종목2, 가격2, volume2), ...],
     [(종목1, 가격1, volume1), (종목2, 가격2, volume2), ...],
                                                     ...]
    """
    timestamp = ['0901', '0902', '0903', '0904', '0905', '0906', '0907', '0908', '0909', '0910', '0911', '0912', '0913', '0914', '0915', '0916', '0917', '0918', '0919', '0920', '0921', '0922', '0923', '0924', '0925', '0926', '0927', '0928', '0929', '0930', '0931', '0932', '0933', '0934', '0935', '0936', '0937', '0938', '0939', '0940', '0941', '0942', '0943', '0944', '0945', '0946', '0947', '0948', '0949', '0950', '0951', '0952', '0953', '0954', '0955', '0956', '0957', '0958', '0959', '1000', '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '1010', '1011', '1012', '1013', '1014', '1015', '1016', '1017', '1018', '1019', '1020', '1021', '1022', '1023', '1024', '1025', '1026', '1027', '1028', '1029', '1030', '1031', '1032', '1033', '1034', '1035', '1036', '1037', '1038', '1039', '1040', '1041', '1042', '1043', '1044', '1045', '1046', '1047', '1048', '1049', '1050', '1051', '1052', '1053', '1054', '1055', '1056', '1057', '1058', '1059', '1100', '1101', '1102', '1103', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1115', '1116', '1117', '1118', '1119', '1120', '1121', '1122', '1123', '1124', '1125', '1126', '1127', '1128', '1129', '1130', '1131', '1132', '1133', '1134', '1135', '1136', '1137', '1138', '1139', '1140', '1141', '1142', '1143', '1144', '1145', '1146', '1147', '1148', '1149', '1150', '1151', '1152', '1153', '1154', '1155', '1156', '1157', '1158', '1159', '1200', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1212', '1213', '1214', '1215', '1216', '1217', '1218', '1219', '1220', '1221', '1222', '1223', '1224', '1225', '1226', '1227', '1228', '1229', '1230', '1231', '1232', '1233', '1234', '1235', '1236', '1237', '1238', '1239', '1240', '1241', '1242', '1243', '1244', '1245', '1246', '1247', '1248', '1249', '1250', '1251', '1252', '1253', '1254', '1255', '1256', '1257', '1258', '1259', '1300', '1301', '1302', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1310', '1311', '1312', '1313', '1314', '1315', '1316', '1317', '1318', '1319', '1320', '1321', '1322', '1323', '1324', '1325', '1326', '1327', '1328', '1329', '1330', '1331', '1332', '1333', '1334', '1335', '1336', '1337', '1338', '1339', '1340', '1341', '1342', '1343', '1344', '1345', '1346', '1347', '1348', '1349', '1350', '1351', '1352', '1353', '1354', '1355', '1356', '1357', '1358', '1359', '1400', '1401', '1402', '1403', '1404', '1405', '1406', '1407', '1408', '1409', '1410', '1411', '1412', '1413', '1414', '1415', '1416', '1417', '1418', '1419', '1420', '1421', '1422', '1423', '1424', '1425', '1426', '1427', '1428', '1429', '1430', '1431', '1432', '1433', '1434', '1435', '1436', '1437', '1438', '1439', '1440', '1441', '1442', '1443', '1444', '1445', '1446', '1447', '1448', '1449', '1450', '1451', '1452', '1453', '1454', '1455', '1456', '1457', '1458', '1459', '1500', '1501', '1502', '1503', '1504', '1505', '1506', '1507', '1508', '1509', '1510', '1511', '1512', '1513', '1514', '1515', '1516', '1517', '1518', '1519', '1520', '1530']
    minute_data = [[] for _ in range(len(timestamp))]

    base_dir = data_dir
    df_list = []
    for code in candidate_basket:
        A_code = 'A' + code
        code_dir = base_dir + A_code + '/'
        file_list = os.listdir(code_dir)
        date_list = [date[:-5] for date in file_list]
        if date not in date_list:
            df = pd.DataFrame()
        else:
            file_name = code_dir + date + '.json'
            df = pd.read_json(file_name, orient='table')
        df_list.append(df)

    for i, df in enumerate(df_list):
        code = candidate_basket[i]
        for j in range(len(df)):
            if df.iloc[j]['time'] in timestamp:
                time_idx = timestamp.index(df.iloc[j]['time'])
                minute_data[time_idx].append((code, df.iloc[j]['price'], df.iloc[j]['volumes']))

    return timestamp, minute_data


def exclude_suspended_stocks(date, code_list):
    """
    :param date: 매매 일자
    :param code_list: 종목 리스트
    :return:
    매매 일자 및 전일 거래 정지 종목을 제외한 리스트를 반환
    """
    ref_date = datetime.strftime(datetime.strptime(date, "%Y%m%d") - timedelta(days=10), "%Y%m%d")
    new_code_list = []
    for code in code_list:
        while True:
            try:
                temp = stock.get_market_ohlcv_by_date(ref_date, date, code)
                break
            except:
                pass
        if temp.iloc[-1]['시가'] != 0 and temp.iloc[-2]['시가'] != 0:
            new_code_list.append(code)
    return new_code_list


def get_target_purchase_price(date, code, purchase_param_list):
    """
    :param date: 매매 일자
    :param code: 종목 코드
    :param purchase_param_list: transaction_params['매수 가격 기준']
    :return:
    해당 종목의 매수 가격 조건
    """
    if purchase_param_list[0] == '지정가':
        if purchase_param_list[1] == '전일 종가':
            ref_date = datetime.strftime(datetime.strptime(date, "%Y%m%d") - timedelta(days=10), "%Y%m%d")
            while True:
                try:
                    temp = stock.get_market_ohlcv_by_date(ref_date, date, code)
                    break
                except:
                    pass
            yesterday_close = temp.iloc[-2]['종가']
            target_purchase_price = yesterday_close * (1 + float(purchase_param_list[2][:-1])/100)
    elif purchase_param_list[0] == '변동성 돌파':
        K = purchase_param_list[1]
        ref_date = datetime.strftime(datetime.strptime(date, "%Y%m%d") - timedelta(days=10), "%Y%m%d")
        while True:
            try:
                temp = stock.get_market_ohlcv_by_date(ref_date, date, code)
                break
            except:
                pass
        target_purchase_price = temp.iloc[-1]['시가'] + K * (temp.iloc[-2]['고가'] - temp.iloc[-2]['저가'])
    return target_purchase_price


def get_pivot_values(date, code):
    """
    :param code: 종목 코드 (e.g. "005930")
    :param date: 일자 (e.g. ('20210708')
    :return:
    2차 저항선, 1차 저항선, 피봇, 1차 지지선, 2차 지지선
    """
    ref_date = datetime.strftime(datetime.strptime(date, "%Y%m%d") - timedelta(days=10), "%Y%m%d")
    while True:
        try:
            df = stock.get_market_ohlcv_by_date(ref_date, date, code)
            break
        except:
            pass
    open = df.iloc[-2]['시가']
    high = df.iloc[-2]['고가']
    low = df.iloc[-2]['저가']
    close = df.iloc[-2]['종가']
    pivot = (high + low + close) / 3
    second_resistance = pivot + high - low
    first_resistance = 2 * pivot - low
    first_support = 2 * pivot - high
    second_support = pivot - high + low
    return second_resistance, first_resistance, pivot, first_support, second_support


def get_target_sell_price(date, code, sell_param_list):
    """
    :param date: 매매 일자
    :param code: 종목 코드
    :param sell_param_list: transaction_params['조건 부합 시 매도 가격 기준'/'보유일 만기 매도 가격 기준']
    :return:
    해당 종목의 매도 가격 조건
    """
    if sell_param_list[0] == '지정가':
        if sell_param_list[1] == '전일 종가':
            ref_date = datetime.strftime(datetime.strptime(date, "%Y%m%d") - timedelta(days=10), "%Y%m%d")
            while True:
                try:
                    temp = stock.get_market_ohlcv_by_date(ref_date, date, code)
                    break
                except:
                    pass
            yesterday_close = temp.iloc[-2]['종가']
            target_sell_price = yesterday_close * (1 + float(sell_param_list[2][:-1])/100)
        elif sell_param_list[1] == '피벗 기준선':
            second_resistance, first_resistance, pivot, first_support, second_support = get_pivot_values(date, code)
            target_sell_price = pivot * (1 + float(sell_param_list[2][:-1])/100)
        elif sell_param_list[2] == '피벗 1차지지선':
            second_resistance, first_resistance, pivot, first_support, second_support = get_pivot_values(date, code)
            target_sell_price = first_support * (1 + float(sell_param_list[2][:-1])/100)
        elif sell_param_list[2] == '피벗 2차지지선':
            second_resistance, first_resistance, pivot, first_support, second_support = get_pivot_values(date, code)
            target_sell_price = second_support * (1 + float(sell_param_list[2][:-1])/100)
        elif sell_param_list[2] == '피벗 1차저항선':
            second_resistance, first_resistance, pivot, first_support, second_support = get_pivot_values(date, code)
            target_sell_price = first_resistance * (1 + float(sell_param_list[2][:-1])/100)
        elif sell_param_list[2] == '피벗 2차저항선':
            second_resistance, first_resistance, pivot, first_support, second_support = get_pivot_values(date, code)
            target_sell_price = second_resistance * (1 + float(sell_param_list[2][:-1])/100)
    return target_sell_price


def exclude_no_data_stocks(code_list):
    """
    :param code_list: 종목 코드 리스트
    :return:
    데이터 미 보유 제외 종목 코드 리스트
    """
    with open('krx_codes.json', 'r') as f:
        stock_code_list = json.load(f)
    with open('ETF_codes.json', 'r') as f:
        etf_code_list = json.load(f)
    all_code_list = stock_code_list + etf_code_list
    new_code_list = []
    for code in code_list:
        if code in all_code_list:
            new_code_list.append(code)
    return new_code_list


def get_price_volumes(minute_data, time_idx, code):
    """
    :param minute_data: minute_data
    :param time_idx: idx
    :param code: 종목 코드
    :return:
    해당 종목의 해당 시간대 가격 및 거래량
    * 없는 경우: 0, 0
    """
    for item in minute_data[time_idx]:
        if item[0] == code:
            price = item[1]
            volumes = item[2]
            return price, volumes
    return 0, 0


def _transaction(date, candidate_code_list, balance, **transaction_params):
    """
    :param date: 매매 일자
    :param candidate_list: 후보 종목 리스트
    :param Balance: Balance Class 객체
    :param transaction_params: 
    transaction_params = {
    'data_dir': 'C:/Git/Data/수정/minute_Data/',
    '매수 가격 기준': ['지정가', '전일 종가', '-1.5%'],
    '재 매수 허용': False,
    '목표가': '10%',
    '손절가': [True, '-10%'],
    '종목 최소 보유일': [True, 0],
    '종목 최대 보유일': [True, 3],
    '조건 부합 시 매도 가격 기준': ['지정가', '전일 종가', '-3%'],
    '보유일 만기 매도 가격 기준': ['지정가', '전일 종가', '-3%'],
    'tax_rate': 0.003,
    'fee_rate': 0.000088,
    'buy_flag': True,
    'sell_flag': False,
    'is_stock': True,
    }
    :return: 
    매매 알고리즘 실행 후 하기 값 반환

    Outputs
    day_stock_list: 거래 종료 후 보유 종목 리스트
    day_sold_stock_list: 매매일 실현 종목 리스트
    day_transaction_history: 매매일 거래 내역
    asset_change, asset: 당일 수익률(주식 변동 + 실현 수익, 백분율), 총 자산
    """
    stock_data_dir = transaction_params['stock_data_dir']
    ETF_data_dir = transaction_params['ETF_data_dir']
    purchase_param_list = transaction_params['매수 가격 기준']
    allow_repurchase = transaction_params['재 매수 허용']
    target_margin = transaction_params['목표가']
    use_stop_loss = transaction_params['손절가'][0]
    loss_margin = transaction_params['손절가'][1]
    use_min_hold = transaction_params['종목 최소 보유일'][0]
    min_hold = transaction_params['종목 최소 보유일'][1]
    use_maturity = transaction_params['종목 최대 보유일'][0]
    maturity = transaction_params['종목 최대 보유일'][1]
    sell_param_list = transaction_params['조건 부합 시 매도 가격 기준']
    sell_param_list_after_maturity = transaction_params['보유일 만기 매도 가격 기준']
    tax_rate = transaction_params['tax_rate']
    fee_rate = transaction_params['fee_rate']
    buy_flag = transaction_params['buy_flag']
    sell_all_flag = transaction_params['sell_all_flag']
    is_stock = transaction_params['is_stock']

    data_dir = stock_data_dir if is_stock else ETF_data_dir

    """
    데이터 미 보유 종목 제외
    """
    candidate_code_list = exclude_no_data_stocks(candidate_code_list)
    
    """
    거래 정지 종목 제외 (전날 or 당일 거래 정지 종목)
    """
    candidate_code_list = exclude_suspended_stocks(date, candidate_code_list)
    stock_code_list = exclude_suspended_stocks(date, balance.get_all_stock_code_list())

    """
    재 매수 방지 option
    * 만기 사용 시 재 매수 금지
    """
    if not allow_repurchase or use_maturity:
        candidate_code_list = [code for code in candidate_code_list if code not in stock_code_list]

    """
    Load 매매일 분 데이터
    timestamp
    ['0901', '0902', ..., '1520', '1530']
    minute_data
    [[(종목1, 가격1, volume1), (종목2, 가격2, volume2), ...],
     [(종목1, 가격1, volume1), (종목2, 가격2, volume2), ...],
                                                     ...]
    """
    candidate_and_stock_code_list = candidate_code_list + stock_code_list
    timestamp, minute_data = _load_minute_series(candidate_and_stock_code_list, date, data_dir)

    """
    청산 Condition
    """
    if sell_all_flag:
        stock_list = balance.get_all_stock_list()
        for stock in stock_list:
            quantity = stock['수량']
            # 최대 5분간 매도
            for time_idx in range(5):
                price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=stock['코드'])
                # 거래 없는 경우
                if price == 0 or volumes == 0:
                    continue
                # 거래량 충분한 경우:
                if volumes >= quantity:
                    balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                       sell_price=price, sell_quantity=quantity, is_stock=is_stock)
                    break
                # 거래량 부족한 경우:
                else:
                    balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                       sell_price=price, sell_quantity=volumes, is_stock=is_stock)
                    quantity -= volumes
            if quantity != 0:
                balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                   sell_price=price, sell_quantity=quantity, is_stock=is_stock)

    """
    보유일 만기 매도 가격 기준 option = '익일 시가'
    """
    if use_maturity and sell_param_list_after_maturity[0] == '익일 시가':
        stock_list = balance.get_all_stock_list()
        for stock in stock_list:
            if stock['보유일수'] >= maturity:
                quantity = stock['수량']
                # 최대 5분간 매도
                for time_idx in range(5):
                    price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=stock['코드'])
                    # 거래 없는 경우
                    if price == 0 or volumes == 0:
                        continue
                    # 거래량 충분한 경우:
                    if volumes >= quantity:
                        balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                           sell_price=price, sell_quantity=quantity, is_stock=is_stock)
                        break
                    # 거래량 부족한 경우:
                    else:
                        balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                           sell_price=price, sell_quantity=volumes, is_stock=is_stock)
                        quantity -= volumes
                if quantity != 0:
                    balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                       sell_price=price, sell_quantity=quantity, is_stock=is_stock)

    """
    분 단위 매매 시뮬레이션
    """
    today_bought_code_list = []
    for time_idx in range(len(timestamp)):
        # 매수
        if buy_flag and balance.stock_num < balance.max_stock_num:
            for code in candidate_code_list:
                if code not in today_bought_code_list:
                    target_purchase_price = get_target_purchase_price(date=date, code=code,
                                                                      purchase_param_list=purchase_param_list)
                    target_sell_price = get_target_sell_price(date, code, sell_param_list)
                    price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=code)
                    # 거래 없는 경우
                    if price == 0 or volumes == 0:
                        continue
                    # 매수 조건 만족 시
                    # {매수 시점 가격 >= 조건 부합 시 매도 가격}인 경우 매수 방지 -> 매수 시점에 매도 조건을 만족하는 모순
                    # {매수 가격 <= 조건 부합 시 매도 가격 * (1 - fee_rate - tax_rate) / (1 + fee_rate)}인 경우 매수 -> 매도 가격이 손익 분기 넘도록
                    if price <= target_purchase_price and not price >= target_sell_price:
                        break_even_price = target_sell_price * (1 - fee_rate - tax_rate) / (1 + fee_rate) \
                            if is_stock else target_sell_price * (1 - fee_rate) / (1 + fee_rate)
                        if price <= break_even_price:
                            quantity = (balance.get_asset() / balance.max_stock_num) // price
                            # 최대 5분간 매수
                            bought = False
                            for p_time_idx in range(time_idx, min(time_idx+5, len(timestamp)-1)):
                                price, volumes = get_price_volumes(minute_data=minute_data, time_idx=p_time_idx, code=code)
                                # 거래 없는 경우
                                if price == 0 or volumes == 0:
                                    continue
                                bought = True
                                # 거래량 충분한 경우
                                if volumes >= quantity:
                                    balance.purchase_stock(date=date, time=timestamp[p_time_idx], code=code,
                                                           price=price, quantity=quantity, is_stock=is_stock)
                                    break
                                # 거래량 부족한 경우
                                else:
                                    balance.purchase_stock(date=date, time=timestamp[p_time_idx], code=code,
                                                           price=price, quantity=volumes, is_stock=is_stock)
                                    quantity -= volumes
                            # 당일 재매수 금지
                            if bought:
                                today_bought_code_list.append(code)
                if balance.stock_num >= balance.max_stock_num:
                    break

        # 매도
        stock_list = balance.get_all_stock_list()
        for stock in stock_list:
            # 최소 보유일
            if use_min_hold:
                if stock['보유일수'] < min_hold:
                    continue
            bought_price = stock['매입가']
            # 목표가
            win_price = bought_price * (1 + float(target_margin[:-1])/100)
            # 손절가
            lose_price = bought_price * (1 + float(loss_margin[:-1])/100) if use_stop_loss else 0
            # 만기 옵션 O
            if use_maturity:
                # 만기 이전
                if stock['보유일수'] < maturity:
                    price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=stock['코드'])
                    # 거래 없는 경우
                    if price == 0 or volumes == 0:
                        continue
                    # 익절/손절
                    if price >= win_price or price <= lose_price:
                        quantity = stock['수량']
                        # 최대 5분간 매도
                        for s_time_idx in range(time_idx, min(time_idx+5, len(timestamp)-1)):
                            price, volumes = get_price_volumes(minute_data=minute_data, time_idx=s_time_idx, code=stock['코드'])
                            # 거래 없는 경우
                            if price == 0 or volumes == 0:
                                continue
                            # 거래량 충분한 경우
                            if volumes >= quantity:
                                balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                                   sell_price=price, sell_quantity=quantity, is_stock=is_stock)
                                break
                            # 거래량 부족한 경우
                            else:
                                balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                                   sell_price=price, sell_quantity=volumes, is_stock=is_stock)
                                quantity -= volumes
                        if quantity != 0:
                            balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                               sell_price=price, sell_quantity=quantity, is_stock=is_stock)
                        continue

                    # 조건 부합 시 매도 가격 기준
                    target_sell_price = get_target_sell_price(date, stock['코드'], sell_param_list)
                    if price >= target_sell_price:
                        quantity = stock['수량']
                        # 최대 5분간 매도
                        for s_time_idx in range(time_idx, min(time_idx+5, len(timestamp)-1)):
                            price, volumes = get_price_volumes(minute_data=minute_data, time_idx=s_time_idx, code=stock['코드'])
                            # 거래 없는 경우
                            if price == 0 or volumes == 0:
                                continue
                            # 거래량 충분한 경우
                            if volumes >= quantity:
                                balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'], sell_price=price,
                                                   sell_quantity=quantity, is_stock=is_stock)
                                break
                            # 거래량 부족한 경우
                            else:
                                balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'], sell_price=price,
                                                   sell_quantity=volumes, is_stock=is_stock)
                                quantity -= volumes
                        if quantity != 0:
                            balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'], sell_price=price,
                                               sell_quantity=quantity, is_stock=is_stock)

                # 만기 이후
                else:
                    price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=stock['코드'])
                    # 거래 없는 경우
                    if price == 0 or volumes == 0:
                        continue
                    # 익절/손절
                    if price >= win_price or price <= lose_price:
                        quantity = stock['수량']
                        # 최대 5분간 매도
                        for s_time_idx in range(time_idx, min(time_idx+5, len(timestamp)-1)):
                            price, volumes = get_price_volumes(minute_data=minute_data, time_idx=s_time_idx, code=stock['코드'])
                            # 거래 없는 경우
                            if price == 0 or volumes == 0:
                                continue
                            # 거래량 충분한 경우
                            if volumes >= quantity:
                                balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'], sell_price=price,
                                                   sell_quantity=quantity, is_stock=is_stock)
                                break
                            # 거래량 부족한 경우
                            else:
                                balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'], sell_price=price,
                                                   sell_quantity=volumes, is_stock=is_stock)
                                quantity -= volumes
                        if quantity != 0:
                            balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'], sell_price=price,
                                               sell_quantity=quantity, is_stock=is_stock)
                        continue

                    # 보유일 만기 매도 가격 기준
                    if sell_param_list_after_maturity[0] == '지정가':
                        target_sell_price = get_target_sell_price(date, stock['코드'], sell_param_list_after_maturity)
                        if price >= target_sell_price:
                            quantity = stock['수량']
                            # 최대 5분간 매도
                            for s_time_idx in range(time_idx, min(time_idx + 5, len(timestamp) - 1)):
                                price, volumes = get_price_volumes(minute_data=minute_data, time_idx=s_time_idx,
                                                                   code=stock['코드'])
                                # 거래 없는 경우
                                if price == 0 or volumes == 0:
                                    continue
                                # 거래량 충분한 경우
                                if volumes >= quantity:
                                    balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                                       sell_price=price,
                                                       sell_quantity=quantity, is_stock=is_stock)
                                    break
                                # 거래량 부족한 경우
                                else:
                                    balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                                       sell_price=price,
                                                       sell_quantity=volumes, is_stock=is_stock)
                                    quantity -= volumes
                            if quantity != 0:
                                balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                                   sell_price=price,
                                                   sell_quantity=quantity, is_stock=is_stock)

            # 만기 옵션 X
            else:
                price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=stock['코드'])
                # 거래 없는 경우
                if price == 0 or volumes == 0:
                    continue
                # 익절/손절
                if price >= win_price or price <= lose_price:
                    quantity = stock['수량']
                    # 최대 5분간 매도
                    for s_time_idx in range(time_idx, min(time_idx + 5, len(timestamp) - 1)):
                        price, volumes = get_price_volumes(minute_data=minute_data, time_idx=s_time_idx,
                                                           code=stock['코드'])
                        # 거래 없는 경우
                        if price == 0 or volumes == 0:
                            continue
                        # 거래량 충분한 경우
                        if volumes >= quantity:
                            balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                               sell_price=price,
                                               sell_quantity=quantity, is_stock=is_stock)
                            break
                        # 거래량 부족한 경우
                        else:
                            balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                               sell_price=price,
                                               sell_quantity=volumes, is_stock=is_stock)
                            quantity -= volumes
                    if quantity != 0:
                        balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                           sell_price=price,
                                           sell_quantity=quantity, is_stock=is_stock)
                    continue

                # 조건 부합 시 매도 가격 기준
                target_sell_price = get_target_sell_price(date, stock['코드'], sell_param_list)
                if price >= target_sell_price:
                    quantity = stock['수량']
                    # 최대 5분간 매도
                    for s_time_idx in range(time_idx, min(time_idx + 5, len(timestamp) - 1)):
                        price, volumes = get_price_volumes(minute_data=minute_data, time_idx=s_time_idx,
                                                           code=stock['코드'])
                        # 거래 없는 경우
                        if price == 0 or volumes == 0:
                            continue
                        # 거래량 충분한 경우
                        if volumes >= quantity:
                            balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                               sell_price=price,
                                               sell_quantity=quantity, is_stock=is_stock)
                            break
                        # 거래량 부족한 경우
                        else:
                            balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                               sell_price=price,
                                               sell_quantity=volumes, is_stock=is_stock)
                            quantity -= volumes
                    if quantity != 0:
                        balance.sell_stock(sell_date=date, sell_time=timestamp[s_time_idx], code=stock['코드'],
                                           sell_price=price,
                                           sell_quantity=quantity, is_stock=is_stock)

        # 현재가 업데이트
        current_price_list = []
        stock_list = balance.get_all_stock_list()
        for stock in stock_list:
            prev_price = stock['현재가']
            price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=stock['코드'])
            # 거래 없는 경우
            if price == 0 or volumes == 0:
                current_price_list.append(prev_price)
            else:
                current_price_list.append(price)
        balance.update_current_price(current_price_list)

    """
    보유일 만기 매도 가격 기준 option = '당일 종가'
    """
    if use_maturity and sell_param_list_after_maturity[0] == '당일 종가':
        stock_list = balance.get_all_stock_list()
        for stock in stock_list:
            if stock['보유일수'] >= maturity - 1:
                quantity = stock['수량']
                # 최대 5분간 매도
                for time_idx in range(len(timestamp)-6, len(timestamp)):
                    price, volumes = get_price_volumes(minute_data=minute_data, time_idx=time_idx, code=stock['코드'])
                    # 거래 없는 경우
                    if price == 0 or volumes == 0:
                        continue
                    # 거래량 충분한 경우:
                    if volumes >= quantity:
                        balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                           sell_price=price, sell_quantity=quantity, is_stock=is_stock)
                        break
                    # 거래량 부족한 경우:
                    else:
                        balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                           sell_price=price, sell_quantity=volumes, is_stock=is_stock)
                        quantity -= volumes
                if quantity != 0:
                    balance.sell_stock(sell_date=date, sell_time=timestamp[time_idx], code=stock['코드'],
                                       sell_price=price, sell_quantity=quantity, is_stock=is_stock)

    """
    Outputs
    day_stock_list: 거래 종료 후 보유 종목 리스트
    day_sold_stock_list: 매매일 실현 종목 리스트
    day_transaction_history: 매매일 거래 내역
    asset_change, _yield, asset: 총 자산 변동(주식 변동 + 실현 수익), 당일 수익률(주식 변동 + 실현 수익, 백분율), 총 자산
    거래 종료
    """
    day_stock_list = balance.get_all_stock_list()
    day_sold_stock_list = balance.get_sold_stock_list()
    day_transaction_history = balance.get_transaction_history()
    asset_change, _yield, asset = balance.close_transaction()

    return day_stock_list, day_sold_stock_list, day_transaction_history, asset_change, _yield, asset

