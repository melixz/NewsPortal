from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import mail_admins, send_mail, EmailMultiAlternatives
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from .models import Post, Appointment, Category, CategorySubscribe
from .filters import PostFilter
from .forms import PostForm
from NewsPortal import settings
from django.utils.translation import gettext as _ # импортируем функцию для перевода


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

    def form_valid(self, form):
        # Фильтр по автору и дате создания (за последние 24 часа)
        author = self.request.user
        now = timezone.now()
        since_24_hours = now - timezone.timedelta(days=1)
        posts_count = Post.objects.filter(author=author, time_in__gte=since_24_hours).count()
        if posts_count >= 3:
            # Если пользователь уже создал 3 или более постов за последние 24 часа, то отправляем ошибку
            return HttpResponseBadRequest(f'{self.request.user.username}, Вы превысили лимит по количеству создаваемых'
                                          f' постов в сутки.')
        else:
            # Иначе, создаем новый пост
            response = super().form_valid(form)
            self.success_url = reverse_lazy('new_post', kwargs={'pk': self.object.id})
            post = self.object
            post_url = self.request.build_absolute_uri(reverse('some_news', args=[post.pk]))
            categories = post.category.all()
            category_name = []
            subscribers_emails = []

            for category in categories:
                category_name.append(category.name)
                subscribers = category.subscribe.all()
                subscribers_emails += [sub.email for sub in subscribers]

            for subscriber in subscribers:
                username = subscriber.username

            send_mail(
                subject=f'{post.title}"{category_name}"',
                message=f'Здравствуй {username}. Новая статья в твоём любимом разделе! {post.text[:50]}'
                        f'\n\n Ссылка на новый пост: {post_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=subscribers_emails
            )
            return response


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


class AppointmentView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'templates/make_appointment.html', {})

    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
            client_name=request.POST['client_name'],
            message=request.POST['message'],
        )
        appointment.save()

        html_content = render_to_string(
            'templates/appointment_created.html',
            {
                'appointment': appointment,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
            body=appointment.message,  # это то же, что и message
            from_email='su8scriber@yandex.ru',
            to=['su8scriber1@gmail.com'],  # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "appointment/appointment_created.html")  # добавляем html

        mail_admins(
            subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        msg.send()

        return redirect('make_appointment')


class CategoryPost(DetailView):
    model = Category
    template_name = 'categories/post_category.html'
    context_object_name = 'postcategory'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(category=kwargs['object'])
        return context


# Добавление категории:
class AddCategoryView(CreateView):
    model = Category
    template_name = 'categories/add_category.html'
    fields = '__all__'


# Список категорий:
class CategoryList(ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'category'


# Функция позволяющая подписаться на категорию
def subscribe_to_category(request, pk):

    current_user = request.user
    CategorySubscribe.objects.create(category=Category.objects.get(pk=pk), subscriber=User.objects.get(pk=current_user.id))

    return render(request, 'subscribe.html')


class Index(View):
    def get(self, request):
        string = _('Hello world')

        context = {
            'string': string
        }

        return HttpResponse(render(request, 'index.html', context))


