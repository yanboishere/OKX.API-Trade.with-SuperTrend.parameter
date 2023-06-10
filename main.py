import okx.account_api as account
import okx.futures_api as future
import numpy as np
import talib


class OKXTrader:
    def __init__(self, api_key, secret_key, passphrase):
        # 初始化 API 对象
        self.account_api = account.AccountAPI(api_key, secret_key, passphrase, True)
        self.future_api = future.FutureAPI(api_key, secret_key, passphrase, True)

    def get_historical_klines(self, symbol, interval, limit):
        # 获取历史 K 线数据
        kline_data = self.future_api.get_kline(symbol=symbol, interval=interval, limit=limit)
        klines = np.array(kline_data['data'])
        times = klines[:, 0]
        high_prices = klines[:, 2].astype(float)
        low_prices = klines[:, 3].astype(float)
        close_prices = klines[:, 4].astype(float)
        return times, high_prices, low_prices, close_prices

    def calculate_super_trend(self, close_prices, period, multiplier, upper_bound=0, lower_bound=0, buy_signal=False, sell_signal=False):
        # 计算超级趋势指标
        atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=period)
        up_band = (close_prices[-1] + (multiplier * atr[-1]))
        down_band = (close_prices[-1] - (multiplier * atr[-1]))
        if close_prices[-2] > upper_bound[-1]:
            upper_bound = np.append(upper_bound, max(up_band, upper_bound[-1]))
            lower_bound = np.append(lower_bound, down_band)
            buy_signal = True
        elif close_prices[-2] < lower_bound[-1]:
            upper_bound = np.append(upper_bound, up_band)
            lower_bound = np.append(lower_bound, min(down_band, lower_bound[-1]))
            sell_signal = True
        else:
            upper_bound = np.append(upper_bound, up_band)
            lower_bound = np.append(lower_bound, down_band)
        return upper_bound, lower_bound, buy_signal, sell_signal

    def execute_trade_strategy(self, symbol, quantity, price, buy_signal, sell_signal):
        # 执行交易策略
        if buy_signal:
            order_result = self.future_api.take_order(symbol=symbol, type='1', price=price, size=quantity,
                                                      match_price='0', leverage='20', order_type='0')
            print('买入成功！')
        elif sell_signal:
            order_result = self.future_api.take_order(symbol=symbol, type='2', price=price, size=quantity,
                                                      match_price='0', leverage='20', order_type='0')
            print('卖出成功！')
        else:
            print('没有买卖信号')
        return order_result

    def run_strategy(self, symbol, interval, limit, quantity, stop_loss_pct, period, multiplier):
        # 运行交易策略
        upper_bound = np.array([0])
        lower_bound = np.array([0])
        buy_signal = False
        sell_signal = False
        
        while True:
            try:
                times, high_prices, low_prices, close_prices = self.get_historical_klines(symbol, interval, limit)
                upper_bound, lower_bound, buy_signal, sell_signal = self.calculate_super_trend(close_prices, period, multiplier,
                                                                                              upper_bound, lower_bound, buy_signal, sell_signal)
                last_price = float(self.account_api.get_specific_ticker(product_id=symbol)['last'])
                order_result = self.execute_trade_strategy(symbol, quantity, last_price, buy_signal, sell_signal)
                if order_result['code'] == '0':
                    print(f"订单 {order_result['order_id']} 执行成功！")
                position_data = self.future_api.get_position(symbol)
                if position_data['data']:
                    position_qty = float(position_data['data'][0]['position'])
                    if position_qty > 0 and (last_price / float(position_data['data'][0]['avg_cost'])) - 1 < -stop_loss_pct:
                        self.future_api.close_position(symbol, '2', position_qty)
                        print('触发止损！平多仓')
                    elif position_qty < 0 and (float(position_data['data'][0]['avg_cost']) / last_price) - 1 < -stop_loss_pct:
                        self.future_api.close_position(symbol, '1', abs(position_qty))
                        print('触发止损！平空仓')
                else:
                    print('当前没有仓位')

        except Exception as e:
            print(f'发生错误: {e}')
