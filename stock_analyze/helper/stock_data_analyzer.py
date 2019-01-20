from pandas import DataFrame, Series

from a_stock.utils import print_err
from stock_analyze.helper.stock_data_manager import get_recent_data
from stock_analyze.exceptions import DataMissingError


def _pc_volume_corr(df_basic_data):
    '''calculate the corr between price pct change and volume pct change'''
    pct_change = DataFrame(df_basic_data['Adj Close'].pct_change())
    return pct_change.corrwith(df_basic_data['Volume'].pct_change())


def beta(stock_code, index_code, market_code):
    ''' 贝塔系数 '''

    stock365 = get_recent_data(stock_code, market_code, 365, update=False)
    if stock365.shape[0] < 200:
        raise DataMissingError

    index365 = get_recent_data(index_code, market_code, 365, update=False)
    if index365.shape[0] < 200:
        raise DataMissingError

    s200 = stock365[:200]
    i200 = index365[:200]
    ser_s_pct = s200['Adj Close'].pct_change()
    ser_i_pct = i200['Adj Close'].pct_change()

    # 标准差
    s_std = ser_s_pct.std()
    i_std = ser_i_pct.std()
    #  相关系统
    corr = ser_s_pct.corr(ser_i_pct)
    # 贝塔
    b = corr * (s_std / i_std);
    return '{:.2f}'.format(b)


def pv_analyzation(stock_code, market_code):
    '''计算最近90,30,7交易日的平均收盘价，平均成交量'''
    _df365 = get_recent_data(stock_code, market_code, 365, update=False)
    if _df365.shape[0] < 90:
        raise DataMissingError

    df90 = _df365[:90]
    df30 = _df365[:30]
    df7 = _df365[:7]
    # 平均值
    p_mean_90 = df90['Adj Close'].mean()
    v_mean_90 = df90['Volume'].mean()
    p_mean_30 = df30['Adj Close'].mean()
    v_mean_30 = df30['Volume'].mean()
    p_mean_7 = df7['Adj Close'].mean()
    v_mean_7 = df7['Volume'].mean()

    row_p_mean = Series([p_mean_90, p_mean_30, p_mean_7]).map(lambda x: '%.2f' % x)
    row_v_mean = Series([v_mean_90, v_mean_30, v_mean_7]).map(lambda x: '{:.2f}'.format(x / 1000000))

    return DataFrame(columns=['90日', '30日', '7日'],
                     index=['平均收盘价', '平均成交量/万手'],
                     data=[row_p_mean.values, row_v_mean.values])


def stocks_corr_analyzation(days, stock, *compare_stocks):
    ''' analyze the pct_change corr between stocks '''
    compare_stock_data = {}
    for s in compare_stocks:
        try:
            compare_stock_data[s.name] = get_recent_data(s.code, s.market_code, days, update=False)
        except Exception as e:
            print_err(e)

    df_compare_stocks_pct = DataFrame({
        stock: df['Adj Close'] for stock, df in compare_stock_data.items()
    }).pct_change()

    if stock is not None:
        if stock in compare_stocks:
            ser_stock_pct = df_compare_stocks_pct[stock.name]
            df_compare_stocks_pct.drop(columns=stock.name, inplace=True)
        else:
            df = get_recent_data(stock.code, stock.market_code, days, update=False)
            ser_stock_pct = df['Adj Close'].pct_change()

        ser = df_compare_stocks_pct.corrwith(ser_stock_pct)
        # 筛选出0.5以上的，并格式化
        ser = ser[ser >= 0.5].map(lambda x: '{:.2f}'.format(x))
        ser.name = '涨跌相关性'
        return ser.to_frame()
    else:
        df = df_compare_stocks_pct.corr()
        return df.applymap(lambda x: '{:.2f}'.format(x))

# if __name__ == '__main__':
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

# print(industry_stocks_updown_count())

# gen = get_recent_data_generator('000001', '2', 7)
# for g in gen:
#     print(g)
