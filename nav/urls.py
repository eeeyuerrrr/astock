from django.urls import path
from . import views



app_name = 'nav'

urlpatterns = [
    # ~~~~~~~~~~~~~~~~~ page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('page/sites/', views.page_site_list, name='page-sites'),

    # ~~~~~~~~~~~~~~~~~ api ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('api/sites/', views.SiteList.as_view(), name='api-sites'),
]


