from django.urls import path
from . import views

app_name = 'stock_analyze'

urlpatterns = [
    # ~~~~~~~~~~~~~~~~~~~~~ page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ex: /stock_analyze/page/index
    path('page/index/', views.page_index, name='page-index'),
    path('page/industry_list/', views.page_industries, name='page-industries'),
    path('page/industries/<int:id>/', views.page_industry_detail, name='page-industry-detail'),
    path('page/stocks/<int:id>/', views.page_stock_detail, name='page-stock-detail'),

    # ~~~~~~~~~~~~~~~~~~~~~~ api json ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ex: /stock_analyze/api/industries
    path('api/industries/', views.IndustryList.as_view(), name='api-industry-list'),
    path('api/industries/<int:pk>/', views.IndustryDetail.as_view(), name='api-industry-detail'),
    path('api/industries/stocks_updown', views.all_industry_stocks_updown, name='api-all-stocks-updown'),
    path('api/industries/stocks_updown/<int:industry_id>', views.industry_stocks_updown, name='api-stocks-updown'),
    path('api/stocks/<int:pk>/', views.StockDetail.as_view(), name='api-stock-detail'),
    path('api/stocks/cur_price_realtime/<stock_code>/<market_code>', views.stock_cur_price_realtime,
         name='api-stock-cur-price-realtime'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~ api html ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('industries/stocks_corr_analyzation/<int:industry_id>', views.industry_stocks_corr_analyzation,
         name='industry_stocks_corr_analyzation'),
    path('stocks/recent_data/<int:stock_id>/<int:days>', views.stock_recent_data,
         name='stock_recent_data'),
    path('stocks/stock_pv_analyzation/<int:stock_id>', views.stock_pv_analyzation,
         name='stock_pv_analyzation'),
    path('stocks/stocks_corr_analyzation/<int:stock_id>', views.stocks_corr_analyzation,
         name='stocks_corr_analyzation'),

]
