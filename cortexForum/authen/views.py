# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse

from .models import ForumUser
from .forms import registrationForm,loginForm,settingpasswordForm
from django.contrib import messages


# Create your views here.



# 进行有关注册部分
def user_register(request):
    '''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('homepage'))  # 怎么从另一个 app 里调用自己想要的
    '''
    user=None
    if request.method == 'POST':
        # 头像处理之后再做
        form = registrationForm(request.POST)
        if form.is_valid():
            information = form.cleaned_data
            new_user = User.objects.create_user(
                    username=information.get('username'),
                    password=information.get('password'),
                    email=information.get('email')
            )
            new_user.save()
            forumUser = ForumUser(user=new_user)
            forumUser.save()
            user=new_user

            '''
            这一部分不需要，最后在设置里进行信息更新
            formUser.introduce = information.get('introduce', '')
            formUser.github = information.get('github', '')
            formUser.website = information.get('website', '')
            formUser.douban = information.get('douban', '')
            formUser.weibo = information.get('weibo', '')
            '''
            # 是这样重新返回？我可不确定
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form=registrationForm()

    context={'form':form,
             'user':user
             }
    return render(request,'authen/user_register.html',context)



# 进行有关登陆部分
def user_login(request):
    '''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('homepage'))
    '''

    if request.method=='POST':
        form=loginForm(request.POST)
        if form.is_valid():
            information=form.cleaned_data
            user=authenticate(username=information.get('username'),
                              password=information.get('password'))
            if user is not None:
                login(request,user)
                return HttpResponseRedirect(reverse('homepage'))
            # 接下来 error_messages 如何定义为好,肯定是要显示出来啊
    else:
        form=loginForm()
        user=None

    context={'form':form,
             }
    return render(request,'authen/user_login.html',context)

@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))


def user_forget_password(request):
    # 如果忘记自己密码的话，说明自己还需要找回的功能
    pass

@login_required()
def user_set_password(request):
    # 重设密码
    user = request.user if request.user else None
    if request.method=='POST':
        form=settingpasswordForm(request.POST,user=request.user)
        if form.is_valid():

            password=form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            messages.success(request,u'密码成功更新')
            return HttpResponseRedirect(reverse('homepage',kwargs='user'))
    else:
        form=settingpasswordForm()
    context={
        'form':form,
        'user':user,
    }


    return render(request,'authen/user_setpassword.html',context)

def homepage(request):
    return render(request,'forum/homepage.html',{})