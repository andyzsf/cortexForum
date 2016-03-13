# -*- coding:utf-8 -*-
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^topic/create/(.*)/$', views.create_topic, name='create_topic'),
    url(r'^$', views.get_homepage, name='homepage'),
    url(r'^forum/topic/(.*)/$',views.get_topic,name='get_topic'),
    url(r'^forum/node/(.*)/$',views.get_topic_by_node,name='get_topic_by_node'),
    url(r'^upvote/$',views.upvote,name='upvote'),
    url(r'user/(.*)/$',views.get_user_profile,name='get_user_profile'),
    url(r'^wiki/$',views.get_wiki,name='get_wiki'),
]
