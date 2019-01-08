# coding: utf-8

import os
import sys
import django

# set up django env
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "a_stock.settings")
django.setup()

import MySQLdb
from stock_analyze.models import Stock, Industry

def get_db_connection():
    return MySQLdb.connect(
        host='127.0.0.1',
        port=3306,
        user='admin',
        passwd='sql123456',
        db='stock',
        charset='utf8'  # 要指定编码，否则中文可能乱码
    )


# 读取一个已经存在的数据库
def get_stocks():
    stocks = []
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('select name,code,market_code,industry_id from stock_info')
            results = cur.fetchall()
            for r in results:
                stocks.append({'name': r[0], 'code': r[1], 'market_code':r[2],'industry_id': r[3]})

    except Exception as e:
        print(repr(e))
    finally:
        if conn is not None:
            conn.close()
    return stocks


def get_industries():
    all_industry = {}
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('select name,code,id from industry')
            results = cur.fetchall()
            for r in results:
                all_industry[r[2]] = {'name':r[0], 'code':r[1] }
    except Exception as e:
        print(repr(e))
    finally:
        if conn is not None:
            conn.close()
    return all_industry

def main():
    stocks = get_stocks()
    industries = get_industries()
    for stock in stocks:
        industry = industries[stock['industry_id']]
        save2django(stock, industry)


def save2django(stock, industry):
    sto, created = Stock.objects.get_or_create(code=stock['code'], name=stock['name'], market_code=stock['market_code'])
    indus, created = Industry.objects.get_or_create(code=industry['code'], name=industry['name'])
    sto.industry_set.add(indus)


if __name__ == '__main__':
    main()
