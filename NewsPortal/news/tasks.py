from celery import Celery
from celery.decorators import shared_task
from your_app.models import Post

app = Celery('your_app_name')

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
    for username, email in subscribers_list.items():
        post_for_subscribers.delay(username, post.title, post.text[:50], email, post.pk)

@your_signal.connect
def your_signal_handler(sender, **kwargs):
    send_post_for_subscribers_celery.delay(sender.pk)

