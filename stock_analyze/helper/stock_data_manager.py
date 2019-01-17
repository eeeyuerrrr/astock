import datetime

import stock_analyze.helper.stock_data as sd
import stock_analyze.helper.mongodb_helper as mh
import pandas as pd


def get_data(stock_code, market_code, days):
    coll = mh.get_stock_collection(stock_code, market_code)
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=days)

    cache_lates = coll.find_latest(count=1)
    if cache_lates.count() == 0:
        # when cache db has nothing, request all
        print('[+] cache have nothing, so request all')
        _request_and_cache(stock_code, market_code, start, end)
    else:
        cache_lates_date = cache_lates[0]['date'].date()
        print('[+] cache latest: {}'.format(cache_lates_date))
        if end.date() > cache_lates_date:
            # when cache db latest day early than today, request the missing days
            s = cache_lates_date + datetime.timedelta(days=1)
            _request_and_cache(stock_code, market_code, s, end, cache_exclude_dates=(cache_lates_date,))
        else:
            # when cache db latest day is today, request and update today
            coll.delete_one(date=cache_lates[0]['date'])
            _request_and_cache(stock_code, market_code, end, end)

        cache_oldest = coll.find_oldest(count=1)
        cache_oldest_date = cache_oldest[0]['date'].date()
        if start.date() < cache_oldest_date:
            print('[+] cache oldest: {}'.format(cache_oldest_date))
            e = cache_oldest - datetime.timedelta(days=1)
            _request_and_cache(stock_code, market_code, start, e, cache_exclude_dates=(cache_oldest_date,))

    columns = {'_id':0, 'date':1, 'High':1, 'Low':1, 'Open':1, 'Close':1, 'Volume':1, 'Adj Close':1}
    df = pd.DataFrame(list(coll.find_between_date(start, end, columns)))
    df.columns = sd.translate_column_name(df.columns)
    return df


def _request_and_cache(stock_code, market_code, start, end, cache_exclude_dates=None):
    df = sd.get_stock_data(stock_code, market_code, start, end)
    if df.shape[0] > 0:
        coll = mh.get_stock_collection(stock_code, market_code)
        coll.insert_dataframe(df, cache_exclude_dates)
