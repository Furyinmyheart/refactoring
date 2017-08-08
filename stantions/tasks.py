import logging

from celery.schedules import crontab
from celery.task import periodic_task

from dc.celery import app as celery_app, backoff
from stantions.info_downloader import download_stantion_info, ResponseException, HttpException
from stantions.models import Expert, Stantion

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2)
def get_stantion_info(self, reg_number: int):
    try:
        info = download_stantion_info(reg_number)

        expert_fio = info['expert_fio']
        point_address = info['point_address']
        org_title = info['org_title']

        if expert_fio and point_address and org_title:
            stantion = Stantion.objects.create(
                active=False,
                auto_update=True,
                order=0,
                org_title=org_title,
                reg_number=reg_number,
                point_address=point_address,
                daily_limit=0,
            )
            if expert_fio and len(expert_fio) == 3:
                Expert.objects.create(
                    last_name=expert_fio[0],
                    first_name=expert_fio[1],
                    middle_name=expert_fio[2],
                    stantion_id=stantion.pk,
                )

    except ResponseException as e:
        logger.error('No valid response received')
        self.retry(countdown=backoff(self.request.retries), exc=e)

    except HttpException as e:
        logger.error(str(e))
        self.retry(countdown=backoff(self.request.retries), exc=e)


@periodic_task(bind=True, run_every=(crontab(minute=10, hour=0, day_of_month='1,14')), max_retries=2)
def update_stantions_info(self):
    try:
        for stantion in Stantion.objects.filter(auto_update=True):

            if stantion.reg_number:
                info = download_stantion_info(stantion.reg_number)

                expert_fio = info['expert_fio']
                point_address = info['point_address']
                org_title = info['org_title']

                if expert_fio and point_address and org_title:
                    stantion.org_title = org_title
                    stantion.point_address = point_address
                    stantion.save()

                    if expert_fio and len(expert_fio) == 3:
                        expert = stantion.expert_set.first()
                        if not expert:
                            expert = Expert(stantion_id=stantion.pk)
                        expert.last_name = expert_fio[0]
                        expert.first_name = expert_fio[1]
                        expert.middle_name = expert_fio[2]
                        expert.save()

    except ResponseException as e:
        logger.error('No valid response received')
        self.retry(countdown=backoff(self.request.retries), exc=e)

    except HttpException as e:
        logger.error(str(e))
        self.retry(countdown=backoff(self.request.retries), exc=e)


@periodic_task(run_every=(crontab(minute=5, hour=0)))
def reset_stantion_limits():
    for stantion in Stantion.objects.all():
        stantion.requests_created = 0
        stantion.save(update_fields=('requests_created',))
