# 模拟盘代码
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
