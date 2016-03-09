# -*- coding:utf-8 -*-
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^topic/create/(.*)/$', views.create_topic, name='create_topic')
]
