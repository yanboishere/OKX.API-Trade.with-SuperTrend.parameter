
```
//@version=4
study("Supertrend", overlay = true, format=format.price, precision=2, resolution="")
```

前两行是注释，指示使用的TradingView版本和这个特定研究的名称。第三行中，`overlay=true`表示该指标将叠加在价格图表上而不是显示在单独的面板中。 `format=format.price`指定y轴上价格标签的格式，而`precision=2`设置要显示的价格小数位数。 `resolution =“”`表示该指标应使用与应用于其的图表相同的分辨率。

```
Periods = input(title="ATR Period", type=input.integer, defval=10)
src = input(hl2, title="Source")
Multiplier = input(title="ATR Multiplier", type=input.float, step=0.1, defval=3.0)
changeATR= input(title="Change ATR Calculation Method ?", type=input.bool, defval=true)
showsignals = input(title="Show Buy/Sell Signals ?", type=input.bool, defval=true)
highlighting = input(title="Highlighter On/Off ?", type=input.bool, defval=true)
```

这些行定义用户输入，允许用户自定义指标的参数。 `input()`是创建输入字段的函数。每个输入都有一个标题，该标题出现在设置面板上方的输入旁边，具有数据类型（`integer`，`float`，`bool`等），默认值（`defval`）以及有时针对该输入类型的其他参数（例如`step`设置浮点输入值之间的增量）。

- `Periods`：这是指标计算中使用的周期长度，在本例中对应于ATR期间。
- `src`：这指定了用于指标的输入来源，设置为高和低价格的平均值（`hl2`）。
- `Multiplier`：这设置Supertrend计算中使用的乘数。
- `changeATR`：此输入允许用户选择作为ATR计算基础的简单移动平均线（`sma()`）或指数移动平均线（`atr()`）之间的区别。
- `showsignals`：此输入控制是否在图表上显示买入/卖出信号。
- `highlighting`：此输入控制是否突出显示Supertrend线。

```
atr2 = sma(tr, Periods)
atr= changeATR ? atr(Periods) : atr2
```

这些行根据用户输入计算用于Supertrend计算的ATR（平均真实范围）。 `atr2`是默认的ATR值，使用指定期长上的`tr`（真实范围）的简单移动平均线进行计算。如果`changeATR`为`true`，则将`atr`设置为使用指数移动平均线计算的ATR值。

```
up=src-(Multiplier*atr)
up1 = nz(up[1],up)
up := close[1] > up1 ? max(up,up1) : up
dn=src+(Multiplier*atr)
dn1 = nz(dn[1], dn)
dn := close[1] < dn1 ? min(dn, dn1) : dn
```

这些行计算Supertrend指标的上部和下部带。 `up`是上部带，计算为输入源与ATR和乘数的乘积之差。 `up1`是`up`的前一个值，用于确定当前值是否应该向上调整。如果收盘价大于`up1`，则将`up`设置为当前值和上一个值中的最大值。否则，`up`保持不变。

`dn`类似于`up`，但在ATR项前面具有相反的符号。 `dn1`是`dn`的前一个值，用于确定当前值是否应向下调整。如果收盘价小于`dn1`，则将`dn`设置为当前值和上一个值中的最小值。否则，`dn`保持不变。

```
trend = 1
trend := nz(trend[1], trend)
trend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend
```

这些行跟踪当前趋势，并确定应该在哪个方向上交易。 最初将`trend`设置为1，表示上涨趋势。然后，通过防止`trend`未定义并将其设置为先前值，将`trend`更新为前一个计算周期的`trend`。最后，如果`trend`为-1且收盘价高于上一个周期的下部带，则`trend`设置为1（表示新的上涨趋势）。或者，如果`trend`为1且收盘价低于上一个周期的上部带，则`trend`设置为-1（表示新的下跌趋势）。

```
bgcolor(highlighting and trend == 1 ? color.green : trend == -1 ? color.red : na, transp=70)
plot(showsignals and trend == 1 ? up : na, title="SuperTrend Up", color=color.green, linewidth=2, style=plot.style_line)
plot(showsignals and trend == -1 ? dn : na, title="SuperTrend Down", color=color.red, linewidth=2, style=plot.style_line)
```

这些行用于绘制Supertrend指标。 `bgcolor()`用于在背景中突出显示当前趋势，并在`trend`为1时设置绿色，-1时设置红色。 `plot()`用于绘制上部带和下部带的曲线，如果`showsignals`为`true`并且当前趋势为1，则绘制`up`，颜色为绿色；如果当前趋势为-1，则绘制`dn`，颜色为红色。

这就是Supertrend指标的完整代码及其工作原理。它可以帮助交易者识别价格趋势并确定进入和退出交易的时机。

收盘价相对于上限和下限的位置。 trend 初始化为 1（表示上升趋势），然后根据以下规则更新：

如果 trend 的前一个值是 -1（表示下降趋势）并且当前收盘价高于 dn 的前一个值，则趋势切换到 1（表示上升趋势）。
如果 trend 的前一个值为 1（表示上升趋势），而当前收盘价低于 up 的前一个值，则趋势切换为 -1（表示下降趋势）。
否则，趋势与其之前的值保持不变。

    plot(hl2, color=color.white, title="Price")
    bgcolor(highlighting ? (trend == 1 ? color.green : color.red) : na, transp=70)
    plot(trend == 1 ? up : dn, title="Supertrend", color=color.blue, linewidth=2)
    longCondition = trend == 1 and trend[1] == -1
    shortCondition = trend == -1 and trend[1] == 1
    if (showsignals)
        strategy.entry("Long", strategy.long, when=longCondition)
        strategy.entry("Short", strategy.short, when=shortCondition)
        
这些线绘制了超级趋势线，并可选择根据当前趋势是看涨还是看跌，用绿色或红色背景突出显示它。 Supertrend 线本身根据当前趋势方向使用上限或下限绘制为蓝线。

longCondition 和 shortCondition 变量用于为交易策略生成买入和卖出信号。 当趋势从看跌转向看涨时产生一个多头信号（trend == 1 和 trend[1] == -1），而当趋势从看涨转向看跌时产生一个空头信号（trend == -1 和 趋势 [1] == 1)。 如果 showsignals 为真，则这些信号将发送到 TradingView 策略测试器进行回测。
