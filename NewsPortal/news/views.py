
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from .models import Post
from django.db.models import Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import PostForm


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

class SearchResultsView(ListView):
    model = Post
    template_name = 'flatpages/search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('Category')
        object_list = Post.objects.filter(
            Q(title__icontains=query) |
            Q(text__icontains=query) |
            Q(time_in__icontains=query) |
            Q(rating__icontains=query) |
            Q(type__icontains=query)
        )
        if category_id:
            object_list = object_list.filter(category__id=category_id)
        object_list = object_list.distinct()
        return object_list

class PostCreate(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'posts/new_post.html'
    permission_required = ('NewsPortal.add_post',)

class PostUpdate(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'posts/post_edit.html'
    permission_required = ('NewsPortal.change_post',)

class PostDelete(DeleteView):
    model = Post
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('post_list')

class ArticleDetailView(DetailView):
    model = Post
    template_name = 'articles/article.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        context['title'] = self.object.title
        return context


# Создание статьи
class ArticleCreate(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'articles/new_article.html'
    permission_required = ('NewsPortal.add_post',)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.success_url = reverse_lazy('new_article', kwargs={'pk': self.object.id})
        return response


# Редактирование статьи
class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'articles/article_edit.html'
    success_url = reverse_lazy('new_article')
    permission_required = ('NewsPortal.change_post',)


# Удаление статьи:
class ArticleDelete(DeleteView):
    model = Post
    template_name = 'articles/article_delete.html'
    success_url = reverse_lazy('posts')



