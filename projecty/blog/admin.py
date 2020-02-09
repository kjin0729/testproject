from django.contrib import admin
from .forms import AdminPostCreateForm
form .models import Post, Comment, Reply, Tag, EmailPush, LInePush
# Register your models here.


class ReplyInline(admin.StackedInline):
    model = Reply
    extra = 5


class CommentAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]


def notify(modeladmin, request, queryset):
    for post in queryset:
        post.line_push(request)
        post.brower_push()
        post.email_push(request)


class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text')
    
