# OKX-API-Trade-with-SuperTrend-parameter
Personal experimental project

**Since the content of this repository has not yet been tested over a long period of time to determine its reliability, it is recommended that at this stage you use it for learning purposes only.**

<img width="121" alt="截屏2023-06-11 上午10 22 25" src="https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/assets/76860915/1c26ae3e-eb78-4efe-86c3-15f717cdfa75">

## Intro.

Call the OKX API to confirm the process of appearance and disappearance of upper or lower limit lines for the super trend parameters in crypto trading pairs in TraderView, and perform multiple buying and selling transactions based on this parameter index.

<img width="1030" alt="截屏2023-06-11 上午11 29 02" src="https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/assets/76860915/fc0a79a5-9a17-4765-a180-16d8b31470ea">


（The red long-term trend line is a bearish signal, while the green one is a bullish signal.  

Example data picture from @tradingview.com）


Experimental results on the simulation platform can be found in the 'Demo.py' file. The code follows the following general process:

- Import the necessary libraries and set API key information and transaction parameters.
- Instantiate the `OKXTrader` class, initialize the account API and futures API, and historical K-line cache.
- Define the `get_historical_klines` function to obtain historical K-line data and convert it into a numpy array. If the K-line data for the trading pair already exists in the cache, read directly from the cache; otherwise, use the API to obtain historical K-line data and save it to the cache.
- Define the `calculate_super_trend` function to calculate the super trend indicator. The function accepts parameters such as the closing price sequence, the time window size of the ATR indicator, and the multiples used in calculating the upper and lower limits, and returns new upper and lower limits, buy signals, and sell signals.
- Define the `execute_trade_strategy` function to execute the trading strategy. The function takes parameters such as the trading pair, order quantity, order price, buy signal, sell signal, stop loss ratio, and take profit ratio, and executes corresponding trading operations based on the current position and trading signal.
- Instantiate the `OKXTrader` class and call the `get_historical_klines` function to obtain historical K-line data.
- Call the `calculate_super_trend` function to calculate the super trend indicator and execute the trading strategy based on buy and sell signals. If there are buy or sell signals, obtain the latest trading price as the order price, calculate the order quantity, and call the `execute_trade_strategy` function to execute the transaction. If there are no buy or sell signals, output a message indicating that no buy or sell signals have been issued.

## Libraries

You can use pip tool to install the libraries used in the code. Enter the following commands in the command line:

```
pip install numpy
pip install talib
pip install python-okx
```

Please note that the talib library requires TA-Lib dependency library to be installed locally before it can run properly. You can download the corresponding binary file from the official website of  [TA-Lib] (http://www.ta-lib.org/hdr_dw.html) according to your operating system and Python version, or refer to the GitHub repository of [TA-Lib] (https://github.com/mrjbq7/ta-lib) for source code compilation installation.

## reference links

OKX-Api

## Sponsor me. 

### Bitcoin address 
bc1q32mjead3kg0lx25yy9mcy9m8845zatvhcfvj92

### Ethereum address
0xBBc1fE874422F61fB135e72C3229Fffc3Cb266Fb

## Disclaimer

This experimental project is a personal learning project developed based on the API interface provided by OKEx for trading cryptocurrencies, and is only used for academic research and personal experimental purposes.

There are risks involved in using this project, which may result in financial losses and investment risks. The user should be aware of relevant laws, regulations, and market conditions and assume all consequences and responsibilities. The developer of this project is not responsible for any losses caused by the user's use of the project. The user should evaluate and decide whether to use the code of this project on their own.

When using this project, please comply with the user agreement and relevant regulations of the OKX platform, and pay attention to protecting personal information and account security. The developer of this project is not responsible for any consequences resulting from the violation of OKEx platform rules.

Finally, the code of this project is for reference only and is not responsible for trading results. Users should evaluate risks and make investment decisions based on their own circumstances when using this project.

![IMG_7FD989399B3F-1](https://github.com/yanboishere/OKX.API-Trade.with-SuperTrend.parameter/assets/76860915/0f880202-2c84-4e88-acad-336b8afe6d79)

（Picture From Twitter）


©️ Yanbo 2023







