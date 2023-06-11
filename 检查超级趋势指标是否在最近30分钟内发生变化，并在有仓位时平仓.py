# 检查超级趋势指标是否在最近30分钟内发生变化，并在有仓位时平仓：

    def execute_trade_strategy(self, symbol, quantity, price, buy_signal, sell_signal, stop_loss_pct, take_profit_pct, last_trade_time):
        """
        执行交易策略

        :param symbol: 交易对
        :param quantity: 下单数量
        :param price: 下单价格
        :param buy_signal: 是否买入信号
        :param sell_signal: 是否卖出信号
        :param stop_loss_pct: 止损比例
        :param take_profit_pct: 止盈比例
        :param last_trade_time: 上一次交易时间
        :return: 订单结果
        """
        order_result = None
        try:
            # 获取当前仓位
            position_data = self.future_api.get_demo_specific_position(symbol=symbol)  # 使用模拟盘API获取持仓信息
            current_qty = int(position_data['holding'][0]['avail_qty'])

            # 如果有仓位，检查是否需要平仓
            if current_qty != 0:
                # 获取当前时间和上一次交易时间的差值，单位为秒
                current_time = time.time()
                time_diff = current_time - last_trade_time
                
                # 如果超过30分钟没有变化，平仓操作并更新上一次交易时间
                if time_diff > 1800:
                    if current_qty > 0:
                        # 平多仓
                        order_data = self.future_api.take_demo_order(symbol=symbol, side='sell', price=price, qty=current_qty,
                                                                     order_type='limit', match_price=False)
                    else:
                        # 平空仓
                        order_data = self.future_api.take_demo_order(symbol=symbol, side='buy', price=price, qty=-current_qty,
                                                                     order_type='limit', match_price=False)
                    last_trade_time = current_time

            # 如果没有持仓，根据买入信号和卖出信号执行交易
            elif buy_signal:
                # 如果没有持仓，则开多单
                order_data = self.future_api.take_demo_order(symbol=symbol, side='buy', price=price, qty=quantity,
                                                             order_type='limit', match_price=False)  # 使用模拟盘API下单
                last_trade_time = time.time()

            elif sell_signal:
                # 如果没有持仓，则开空单
                order_data = self.future_api.take_demo_order(symbol=symbol, side='sell', price=price, qty=quantity,
                                                             order_type='limit', match_price=False)
                last_trade_time = time.time()

        except Exception as e:
            # 发生错误时打印错误信息
            print(f'执行交易策略时发生错误: {e}')

        # 返回订单结果和上一次交易时间
        return order_result, last_trade_time
      
# 然后，你可以修改主程序来跟踪上一次交易时间，并使用更新后的参数调用execute_trade_strategy方法：

# 实例化OKXTrader类
trader = OKXTrader(api_key, secret_key, passphrase)

# 初始化上一次交易时间为当前时间
last_trade_time = time.time()

while True:
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
        order_result, last_trade_time = trader.execute_trade_strategy(symbol, quantity, price, buy_signal, sell_signal,
