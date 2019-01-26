from django.views.decorators.cache import cache_page

from a_stock.throttles import DownloadThrottle
from a_stock.utils import print_err
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status, generics
from rest_framework.decorators import api_view, renderer_classes, throttle_classes
from rest_framework.exceptions import APIException, ParseError, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import StaticHTMLRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

import stock_analyze.helper.stock_data_manager as sd
from stock_analyze.exceptions import DataMissingError
from .models import Industry, Stock
from .serializers import StockSerializer4Detail, IndustrySerializer4List, IndustrySerializer4Detail, \
    StockSerializer4List
from stock_analyze.helper.utils import df2html, translate_column_name

QUERY_DATA_MAX_DAYS = 365


# rest_framework pagination class
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


# ~~~~~~~~~~~~~~~~~~~~~~ page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_index(request):
    return Response(template_name='stock_analyze/home.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_industries(request):
    return Response(template_name='stock_analyze/industries.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_industry_detail(request, id):
    return Response({'id': id}, template_name='stock_analyze/industry_detail.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_stock_detail(request, id):
    return Response({'id': id}, template_name='stock_analyze/stock_detail.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_index_detail(request, stock_code, market_code):
    index = get_object_or_404(Stock, code=stock_code, market_code=market_code)
    return Response({'id': index.id}, template_name='stock_analyze/index_detail.html')


def page_stock_rzrq(request, id):
    #  融资融券
    stock = get_object_or_404(Stock, id=id)
    if stock.isindex:
        return redirect('http://data.eastmoney.com/rzrq/')
    else:
        return redirect('http://data.eastmoney.com/rzrq/stock/{}.html'.format(stock.code))


# ~~~~~~~~~~~~~~~~~~~~~~~ api ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class IndustryList(generics.ListAPIView):
    queryset = Industry.objects.order_by('order')
    serializer_class = IndustrySerializer4List
    pagination_class = StandardResultsSetPagination


class IndustryDetail(generics.RetrieveAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer4Detail


class StockDetail(generics.RetrieveAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer4Detail


@api_view(('GET',))
def stock_cur_price_realtime(request, stock_code, market_code):
    try:
        pc, pc_change, pc_change_pct, time = sd.cur_price_info(
            stock_code, market_code, enable_cache=False)
        return Response(data={
            'pc': pc,
            'pc_change': pc_change,
            'pc_change_pct': pc_change_pct,
            'update_time': time
        })
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
def stock_cur_price(request):
    try:
        pc, pc_change, pc_change_pct, time = sd.cur_price_info(
            request.GET['stock_code'], request.GET['market_code'], enable_cache=False)
        return Response(data={
            'pc': pc,
            'pc_change': pc_change,
            'pc_change_pct': pc_change_pct,
            'update_time': time
        })
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
def all_industry_stocks_updown(request):
    try:
        updowns = Industry.all_industry_stocks_updown()
        return Response(updowns)
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
def industry_stocks_updown(request, industry_id):
    industry = get_object_or_404(Industry, id=industry_id)
    try:
        updowns = industry.cur_industry_stocks_updown()
        return Response(updowns)
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def stock_recent_data(request, stock_id, days):
    if days > QUERY_DATA_MAX_DAYS:  # 查询不超过一年
        raise ValidationError

    try:
        stock = Stock.get(id=stock_id)
        df = stock.recent_data(days)
        df.columns = translate_column_name(df.columns)
        table_html = df2html(df)
        return Response(table_html)
    except Stock.DoesNotExist:
        raise NotFound
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def stock_pv_analyzation(request, stock_id):
    try:
        stock = Stock.objects.get(id=stock_id)
        df = stock.pv_analyzation()
        table_html = df2html(df)
        return Response(table_html)
    except ObjectDoesNotExist:
        raise NotFound
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def stocks_corr_analyzation(request, stock_id):
    try:
        stock = Stock.get(id=stock_id)
        industry = stock.get_belong_industries()[0]
        df_corr = stock.corr_with_industry_stocks(industry)
        table_html = df2html(df_corr)
        return Response(table_html)
    except ObjectDoesNotExist:
        raise NotFound
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def industry_stocks_corr_analyzation(request, industry_id):
    try:
        industry = Industry.get(id=industry_id)
        df_corr = industry.industry_stocks_corr()
        table_html = df2html(df_corr)
        return Response(table_html)
    except ObjectDoesNotExist:
        raise NotFound
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
@throttle_classes((DownloadThrottle,))
def download_stock_data(request, stock_id, days):
    # need login
    if not request.user.is_authenticated:
        return redirect('account:page_login')

    # response StreamingHttpResponse to download csv file
    if days > QUERY_DATA_MAX_DAYS:
        raise ValidationError

    try:
        s = Stock.objects.get(id=stock_id)
        date = str(datetime.now().date())
        response = StreamingHttpResponse(
            sd.get_recent_data_generator(s.code, s.market_code, days), content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; filename="{}-{}-{}.csv"'.format(s.code, date, days)
        return response
    except ObjectDoesNotExist:
        raise NotFound
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
def stocks_search(request):
    try:
        kw = request.GET['kw']
        stocks = Stock.objects.filter(Q(name__contains=kw) | Q(code__contains=kw))[:100]
        serializer = StockSerializer4List(stocks, many=True)
        return Response(serializer.data)
    except KeyError:
        raise ParseError
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
def stock_beta(request, id):
    try:
        stock = Stock.objects.get(id=id)
        beta = stock.beta()
        return Response(dict(result=beta))
    except ObjectDoesNotExist:
        return Response(dict(result='数据缺失'))
    except DataMissingError:
        return Response(dict(result='数据缺失'))
    except Exception as e:
        print_err(e)
        raise APIException
