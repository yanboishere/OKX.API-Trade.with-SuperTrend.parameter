import okx.account_api as account
import okx.futures_api as future
import numpy as np
import talib

class OKXTrader:
    def __init__(self, api_key, secret_key, passphrase):
        # 初始化账户API和期货API
        self.account_api = account.AccountAPI(api_key, secret_key, passphrase, True)
        self.future_api = future.FutureAPI(api_key, secret_key, passphrase, True)

    def get_historical_klines(self, symbol, interval, limit):
        try:
            # 获取历史K线数据
            kline_data = self.future_api.get_kline(symbol=symbol, interval=interval, limit=limit)
        except Exception as e:
            # 发生错误时打印错误信息并返回None
            print(f'获取历史K线数据时发生错误: {e}')
            return None, None, None, None
        
        # 将k线数据转换为numpy数组
        klines = np.array(kline_data['data'])
        
        # 分离出不同的价格数据
        times = klines[:, 0]
        high_prices = klines[:, 2].astype(float)
        low_prices = klines[:, 3].astype(float)
        close_prices = klines[:, 4].astype(float)
        
        # 返回不同的价格数据
        return times, high_prices, low_prices, close_prices

    def calculate_super_trend(self, close_prices, period, multiplier, upper_bound=0, lower_bound=0, buy_signal=False, sell_signal=False):
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

    def execute_trade_strategy(self, symbol, quantity, price, buy_signal, sell_signal):
        order_result = None
        try:
            # 如果有买入信号，则执行市价买入订单
            if buy_signal:
                order_result = self.future_api.take_order(symbol=symbol, type='1', price=price, size=quantity,
                                                          match_price='0', leverage='20', order_type='0')
                print('买入成功！')
            
            # 如果有卖出信号，则执行市价卖出订单
            elif sell_signal:
                order_result = self.future_api.take_order(symbol=symbol, type='2', price=price, size=quantity,
                                                          match_price='0', leverage='20', order_type='0')
                print('卖出成功！')
            
            # 如果没有买卖信号，则打印提示信息
            else:
                print('没有买卖信号')
        
        except Exception as e:
            # 发生错误时打印错误信息
            print(f'执行交易策略时发生错误: {e}')
        
        # 返回订单结果
        return order_result

    def run_strategy(self, symbol, interval, limit, quantity, stop_loss_pct, period, multiplier):
        upper_bound = np.array([0])
        lower_bound = np.array([0])
        buy_signal = False
        sell_signal = False
        
        while True:
            try:
                #                # 获取历史K线数据
                times, high_prices, low_prices, close_prices = self.get_historical_klines(symbol, interval, limit)
                
                # 如果没有获取到数据，则跳过此次循环
                if times is None:
                    continue
                    
                # 计算新的上轨、下轨、买入信号和卖出信号
                upper_bound, lower_bound, buy_signal, sell_signal = self.calculate_super_trend(close_prices, period, multiplier,
                                                                                              upper_bound, lower_bound, buy_signal, sell_signal)
                
                # 获取最新的标的资产价格
                last_price = float(self.account_api.get_specific_ticker(product_id=symbol)['last'])
                
                # 执行交易策略
                order_result = self.execute_trade_strategy(symbol, quantity, last_price, buy_signal, sell_signal)
                
                # 如果订单执行成功，则打印信息
                if order_result is not None and order_result['code'] == '0':
                    print(f"订单 {order_result['order_id']} 执行成功！")
                    
                # 检查仓位是否需要止损平仓
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
                    print('当前没有持仓')
            
            except Exception as e:
                # 发生错误时打印错误信息
                print(f'运行策略时发生错误: {e}')

