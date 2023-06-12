# OKX-API-Trade-with-SuperTrend-parameter

## 超级趋势判断 自动化OKX api交易程序 

### 包含 实盘｜模拟盘 

个人实验项目

因该仓库的内容还未经过长期测试确定其的可靠性 所以现阶段 建议您可以参考其学习 

<img width="121" alt="截屏2023-06-11 上午10 22 25" src="https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/assets/76860915/3abda6c3-d511-4f59-9767-621032ee35a1">

## 简介

调用OKX API 

对于crypto交易对中 TraderView中的超级趋势参数 出现以及消失**上限线或下限线** 前后过程进行确认 

从而根据该参数指标的出现 进行多次买卖

---

红色长期趋势粗线是看跌信号，绿色是看涨信号。

（该趋势线为实时趋势 随着K线走向而实时产生）

<img width="1030" alt="244910477-fc0a79a5-9a17-4765-a180-16d8b31470ea" src="https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/assets/76860915/5c337cdb-64be-4cb0-85f3-5146d610a656">

（本仓库成立前一天 该指标在近3天时间段中的表现情况 BTC-USD）

---

<img width="1025" alt="截屏2023-06-12 下午9 02 24" src="https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/assets/76860915/a95229f6-b578-4eb9-81b6-e04324d59a9c">

（作者实盘数据 BTC-USDT）

@TradingView


模拟盘实验 请见 ‘Demo.py’ 文件
    该代码可用于在OKE模拟盘上自动交易加密货币。它的大致流程如下：
    
 - 导入必要的库和设置API密钥信息以及交易参数。
 
 - 实例化`OKXTrader`类，并初始化账户API和期货API，以及历史K线缓存。
 
 - 定义`get_historical_klines`函数，用于获取历史K线数据，并将其转换为numpy数组。如果缓存中已经存在该交易对的K线数据，则直接从缓存中读取；否则使用API获取历史K线数据，并将其保存到缓存中。
 
 - 定义`calculate_super_trend`函数，用于计算超级趋势指标。该函数接受收盘价序列、ATR指标的时间窗口大小、计算上轨和下轨的倍数等参数，并返回新的上轨、下轨、买入信号和卖出信号。

 - 定义`execute_trade_strategy`函数，用于执行交易策略。该函数接受交易对、下单数量、下单价格、买入信号、卖出信号、止损比例和止盈比例等参数，并根据当前仓位和交易信号执行相应的交易操作。
 
 - 实例化`OKXTrader`类，并调用`get_historical_klines`函数获取历史K线数据。
 
 - 调用`calculate_super_trend`函数计算超级趋势指标，并根据买入信号和卖出信号执行交易策略。如果存在买入或卖出信号，则获取最新成交价作为下单价格，计算下单数量并调用`execute_trade_strategy`函数执行交易。如果不存在买入或卖出信号，则输出信息提示没有发出买入或卖出信号。 

---
## SuperTrend 源码

by KivancOzbilgic 

        //@version=4
        study("Supertrend", overlay = true, format=format.price, precision=2, resolution="")

        Periods = input(title="ATR Period", type=input.integer, defval=10)
        src = input(hl2, title="Source")
        Multiplier = input(title="ATR Multiplier", type=input.float, step=0.1, defval=3.0)
        changeATR= input(title="Change ATR Calculation Method ?", type=input.bool, defval=true)
        showsignals = input(title="Show Buy/Sell Signals ?", type=input.bool, defval=true)
        highlighting = input(title="Highlighter On/Off ?", type=input.bool, defval=true)
        atr2 = sma(tr, Periods)
        atr= changeATR ? atr(Periods) : atr2
        up=src-(Multiplier*atr)
        up1 = nz(up[1],up)
        up := close[1] > up1 ? max(up,up1) : up
        dn=src+(Multiplier*atr)
        dn1 = nz(dn[1], dn)
        dn := close[1] < dn1 ? min(dn, dn1) : dn
        trend = 1
        trend := nz(trend[1], trend)
        trend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend
        upPlot = plot(trend == 1 ? up : na, title="Up Trend", style=plot.style_linebr, linewidth=2, color=color.green)
        buySignal = trend == 1 and trend[1] == -1
        plotshape(buySignal ? up : na, title="UpTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.green, transp=0)
        plotshape(buySignal and showsignals ? up : na, title="Buy", text="Buy", location=location.absolute, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white, transp=0)
        dnPlot = plot(trend == 1 ? na : dn, title="Down Trend", style=plot.style_linebr, linewidth=2, color=color.red)
        sellSignal = trend == -1 and trend[1] == 1
        plotshape(sellSignal ? dn : na, title="DownTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.red, transp=0)
        plotshape(sellSignal and showsignals ? dn : na, title="Sell", text="Sell", location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white, transp=0)
        mPlot = plot(ohlc4, title="", style=plot.style_circles, linewidth=0)
        longFillColor = highlighting ? (trend == 1 ? color.green : color.white) : color.white
        shortFillColor = highlighting ? (trend == -1 ? color.red : color.white) : color.white
        fill(mPlot, upPlot, title="UpTrend Highligter", color=longFillColor)
        fill(mPlot, dnPlot, title="DownTrend Highligter", color=shortFillColor)
        alertcondition(buySignal, title="SuperTrend Buy", message="SuperTrend Buy!")
        alertcondition(sellSignal, title="SuperTrend Sell", message="SuperTrend Sell!")
        changeCond = trend != trend[1]
        alertcondition(changeCond, title="SuperTrend Direction Change", message="SuperTrend has changed direction!")
        
其详细原理 请见：[How.SuperTrend.code.works_cn.md](https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/blob/master/How.SuperTrend.code.works_cn.md)


---

## 处理边界问题 注意事项

代码中的逻辑在处理边界问题时可能存在问题，比如在计算ATR指标时，如果历史K线数据不足以计算所需的ATR窗口大小，就会出现异常。

同时，在获取最新成交价时，由于市场波动等原因，价格可能已经发生变化，这时下单可能会失败。

建议在下单前先进行一定的价格缓存和判断，避免由于市场波动造成的误操作。


### 1.获取到的历史K线数据的时间是收盘价对应的时间。
    
在get_historical_klines方法中，从K线数据中分离出收盘价序列后，直接返回的是时间、高价、低价和收盘价四个序列，并没有进行任何转换或处理。

因此，在计算超级趋势指标时使用的时间序列就是收盘价对应的时间。    
    
### 2.在计算超级趋势指标时使用的时间序列是收盘价对应的时间。
    
在calculate_super_trend方法中，接收到的参数包括close_prices，也就是收盘价序列。

同时，在计算上轨和下轨时，使用的是收盘价序列的最后一个值（close_prices[-1]），因此买入信号或卖出信号生成的位置也与收盘价序列对应。

由此得出，在计算超级趋势指标时使用的时间序列就是收盘价对应的时间。
    
### 3.在OKX的币币交易中，每个交易对都有一个收盘价。
    
收盘价指当天24:00:00 (UTC+8) 时最后一笔成交价。

如果当天没有成交，则该日收盘价为0。
    
可以通过访问OKX API来获取特定交易对的历史K线数据，其中包含了每个时间周期内的开盘价、最高价、最低价、收盘价以及成交量等信息。
    
### 4.由于市场波动和交易行为等原因，不同交易所和不同交易对之间的收盘价可能存在差异。
    
因此，在运行交易策略时，应该针对具体的交易所和交易对进行相应的处理，避免由于收盘价不准确造成的误判。

---

# demo.py 虚拟盘转为实盘 注意事项
在将虚拟盘交易转为实盘交易之前，需要先进行以下步骤：

## 1.确认API Key、Secret Key和Passphrase的权限是否足够进行实盘交易，并且确保账户有足够的资金用于交易。

修改代码中的初始化部分，将 self.future_api 和 self.account_api 的第四个参数 True 改为 False，以开启真实交易模式。例如：

    self.account_api = account.AccountAPI(api_key, secret_key, passphrase, False)
    self.future_api = future.FutureAPI(api_key, secret_key, passphrase, False)
## 2.在执行交易策略时，需要使用真实的价格和数量信息，并且在下单时注意设置正确的委托类型和杠杆倍数。

例如：

    # 如果没有持仓，则开多单
    order_data = self.future_api.take_order(symbol=symbol, side='buy', price=price, qty=quantity,
                                            order_type='limit', match_price=False, leverage=10)
    
    # 如果没有持仓，则开空单
    order_data = self.future_api.take_order(symbol=symbol, side='sell', price=price, qty=quantity,
                                            order_type='limit', match_price=False, leverage=10)
                                            
## 3.在更新止损或止盈价格时，需要使用实际的价格而不是相对价格，并且需要注意价格精度和交易所规定的最小变动单位。例如：

    # 根据止损和止盈比例设置止损和止盈价格
    last_trade_price = float(self.future_api.get_last_trade(symbol=symbol)['price'])
    stop_loss_price = round(last_trade_price * (1 - stop_loss_pct), 2)
    take_profit_price = round(last_trade_price * (1 + take_profit_pct), 2)

    # 更新止损和止盈价格
    self.future_api.update_order(symbol=symbol, order_id=order_result['order_id'],
                             stop_loss=str(stop_loss_price), take_profit=str(take_profit_price))

## 4.在进行实盘交易之前，建议先进行模拟交易或使用小额资金进行测试，确保代码的正确性和交易策略的有效性。同时要注意风险管理，设置合理的止损和止盈规则，避免不必要的亏损。

## 5.当触发买入或卖出信号时，会通过self.future_api.take_order函数开仓，此处需要注意的是，在开仓之前应该先检查当前是否已经有持仓，如果已经有持仓，则不能再次开仓。同时，还需要考虑在止损和止盈时，对于已经存在的持仓也需要进行更新而非重新开仓。


# 免责声明：

本实验项目是基于OKX提供的API接口进行开发并对加密货币进行交易的个人学习项目，仅用于学术研究和个人实验目的。

使用该项目存在风险，可能导致资金损失和投资风险。使用者应了解相关法律法规和市场情况，自行承担一切后果和责任。本项目的开发者不对由于使用者使用该项目而造成的任何损失负责。使用者应自行评估和决定是否使用本项目的代码。

在使用本项目时，请务必遵守OKX平台的用户协议和相关规定，并注意保护个人信息和账户安全。本项目的开发者不对因违反OKX平台规定而导致的任何后果负责。

最后，本项目的代码仅供参考，不对交易结果负责。使用者在使用本项目时应根据自身状况进行风险评估和投资决策。 

![IMG_7FD989399B3F-1](https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/assets/76860915/0f880202-2c84-4e88-acad-336b8afe6d79)

（图片来源于 Twitter）


©️ Yanbo 2023

