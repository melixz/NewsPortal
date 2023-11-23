
from django.views.generic import (ListView, DetailView)
from .models import Post


class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'flatpages/posts.html'
    context_object_name = 'posts'
    paginate_by = 10

class PostDetailView(DetailView):
    model = Post
    template_name = 'flatpages/some_news.html'
    context_object_name = 'some_news'


