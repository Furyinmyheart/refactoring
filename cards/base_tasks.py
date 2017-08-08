import logging

from alert_messages.models import Message
from cards.models import Request
from dc.celery import app
from finance.models import Transaction

logger = logging.getLogger(__name__)


class RequestErrorBaseTask(app.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    request_id = None

    def send_message_to_user(self, request):
        Message.objects.create(
            text='<a href="{}">Заявка {}</a>: {}'.format(request.get_absolute_url(), request.pk,
                                                         request.task_logs.first()),
            to_user_id=request.author.pk, level=3, is_html=True)

    def transaction_done(self):
        if self.request_id:
            for transaction in Transaction.objects.filter(request_id=self.request_id, status__in=[1, 2]):
                transaction.done()

    def transaction_cancel(self):
        if self.request_id:
            for transaction in Transaction.objects.filter(request_id=self.request_id, status__in=[1, 2]):
                transaction.cancel()

    def after_return(self, status, retval, task_id, *args, **kwargs):

        if status == "FAILURE":
            # You can do also something if the tasks fail instead of check the retries
            logger.error('task status == "FAILURE"')
            if self.request_id is not None:
                request = Request.objects.get(pk=self.request_id)

                Request.objects.filter(pk=self.request_id).update(status=3)
                logger.debug('return request_limits')
                request.author.undo_decrement_request_limits()

                self.transaction_cancel()

                # make user notification
                self.send_message_to_user(request)

                logger.debug('set request is cancel')

        super(RequestErrorBaseTask, self).after_return(status, retval, task_id, *args, **kwargs)


class RequestEditErrorBaseTask(RequestErrorBaseTask):
    """Abstract base class for all tasks in my app."""

    abstract = True

    request_id = None

    def after_return(self, status, retval, task_id, *args, **kwargs):

        if status == "FAILURE":
            # You can do also something if the tasks fail instead of check the retries
            logger.error('task status == "FAILURE"')
            if self.request_id is not None:
                request = Request.objects.get(pk=self.request_id)

                Request.objects.filter(pk=self.request_id).update(status=5)
                # make user notification
                self.send_message_to_user(request)

        super(RequestErrorBaseTask, self).after_return(status, retval, task_id, *args, **kwargs)


class RequestDeleteErrorBaseTask(RequestErrorBaseTask):
    """Abstract base class for all tasks in my app."""

    abstract = True

    request_id = None

    def retry(self, *args, **kwargs):
        logger.error(kwargs)
        super().retry(*args, **kwargs)

    def after_return(self, status, retval, task_id, *args, **kwargs):

        if status == "FAILURE":
            # You can do also something if the tasks fail instead of check the retries
            logger.error('task status == "FAILURE"')
            if self.request_id is not None:
                request = Request.objects.get(pk=self.request_id)

                # make user notification
                self.send_message_to_user(request)

        super(RequestErrorBaseTask, self).after_return(status, retval, task_id, *args, **kwargs)