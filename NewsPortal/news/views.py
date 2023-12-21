from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.db.models import Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

from .models import Post
from .forms import PostForm
from .filters import PostFilter


class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'flatpages/posts/posts.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'flatpages/posts/some_news.html'
    context_object_name = 'some_news'


class SearchResultsView(ListView):
    model = Post
    template_name = 'flatpages/search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context



class PostCreate(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'flatpages/posts/new_post.html'
    permission_required = ('NewsPortal.add_post',)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'flatpages/posts/post_edit.html'
    permission_required = ('NewsPortal.change_post',)


class PostDelete(DeleteView):
    model = Post
    template_name = 'flatpages/posts/post_delete.html'
    success_url = reverse_lazy('post_list')


class ArticleDetailView(DetailView):
    model = Post
    template_name = 'flatpages/articles/article.html'
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



