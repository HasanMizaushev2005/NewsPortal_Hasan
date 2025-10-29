from celery import shared_task
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from NewsPortal.models import Category, Post
from django.conf import settings

@shared_task
def subscribers_notification_task(**params):
    send_mail(**params)

@shared_task
def new_post_notification_task(**params):
    send_mail(**params)

@shared_task
def send_weekly_letter_with_new_posts():
    one_week_ago = timezone.now() - timedelta(days=7)
    categories_with_subscribers = Category.objects.filter(subscribers__isnull=False).distinct()

    for category in categories_with_subscribers:
        new_posts = Post.objects.filter(category=category, datetime__gte=one_week_ago).order_by('-datetime')

        if not new_posts.exists():
            continue

        subscribers = category.subscribers.all()
        for user in subscribers:
            if user.email:
                html_content = (
                    f'<h2>Новые статьи за последнюю неделю 🤩</h2>'
                    f'<p>Информируем <strong>{user.username}</strong>, что за последнюю неделю в категории "{category.name_category}" появились новые публикации:\n</p>'
                )
                for post in new_posts:
                    html_content += f'<p><a href="{settings.SITE_URL}/post/{post.id}">{post.title}</a> Краткое содержание: {post.preview()}\n</p>'

                send_mail(
                    subject=f'Еженедельная рассылка :)',
                    message='',
                    html_message=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email]
                )