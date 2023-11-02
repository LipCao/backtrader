import pandas as pd
from datetime import datetime
import backtrader as bt
import matplotlib.pyplot as plt
import tushare as ts

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置画图时中文显示
plt.rcParams["axes.unicode_minus"] = False  # 设置画图时的负号显示


# 1.数据加载
def get_data(code='600519', starttime='2017-01-01', endtime='2020-01-01'):
    df = ts.get_k_data(code, start=starttime, end=endtime)
    df.index = pd.to_datetime(df.date)
    df['openinterest'] = 0
    # 对df的数据列进行一个整合
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    return df


stock_df = get_data()
stock_df1 = get_data(code = '600419')

fromdate = datetime(2017, 1, 1)
todata = datetime(2020, 1, 1)
# 加载并读取数据源 dataname(数据来源) fromdate（date格式） todate
# 第一个数据集
data = bt.feeds.PandasData(dataname=stock_df, fromdate=fromdate, todate=todata)

# 第二个数据集
data1 = bt.feeds.PandasData(dataname=stock_df1, fromdate=fromdate, todate=todata)

# 2.构建策略
# 上穿20日线买入📈，跌穿20日均线卖出📉
class MyStrategy(bt.Strategy):
    # params = {
    #     ('maperiod', 20),
    # }
    # 使用字典定义params
    params = dict(
        period_20=20,
        period_15=15,
    )

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.price = None
        self.comm = None
        # 添加移动均线指标，内置了talib模块
        self.ma20 = bt.indicators.SMA(self.datas[0], period=self.p.period_20)
        self.ma15 = bt.indicators.SMA(self.datas[0], period=self.p.period_15)
        # 15 20日均线差额
        self.ma_diff = self.ma15 - self.ma20

    # 每个bar都会执行一次
    def next(self):
        #print('20日均线: %.2f' % self.ma20[0])
        #print('15日均线: %.2f' % self.ma15[0])
        #print('15 20日差额 %.2f' % self.ma_diff[0])
        # 拿到lines中各个line的name
        #print(self.data.lines.getlinealiases())
        #print(self.data1._name)
        # 拿到茅台当天的close 第一个数据集
        #print( self.data.close[0],self.data.close[-1])
        #日期
        #print(bt.num2date(self.data.lines[6][0]))


        # 判断是否有交易指令正在进行
        if self.order:
            return
        # 空仓
        if not self.position:
            # 收盘价上穿20日均线
            if self.data.close[0] > self.ma20[0]:
                self.order = self.buy(size=200)
        # 持仓
        else:
            # 收盘价下穿20日均线
            if self.data.close[0] < self.ma20[0]:
                self.order = self.sell(size=200)


# 3.策略设置
cerebro = bt.Cerebro()  # 构建大脑
cerebro.addstrategy(MyStrategy)  # 添加策略
cerebro.adddata(data, name='茅台')  # 添加数据
cerebro.adddata(data1, name='天润')
# 设置初始金额
cash = 100000
cerebro.broker.setcash(cash)
# 设置手续费
cerebro.broker.setcommission(commission=0.0002)
# 设置滑点百分比
cerebro.broker.set_slippage_perc(1)

# 4.运行
f = fromdate.strftime('%Y-%m-%d')
t = todata.strftime('%Y-%m-%d')
print('初始金额: %.2f 回测时间: %s ~ %s' % (cash, f, t))
cerebro.run()
print('最终金额: %.2f 回测时间: %s ~ %s' % (cerebro.broker.getvalue(), f,
      t))
