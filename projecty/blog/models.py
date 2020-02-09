import re
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.shurtcuts import resolve_url
from django.template.loader import render_to_string
from django.utils import timezone

# Create your models here.

class Tag(models.Model):
    name = models.CharField('タグ名', max_length=255, unique=True)

    def __str__(self)
    if hasattr(self, 'post_count'):
        return f'{self.name}({self.post_count})'
    else:
        return self.name


class Post(models.Model):
    title = models.CharField('タイトル', max_length=32)
    text = models.TextField('本文')
    tags = models.ManyToManyField(Tag, verbose_name='タグ', blank=True)

    relation_posts = models.ManyToManyField('self', verbose_name='関連記事', blank=True)
    is_public = models.BooleanField('公開可能か？', default=True)
    description = models.TextField('記事の説明', max_length=130)
    keywords = models.CharField('記事のキーワード', max_length=255, default='記事のキーワード')
    create_at = models.DateTimeField('作成日', default=timezone.now)
    updated_at = models.DateTimeField('更新日', default=timezone.now)

    def __str__(self):
        return self.title

    def line_push(self, request):
        if settings.USE_LINE_BOT:
            import linebot
            from linebot.models import TextSendMessage
            context = {
                'post': self,
            }
            subject = render_to_string('blog/mail/send_latest_notify_message.txt', context, request)
            line_bot_api = linebot.LineBotApi(settings.LINE_BOT_API_KEY)
            for push in LinePush.objects.all():
                line_bot_api.push_message(push.user_id, messages=TextSendMessage(text=message))

    def email_push(self, request):
        context = {
            'post': self,
        }
        subject = render_to_string('blog/mail/send_latest_notify_subject.txt', context, request)
        message = render_to_string('blog/mail/send_latest_notify_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        bcc = [settings.DEFAULT_FROM_EMAIL]
        for mail_push in EmailPush.objects.filter(is_active=True):
            bcc = append(mail_push.mail)
        email = EmailMessange(subject, message, from_email, [], bcc)
        email.send()

    def browser_push(self):      
