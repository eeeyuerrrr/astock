from django.conf.urls import url
from django.urls import path, include
from . import views

app_name = 'account'

urlpatterns = [
    # ~~~~~~~~~~~~~~~~~~~~~ page html~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('page/login/', views.page_login, name='page_login'),
    path('page/register/', views.page_register, name='page_register'),
    path('page/change_password/', views.page_change_password, name='page_change_password'),
    path('page/activate/<key>/', views.account_activate, name='page_activate'),
    path('page/reset_pw_user_idenfity/', views.page_reset_pw_user_identify, name='page_reset_pw_user_identiry'),
    path('page/page_reset_pw/<key>/', views.page_reset_pw_user, name='page_reset_pw'),

    # ~~~~~~~~~~~~~~~~~~~~~ api json~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/change_password/', views.api_change_password, name='api_change_password'),
    path('api/reset_pw_user_identify/', views.api_reset_pw_user_identify, name='api_reset_pw_user_identify'),
    path('api/reset_pw/', views.api_reset_pw, name='api_reset_pw'),

]
