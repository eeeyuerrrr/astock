from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'stock_analyze'

CACHE_TIME_LONG = 60 * 24
CACHE_TIME_MEDIUM = 60 * 10
CACHE_TIME_SHORT = 60 * 1

urlpatterns = [
    # ~~~~~~~~~~~~~~~~~~~~~ page html~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ex: /stock_analyze/page/index
    path('page/index/', views.page_index,
         name='page-index'),
    path('page/industry_list/', views.page_industries,
         name='page-industries'),
    path('page/industries/<int:id>/', views.page_industry_detail,
         name='page-industry-detail'),
    path('page/stocks/<int:id>/', views.page_stock_detail,
         name='page-stock-detail'),
    path('page/index_detail/<stock_code>/<market_code>/', views.page_index_detail,
         name='page-index-detail'),
    path('page/stocks/rzrq/<int:id>', views.page_stock_rzrq, name='page-stock-rzrq'),

    # ~~~~~~~~~~~~~~~~~~~~~~ api json ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ex: /stock_analyze/api/industries
    path('api/industries/', cache_page(CACHE_TIME_LONG)(views.IndustryList.as_view()),
         name='api-industry-list'),
    path('api/industries/<int:pk>/', cache_page(CACHE_TIME_LONG)(views.IndustryDetail.as_view()),
         name='api-industry-detail'),
    path('api/industries/stocks_updown/', cache_page(CACHE_TIME_SHORT)(views.all_industry_stocks_updown),
         name='api-all-stocks-updown'),
    path('api/industries/stocks_updown/<int:industry_id>/', cache_page(CACHE_TIME_SHORT)(views.industry_stocks_updown),
         name='api-stocks-updown'),
    path('api/stocks/<int:pk>/', cache_page(CACHE_TIME_SHORT)(views.StockDetail.as_view()),
         name='api-stock-detail'),
    path('api/stocks/cur_price_realtime/<stock_code>/<market_code>/', views.stock_cur_price_realtime,
         name='api-stock-cur-price-realtime'),
    path('api/stocks/cur_price/', cache_page(CACHE_TIME_SHORT)(views.stock_cur_price),
         name='api-stock-cur-price'),
    path('api/stocks/search/', cache_page(CACHE_TIME_LONG)(views.stocks_search), name='api-stocks-search'),
    path('api/stocks/beta/<int:id>', cache_page(CACHE_TIME_LONG)(views.stock_beta), name='api-stocks-beta'),
    path('api/stocks/last_deal_data/<int:id>/', cache_page(CACHE_TIME_SHORT)(views.stock_last_deal_data),
         name='last_deal_data'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~ api html ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('api/industries/stocks_corr_analyzation/<int:industry_id>', cache_page(CACHE_TIME_LONG)(views.industry_stocks_corr_analyzation),
         name='industry_stocks_corr_analyzation'),
    path('api/stocks/recent_data/<int:stock_id>/<int:days>', cache_page(CACHE_TIME_LONG)(views.stock_recent_data),
         name='stock_recent_data'),
    path('api/stocks/stock_pv_analyzation/<int:stock_id>', cache_page(CACHE_TIME_LONG)(views.stock_pv_analyzation),
         name='stock_pv_analyzation'),
    path('api/stocks/stocks_corr_analyzation/<int:stock_id>', cache_page(CACHE_TIME_LONG)(views.stocks_corr_analyzation),
         name='stocks_corr_analyzation'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~ api file ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('api/data_download/stocks/<int:stock_id>/<int:days>', views.download_stock_data,
         name='api-download-stock-data'),

]
