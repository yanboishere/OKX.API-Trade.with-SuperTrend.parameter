# 导入相关库
import okx.demo_account_api as account  # 使用模拟盘账户API
import okx.demo_futures_api as future   # 使用模拟盘期货API
import time
import numpy as np
import talib


# API密钥信息
api_key = 'YOUR_API_KEY'
secret_key = 'YOUR_SECRET_KEY'
passphrase = 'YOUR_PASSPHRASE'

# 交易参数

"""
`symbol`：您要交易的加密货币对，此处为BTC/USDT。
`interval`：您要使用的K线时间间隔，此处为小时级别的K线。
`quantity`：每次下单的数量，此处为1个BTC。
`stop_loss_pct`：止损比例，当价格下跌到某个比例以下时会触发止损，此处设置为2%。
`take_profit_pct`：止盈比例，当价格上涨到某个比例以上时会触发止盈，此处设置为2%。
`leverage`：杠杆倍数，此处设置为10。
"""

symbol = 'btc-usdt'
interval = '1h'
quantity = 1
stop_loss_pct = 0.02
take_profit_pct = 0.02
leverage = 10


class OKXTrader:
    def __init__(self, api_key, secret_key, passphrase):
        try:
            # 初始化账户API和期货API
            self.account_api = account.AccountAPI(api_key, secret_key, passphrase, True)
            self.future_api = future.FutureAPI(api_key, secret_key, passphrase, True)
            # 初始化历史K线缓存
            self.historical_klines = {}
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
        """
        获取历史K线数据

        :param symbol: 交易对
        :param interval: K线周期
        :param limit: 返回的K线数量
        :return: 历史K线数据的时间、高价、低价和收盘价
        """
        # 检查历史K线缓存是否已经存在该交易对的K线数据
        if symbol in self.historical_klines and interval in self.historical_klines[symbol]:
            times, high_prices, low_prices, close_prices = self.historical_klines[symbol][interval]
        else:
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

                # 缓存K线数据
                if symbol not in self.historical_klines:
                    self.historical_klines[symbol] = {}
                self.historical_klines[symbol][interval] = (times, high_prices, low_prices, close_prices)

            except Exception as e:
                # 发生错误时打印错误信息
                print(f'获取历史K线数据时发生错误: {e}')

        # 返回不同的价格数据
        return times, high_prices, low_prices, close_prices

    def calculate_super_trend(self, close_prices, period, multiplier, upper_bound=0, lower_bound=0, buy_signal=False,
                              sell_signal=False):
        """
        计算超级趋势指标

        :param close_prices: 收盘价序列
        :param period: ATR指标的时间窗口大小
        :param multiplier: 计算上轨和下轨的倍数
        :param upper_bound: 上轨列表，用于生成买入信号
        :param lower_bound: 下轨列表，用于生成卖出信号
        :param buy_signal: 是否生成买入信号
        :param sell_signal: 是否生成卖出信号
        :return: 返回新的上轨、下轨、买入信号和卖出信号
        """
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
        """
        执行交易策略

        :param symbol: 交易对
        :param quantity: 下单数量
        :param price: 下单价格
        :param buy_signal: 是否买入信号
        :param sell_signal: 是否卖出信号
        :param stop_loss_pct: 止损比例
        :param take_profit_pct: 止盈比例
        :return: 订单结果
        """
        order_result = None
        try:
            # 获取当前仓位
            position_data = self.future_api.get_demo_specific_position(symbol=symbol)  # 使用模拟盘API获取持仓信息
            current_qty = int(position_data['holding'][0]['avail_qty'])

            # 根据买入信号和卖出信号执行交易
            if buy_signal and current_qty <= 0:
                # 如果没有持仓，则开多单
                order_data = self.future_api.take_demo_order(symbol=symbol, side='buy', price=price, qty=quantity,
                                                             order_type='limit', match_price=False)  # 使用模拟盘API下单

            elif sell_signal and current_qty >= 0:
                # 如果没有持仓，则开空单
                order_data = self.future_api.take_demo_order(symbol=symbol, side='sell', price=price, qty=quantity,
                                                             order_type='limit', match_price=False)

            elif current_qty > 0 and (stop_loss_pct > 0 or take_profit_pct > 0):
                # 如果持有多头仓位，根据止损和止盈比例设置止损和止盈价格
                last_trade_price = self.future_api.get_last_trade(symbol=symbol)['price']
                stop_loss_price = round(last_trade_price * (1 - stop_loss_pct), 2)
                take_profit_price = round(last_trade_price * (1 + take_profit_pct), 2)

                # 更新止损和止盈价格
                self.future_api.update_demo_order(symbol=symbol, order_id=order_result['order_id'],
                                                   stop_loss=str(stop_loss_price), take_profit=str(take_profit_price))

            elif current_qty < 0 and (stop_loss_pct > 0 or take_profit_pct > 0):
                # 如果持有空头仓位，根据止损和止盈比例设置止损和止盈价格
                last_trade_price = self.future_api.get_last_trade(symbol=symbol)['price']
                stop_loss_price = round(last_trade_price * (1 + stop_loss_pct), 2)
                take_profit_price = round(last_trade_price * (1 - take_profit_pct), 2)

                # 更新止损和止盈价格
                self.future_api.update_demo_order(symbol=symbol, order_id=order_result['order_id'],
                                                   stop_loss=str(stop_loss_price), take_profit=str(take_profit_price))

        except Exception as e:
            # 发生错误时打印错误信息
            print(f'执行交易策略时发生错误: {e}')

        # 返回订单结果
        return order_result

# 实例化OKXTrader类
trader =OKXTrader(api_key, secret_key, passphrase)

# 获取历史K线数据
times, high_prices, low_prices, close_prices = trader.get_historical_klines(symbol, interval, limit=200)

# 计算超级趋势指标
upper_bound, lower_bound, buy_signal, sell_signal = trader.calculate_super_trend(close_prices, period=10, multiplier=3)

# 执行交易策略
if buy_signal or sell_signal:
    # 获取最新成交价作为下单价格
    price = float(trader.future_api.get_last_trade(symbol)['price'])

    # 计算下单数量
    account_data = trader.account_api.get_account_info()
    available_balance = float(account_data['data'][0]['details']['available_balance'])
    quantity = min(quantity, int(available_balance / price))

    # 执行交易策略并打印订单结果
    order_result = trader.execute_trade_strategy(symbol, quantity, price, buy_signal, sell_signal, stop_loss_pct, take_profit_pct)
    print(f'执行交易策略，订单结果: {order_result}')
else:
    print('没有发出买入或卖出信号')