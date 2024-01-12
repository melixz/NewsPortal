from celery import shared_task
from .models import Post
from .signals import post_for_subscribers


@shared_task
def send_post_for_subscribers_celery(post_pk):
    post = Post.objects.get(id=post_pk)
    categories = post.category.all()
    subscribers_all = []
    for category in categories:
        subscribers_all += category.subscribe.all()
    subscribers_list = {}
    for person in subscribers_all:
        subscribers_list[person.username] = person.email
    for n in subscribers_list.items():
        post_for_subscribers(n[0], post.title, post.text[:50], n[1], post.pk)