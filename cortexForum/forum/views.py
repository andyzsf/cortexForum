# -*- coding:utf-8 -*-
import json, hashlib, math

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import Topic, Reply, Notification, Collect, Node
# from cortexForum.authen.models import ForumUser
from .forms import CreateForm, ReplyForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import json as simplejson


# Create your views here.

# 这一部分主要是对各种的 topic 部分的逻辑进行处理


# 1. 获得整初始化页面的内容
# 先不对分页的内容进行处理
def get_homepage(request):
    user = request.user

    # 显示帖子内容，热门帖子，热门回复
    topics = Topic.objects.get_all_topic()
    # 添加分页的内容
    paginator=Paginator(topics,10)
    page=request.GET.get('page')
    try:
        topics=paginator.page(page)
    except PageNotAnInteger:
        topics=paginator.page(1)
    except EmptyPage:
        topics=paginator.page(paginator.num_pages)
    # 生成排列式
    pagerank=[x+1 for x in xrange(topics.paginator.num_pages)]

    hot_nodes = Node.objects.get_all_hot_Node()
    hot_topics = Topic.objects.get_hot_topic()
    hot_replies = Reply.objects.get_hot_reply()

    # 显示当前系统的运行状态,可能的话加上只在今天进行回复和发表的主题
    # 可以用 {% exntends %}来简化，之后再说
    # user_count = authen.ForumUser.objects.count()
    node_count = Node.objects.all().count()
    topic_count = Topic.objects.all().count()
    reply_count = Reply.objects.all().count()
    target = {1, 2, 3}
    notifications_count=Notification.objects.filter(status=0).count()
    context = {
        'user': user,
        'topics': topics,
        'hot_nodes': hot_nodes,
        'hot_topics': hot_topics,
        'hot_replies': hot_replies,
        # 'user_count': user_count,
        'node_count': 1,
        'topic_count': topic_count,
        'reply_count': reply_count,
        'target': {1, 2, 3},
        'notifications_count':notifications_count,
        'pagerank':pagerank,
    }

    return render(request, 'forum/homepage.html', context)


# 返回某个具体的 topic 的内容
def get_topic(request, topic_id=None):
    # 先用最直接的吧，返回所有的 reply 内容

    # 首先进行 ajax 的处理

    user = request.user if request.user.is_authenticated() else None
    reply = Reply.objects.get_all_replies_by_topic(topic_id=topic_id)

    # 在成功显示之后，要能够添加评论
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = Reply(
                    content=form.cleaned_data.get('content')
            )
            topic = Topic.objects.get(id=topic_id)
            reply.topic = topic
            reply.author_id = user.id
            reply.save()
            reply_count = topic.reply_count + 1
            #topic.update(reply_count=reply_count)
            # update() 针对所有的 objects() 对象而言
            # 增加对应 topic 的回复数
            topic.reply_count=reply_count
            topic.save()
            # 增加对主题发布者的信息提醒
            if user.id != topic.author_id:
                notification=Notification(
                    content=form.cleaned_data.get('content'),
                    involved_user=topic.author,
                    involved_topic=topic,
                    involved_reply=reply,
                    trigger_user=user.forumuser,
                )
                noti=[]
                noti.append(notification)
                Notification.objects.bulk_create(noti)



            return HttpResponseRedirect(reverse('get_topic', kwargs={'topic_id': topic_id}))

    else:
        form = ReplyForm()
    topic=Topic.objects.get(id=topic_id)

    context = {
        'user': user,
        'reply': reply,
        'form': form,
        'topic':topic,
    }
    # 在成功显示之后，要能够添加评论


    return render(request, 'forum/get_topic.html', context)


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


def get_topic_by_node(request, slug):
    # 根据 slug 来得到所对应的所有 topic 内容以及关于 topic 的介绍
    # node=Node.objects.get_object_or_404(Node,slug=slug)
    user = request.user
    node_topic = Topic.objects.get_all_topic_by_node_slug(node_slug=slug)
    context = {
        'user': user,
        'node_topic': node_topic,
        'slug':slug,
    }
    return render(request, 'forum/get_topic_node.html', context)


def upvote(request):
    # Ajax 来同步赞同数和反对数
    # 未完成，无法同步显示
    # jsp 已经不仅仅是一门前端语言，更准确的说是 web 开发过程中的一门通用语言
    if request.is_ajax():
        upvote_count = request.POST.get('upvote_count', '')
        id = request.POST.get('reply_id', '')
        reply = Reply.objects.get(id=reply_id)
        reply.update(
                upvote_count=upvote_count,
                agree_count=upvote_count - reply.downvote_count,
        )
        respose_dict = {
            'upvote_count': upvote_count,
        }
        return HttpResponse(simplejson.dumps(respose_dict), mimetype="application/json")
        # return render(request,'forum/upvote.html')

def get_user_profile(request,user_name):
    # 根据用户名来获取对应的主页
    user=User.objects.get(username=user_name)
    # 得到用户发表的主题和回复的信息
    user_topic=Topic.objects.get_all_topic_create_by_user(user.username)
    user_reply=Reply.objects.get_all_replies_by_user_id(user.username)

    context={
        'username':user.username,
        'introduce':user.forumuser.introduce,
        'fortune':user.forumuser.fortune,
        'updated':user.forumuser.updated,
        'website':user.forumuser.website,
        'github':user.forumuser.github,
        'douban':user.forumuser.douban,
        'weibo':user.forumuser.weibo,

        'user_topic':user_topic,
        'user_reply':user_reply,
    }
    return render(request,'authen/user_profile.html',context)

def get_wiki(request):
    return render(request,'forum/wiki.html')
