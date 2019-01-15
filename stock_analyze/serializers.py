from rest_framework import serializers
from .models import Industry, Stock


class IndustrySerializer4List(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'name', 'code', 'detail_page_url')


class StockSerializer4List(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('id', 'name', 'code', 'market_code', 'detail_page_url')


class StockSerializer4Detail(serializers.ModelSerializer):
    industry_set = IndustrySerializer4List(many=True)

    class Meta:
        model = Stock
        fields = ('id', 'name', 'code', 'market_code', 'industry_set',
                  'cur_price', 'market_name', 'detail_page_url')
        depth = 1


class IndustrySerializer4Detail(serializers.ModelSerializer):
    stocks = StockSerializer4List(many=True)

    class Meta:
        model = Industry
        fields = ('id', 'name', 'code', 'stocks')
        depth = 1
