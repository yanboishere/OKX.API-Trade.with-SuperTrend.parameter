
```
//@version=4
study("Supertrend", overlay = true, format=format.price, precision=2, resolution="")
```

The first two lines are just comments indicating the version of TradingView used and the name of this particular study. In the third line, `overlay=true` means that the indicator will be overlaid on the price chart rather than displayed in a separate pane. `format=format.price` specifies the format of the price labels on the y-axis, and `precision=2` sets the number of decimal places to display for the prices. `resolution=""` indicates that the indicator should use the same resolution as the chart it's applied to.

```
Periods = input(title="ATR Period", type=input.integer, defval=10)
src = input(hl2, title="Source")
Multiplier = input(title="ATR Multiplier", type=input.float, step=0.1, defval=3.0)
changeATR= input(title="Change ATR Calculation Method ?", type=input.bool, defval=true)
showsignals = input(title="Show Buy/Sell Signals ?", type=input.bool, defval=true)
highlighting = input(title="Highlighter On/Off ?", type=input.bool, defval=true)
```

These lines define user inputs that allow users to customize the indicator's parameters. `input()` is the function that creates the input field. Each input has a title that appears next to the input on the settings panel, a data type (`integer`, `float`, `bool`, etc.), a default value (`defval`), and sometimes other parameters specific to that input type (`step`, for example, sets the increment between values for a float input).

- `Periods`: This is the period length used in the indicator's calculation, in this case corresponding to the ATR period.
- `src`: This specifies the input source for the indicator, which is set to the average of the high and low prices (`hl2`).
- `Multiplier`: This sets the multiplier used in the Supertrend calculation.
- `changeATR`: This input allows the user to choose between using the simple moving average (`sma()`) or the exponential moving average (`atr()`) as the basis for the ATR calculation.
- `showsignals`: This input controls whether or not buy/sell signals should be displayed on the chart.
- `highlighting`: This input controls whether or not the Supertrend line should be highlighted with color.

```
atr2 = sma(tr, Periods)
atr= changeATR ? atr(Periods) : atr2
```

These lines calculate the ATR (average true range) value used in the Supertrend calculation, based on the user inputs. `atr2` is the default ATR value calculated using a simple moving average of `tr` (the true range) over the specified period length. If `changeATR` is `true`, then `atr` is set equal to the ATR calculated using an exponential moving average instead.

```
up=src-(Multiplier*atr)
up1 = nz(up[1],up)
up := close[1] > up1 ? max(up,up1) : up
dn=src+(Multiplier*atr)
dn1 = nz(dn[1], dn)
dn := close[1] < dn1 ? min(dn, dn1) : dn
```

These lines calculate the upper and lower bands of the Supertrend indicator. `up` is the upper band, calculated as the difference between the input source and the product of the ATR and the multiplier. `up1` is the previous value of `up`, which is used to determine whether the current value of `up` should be adjusted upwards or not. If the close price is greater than `up1`, then `up` is set equal to the maximum of the current and previous values of `up`. Otherwise, `up` remains unchanged.

`dn` is the lower band, calculated similarly to `up`, but with the opposite sign in front of the ATR term. `dn1` is the previous value of `dn`, which is used to determine whether the current value of `dn` should be adjusted downwards or not. If the close price is less than `dn1`, then `dn` is set equal to the minimum of the current and previous values of `dn`. Otherwise, `dn` remains unchanged.

```
trend = 1
trend := nz(trend[1], trend)
trend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend
```

These lines calculate the Supertrend line itself by determining the current trend direction based on the position of the close price relative to the upper and lower bands. `trend` is initialized to 1 (indicating an uptrend) and then updated based on the following rules:

- If the previous value of `trend` was -1 (indicating a downtrend) and the current close price is above the previous value of `dn`, then the trend switches to 1 (indicating an uptrend).
- If the previous value of `trend` was 1 (indicating an uptrend) and the current close price is below the previous value of `up`, then the trend switches to -1 (indicating a downtrend).
- Otherwise, the trend remains unchanged from its previous value.

```
plot(hl2, color=color.white, title="Price")
bgcolor(highlighting ? (trend == 1 ? color.green : color.red) : na, transp=70)
plot(trend == 1 ? up : dn, title="Supertrend", color=color.blue, linewidth=2)
longCondition = trend == 1 and trend[1] == -1
shortCondition = trend == -1 and trend[1] == 1
if (showsignals)
    strategy.entry("Long", strategy.long, when=longCondition)
    strategy.entry("Short", strategy.short, when=shortCondition)
```

These lines plot the Supertrend line and, optionally, highlight it with a green or red background depending on whether the current trend is bullish or bearish. The Supertrend line itself is plotted as a blue line using either the upper or lower band, depending on the current trend direction.

The `longCondition` and `shortCondition` variables are used to generate buy and sell signals for a trading strategy. A long signal is generated when the trend switches from bearish to bullish (`trend == 1` and `trend[1] == -1`), while a short signal is generated when the trend switches from bullish to bearish (`trend == -1` and `trend[1] == 1`). If `showsignals` is true, then these signals are sent to the TradingView strategy tester for backtesting.
