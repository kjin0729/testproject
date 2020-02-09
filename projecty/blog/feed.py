from django.contrib.syndication.views import Feed
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from .models import Post


class RssLatestPostsFeed(Feed):
    link = reverse_lazy('blog:top')

    def items(self):
        return Post.objects.filter(
            is_public=True
        ).order_by('-created_at').prefetch_related('tags')[:15]

    def items_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return resolve_url('blog:post_detail', pk=item.pk)

    def item_pubdate(self, item):
        return item.created_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]


class AtomLastestPostsFeed(RssLatestPostsFeed):
    feed_type = Atom1Feed
