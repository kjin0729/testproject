janimport json
from django.conf import settimgs
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import (
    PostSearchForm, CommentCreateForm, ReplyCreateForm,
    EmailForm, FileUploadForm
)
from .models import Post, Comment, Reply, EmailPush, LinePush, Tag

# Create your views here.

class PublicPostIndexView(generic.ListView):
    paginate_by = 10
    model = Post

    def_get_queryset(self):
    queryset = super().get_queryset()
     self.form = form = PostSearchForm(self.request.GET or None)
     if form.is_valid():
         tags =  form.cleaned_data.get('tags')
         if tags:
             for tag in tags:
                 queryset = queryset.filter(tags=tag)

        key_word = form.cleaned_data.get('key_word')
        if key_word:
            for word in key_word.split():
                queryset = queryset.filter(Q(title_icontains=word) | Q(text_icontains=word))

    queryset = queryset.order_by('-updated_at').prefetch_related('tags')
    return queryset

    def get_queryset(self):
        return self.get_queryset().filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        return context


class PrivatePostIndexView(LoginRequiredMixin, PublicPostIndexView):
    def get_queryset(self):
        return self._get_queryset().filter(is_public=False)

class PostDetailView(generic.DetailView):
    model = Post

    def get_queryset(self):
        return super().get_queryset().prefetch_related('tags', 'comment_set__reply_set')

    def get_object(self, queryset=None):
        post = super().get_object()
        if post.is_public or self.request.user.is_authenticated:
            return post
        else:
            raise Http404


class CommentCreate(generic.CreateView):
    model = Comment
    form_class = CommentCreateForm

    def form_valid(self, form):
        post_pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_pk)
        comment = form.save(commit=False)
        comment.target = post
        comment.request = self.request
        comment.save()
        message.info(self.request, 'コメントしました。')
        return redirect('blog:post_detail', pk=post_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context


class ReplyCreate(generic.CreateView):
    model = Reply
    form_class = ReplyCreateForm
    template_name = 'blog/comment_form.html'

    def form_valid(self, form):
        comment_pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        reply = form.save(commit=False)
        reply.target = comment
        reply.request = self.request
        reply.save()
        messages.info(self.request, '返信しました。')
        return redirect('blog:post_detail', pk=comment.target.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        context['post'] = comment.target
        return context

@require_POST
def subscribe_email(request):
    form = EmailForm(request.POST)

    if form.is_valid():
        push = form.save()
        context = {
        'token': dumps(push.pk)
        }
        subject = render_to_string('blog/mail/confirm_push_subject.txt', context, request)
        message = render_to_string('blog/mail/confirm_push_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [push.mail]
        bcc = [settings.DAEFAULT_FROM_EMAIL]
        email = EmailMEssage(subject, message, from_email, to, bcc)
        email.send()
        return JsonResponse({'message': 'Thanks!! メールに、登録用のURLを送付しました。'})

    return JsonResponse(form.errors.get_json_data(), status=400)


def subscribe_email_register(request, token):
    try:
        user_pk = loads(token, max_age=60*60*24)

    except SignatureExpired:
        return HttpResponseBadRequest()

    else:
        try:
            push = EmailPush.objects.get(pk=user_pk)
        except EmailPush.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            if not push.is_active():
                push.is_active = True
                push.save()
                return redirect('blog:subscribe_email_done')

    return HttpResponseBadRequest()

def subscribe_email_done(request):
    return render(request, 'blog/subscribe_email_done.html')


@csrf_exempt
def line_callback(request):
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        events = request_json['events']
        line_user_id = events[0]['source']['userId']

        if line_user_id == 'Udeadbeefdeadbeefdeadbeefdeadbeef':
            pass

        elif events[0]['type'] == 'follow':
            LinePush.objects.create(user_id=line_user_id)

        elif events[0]['type'] == 'unfollow':
            LInePush.objects.filter(user_id=line_user_id).delete()


    return HttpResponse()


def image_upload(request):
    form = FileUploadForm(files=request.FILES)
    if form.is_valid():
        path = form.save()
        url = '{0}://{1}{2}'.format(
            request.scheme,
            request.get_host(),
            path,
        )
        return JsonResponse({'url': url})
    return HttpResponseBadRequest()


def posts_suggest(request):
    keyword = request.GET.get('keyword')
    if keyword:
        post_list = [{'pk': post.pk, 'name': str(post)} for post in Post.objects.filter(title_icontains=keyword)]
    else:
        post_list = []
    return JsonResponse({'object_list': post_list})
