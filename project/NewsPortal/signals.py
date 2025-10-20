from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from pyexpat.errors import messages
from datetime import timedelta

from .models import Category, Post


# @receiver(pre_save, sender=Post)
# def post_limit_notification(sender, instance, *args, **kwargs):
#     if instance.pk:
#         return
#     before_datetime = timezone.now() - timedelta(days=1)
#     posts_count = Post.objects.filter(author=instance.author, datetime__gte=before_datetime).count()
#     if posts_count >= 3:
#         raise PermissionDenied('❌ Вы не можете создавать больше 3 постов в сутки!')

@receiver(m2m_changed, sender=Post.category.through)
def new_post_notification(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        post_categories = Category.objects.filter(pk__in=pk_set)
        for category in post_categories:
            subscribers = category.subscribers.all()
            for user in subscribers:
                if user.email:
                    html_content = (
                        f'<h2>Новая публикация</h2>'
                        f'<p>Информируем <strong>{user.username}</strong>, что на сайте NewsPortal появилась новая публикация!</p>'
                        f'<p>Краткое содержание: {instance.preview()}</p>'
                        f'<p>Полный текст статьи можно посмотреть, перейдя по ссылке: '
                        f'<a href="{settings.SITE_URL}/post/{instance.id}">Новая публикация</a></p>'
                    )
                    send_mail(
                        subject=f'Новая публикация в категории {category.name_category}',
                        message='',
                        html_message=html_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email]
                    )


@receiver(m2m_changed, sender=Category.subscribers.through)
def subscribers_notification(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        user = User.objects.get(pk__in=pk_set)
        send_mail(
            subject='Новая подписка',
            message=(
                f'Привет, {user.username}! Вы подписались на категорию {instance.name_category}! '
                f'Список категорий ваших подписок: {", ".join([cat.name_category for cat in user.categories.all()])}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
    if action == 'post_remove':
        user = User.objects.get(pk__in=pk_set)
        send_mail(
            subject='Отписка от категории',
            message=(
                f'Привет, {user.username}! Вы отписались от категории {instance.name_category}! '
                f'Список категорий ваших подписок: {", ".join([cat.name_category for cat in user.categories.all()])}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )