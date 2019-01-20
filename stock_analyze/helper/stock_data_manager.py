import datetime
import json

import pandas as pd
import pandas_datareader.data as web
import requests
import requests_cache

import stock_analyze.helper.mongodb_helper as mh
from a_stock.utils import print_err
from stock_analyze.helper import utils

ENABLE_PANDAS_CACHE = True

# pandas datareader cache
PANDAS_SESSION = requests_cache.CachedSession(cache_name='pandas_datareader_cache',
                                              backend='sqlite', expire_after=datetime.timedelta(hours=8))

# request cache
requests_cache.install_cache(cache_name='requests_cache',
                             backend='sqlite', expire_after=datetime.timedelta(minutes=10))


def _request(url, enable_cache=True):
    if not enable_cache:
        with requests_cache.disabled():  # temporary disabling caching
            return requests.get(url, headers=utils.request_headers)
    else:
        return requests.get(url, headers=utils.request_headers)
    # print('request from cache:', response.from_cache)


def _get_stock_data(stock_code, market_code, start, end):
    '''get data from yahoo through pandas datareader'''
    request_code = utils.get_stock_request_code(stock_code, market_code)
    print('[+] get data from pandas: {}, {}, {}, {}'.format(request_code, 'yahoo', start, end))
    if ENABLE_PANDAS_CACHE:
        df = web.DataReader(request_code, 'yahoo', start, end, session=PANDAS_SESSION)
    else:
        df = web.DataReader(request_code, 'yahoo', start, end)
    return df[df['Volume'] > 0]  # 过滤掉成交量是0的，某些情况下如节假日没有开盘成交量为0


def get_recent_data_generator(stock_code, market_code, days):
    df = get_recent_data(stock_code, market_code, days, update=True)
    df.columns = utils.translate_column_name(df.columns)
    yield (','.join([''] + df.columns.tolist() + ['\n'])).encode('utf-8')
    for i in range(df.shape[0]):
        yield (
            ','.join([str(df.index[i])]
                     + list(map(str, df.iloc[i].tolist()))
                     + ['\n'])
        ).encode('utf-8')


def get_recent_data(stock_code, market_code, days, update=True):
    return _get_data_with_cache_db(stock_code, market_code, days, update=update)


def _get_data_with_cache_db(stock_code, market_code, days, update=True):
    coll = mh.get_stock_collection(stock_code, market_code)
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=days)

    cache_lates = coll.find_latest(count=1)
    if cache_lates.count() == 0:
        # when cache db has nothing, request all
        print('[+] cache have nothing, so request all')
        _request_and_cache_db(stock_code, market_code, start, end)
    elif update:
        cache_lates_date = cache_lates[0]['date']
        print('[+] cache latest: {}'.format(cache_lates_date))
        coll.delete_one(date=cache_lates_date)
        # request the missing days and update the latest in db cache
        _request_and_cache_db(stock_code, market_code, cache_lates_date, end)

        cache_oldest = coll.find_oldest(count=1)
        if cache_oldest.count() > 0:
            cache_oldest_date = cache_oldest[0]['date']
            print('[+] cache oldest: {}'.format(cache_oldest_date))
            if start.date() + datetime.timedelta(days=7) < cache_oldest_date.date():
                e = cache_oldest_date - datetime.timedelta(days=1)
                _request_and_cache_db(stock_code, market_code, start, e, cache_exclude_dates=(cache_oldest_date.date(),))

    find_cols = {'_id': 0, 'date': 1, 'High': 1, 'Low': 1, 'Open': 1, 'Close': 1, 'Volume': 1, 'Adj Close': 1}
    data = coll.find_between_date(start, end, find_cols)
    values = []
    date_index = []
    for d in data:
        date_index.append(d.pop('date'))
        values.append(d)
    return pd.DataFrame(data=values, index=date_index)




def _request_and_cache_db(stock_code, market_code, start, end, cache_exclude_dates=None):
    try:
        df = _get_stock_data(stock_code, market_code, start, end)
        if df.shape[0] > 0:
            coll = mh.get_stock_collection(stock_code, market_code)
            coll.insert_dataframe(df, cache_exclude_dates)
    except KeyError as e:
        print_err(e)


def _get_recent_data_no_cache_db(stock_code, market_code, days):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    return _get_stock_data(stock_code, market_code, start, end)


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
