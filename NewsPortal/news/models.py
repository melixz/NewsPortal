from datetime import *
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.utils.translation import pgettext_lazy


article = 'AR'
news = 'NW'

TYPE = [
    (article, "Статья"),
    (news, "Новость")
]


class Author(models.Model):
    name = models.CharField(max_length=255)
    users = models.OneToOneField(User, on_delete=models.CASCADE)
    user_rating = models.IntegerField(default=0)

    def update_rating(self):
        comment_rating = Comment.objects.filter(user_id=self.users.id).aggregate(models.Sum('rating'))['rating__sum']
        posts_rating = Post.objects.filter(author_id=self).aggregate(models.Sum('rating'))
        post_id = Post.objects.filter(author_id=self).values_list('id', flat=True)
        rating_comment_to_posts = Comment.objects.filter(post_id__in=post_id).aggregate(models.Sum('rating'))[
            'rating__sum']
        self.user_rating = (int(posts_rating['rating__sum']) * 3) + int(comment_rating) + int(rating_comment_to_posts)
        self.save()

    def can_create_post(self):
        today = date.today()
        post_count = Post.objects.filter(author=self, created_at__date=today).count()
        max_posts_per_day = 3
        if post_count < max_posts_per_day:
            return True
        else:
            return False


class Category(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name=pgettext_lazy('catname', 'catname'))
    subscribe = models.ManyToManyField(User, through='CategorySubscribe', verbose_name=pgettext_lazy('subscriber', 'subscriber'))

    def __str__(self):
        return f'{self.name.title()}'

    def get_absolute_url(self):
        return reverse('add_category')



class CategorySubscribe(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=pgettext_lazy('category', 'category'))
    subscriber = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=pgettext_lazy('subscriber', 'subscriber'))


class Appointment(models.Model):
    date = models.DateField(
        default=datetime.utcnow,
    )
    client_name = models.CharField(
        max_length=200
    )
    message = models.TextField()

    def __str__(self):
        return f'{self.client_name}: {self.message}'


class Post(models.Model):
    author = models.ForeignKey(Author, default=1, on_delete=models.SET_DEFAULT, verbose_name=pgettext_lazy('Author', 'Author'))
    type = models.CharField(max_length=7, choices=TYPE, verbose_name=pgettext_lazy('Type', 'Type'))
    time_in = models.DateTimeField(auto_now_add=True, verbose_name=pgettext_lazy('Time_in', 'Time_in'))
    category = models.ManyToManyField(Category, through='PostCategory', verbose_name=pgettext_lazy('Category', 'Category'))
    title = models.CharField(max_length=255, verbose_name=pgettext_lazy('Title', 'Title'))
    text = models.TextField(verbose_name=pgettext_lazy('Text', 'Text'))
    rating = models.IntegerField(default=0, verbose_name=pgettext_lazy('Rating', 'Rating'))


    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        text = self.text[:124]
        if len(self.text) > 124:
            text += '...'
        return text

    def __str__(self):
        return f'{self.title.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        if self.type == article:
            return reverse('article', args=[str(self.id)])
        elif self.type == news:
            return reverse('some_news', args=[str(self.id)])
        else:
            return reverse('/', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'text']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})


class DailyPostLimit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    limit = models.PositiveIntegerField(default=3)