
import backtrader as bt
from backtrader_ctpcn_api.ctpstore import CTPStore
from backtrader_ctpcn_api.ctputil import  CtpStrategy
from time import sleep
import pandas as pd
import datetime
import pytz

if __name__ == '__main__':
    # http://122.51.136.165:50080/detail.html 查看行情服务器状态
    ctp_setting = {
        "CONNECT_INFO": {
            "userid": "????",  # 你在simnow注册的账户里的investorId
            "password": "????",  # 你在simnow注册的账户密码
            "brokerid": "9999",
            "md_address": "tcp://180.168.146.187:10211",  # 行情前置，行情服务器地址
            "td_address": "tcp://180.168.146.187:10201",  # 交易前置，交易服务器地址
            "product_info": "",
            "appid": "simnow_client_test",
            "auth_code": "0000000000000000"
        },
        "INTERFACE": "ctp",  # ctp/ctp_se载入接口名称，目前支持ctp生产以及ctp_se穿透式验证接口
        "TD_FUNC": True,  # 开启交易功能
        "MD_FUNC": True,  # 开启行情接收
        "XMIN": [],  # ctpbee生成几分钟bar，例如[1]
        "TODAY_EXCHANGE": ["SHFE", "INE"],  # 需要支持平今的交易所代码列表
        "CLOSE_PATTERN": "today",  # 对支持平今的交易所，指定优先平今或者平昨
    }
    tz = pytz.timezone('Asia/Shanghai')
    cerebro = bt.Cerebro()

    # 创建ctp store
    store = CTPStore(ctp_setting)

    # 定义数据
    # ag2206.SHFE是上期所白银期货  AP2210.ZCE郑商所 a2207.DCE大商所 中国金融期货交易所（IF2205.CFFEX）
    # vnpy 支持中国8大合规交易所中的5所，包括上海期货交易所，大连期货交易所、郑州期货交易所、中金所、能源所。
    data0_name = 'ag2206.SHFE'  # ag2206是上期所白银期货
    data1_name = 'ag2207.SHFE'

    # 回填数据文件所在路径
    csvpath = 'E:/myquant/backtrader_ctpcn/'
    data0 = store.getdata(dataname=data0_name, timeframe=bt.TimeFrame.Ticks,
                          # 回填数据来自哪里，如果不想回填，则设backfill_from=None
                          backfill_from=load_hist_ticks(csvpath + 'tickhistory.csv'),
                          qcheck=5,  # 等待远端tick的超时
                          sessionstart=datetime.time(21, 00, 00),  # 开市时间
                          sessionend=datetime.time(15, 00, 00),  # 闭市时间
                          tzinput=tz,
                          tz=tz
                          )

    # cerebro.adddata(data0)
    # 重采样tick合成需要的bar，注意设置name
    cerebro.resampledata(data0, timeframe=bt.TimeFrame.Seconds, compression=10, name=data0_name + '10s')

    # 多合约
    data1 = store.getdata(dataname=data1_name, timeframe=bt.TimeFrame.Ticks,
                          # 回填数据来自哪里，如果不想回填，则设backfill_from=None
                          backfill_from=load_hist_ticks(csvpath + 'tickhistory1.csv'),
                          qcheck=5,  # 等待远端tick的超时
                          sessionstart=datetime.time(21, 00, 00),  # 开市时间
                          sessionend=datetime.time(15, 00, 00),  # 闭市时间
                          tzinput=tz,
                          tz=tz
                          )
    # cerebro.adddata(data1)
    # 回放tick合成需要的bar，注意设置name
    cerebro.resampledata(data1, timeframe=bt.TimeFrame.Seconds, compression=10, name=data1_name + '10s')

    # 注入策略，注意store参数设置
    cerebro.addstrategy(SmaCross, store=store)

    # 当仿真行情与实盘同步时，is_realtime设为True，否则设为False
    cerebro.run(is_realtime=True, tz=tz)