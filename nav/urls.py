from django.urls import path
from . import views



app_name = 'nav'

urlpatterns = [
    # ~~~~~~~~~~~~~~~~~ page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('page/sites/', views.page_site_list, name='page-sites'),

    # ~~~~~~~~~~~~~~~~~ api ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('api/sites/', views.api_site_list, name='api-sites'),
    path('api/add_user_site/', views.api_add_user_site, name='api-add-user-site'),
    path('api/remove_user-site/', views.api_remove_user_site, name='api-remove-user-site'),
]


