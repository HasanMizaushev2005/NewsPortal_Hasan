import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send_weekly_letter_with_new_posts_every_monday_8am': {
        'task': 'NewsPortal.tasks.send_weekly_letter_with_new_posts',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'), # каждый понедельник в 8:00 утра
    },
}