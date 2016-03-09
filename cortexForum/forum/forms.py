# -*- coding:utf-8 -*-
from django import forms
from django.conf import settings

error_messages = {
    'title': {
        'required': u'必须填写标题',
        'max_length': u'标题长度过长',
    },
    'content': {
        'required': u'必须填写内容',
    }
}


class CreateForm(forms.Form):
    # 创建主题的内容
    title = forms.CharField(max_length=128, help_text=u'请输入标题',
                            error_messages=error_messages.get('title'))
    content = forms.CharField(widget=forms.Textarea,
                              error_messages=error_messages.get('content'))
    '''
    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
    '''
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title in settings.LAW_RESERVED:
            raise forms.ValidationError(u'帖子包含不合法字符')
        return title

    def clean_content(self):
        '''
        content = self.cleaned_data.get('content')
        for str in settings.LAW_RESERVED:
            if content.find(str):
                raise forms.ValidationError(u'内容不合法')
        '''
        return self.cleaned_data.get('content')

class ReplyForm(forms.Form):
    content=forms.CharField(widget=forms.Textarea,
                            error_messages=error_messages.get('content'))
