import okx.account_api as account
import okx.futures_api as future
import numpy as np
import talib


class OKXTrader:
    def __init__(self, api_key, secret_key, passphrase):
        try:
            # 初始化账户API和期货API
            self.account_api = account.AccountAPI(api_key, secret_key, passphrase, True)
            self.future_api = future.FutureAPI(api_key, secret_key, passphrase, True)
        except Exception as e:
            # 发生错误时打印错误信息并关闭API连接
            print(f'初始化API时发生错误: {e}')
            self.future_api = None
            self.account_api = None

    def __del__(self):
        try:
            # 关闭API连接
            if self.future_api is not None:
                self.future_api.close()
            if self.account_api is not None:
                self.account_api.close()
        except Exception as e:
            # 发生错误时打印错误信息
            print(f'关闭API连接时发生错误: {e}')

    def get_historical_klines(self, symbol, interval, limit):
        times, high_prices, low_prices, close_prices = None, None, None, None
        try:
            # 获取历史K线数据
            kline_data = self.future_api.get_kline(symbol=symbol, interval=interval, limit=limit)

            # 将k线数据转换为numpy数组
            klines = np.array(kline_data['data'])

            # 分离出不同的价格数据
            times = klines[:, 0]
            high_prices = klines[:, 2].astype(float)
            low_prices = klines[:, 3].astype(float)
            close_prices = klines[:, 4].astype(float)

        except Exception as e:
            # 发生错误时打印错误信息
            print(f'获取历史K线数据时发生错误: {e}')

        # 返回不同的价格数据
        return times, high_prices, low_prices, close_prices

    def calculate_super_trend(self, close_prices, period, multiplier, upper_bound=0, lower_bound=0, buy_signal=False,
                              sell_signal=False):
        try:
            # 计算ATR指标
            atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=period)

            # 计算上轨和下轨
            up_band = (close_prices[-1] + (multiplier * atr[-1]))
            down_band = (close_prices[-1] - (multiplier * atr[-1]))

            # 生成买入信号或卖出信号
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

        except Exception as e:
            # 发生错误时打印错误信息
            print(f'计算超级趋势时发生错误: {e}')

        # 返回新的上轨、下轨、买入信号和卖出信号
        return upper_bound, lower_bound, buy_signal, sell_signal

    def execute_trade_strategy(self, symbol, quantity, price, buy_signal, sell_signal, stop_loss_pct, take_profit_pct):
        order_result = None
        try:
            # 如果有买入信号，则执行市价买入订单
            if buy_signal:
                stop_loss_price = price - price * stop_loss_pct
                take_profit_price = price + price * take_profit_pct
                params = {'symbol': symbol, 'type': '1', 'price': price, 'size': quantity,
                          'match_price': '0', 'leverage': '20', 'order_type': '0',
                          'stop_loss': stop_loss_price, 'take_profit': take_profit_price}
                order_result = self.future_api.take_order(**params)
                print('买入成功！')

            # 如果有卖出信号，则执行市价卖出订单
            elif sell_signal:
                stop_loss_price = price + price * stop_loss_pct
take_profit_price = price - price * take_profit_pct
params = {'symbol': symbol, 'type': '2', 'price': price, 'size': quantity,
'match_price': '0', 'leverage': '20', 'order_type': '0',
'stop_loss': stop_loss_price, 'take_profit': take_profit_price}
order_result = self.future_api.take_order(**params)
print('卖出成功！')

    except Exception as e:
        # 发生错误时打印错误信息
        print(f'执行交易策略时发生错误: {e}')

    # 返回订单结果
    return order_result

def run_trading_algorithm(self, symbol, interval, limit, period, multiplier, quantity, stop_loss_pct,
                          take_profit_pct):
    try:
        # 获取历史K线数据
        times, high_prices, low_prices, close_prices = self.get_historical_klines(symbol=symbol, interval=interval,
                                                                                  limit=limit)

        # 计算超级趋势指标
        upper_bound, lower_bound, buy_signal, sell_signal = self.calculate_super_trend(close_prices=close_prices,
                                                                                        period=period,
                                                                                        multiplier=multiplier)

        # 执行交易策略
        if buy_signal or sell_signal:
            latest_price = float(close_prices[-1])
            order_result = self.execute_trade_strategy(symbol=symbol, quantity=quantity, price=latest_price,
                                                        buy_signal=buy_signal, sell_signal=sell_signal,
                                                        stop_loss_pct=stop_loss_pct,
                                                        take_profit_pct=take_profit_pct)
            print(order_result)

    except Exception as e:
        # 发生错误时打印错误信息
        print(f'运行交易算法时发生错误: {e}')
