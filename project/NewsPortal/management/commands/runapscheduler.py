import logging
from datetime import timedelta

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail

from NewsPortal.models import Category, Post

logger = logging.getLogger(__name__)


# наша задача
def send_weekly_letter():
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

# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_weekly_letter,
            trigger=CronTrigger(day_of_week="mon", hour="09", minute="00"),
            id="send_weekly_letter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'send_weekly_newsletter'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")