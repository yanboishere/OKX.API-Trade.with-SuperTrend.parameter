# import语句
import okx.account_api as account
import okx.futures_api as future
import numpy as np
import talib

# 认证信息
api_key = 'YOUR_API_KEY'  # 填写您的API Key
secret_key = 'YOUR_SECRET_KEY'  # 填写您的Secret Key
passphrase = 'YOUR_PASSPHRASE'  # 填写您的Passphrase

# 连接到 OKX API
account_api = account.AccountAPI(api_key, secret_key, passphrase, True)
future_api = future.FutureAPI(api_key, secret_key, passphrase, True)

# 超级趋势指标参数设置
period = 14  # 计算周期
multiplier = 3  # 价格变化的乘数
upper_bound = 0  # 上限线初始值
lower_bound = 0  # 下限线初始值
buy_signal = False  # 是否发生买入信号
sell_signal = False  # 是否发生卖出信号

# 获取历史K线数据
def get_historical_klines(symbol, interval, limit):
    kline_data = future_api.get_kline(symbol=symbol, interval=interval, limit=limit)  # 调用OKX API获取K线数据
    klines = np.array(kline_data['data'])  # 将获取的K线数据转换为NumPy数组
    times = klines[:, 0]  # 获取时间戳列
    high_prices = klines[:, 2].astype(float)  # 获取最高价列并将其转换为浮点数类型
    low_prices = klines[:, 3].astype(float)  # 获取最低价列并将其转换为浮点数类型
    close_prices = klines[:, 4].astype(float)  # 获取收盘价列并将其转换为浮点数类型
    return times, high_prices, low_prices, close_prices  # 返回K线数据

# 计算超级趋势指标的上限线和下限线
def calculate_super_trend(close_prices, period, multiplier, upper_bound, lower_bound, buy_signal, sell_signal):
    atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=period)  # 使用TA-Lib库计算平均真实范围(ATR)
    up_band = (close_prices[-1] + (multiplier * atr[-1]))  # 计算上限线值
    down_band = (close_prices[-1] - (multiplier * atr[-1]))  # 计算下限线值
    if close_prices[-2] > upper_bound[-1]:  # 判断是否发生买入信号
        upper_bound = np.append(upper_bound, max(up_band, upper_bound[-1]))  # 更新上限线值
        lower_bound = np.append(lower_bound, down_band)  # 更新下限线值
        buy_signal = True  # 发生买入信号
    elif close_prices[-2] < lower_bound[-1]:  # 判断是否发生卖出信号
        upper_bound = np.append(upper_bound, up_band)  # 更新上限线值
        lower_bound = np.append(lower_bound, min(down_band, lower_bound[-1]))  # 更新下限线值
        sell_signal = True  # 发生卖出信号
    else:
        upper_bound = np.append(upper_bound, up_band)  # 更新上限线值
        lower_bound = np.append(lower_bound, down_band)  # 更新下限线值
    return upper_bound, lower_bound, buy_signal, sell_signal  # 返回计算结果

# 执行交易策略
def execute_trade_strategy(symbol, quantity, price, buy_signal, sell_signal):
    if buy_signal:  # 如果发生买入信号
        order_result = future_api.take_order(symbol=symbol, type='1', price=price, size=quantity,
                                              match_price='0', leverage='20', order_type='0')  # 下多仓订单
        print('买入成功！')
    elif sell_signal:  # 如果发生卖出信号
        order_result = future_api.take_order(symbol=symbol, type='2', price=price, size=quantity,
                                              match_price='0', leverage='20', order_type='0')  # 下空仓订单
        print('卖出成功！')
    else:
        print('没有买卖信号')
    return order_result  # 返回订单结果

# 主程序
if __name__ == '__main__':
    symbol = 'BTC-USD-210625'  # 合约名称
    interval = '15min'  # K线周期
    limit = 200  # 返回K线数据的数量
    quantity = '1'  # 下单数量
    stop_loss_pct = 0.05  # 止损百分比
    while True:  # 不断循环执行交易策略
        try:
            times, high_prices, low_prices, close_prices = get_historical_klines(symbol, interval, limit)  # 获取历史K线数据
            upper_bound, lower_bound, buy_signal, sell_signal = calculate_super_trend(close_prices, period, multiplier, upper_bound, lower_bound, buy_signal, sell_signal)  # 计算超级趋势指标
            last_price = float(account_api.get_specific_ticker(product_id=symbol)['last'])  # 获取最新成交价
            order_result = execute_trade_strategy(symbol, quantity, last_price, buy_signal, sell_signal)  # 执行交易策略
            if order_result['code'] == '0':  # 如果订单执行成功
                print(f"订单 {order_result['order_id']} 执行成功！")
            position_data = future_api.get_position(symbol)  # 获取当前持仓信息
            if position_data['data']:  # 如果有持仓
                position_qty = float(position_data['data'][0]['position'])  # 获取持仓数量
                if position_qty > 0 and (last_price / float(position_data['data'][0]['avg_cost'])) - 1 < -stop_loss_pct:  # 如果持多仓且亏损超过止损百分比
                    future_api.close_position(symbol, '2', position_qty)  # 止损平多仓
                    print('触发止损！平多仓')
                elif position_qty < 0 and (float(position_data['data'][0]['avg_cost']) / last_price) - 1 < -stop_loss_pct:  # 如果持空仓且亏损超过止损百分比
                    future_api.close_position(symbol, '1', abs(position_qty))  # 止损平空仓
                    print('触发止损！平空仓')
            else:
                print('当前没有持仓')
        except Exception as e:
            print(f'发生错误: {e}')  # 捕获并输出异常信息
