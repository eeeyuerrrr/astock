import json

from django.db import models
from django.urls import reverse

import stock_analyze.helper.stock_data as sd


# ~~~~~~~~~~~~~~~~~~~~~ Stock ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Stock(models.Model):
    name = models.CharField(max_length=10, unique=True, null=False)
    code = models.CharField(max_length=10, null=False)
    market_code = models.PositiveSmallIntegerField()
    isindex = models.BooleanField(default=False)

    class Meta:
        unique_together = ('code', 'market_code')

    def __str__(self):
        return '%s(%s)' % (self.name, self.code)

    def __repr__(self):
        return self.__str__()

    def detail_page_url(self):
        return reverse('stock_analyze:page-stock-detail', args=[self.id])

    def market_name(self):
        market = {1: '上证', 2: '深证'}
        return market[self.market_code] if self.market_code in market.keys() else '未知'

    market_name.admin_order_field = 'market_code'

    def get(**kwargs):
        stocks = Stock.objects.filter(**kwargs).prefetch_related('industry_set')
        if ( stocks is not None) and len(stocks)>0 :
            return stocks[0]
        else:
            raise Stock.DoesNotExist

    def get_belong_industries(self):
        return self.industry_set.all()

    def cur_price(self, enable_cache=True):
        pc, pc_change, pc_change_pct, time = sd.cur_price_info(self.code, self.market_code,
                                                               enable_cache=enable_cache)
        return {'pc': pc, 'pc_change': pc_change, 'pc_change_pct': pc_change_pct, 'update_time': time}

    def recent_data(self, days):
        return sd.get_recent_data(self.code, self.market_code, days)

    def pv_analyzation(self):
        return sd.get_pv_analyzation(self.code, self.market_code)

    def corr_with_industry_stocks(self, industry):
        compare_stocks = industry.get_stocks()
        return sd.stocks_corr_analyzation(90, self, *list(compare_stocks))


# ~~~~~~~~~~~~~~~~~ Industry ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Industry(models.Model):
    name = models.CharField(max_length=10, null=False)
    code = models.CharField(max_length=10, unique=True, null=False)
    stocks = models.ManyToManyField(Stock)
    order = models.SmallIntegerField(default=100)

    def __str__(self):
        return '%s' % self.name

    def __repr__(self):
        return self.__str__()

    def detail_page_url(self):
        return reverse('stock_analyze:page-industry-detail', args=[self.id])

    def get(**kwargs):
        #  prefetch_related同时查询相关字段放入缓存，减少数据库查询
        industrys = Industry.objects.filter(**kwargs).prefetch_related('stocks')
        if (industrys is not None) and (len(industrys)>0):
            return industrys[0]
        else:
            raise Industry.DoesNotExist

    def get_stocks(self):
        return self.stocks.all()

    def stock_count(self):
        return self.stocks.all().count()

    @staticmethod
    def all_industry_stocks_updown():
        return sd.industry_stocks_updown_count()

    def cur_industry_stocks_updown(self):
        return Industry.all_industry_stocks_updown()[self.name]

    def industry_stocks_corr(self):
        compare_stocks = self.get_stocks()
        return sd.stocks_corr_analyzation(90, None, *list(compare_stocks))

# ~~~~~~~~~~~~~~~~~ Stock Index ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
