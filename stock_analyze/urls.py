from django.urls import path

from . import views

app_name = 'stock_analyze'

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
    path('api/industries/', views.IndustryList.as_view(),
         name='api-industry-list'),
    path('api/industries/<int:pk>/', views.IndustryDetail.as_view(),
         name='api-industry-detail'),
    path('api/industries/stocks_updown/', views.all_industry_stocks_updown,
         name='api-all-stocks-updown'),
    path('api/industries/stocks_updown/<int:industry_id>/', views.industry_stocks_updown,
         name='api-stocks-updown'),
    path('api/stocks/<int:pk>/', views.StockDetail.as_view(),
         name='api-stock-detail'),
    path('api/stocks/cur_price_realtime/<stock_code>/<market_code>/', views.stock_cur_price_realtime,
         name='api-stock-cur-price-realtime'),
    path('api/stocks/cur_price/', views.stock_cur_price,
         name='api-stock-cur-price'),
    path('api/stocks/search/', views.stocks_search, name='api-stocks-search'),
    path('api/stocks/beta/<id>', views.stock_beta, name='api-stocks-beta'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~ api html ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('api/industries/stocks_corr_analyzation/<int:industry_id>', views.industry_stocks_corr_analyzation,
         name='industry_stocks_corr_analyzation'),
    path('api/stocks/recent_data/<int:stock_id>/<int:days>', views.stock_recent_data,
         name='stock_recent_data'),
    path('api/stocks/stock_pv_analyzation/<int:stock_id>', views.stock_pv_analyzation,
         name='stock_pv_analyzation'),
    path('api/stocks/stocks_corr_analyzation/<int:stock_id>', views.stocks_corr_analyzation,
         name='stocks_corr_analyzation'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~ api file ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('api/data_download/stocks/<int:stock_id>/<int:days>', views.download_stock_data,
         name='api-download-stock-data'),

]
