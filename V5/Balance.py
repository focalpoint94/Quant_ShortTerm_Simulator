"""
Balanace.py
"""

class _Balance:
    def __init__(self, asset=10000000, max_stock_num=10, tax_rate=0.003, fee_rate=0.000088):
        self.asset = asset
        self.max_stock_num = max_stock_num
        self.stock_num = 0
        self.tax_rate = tax_rate
        self.fee_rate = fee_rate

        """
        자산 = 주식투자금 + 예수금
        * 거래 종료시에만 update -> 당일 수익률 계산
        """
        self.stock_sum = 0
        self.deposit = self.asset

        """
        self.stock_list: 보유 종목 리스트
        {
            '매입날짜': date,
            '매입시각': time,
            '코드': code,
            '매입가': price,
            '수량': quantity,
            '현재가': price,
            '수익률': _yield,
            '주식/ETF': is_stock
            '보유일수': num_days,
        }
        """
        self.stock_list = []

        """
        self.sold_stock_list: 실현 종목 리스트
        {
            '코드': code,
            '매입가': price,
            '매도가': price,
            '수량': quantity,
            '수익률': _yield,
            '손익': profit,
            '보유일수': num_days,
        }
        """
        self.sold_stock_list = []

        """
        self.transaction_history: 거래 내역 리스트
        ['매입/매도', 날짜, 시각, 코드, 가격, 수량, 주식여부]
        """
        self.transaction_history = []

    def _calculate_yield(self, purchase_price, now_price, is_stock):
        if is_stock:
            profit = now_price - purchase_price - purchase_price * self.fee_rate - now_price * (self.tax_rate + self.fee_rate)
            return profit / purchase_price * 100
        else:
            profit = now_price - purchase_price - purchase_price * self.fee_rate - now_price * self.fee_rate
            return profit / purchase_price * 100

    def purchase_stock(self, date, time, code, price, quantity, is_stock):
        # 최대 종목 수 제약
        if self.stock_num == self.max_stock_num:
            return False
        # 매입에 의한 예수금변화
        self.deposit -= price * quantity * (1 + self.fee_rate)
        already_hold = False
        for i, stock in enumerate(self.stock_list):
            if code == stock['코드']:
                already_hold = True
                break
        # 기 보유 종목
        if already_hold:
            stock = self.stock_list[i]
            prev_date = stock['날짜']
            # 분할 매수의 경우
            if date == prev_date:
                prev_price = stock['매입가']
                prev_quantity = stock['수량']
                new_price = (prev_price * prev_quantity + price * quantity) / (prev_quantity + quantity)
                new_quantity = prev_quantity + quantity
                new_yield = self._calculate_yield(new_price, price, is_stock)
                stock['매입가'] = new_price
                stock['수량'] = new_quantity
                stock['현재가'] = price
                stock['수익률'] = new_yield
                # 거래 내역 추가
                self.transaction_history.append(['매입', date, time, code, price, quantity, is_stock])
                return True
            # 재 매입의 경우 (다른 날짜)
            else:
                _yield = self._calculate_yield(price, price, is_stock)
                self.stock_list.append({
                    '날짜': date,
                    '시각': time,
                    '코드': code,
                    '매입가': price,
                    '수량': quantity,
                    '현재가': price,
                    '수익률': _yield,
                    '주식/ETF': is_stock,
                    '보유일수': 0,
                })
                self.stock_num += 1
                # 거래 내역 추가
                self.transaction_history.append(['매입', date, time, code, price, quantity, is_stock])
                return True
        # 신규 종목
        else:
            _yield = self._calculate_yield(price, price, is_stock)
            self.stock_list.append({
                '날짜': date,
                '시각': time,
                '코드': code,
                '매입가': price,
                '수량': quantity,
                '현재가': price,
                '수익률': _yield,
                '주식/ETF': is_stock,
                '보유일수': 0,
            })
            self.stock_num += 1
            # 거래 내역 추가
            self.transaction_history.append(['매입', date, time, code, price, quantity, is_stock])
            return True

    def sell_stock(self, sell_date, sell_time, code, sell_price, sell_quantity, is_stock):
        # 보유 종목 여부 확인
        already_hold = False
        for idx, stock in enumerate(self.stock_list):
            if stock['코드'] == code:
                already_hold = True
                sell_idx = idx
                break
        if not already_hold:
            return False
        # 매도에 의한 예수금 변화
        if is_stock:
            self.deposit += sell_price * sell_quantity - sell_price * sell_quantity * (self.tax_rate + self.fee_rate)
        else:
            self.deposit += sell_price * sell_quantity - sell_price * sell_quantity * self.fee_rate
        # 실현 종목 추가
        sold_stock = self.stock_list[sell_idx]
        bought_price = sold_stock['매입가']
        num_days = sold_stock['보유일수']
        _yield = self._calculate_yield(bought_price, sell_price, is_stock)
        if is_stock:
            profit = sell_quantity * (sell_price - bought_price - bought_price * self.fee_rate - sell_price * (self.tax_rate + self.fee_rate))
        else:
            profit = sell_quantity * (sell_price - bought_price - bought_price * self.fee_rate - sell_price * self.fee_rate)
        self.sold_stock_list.append({
            '코드': code,
            '매입가': bought_price,
            '매도가': sell_price,
            '수량': sell_quantity,
            '수익률': _yield,
            '손익': profit,
            '보유일수': num_days,
        })
        # 거래 내용 추가
        self.transaction_history.append(['매도', sell_date, sell_time, code, sell_price, sell_quantity, is_stock])
        # 보유 종목 업데이트
        # 전량 매도
        if sold_stock['수량'] == sell_quantity:
            del self.stock_list[sell_idx]
            self.stock_num -= 1
        # 부분 매도
        else:
            self.stock_list[sell_idx]['수량'] -= sell_quantity
        return True

    def update_current_price(self, current_price_list):
        for i, stock in enumerate(self.stock_list):
            stock['현재가'] = current_price_list[i]
        for i, stock in enumerate(self.stock_list):
            stock['수익률'] = self._calculate_yield(stock['매입가'], stock['현재가'], stock['주식/ETF'])

    def get_all_stock_code_list(self):
        """
        :return:
        보유 종목 코드 리스트
        """
        code_list = []
        for stock in self.stock_list:
            code_list.append(stock['코드'])
        return code_list

    def get_asset(self):
        return self.asset

    def get_all_stock_list(self):
        return self.stock_list.copy()

    def get_sold_stock_list(self):
        return self.sold_stock_list.copy()

    def get_transaction_history(self):
        return self.transaction_history.copy()

    def close_transaction(self):
        new_stock_sum = 0
        for i, stock in enumerate(self.stock_list):
            quantity = stock['수량']
            cur_price = stock['현재가']
            new_stock_sum += quantity * cur_price
            # 보유일수 += 1
            stock['보유일수'] += 1
        self.stock_sum = new_stock_sum
        new_asset = self.stock_sum + self.deposit
        # 당일 손익
        asset_change = new_asset - self.asset
        # 당일 수익률
        _yield = asset_change / self.asset * 100
        # 자산 업데이트
        self.asset = new_asset
        # 실현 종목 리스트, 거래 내역 리스트 초기화
        self.sold_stock_list = []
        self.transaction_history = []
        
        return asset_change, _yield, new_asset
