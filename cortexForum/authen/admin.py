# -*- coding:utf-8 -*-
from django.contrib import admin

# Register your models here.
# 注册关于用户
from .models import ForumUser


class ForumUserAdmin(admin.ModelAdmin):
    list_display = ('get_name',)
    # 参见：http://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field
    # 还有，必须是 list or tuple

    search_fields = ('get_name',)

    #list_filter = ('is_active', 'is_staff')

    def get_name(self,obj):
        return obj.user.username
    get_name.admin_order_field='user'


#admin.site.unregister(User)
admin.site.register(ForumUser, ForumUserAdmin)
