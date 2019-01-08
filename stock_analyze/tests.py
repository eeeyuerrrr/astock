from django.test import TestCase
from .models import Industry, Stock
from django.test import Client
from django.urls import reverse


# 测试时会创建一个特殊的数据库供测试使用
# 数据库会在每次调用测试方法前被重置


def create_industry(code, name, stocks=None):
    industry = Industry.objects.create(name=name, code=code)
    if stocks:
        industry.stocks.add(*stocks)
    return industry


def create_stock(code, name, market_code, belong_industries=None):
    stock = Stock.objects.create(name=name, code=code, market_code=market_code)
    if belong_industries:
        stock.industry_set.add(*belong_industries)
    return stock


def update_industry_stock_relation(industry, stocks):
    return industry.stocks.add(*stocks)


def set_up_test_data():
    stock1 = create_stock('300462', '华铭智能', 2)
    stock2 = create_stock('001696', '宗申动力', 2)
    stock3 = create_stock('600968', '湖南天雁', 1)
    create_industry('BK0429', '交运设备', [stock1, stock2, stock3])

    industry2 = create_industry('BK0475', '银行')
    stock4 = create_stock('601169', '北京银行', 1)
    stock5 = create_stock('002142', '宁波银行', 2)
    update_industry_stock_relation(industry2, [stock4, stock5])


class IndustryModelTest(TestCase):

    def test_industry_stock(self):
        set_up_test_data()
        industries = Industry.objects.all()
        for industry in industries:
            self.assertIsNotNone(industry.name)
            self.assertIsNotNone(industry.code)
            stocks = industry.get_stocks()
            for stock in stocks:
                self.assertIsNotNone(stock.name)
                self.assertIsNotNone(stock.code)
                self.assertIsNotNone(stock.market_code)
                stock_belong_industries = []
                for ind in stock.get_belong_industries():
                    stock_belong_industries.append(ind)
                self.assertIn(industry, stock_belong_industries)

    def test_industry_sample(self):
        self.assertEqual(Industry.objects.exists(), False)
        self.assertEqual(Stock.objects.exists(), False)
        set_up_test_data()
        self.assertEqual(Industry.objects.exists(), True)
        self.assertEqual(Stock.objects.exists(), True)
        industry = Industry.get(name='交运设备')
        stocks = []
        for stock in industry.get_stocks():
            stocks.append(stock)
        stock1 = Stock.get(name='华铭智能')
        self.assertIn(stock1, stocks)

    def test_client_query(self):
        set_up_test_data()
        response = self.client.get(reverse('page-industries'))
        self.assertQuerysetEqual(
            response.context['industries'],
            ['<Industry: 交运设备>', '<Industry: 银行>']
        )
