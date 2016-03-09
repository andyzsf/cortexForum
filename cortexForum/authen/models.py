# -*- coding:utf-8 -*-

# 这一部分主要是做所有关于认证的工作
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.

class ForumUser(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='/images', blank=True)
    introduce = models.CharField(max_length=128, blank=True)
    fortune = models.IntegerField(default=42)  # 财富值
    updated = models.DateTimeField(default=timezone.now())
    # 唯一不好的就是关于权限管理，自己现在还没有做，明天早上起来看

    # 这一部分是自我介绍的内容
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    douban = models.URLField(blank=True)
    weibo = models.URLField(blank=True)

    def __unicode__(self):
        return self.user.username
