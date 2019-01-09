import csv
import io

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse, FileResponse, StreamingHttpResponse
from rest_framework import status, generics, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Industry, Stock
import stock_analyze.helper.stock_data as sd
import traceback

from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes
from .serializers import StockSerializer, IndustrySerializer4List, IndustrySerializer4Detail
from rest_framework.response import Response
from rest_framework.reverse import reverse
from datetime import datetime
from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer


def print_err(err):
    print(repr(err))
    traceback.print_tb(err.__traceback__)


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
    return Response(template_name='stock_analyze/index.html')


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
    serializer_class = StockSerializer


@api_view(('GET',))
def stock_cur_price_realtime(request, stock_code, market_code):
    try:
        pc, pc_change, pc_change_pct, time = sd.cur_price_info(
            stock_code, market_code, enable_cache=False)
    except Exception as e:
        print_err(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(data={'pc': pc, 'pc_change': pc_change, 'pc_change_pct': pc_change_pct, 'update_time': time})


@api_view(('GET',))
def all_industry_stocks_updown(request):
    try:
        updowns = Industry.all_industry_stocks_updown()
    except Exception as e:
        print_err(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(updowns)


@api_view(('GET',))
def industry_stocks_updown(request, industry_id):
    try:
        industry = Industry.get(id=industry_id)
        updowns = industry.cur_industry_stocks_updown()
    except Industry.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print_err(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(updowns)


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def stock_recent_data(request, stock_id, days):
    try:
        if days > 365:  # 查询不超过一年
            raise Exception

        stock = Stock.get(id=stock_id)
        df = stock.recent_data(days)
        df.columns = sd.YAHOO_STOCK_DATA_COLUMNS_CHINESE
        table_html = sd.df2html(df)
    except Stock.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print_err(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(table_html)


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def stock_pv_analyzation(request, stock_id):
    try:
        stock = Stock.get(id=stock_id)
        df = stock.pv_analyzation()
        table_html = sd.df2html(df)
    except Stock.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print_err(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(table_html)


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def stocks_corr_analyzation(request, stock_id):
    try:
        stock = Stock.get(id=stock_id)
        industry = stock.get_belong_industries()[0]
        df_corr = stock.corr_with_industry_stocks(industry)
        table_html = sd.df2html(df_corr)
    except Stock.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print_err(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(table_html)


@api_view(('GET',))
@renderer_classes((StaticHTMLRenderer,))
def industry_stocks_corr_analyzation(request, industry_id):
    try:
        industry = Industry.get(id=industry_id)
        df_corr = industry.industry_stocks_corr()
        table_html = sd.df2html(df_corr)
    except Industry.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print_err(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(table_html)


def download_stock_data(request, stock_id, days):
    try:
        if days > 365:
            raise Exception('bad request, days too long.')
        s = Stock.get(id=stock_id)
        date = str(datetime.now().date())
        response = StreamingHttpResponse(
            sd.get_recent_data_generator(s.code, s.market_code, days), content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; filename="{}-{}-{}.csv"'.format(s.code, date, days)
    except Stock.DoesNotExist:
        raise Http404
    except Exception as e:
        print_err(e)
        return HttpResponse(status=500)
    else:
        return response
