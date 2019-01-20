import datetime

import pymongo
import pandas


def read_csv():
    with open('./scz.csv','rt', encoding='Latin3', errors='ignore') as f:
        count = 1
        for line in f:
            if count > 1:
                date, _, Open, High, Low, Close, Volume = line.split(',')
                yield ','.join((date.strip('"'), Open, High, Low, Close, Volume))
            else:
                yield line
            count += 1

def format_csv():
    with open('./scz_new.csv', 'wt', encoding='utf-8') as f:
        for line in read_csv():
            f.write(line)

def csv2mongo():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['stock_data']
    coll = db['399001.SZ']

    count = 1
    with open('./scz_new.csv', 'rt', encoding='utf-8') as f:
        for line in f:
            if count > 1:
                date, Open, High, Low, Close, Volume = line.strip().split(',')
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
                d = dict(date=date, Open=float(Open), High=float(High), Low=float(Low),
                         Close=float(Close), Volume=float(Volume))
                d['Adj Close'] = float(Close)
                coll.insert_one(d)

            count += 1


if __name__ == '__main__':
    csv2mongo()
