from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from .models import Category, Post
from .tasks import subscribers_notification_task, new_post_notification_task


@receiver(m2m_changed, sender=Post.category.through)
def new_post_notification(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        post_categories = Category.objects.filter(pk__in=pk_set)
        for category in post_categories:
            subscribers = category.subscribers.all()
            name_category = category.name_category
            for user in subscribers:
                if user.email:
                    email = user.email
                    html_content = (
                        f'<h2>Новая публикация</h2>'
                        f'<p>Информируем <strong>{user.username}</strong>, что на сайте NewsPortal появилась новая публикация!</p>'
                        f'<p>Краткое содержание: {instance.preview()}</p>'
                        f'<p>Полный текст статьи можно посмотреть, перейдя по ссылке: '
                        f'<a href="{settings.SITE_URL}/post/{instance.id}">Новая публикация</a></p>'
                    )
                    params = {
                        'subject': f'Новая публикация в категории {name_category}',
                        'message': '',
                        'html_message': html_content,
                        'from_email': settings.DEFAULT_FROM_EMAIL,
                        'recipient_list': [email]
                    }
                    new_post_notification_task.delay(**params)


@receiver(m2m_changed, sender=Category.subscribers.through)
def subscribers_notification(sender, instance, action, pk_set, **kwargs):
    user = User.objects.get(pk__in=pk_set)
    username = user.username
    email = user.email
    name = instance.name_category
    if action == 'post_add':
        params = {
            'subject': 'Новая подписка',
            'message': f'Привет, {username}! Вы подписались на категорию {name}! '
                       f'Список категорий ваших подписок: {", ".join([cat.name_category for cat in user.categories.all()])}',
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'recipient_list': [email]
        }
        subscribers_notification_task.delay(**params)
    if action == 'post_remove':
        params = {
            'subject': 'Отписка от категории',
            'message': f'Привет, {username}! Вы отписались от категории {name}! '
                       f'Список категорий ваших подписок: {", ".join([cat.name_category for cat in user.categories.all()])}',
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'recipient_list': [email]
        }
        subscribers_notification_task.delay(**params)