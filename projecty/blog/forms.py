from django import forms
from django.db.models import Count
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from .fields import SimpleCaptcharField
from .models import Comment, Reply, Post, EmailPush, Tag
from .widgets import SuggestPostWidget, UploadableTextarea, CustomCheckboxSelectMultiple


class PostSearchForm(forms.Form):
    key_word = forms.CharField(
        label='検索キーワード',
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
    label='タグでの絞り込み',
    required=False,
    queryset=Tag.objects.annotate(post_count=Count('post')).order_by('name'),
    widget=CustomCheckboxSelectMultiple,
    )


class AdminPostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'text': UploadableTextarea(attrs={'placeholder': '[TOC]\n\n## 概要\nこんな感じで'}),
            'relation_posts': SuggestPostWidget(attrs={'data-url': reverse_lazy('blog:posts_suggest')})
        }

class CommentCreateForm(forms.ModelForm):
    captcha = SimpleCaptcharField()

    class Meta:
        model = Comment
        fields = ('name', 'text', 'email')
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'マークダウンに対応しています。\n\n```python\nprint("コードはこのような感じで書く")\n```\n\n[リンクテキスト](https://narito.ninja/)\n\n![画像alt](画像URL)'}
            )
        }


class ReplyCreateForm(forms.ModelForm):
    captcha = SimpleCaptcharField

    class Meta:
        model = Reply
        fields = ('name', 'text')
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'マークダウンに対応しています。\n\n```python\nprint("コードはこのような感じで書く")\n```\n\n[リンクテキスト](https://narito.ninja/)\n\n![画像alt](画像URL)'}
            )
        }

class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailPush
        fields = ('mail',)
        widgets = {
            'mail': forms.EmailInput(attrs={'placeholder': 'メールアドレス'})
        }
        error_messages = {
            'mail': {
                'unique': 'メールアドレスは登録済みです!'
            }
        }

    def clean_email(self):
        mail = self.cleaned_data['mail']
        EmailPush.objects.filter(mail=mail, is_active=False).delete()
        return mail


class FileUploadForm(forms.Form):
    file = forms.FileField()


    def save(self):
        upload_file = self.cleaned_data['file']
        file_name = default_storage.save(upload_file.name, upload_file)
        file_url = default_storage.url(file_name)
        return file_url
