import pandas as pd
from datetime import datetime
import backtrader as bt
from strategies.AvgStrage import SMAStrategy as avgStrage


def get_data():
    dataframe = pd.read_csv('data/CFFEX.IC.HOT_d.csv')
    dataframe['Datatime'] = pd.to_datetime(dataframe['date'])
    dataframe.set_index('Datatime', inplace=True)
    return dataframe


# 1.数据加载
stock_data = get_data()
from_date = datetime(2015, 1, 1)
to_date = datetime(2020, 1, 1)
data = bt.feeds.PandasData(dataname=stock_data, fromdate=from_date, todate=to_date)

# 2.创建运行环境

cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.addstrategy(avgStrage)

cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

cerebro.broker.setcash(1000000)
cerebro.broker.setcommission(commission=0.0006)
cerebro.addsizer(bt.sizers.PercentSizer, percents=90)

# 3.运行
result = cerebro.run()
# 4.输出结果
strats = result[0]
print('Sharpe Ratio:', strats.analyzers.sharpe.get_analysis())
print('DrawDown:', strats.analyzers.drawdown.get_analysis())

cerebro.plot(style='candlestick', barup='red', bardown='green', fmt_x_data='%Y-%m-%d', fmt_x_ticks='%Y-%m-%d')
