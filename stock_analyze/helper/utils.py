

request_headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
                  '(KHTML, like Gecko) Ubuntu Chromium/70.0.3538.110 Chrome/70.0.3538.110 Safari/537.36'
}

COLUMNS_NAME_TRANSLATE = {
    'High': '最高价',
    'Low': '最低价',
    'Open': '开盘价',
    'Close': '收盘价',
    'Adj Close': '调整收盘价',
    'Volume': '成交量',
    'date': '日期',
}


def translate_column_name(columns):
    return [COLUMNS_NAME_TRANSLATE[x] for x in columns]


def df2html(df):
    return df.to_html()

def get_stock_request_code(stock_code, market_code):
    yahoo_marketcode = {'1': '.SS', '2': '.SZ'}
    request_code = stock_code + yahoo_marketcode[str(market_code)]
    return request_code


def log(func):
    def wrapper(*args, **kwargs):
        print('[+] {} call, args: {}, kwargs: {}'.format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper