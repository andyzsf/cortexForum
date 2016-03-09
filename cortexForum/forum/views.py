# -*- coding:utf-8 -*-
import json, hashlib, math

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import Topic, Reply, Notification, Collect, Node
# from cortexForum.authen.models import ForumUser
from .forms import CreateForm, ReplyForm


# Create your views here.

# 这一部分主要是对各种的 topic 部分的逻辑进行处理


# 1. 获得整初始化页面的内容
# 先不对分页的内容进行处理
def get_homepage(request):
    user = request.user

    # 显示帖子内容，热门帖子，热门回复
    topics = Topic.objects.get_all_topic()
    hot_nodes = Node.objects.get_all_hot_Node()
    hot_topics = Topic.objects.get_hot_topic()
    hot_replies = Reply.objects.get_hot_reply()

    # 显示当前系统的运行状态,可能的话加上只在今天进行回复和发表的主题
    # 可以用 {% exntends %}来简化，之后再说
    # user_count = authen.ForumUser.objects.count()
    node_count = Node.objects.all().count()
    topic_count = Topic.objects.all().count()
    reply_count = Reply.objects.all().count()

    context = {
        'user': user,
        'topics': topics,
        'hot_nodes': hot_nodes,
        'hot_topics': hot_topics,
        'hot_replies': hot_replies,
        # 'user_count': user_count,
        'node_count': node_count,
        'topic_count': topic_count,
        'reply_count': reply_count,
    }

    return render(request, 'forum/homepage.html', context)


# 返回某个具体的 topic 的内容
def get_topic(request):
    pass


# 创建 topic
@login_required()
def create_topic(request, slug=None):
    # 必须在某一个固定的节点里建立帖子
    # 创建新的帖子
    user = request.user
    # author=authen.ForumUser.objects.filter(user=user)
    node = get_object_or_404(Node, slug=slug)

    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            topic = Topic(
                    title=form.cleaned_data.get('title'),
                    content=form.cleaned_data.get('content'),
                    # 接下来进行更新就行了
                    node=node,
                    # 用 abstractuser 就好办多了
                    # author=author,
            )
            # user=User.objects.filter(user.id=user.id)
            # 还真是 tricky 啊，__ 和 _ 傻傻分不清……
            topic.author_id = user.id
            topic.save()
            node.topic_count = node.topic_count + 1
            # model 用毛线save,那是对 modelForm 用的
            # topic.save(commit=False)

            '''
            fortune = topic.author__fortune - 4
            if reputation < 0:
                messages.warning(request, u'财富不足，无法发帖')
                return HttpResponseRedirect(reverse('homepage'))
            authen.ForumUser.objects.get(id=user.id).update(fortune=fortune)
            '''
            return HttpResponseRedirect(reverse('homepage'))
            # httpresponseredirect vs redirect,参见：
            # http://stackoverflow.com/questions/13304149/what-the-difference-between-using-django-redirect-and-httpresponseredirect
    else:
        form = CreateForm()

    context = {
        'user': user,
        'form': form,
        'slug': slug,
    }
    return render(request, 'forum/create_topic.html', context)
