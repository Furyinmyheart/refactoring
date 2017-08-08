import logging

from celery.schedules import crontab
from celery.task import periodic_task
from django.utils import timezone

from dc.celery import app as celery_app
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@periodic_task(run_every=(crontab(minute=1, hour=0)))
def reset_user_limits():
    from users.models import MyUser
    for user in MyUser.objects.filter(limit_per_day__gt=0):
        user.requests_available = user.limit_per_day
        user.save(update_fields=('requests_available',))


@celery_app.task
def send_confirm_email(recipient_list: list, confirm_url: str):
    send_mail(subject=render_to_string('emails/confirm_email_subject.txt'),
              message=render_to_string('emails/confirm_email_message.txt', {'confirm_url': confirm_url}),
              from_email=None, recipient_list=recipient_list)


@periodic_task(run_every=(crontab(minute=15, hour=0)))
def send_pay_alert():
    from users.models import MyUser
    from alert_messages.models import Message

    messsage_objs = []
    for user in MyUser.objects.exclude(notification_settings=None):

        localtime = timezone.localtime(timezone.now())

        is_send = False
        if user.notification_settings == 'weekly' and (localtime.weekday() + 1) == user.notification_weekly_day:
            is_send = True
        elif user.notification_settings == 'half_monthly' and localtime.day in [1, 16]:
            is_send = True
        elif user.notification_settings == 'monthly' and localtime.day == 1:
            is_send = True

        if is_send:
            alert_text = render_to_string('messages/pay_notification.txt', {'user': user})
            messsage_objs.append(Message(text=alert_text, from_user_id=None, to_user_id=user.pk, level=3, is_html=True,
                                         is_pay_alert=True, is_pay_alert_hide=False))
    if messsage_objs:
        Message.objects.bulk_create(messsage_objs)
