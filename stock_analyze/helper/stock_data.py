# coding: utf-8
import json

import pandas as pd
import requests
from pandas import DataFrame, Series
import numpy as np
import pandas_datareader.data as web
import requests_cache
import datetime
import time
import traceback


def print_err(err):
    traceback.print_tb(err.__traceback__)


# pandas datareader cache
PANDAS_SESSION = requests_cache.CachedSession(cache_name='pandas_datareader_cache',
                                              backend='sqlite', expire_after=datetime.timedelta(hours=9))
# request cache
requests_cache.install_cache(cache_name='requests_cache',
                             backend='sqlite', expire_after=datetime.timedelta(minutes=30))

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/70.0.3538.110 Chrome/70.0.3538.110 Safari/537.36'
}


def df2html(df):
    return df.to_html()


def _request(url, enable_cache=True):
    if not enable_cache:
        with requests_cache.disabled():  # temporary disabling caching
            return requests.get(url, headers=headers)
    else:
        return requests.get(url, headers=headers)
    # print('request from cache:', response.from_cache)


def get_stock_data(stock_code, market_code, start, end, ):
    '''get data from yahoo through pandas datareader'''
    request_code = stock_code + ('.SS' if int(market_code) == 1 else '.SZ')
    df = web.DataReader(request_code, 'yahoo', start, end, session=PANDAS_SESSION)
    return df[df['Volume'] > 0]  # 过滤掉成交量是0的，某些情况下如节假日没有开盘成交量为0


def get_recent_data(stock_code, market_code, days):
    '''get recent data basic'''
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    return get_stock_data(stock_code, market_code, start, end)


def pc_volume_corr(df_basic_data):
    '''calculate the corr between price pct change and volume pct change'''
    pct_change = DataFrame(df_basic_data['Adj Close'].pct_change())
    return pct_change.corrwith(df_basic_data['Volume'].pct_change())


def get_pv_analyzation(stock_code, market_code):
    '''计算最近90天，30天，7天的平均收盘价，平均成交量，及价量相关性'''
    df90 = get_recent_data(stock_code, market_code, 90)
    df30 = df90[-31:]
    df7 = df90[-8:]

    p_mean_90 = df90.mean()['Adj Close']
    v_mean_90 = df90.mean()['Volume']
    p_mean_30 = df30.mean()['Adj Close']
    v_mean_30 = df30.mean()['Volume']
    p_mean_7 = df7.mean()['Adj Close']
    v_mean_7 = df7.mean()['Volume']

    pv_scorr_90 = pc_volume_corr(df90)
    pv_scorr_30 = pc_volume_corr(df30)
    pv_scorr_7 = pc_volume_corr(df7)

    row_p_mean = Series([p_mean_90, p_mean_30, p_mean_7]).map(lambda x: '%.2f' % x)
    row_v_mean = Series([v_mean_90, v_mean_30, v_mean_7]).map(lambda x: '{:.2f}'.format(x / 1000000))
    row_pv_scorr = Series([pv_scorr_90, pv_scorr_30, pv_scorr_7]).map(lambda x: '%.2f' % x)

    return DataFrame(columns=['90天', '30天', '7天'],
                     index=['平均收盘价', '平均成交量/万手', '价量相关性'],
                     data=[row_p_mean.values, row_v_mean.values, row_pv_scorr.values])


def cur_price_info(stock_code, market_code, enable_cache=True):
    '''get current price, price change, price change percent'''
    try:
        url = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?cb=&id={}{}' \
            .format(stock_code, market_code)
        r = _request(url, enable_cache).text
        v = json.loads(r[r.index('(') + 1: r.rindex(')')])['Value']
        pc, pc_change, pc_change_pct, time = v[25], v[27], v[29], v[-4]
    except Exception as e:
        print_err(e)
        # 停牌之类的股票获取时数据是空的
        print('error happend when get cur price, url: %s' % url)
        return 0, 0, 0, False
    else:
        return pc, pc_change, pc_change_pct, time


def stocks_corr_analyzation(days, stock, *compare_stocks):
    ''' analyze the pct_change corr between stocks '''
    compare_stock_data = {}
    for s in compare_stocks:
        try:
            compare_stock_data[s.name] = get_recent_data(s.code, s.market_code, days)
        except Exception as e:
            print_err(e)

    df_compare_stocks_pct = DataFrame({stock: df['Adj Close'] for stock, df in compare_stock_data.items()}) \
        .pct_change()

    if stock is not None:
        if stock in compare_stocks:
            ser_stock_pct = df_compare_stocks_pct[stock.name]
            df_compare_stocks_pct.drop(columns=stock.name, inplace=True)
        else:
            df = get_recent_data(stock.code, stock.market_code, days)
            ser_stock_pct = df['Adj Close'].pct_change()

        ser = df_compare_stocks_pct.corrwith(ser_stock_pct)
        # 筛选出0.5以上的，并格式化
        ser = ser[ser >= 0.5].map(lambda x: '{:.2f}'.format(x))
        ser.name = '涨跌相关性'
        return ser.to_frame()
        # return ser.to_frame().T
    else:
        df = df_compare_stocks_pct.corr()
        return df.applymap(lambda x: '{:.2f}'.format(x))


def industry_stocks_updown_count(enable_cache=False):
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=&type=CT' \
          '&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FPGBKI&cmd=C._BKHY&st=(ChangePercent)&sr=-1&p=1&ps=1000'
    r = _request(url, enable_cache).text
    ds = json.loads(r[r.index('(') + 1: r.rindex(')')])
    industries = {}
    for d in ds:
        p = d.split(',')
        name, total_value, exchange, count = p[2], p[4], p[5], p[6]
        cs = count.split('|')
        up, down = cs[0], cs[2]
        industries[name] = {'total_value': total_value, 'exchange': exchange, 'up': up, 'down': down}
    return industries


if __name__ == '__main__':
    # t_start = time.time()

    # basic_data = get_recent_data('000001', 1, 30)
    # print(basic_data)

    # pv_corr = pc_volume_corr(basic_data)
    # print(pv_corr)
    # print(pvcorr_score(pv_corr[0]))
    # t_end = time.time()
    # print('spent time %s s' % (t_end - t_start))

    # print(cur_price_info('601128',1, enable_cache=False))

    # print(get_pv_analyzation('601128', 1))

    print(industry_stocks_updown_count())
