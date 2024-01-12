from django.core.mail import mail_managers, EmailMultiAlternatives
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Post


def post_for_subscribers(subscriber, title, short_text, subscribers, pk):
    html_content = render_to_string('posts/post_for_subscribers.html',
                                    {'text': short_text,
                                     "link": f'http://127.0.0.1:8000/post/{pk}',
                                     "user": subscriber})
    # for n in subscribers_email:
    message = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email='dr.melix@gmail.com',
        to=subscribers
    )
    message.attach_alternative(html_content, "text/html")  # добавляем htm
    message.send()


@receiver(post_save, sender=Post)
def notify_managers(sender, instance, created, **kwargs):
    if created:
        subject = f'{instance.title}'
    else:
        subject = f'Пост был изменен{instance.title} {instance.text}'

    mail_managers(
        subject=subject,
        message=instance.text,
    )
    print(f'{instance.title}')


post_save.connect(notify_managers, sender=Post)


@receiver(post_delete, sender=Post)
def notify_managers_post_deleted(sender, instance, **kwargs):
    subject = f'Пост с названием "{instance.title}" был удален'
    mail_managers(
        subject=subject,
        message=f'Текст: {instance.text} ',
    )

    print(subject)