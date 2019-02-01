# coding: utf-8
import datetime

import pymongo
import weakref
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, BulkWriteError
from a_stock.utils import print_err
from stock_analyze.helper.utils import get_stock_request_code


QUERY_RESULT_BATCH_SIZE = 400

stock_collections = weakref.WeakValueDictionary()


def get_stock_collection(stock_code, market_code):
    coll_name = get_stock_request_code(stock_code, market_code)
    if not coll_name in stock_collections:
        s = StockDataCollection(coll_name)
        stock_collections[coll_name] = s
    else:
        s = stock_collections[coll_name]
    return s


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MongoDB(object, metaclass=Singleton):

    def __init__(self):
        client = MongoClient(
            host=settings.MANGODB['host'],
            port=settings.MANGODB['port'],
            maxPoolSize=settings.MANGODB['max_pool'],
        )
        self.db = client[settings.MANGODB['db']]

    def get_collection(self, name):
        return self.db[name]


class StockDataCollection:

    def __init__(self, collection_name):
        self.col = MongoDB().get_collection(collection_name)
        if not self.is_index_exist('date'):
            self.create_index('date', unique=True)

    def insert_one(self, document):
        return self.col.insert_one(document)

    def insert_many(self, documents):
        return self.col.insert_many(documents)

    def insert_dataframe(self, df, exclude_dates=None):
        try:
            print('[+] inserting dataframe to mangodb: {} items'.format(df.shape[0]))
            ds = []
            for i in range(df.shape[0]):
                s = df.iloc[i]
                if (exclude_dates is not None) and (s.name.date() in exclude_dates):
                    continue

                d = s.to_dict()
                d['date'] = s.name
                ds.append(d)

            if len(ds) > 0:
                self.col.insert_many(ds)

        except DuplicateKeyError as e:
            print('[-] DuplicateKeyError: {!r}'.format(e))
        except BulkWriteError as e:
            print('[-] BulkWriteError: {!r}'.format(e))
            self.insert_dataframe_onebyone(df)
        except Exception as e:
            print('[-] Unknow Exception: {!r}'.format(e))
            print_err(e)

    def insert_dataframe_onebyone(self, df):
        try:
            print('[+] inserting dataframe one by one')
            for i in range(df.shape[0]):
                s = df.iloc[i]
                d = s.to_dict()
                d['date'] = s.name
                self.col.insert_one(d)
        except DuplicateKeyError as e:
            print('[-] DuplicateKeyError: {!r}'.format(e))
        except Exception as e:
            print('[-] Unknow Exception: {!r}'.format(e))
            print_err(e)

    def find(self, **kwargs):
        '''return a cursor, which is iterable'''
        return self.col.find(kwargs or {}) \
            .sort([('date', pymongo.DESCENDING)]) \
            .batch_size(QUERY_RESULT_BATCH_SIZE)

    def find_one(self, **kwargs):
        return self.col.find_one(kwargs or {})

    def count_documents(self, **kwargs):
        return self.col.count_documents(kwargs or {})

    def find_lte_date(self, date):
        return self.col.find({
            'date': {
                '$lte': date
            }
        }).sort([('date', pymongo.DESCENDING)])

    def find_gte_date(self, date):
        return self.col.find({
            'date': {
                '$gte': date
            }
        }).sort([('date', pymongo.DESCENDING)]) \
            .batch_size(QUERY_RESULT_BATCH_SIZE)

    def find_between_date(self, start, end, columns=None):
        return self.col.find({
            'date': {
                '$gte': start,
                '$lte': end
            }
        }, columns or {}).sort([('date', pymongo.DESCENDING)]) \
            .batch_size(QUERY_RESULT_BATCH_SIZE)

    def find_latest(self, count=1, **kwargs):
        return self.col.find(kwargs or {}) \
            .sort([('date', pymongo.DESCENDING)]) \
            .limit(count) \
            .batch_size(QUERY_RESULT_BATCH_SIZE)

    def find_oldest(self, count=1, **kwargs):
        return self.col.find(kwargs or {}) \
            .sort([('date', pymongo.ASCENDING)]) \
            .limit(count) \
            .batch_size(QUERY_RESULT_BATCH_SIZE)

    def delete_one(self, **kwargs):
        return self.col.delete_one(kwargs or {})

    def delete_many(self, **kwargs):
        return self.col.delete_many(kwargs or {})

    def create_index(self, col_name, unique):
        return self.col.create_index([(col_name, pymongo.DESCENDING)], unique=unique)

    def is_index_exist(self, col_name):
        return '{}_1'.format(col_name) in self.col.index_information()

    def drop_index(self, col_name):
        return self.col.drop_index('{}_1'.format(col_name))


if __name__ == '__main__':
    # set up django env
    import os
    import sys
    import django

    pathname = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, pathname)
    sys.path.insert(0, os.path.abspath(os.path.join(pathname, '../..')))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "a_stock.settings")
    django.setup()

    import stock_analyze.helper.stock_data_manager as sd

    df = sd.get_recent_data('000001', 1, 90)
    sc = get_stock_collection(sd.get_stock_request_code('000001', 1))
    sc.insert_dataframe(df)
