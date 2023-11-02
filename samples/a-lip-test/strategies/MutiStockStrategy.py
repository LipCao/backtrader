import backtrader as bt


class SMAStrategy(bt.Strategy):
    params = dict(
        period=30,
        priod_15=15,
        stake=100,
    )

    def __init__(self):

        self.smas = dict()

        self.data_close = self.datas[0].close
        self.order = None
        self.price = None
        self.comm = None
        for d in self.datas:
            self.smas[d] = bt.indicators.SMA(d, period=self.p.period)

    def next(self):

        for d in self.datas:
            pos = self.getposition(d).size
            if not pos:
                if d.close[0] > self.smas[d][0]:  # 达到买入条件
                    self.buy(data=d, size=self.p.stake)
            else:
                if d.close[0] < self.smas[d][0]:  # 达到卖出条件
                    self.sell(data=d)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'买入: 价格：{order.executed.price}, 成本：{order.executed.value}, 手续费：{order.executed.comm}')
                self.price = order.executed.price
                self.comm = order.executed.comm
            else:
                self.log(
                    f'卖出: 价格：{order.executed.price}, 成本：{order.executed.value}, 手续费：{order.executed.comm}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单失败')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：{trade.pnl}, 交易收益：{trade.pnlcomm}')

    def log(self, txt, dt=None, doprint=True):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')
