# -*- coding:utf-8 -*-

from .models import ForumUser
from django import forms
from django.conf import settings  # 比引用文件要好多了
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

# 方便选择
error_messages = {
    'username': {
        'required': u'用户名必须填写',
        'min_length': u'用户名长度过短(5-128)个字符',
        'max_length': u'用户名长度过长(5-128)个字符',
        'invalid': u'用户名格式错误，只能包含字母、数字、下划线',
    },
    'email': {
        'required': u'电子邮件地址必须填写',
        'invalid': u'不是正确的电子邮件格式',
    },
    'password': {
        'required': u'密码必须填写',
        'min_length': u'密码长度过短(4-15)个字符',
        'max_length': u'密码长度过长(4-15)个字符',
    }
}


# 我觉得这里自己还需要看一下从 models 建立 forms 有什么优势，否则太麻烦了
class registrationForm(forms.Form):
    username = forms.CharField(help_text='请输入你的用户名，将会作为你的昵称', min_length=5, max_length=128)
    password = forms.CharField(help_text='请输入你的密码', min_length=5, max_length=128)
    password_repeat = forms.CharField(help_text='重复密码', min_length=5, max_length=128)
    email = forms.EmailField(help_text='请输入你的注册邮箱')

    '''
    github = forms.URLField()
    website = forms.URLField()
    douban = forms.URLField()
    weibo = forms.URLField()
    '''

    class Meta:
        model = ForumUser
        exclude = ['user', 'fortune', 'updated', ]

    # 还要对每一个属性进行验证，用的是 clean__attribute 的方法

    def clean_username(self):
        # 不可能为空
        username = self.cleaned_data.get('username')
        try:
            user = ForumUser.objects.get(user__username=username)
            raise forms.ValidationError(u'用户名已经被注册')
        except ForumUser.DoesNotExist:
            if username in settings.RESERVED:
                raise forms.ValidationError(u'用户名中包含保留字符')

        # 最终都要返回该属性
        return username

    def clean_email(self):
        # 同样验证没有被注册过
        email = self.cleaned_data.get('email')
        try:
            email = ForumUser.objects.get(user__email=email)
            raise forms.ValidationError(u'邮箱已经被注册')
        except ForumUser.DoesNotExist:
            return email

    def clean_password_repeat(self):
        # 验证密码是否相同
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_repeat')
        if password != password_repeat:
            raise forms.ValidationError(u'密码确认错误')
        return password_repeat

    def save(self):
        # save函数不用 Super(),默认的保留关键字 commit=True
        # 我这里确实没看懂它为什么最后还要加一个 .set_password()
        user = super(registrationForm, self).save()
        return user


class loginForm(forms.Form):
    username = forms.CharField(min_length=5, max_length=128,
                               help_text=u'请输入用户名',
                               error_messages=error_messages.get('username'))
    password = forms.CharField(min_length=5, max_length=128,
                               help_text=u'请输入密码',
                               error_messages=error_messages.get('password'))

    # 对于 clean ，需要重载
    def __init__(self, *args, **kwargs):

        super(loginForm, self).__init__(*args, **kwargs)
        self.helper=FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.label_class='col-lg-2'
        self.helper.field_class='col-lg-8'
        self.helper.layout=Layout(
            'username',
            'password',

        )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError(u'用户名或密码不正确')
        elif not user.is_active:  # 不是一个函数，而是一个 bool 值
            raise forms.ValidationError(u'该用户已被管理员设置为未激活状态')

        return self.cleaned_data


class settingpasswordForm(forms.Form):
    # 如果密码没有找回
    password_old = forms.CharField(min_length=4, max_length=128,
                                   help_text=u'请输入之前的密码')

    password_new = forms.CharField(min_length=4, max_length=128,
                                   error_messages=error_messages.get('password'),
                                   help_text='请输入新的密码')
    password_repeat = forms.CharField(min_length=4, max_length=128,
                                      error_messages=error_messages.get('password'))

    def __init__(self, *args, **kwargs):
        # 想象看 __init__ 都能做什么
        self.user = kwargs.pop('user', None)
        super(settingpasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 只验证，将更新的工作放在 views 里做
        password_old = self.cleaned_data.get('password_old')
        password_new = self.cleaned_data.get('password_new')
        password_repeat = self.cleaned_data.get('password_repeat')

        if not self.user.check_password(password_old):
            raise forms.ValidationError(u'原始密码错误')
        if password_new != password_repeat:
            raise forms.ValidationError(u'两次密码不统一')
        return self.cleaned_data


        # 如果好我还想加上记住的功能
