# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# from ..authen import ForumUser  # 怎么引入？

# Create your models here.

'''
 ForumUser 对应的 attribute:

topic_author:发表的帖子对应的 author
last_reply_author:最后回复的作者

reply_author:作者发表的每一篇回复对应的 author
notify_user:当有回复的时候，参与回复的 author
trigger_user:当有回复的时候，发表该回复所在的帖子的 author

user_collect:返回所有收集的帖子
'''


class NodeManager(models.Manager):
    '''
    对节点进行管理
    1. 需要返回的是所有的热门节点
    '''

    # 返回热门节点，按照有主题的数量来排序
    def get_all_hot_Node(self):
        query = self.get_queryset().filter(topic_count__gte=0). \
            order_by('-topic_count')
        return query
        #


class Node(models.Model):
    '''
    论坛的节点，是发帖的地方
    '''
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    introduction = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    topic_count = models.IntegerField(default=0)

    objects = NodeManager()  # 为了进行个性化的定制


class TopicManager(models.Manager):
    '''
    进行主题的管理，返回相应的内容
    这里要自己想一下所有的这些该怎么完成
    1. 返回所有的 topic (在主界面展示)
    2. 根据不同节点的 slug 返回对应的 topic
    3. 返回一个人创建的所有 topic
    4. 返回一个人回复的所有 topic,不对，返回的是 reply 这里
    5. 可能还有其他有用的
    '''

    def get_all_topic(self):
        query = self.get_queryset().select_related('node', 'author', 'last_replied_by'). \
            all().order_by('-last_replied_time', '-reply_count', '-created_at')

        return query

    def get_hot_topic(self):
        query = self.get_queryset().select_related('node', 'author', 'last_replied_by'). \
            order_by('-reply_count')
        return query

    def get_all_topic_by_node_slug(self, node_slug):
        query = self.get_queryset().filter(node__slug=node_slug). \
            select_related('node', 'author', 'last_replied_by'). \
            order_by('-last_replied_time', '-reply_count', '-created_at')
        return query

    def get_all_topic_create_by_user(self, username=None):
        # foreignkey+onetoonefield
        query = self.get_queryset().filter(author__user__username = username). \
                select_related('node', 'author').order_by('-created_at')  # 按照创建时间排序
        return query


class Topic(models.Model):
    '''
    发帖子的基本单位

    related_name:
    notify_topic: 当有一个回复时，发生的 topic
    topic_collect: 收藏主题的对应表示
    '''
    title = models.CharField(max_length=128, unique=True)
    content = models.TextField()
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    reply_count = models.IntegerField(default=0)

    last_replied_time = models.DateTimeField(null=True, blank=True)
    node = models.ForeignKey(Node, related_name='node')
    author = models.ForeignKey('authen.ForumUser', related_name='topic_author')
    last_replied_by = models.ForeignKey('authen.ForumUser', related_name='last_reply_author',
                                        null=True, blank=True)

    objects = TopicManager()

    def __unicode__(self):
        return self.title


class ReplyManager(models.Manager):
    '''
    进行回复的管理，返回相应的内容
    要做的有以下几点：
    1.根据 topic 的 id/name 来返回所有的回复内容
    2.根据作者的 id/username 来返回所有的回复内容
    '''

    def get_all_replies_by_topic(self, topic_id):
        # 我不太确定这里的 select_related 是否要选择作者
        # select_related 看起来还不是任意的属性，比如说对该函数，就要用
        # Non-relational field given in select_related: 'content'. Choices are: topic, author
        query = self.get_queryset().select_related('topic', 'author'). \
            filter(topic__id=topic_id).order_by('updated_at')
        return query

    def get_hot_reply(self):
        query = self.get_queryset().select_related('topic', 'author'). \
                    filter(upvote_count__gte=0)[:10]
        return query

    def get_all_replies_by_user_id(self, user_name):
        query = self.get_queryset().select_related('topic', 'author'). \
            filter(author__user__username=user_name).order_by('-updated_at')
        return query

class Reply(models.Model):
    '''
    一个回复应该有什么样的属性呢

    related_name:
    notify_reply:有一个消息提醒时牵涉到的 reply
    '''
    content = models.TextField()
    upvote_count = models.IntegerField(default=0)
    downvote_count = models.IntegerField(default=0)
    agree_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    topic = models.ForeignKey(Topic, related_name='reply')
    author = models.ForeignKey('authen.ForumUser', related_name='reply_author')

    objects = ReplyManager()

    def __unicode__(self):
        return self.content


class CollectManager(models.Manager):
    '''
    显然返回的对象是根据用户 id/name 收集的所有帖子
    '''

    def get_all_collection_by_user(self, user_id):
        query = self.get_queryset().select_related('collect_user', 'collect_topic', ). \
            filter(collect_user__id=user_id).order_by('collected_at')
        return query


class Collect(models.Model):
    '''
    关于用户收集的所有帖子
    应该不是太难，明天早上起来练手
    '''
    collect_user = models.ForeignKey('authen.ForumUser', on_delete=models.CASCADE,
                                     related_name='user_collect')
    # CASCADE是默认的，当删除该用户的时候，就删除了所有他收藏的帖子
    collect_topic = models.ForeignKey(Topic, related_name='topic_collect')
    collected_at = models.DateTimeField(auto_now=True)

    objects = CollectManager()


class NotificationManager(models.Manager):
    '''
    很显然，Manager 的任务就是根据用户 id/name 获得所有的信息提醒
    '''

    def get_all_notifications_for_user(self, user_id):
        query = self.get_queryset().select_related('involved_topic', 'involved_user', 'trigger_user'). \
            filter(trigger_user__id=user_id).order_by('-occurence_time')
        return query

        # 我感觉如果要分页的话还是要用它的 count() 来返回所有的数量？


class Notification(models.Model):
    '''
    关于所有通知消息的内容
    消息提醒是状态，要和 reply 的内容分开
    '''
    status = models.IntegerField(default=0)  # 默认0为未读，1为已读
    content = models.TextField()
    involved_type = models.IntegerField(default=0)  # 0表示为回复，1表示为@
    involved_user = models.ForeignKey('authen.ForumUser', related_name='notify_user')
    involved_topic = models.ForeignKey(Topic, related_name='notify_topic')
    involved_reply = models.ForeignKey(Reply, related_name='notify_reply')
    trigger_user = models.ForeignKey('authen.ForumUser', related_name='trigger_user')
    occurence_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.content
