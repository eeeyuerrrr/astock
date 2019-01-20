import random
import time

from stock_analyze.models import Stock
from stock_analyze.helper.stock_data_manager import get_recent_data
from a_stock.utils import print_err


def start_scrapy():
    count = 0
    stocks = Stock.objects.filter()[count:]
    print('[+] Total {} stocks '.format(stocks.count()))
    for s in stocks:
        try:
            count += 1
            print('[+] Scraping the {} item'.format(count))
            print('[+] stock_code: {}, market_code: {}'.format(s.code, s.market_code))
            get_recent_data(s.code, s.market_code, 400)
            print('[+] scrapy success.')
            print('[+] sleep a random time...'+'\n')
            time.sleep(random.random())
        except Exception as e:
            print('[-] Error happened.')
            print_err(e)
