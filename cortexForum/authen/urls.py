# -*- coding:utf-8 -*-
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^register/$', views.user_register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^forget_password/$', views.user_forget_password, name='forgetPassword'),
    url(r'^set_password/$', views.user_set_password, name='setPassword'),


]
