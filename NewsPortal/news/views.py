from datetime import datetime, timedelta
from django.views.generic import (ListView, DetailView)
from .models import Post
from .filters import PostFilter
from django.db.models import Q

class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'flatpages/posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwards):
        context = super().get_context_data(**kwards)
        today = datetime.utcnow().date()
        # фильтр по текущему пользователю и дате создания
        q_user = Q(author=self.request.user)
        q_date = Q(time_in__gte=today, time_in__lt=today + timedelta(days=1))
        today_posts = self.model.objects.filter(q_user, q_date)
        user_posts_count = self.model.objects.filter(author=self.request.user).count()
        context['user_today_posts_count'] = today_posts.count()
        context['user_posts_count'] = user_posts_count
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        context['filterset'] = self.filterset
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'flatpages/some_news.html'
    context_object_name = 'some_news'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'post-{self.kwargs["pk"]}',
                        None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj
