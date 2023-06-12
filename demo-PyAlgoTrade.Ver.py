# 导入相关库
import okx.demo_account_api as account  # 使用模拟盘账户API
import okx.demo_futures_api as future   # 使用模拟盘期货API
import time
import numpy as np
from pyalgotrade import strategy, plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import bollinger, super_trend

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
当然，你也可以自行调整该参数
"""

symbol = 'btc-usdt'
interval = '1h'
quantity = 1
stop_loss_pct = 0.02
take_profit_pct = 0.02
leverage = 10


class OKXTrader(strategy.BacktestingStrategy):
    def __init__(self, feed, cash):
        super().__init__(feed, cash)
        self.symbol = symbol
        self.buy_signal = False
        self.sell_signal = False

        # 初始化期货API
        self.future_api = future.FutureAPI(api_key, secret_key, passphrase, True)

        # 创建技术指标
        self.bollinger_bands = bollinger.BollingerBands(feed['close'], 20, 2)
        self.super_trend = super_trend.SuperTrend(feed, 10, 3)

    def onBars(self, bars):
        # 获取当前仓位
        position_data = self.future_api.get_demo_specific_position(symbol=self.symbol)  # 使用模拟盘API获取持仓信息
        current_qty = int(position_data['holding'][0]['avail_qty'])

        # 判断是否发出买入或卖出信号
        if self.buy_signal and current_qty <= 0:
            # 如果没有持仓，则开多单
            price = bars[self.symbol].getClose()
            order_data = self.future_api.take_demo_order(symbol=self.symbol, side='buy', price=price, qty=quantity,
                                                         order_type='limit', match_price=False)  # 使用模拟盘API下单
            self.buy_signal = False

        elif self.sell_signal and current_qty >= 0:
            # 如果没有持仓，则开空单
            price = bars[self.symbol].getClose()
            order_data = self.future_api.take_demo_order(symbol=self.symbol, side='sell', price=price, qty=quantity,
                                                         order_type='limit', match_price=False)
            self.sell_signal = False

        elif current_qty > 0 and (stop_loss_pct > 0 or take_profit_pct > 0):
            # 如果持有多头仓位，根据止损和止盈比例设置止损和止盈价格
            last_trade_price = self.future_api.get_last_trade(symbol=self.symbol)['price']
            stop_loss_price = round(last_trade_price * (1 - stop_loss_pct), 2)
            take_profit_price = round(last_trade_price * (1 + take_profit_pct), 2)

            # 更新止损和止盈价格
            self.future_api.update_demo_order(symbol=self.symbol, order_id=order_result['order_id'],
                                               stop_loss=str(stop_loss_price), take_profit=str(take_profit_price))

        elif current_qty < 0 and (stop_loss_pct > 0 or take _profit_pct > 0):
# 如果持有空头仓位，根据止损和止盈比例设置止损和止盈价格
last_trade_price = self.future_api.get_last_trade(symbol=self.symbol)['price']
stop_loss_price = round(last_trade_price * (1 + stop_loss_pct), 2)
take_profit_price = round(last_trade_price * (1 - take_profit_pct), 2)

        # 更新止损和止盈价格
        self.future_api.update_demo_order(symbol=self.symbol, order_id=order_result['order_id'],
                                           stop_loss=str(stop_loss_price), take_profit=str(take_profit_price))

    # 计算技术指标
    bollinger_upper_band = self.bollinger_bands.getUpperBand()[-1]
    bollinger_lower_band = self.bollinger_bands.getLowerBand()[-1]
    super_trend_value = self.super_trend[-1]

    # 判断是否发出买入或卖出信号
    if bars[self.symbol].getClose() > bollinger_upper_band and super_trend_value > bars[
        self.symbol].getClose():
        self.buy_signal = True
    elif bars[self.symbol].getClose() < bollinger_lower_band and super_trend_value < bars[
        self.symbol].getClose():
        self.sell_signal = True

def getBollingerBands(self):
    return self.bollinger_bands
# 获取历史K线数据
  feed = yahoofinance.build_feed([symbol], 2021, 2022, interval)

# 初始化策略并运行回测
  cash = 100000
  strategy = OKXTrader(feed, cash)
  plt = plotter.StrategyPlotter(strategy)
  strategy.run()
  plt.plot()

# 输出回测结果
  print(f"Initial portfolio value: {cash:.2f}")
  print(f"Final portfolio value: {strategy.getBroker().getEquity():.2f}")
  print(f"Total return: {100 * (strategy.getBroker().getEquity() / cash - 1):.2f}%")

