# -*- coding: utf-8 -*-
import sys
import traceback
import logging
import datetime

from django.db import transaction
from celery import Task
from django.utils import timezone

from .models.notifications import Notification, NotificationSendingAttempt, MassNotification
from .models.enums import *


logger = logging.getLogger('pl_app')


class SendNotificationTask(Task):
    name = 'send_notification_task'

    def run(self, notification_id):
        with transaction.atomic():
            try:
                notification = Notification.objects.select_for_update().get(
                    pk=notification_id,
                    status=STATUS_WAITING
                )
            except Notification.DoesNotExist:
                return
            else:
                notification.status = STATUS_PROCESSING
                notification.save()

        if notification:
            notification = notification.type_cast()

            attempts_count = notification.attempts.all().count()

            if attempts_count >= 3:  #TODO settings
                notification.status = STATUS_ERROR
                notification.save()
            else:
                attempt = NotificationSendingAttempt()
                attempt.notification = notification
                attempt.save()

                with transaction.atomic():
                    try:
                        notification.send()
                    except Exception as e:
                        exc_type, exc_value, _ = sys.exc_info()

                        logger.error(
                            'Error sending notification: id %s (%s)',
                            notification_id, e, exc_info=True, extra={'stack': True}
                        )

                        attempt.traceback = traceback.format_exc()
                        attempt.error = '{0}: {1}'.format(exc_type.__name__, exc_value)

                        attempt.status = NotificationSendingAttempt.ATTEMPT_STATUS_ERROR
                        notification.status = STATUS_WAITING
                        notification.scheduled_at \
                            = timezone.now() \
                            + datetime.timedelta(
                                seconds=30 * (attempts_count + 1)
                            )
                    else:
                        if notification.status == STATUS_SENT:
                            attempt.status = NotificationSendingAttempt.ATTEMPT_STATUS_SENT
                        else:
                            attempt.status = NotificationSendingAttempt.ATTEMPT_STATUS_ERROR
                            notification.status = STATUS_WAITING

                    attempt.save()
                    notification.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(SendNotificationTask, self).on_failure(exc, task_id, args, kwargs, einfo)

        notification_id = args[0]

        logger.error(
            'Error sending notification: id %s (%s %s)', notification_id,
            einfo.type.__name__, einfo.traceback
        )

        with transaction.atomic():
            try:
                notification = Notification.objects.select_for_update().get(
                    pk=notification_id,
                    status=STATUS_PROCESSING
                )
            except Notification.DoesNotExist:
                return
            else:
                notification.status = STATUS_ERROR
                notification.save()


class SendMassNotificationTask(Task):
    name = 'send_mass_notification_task'

    def run(self, mass_notification_id):
        with transaction.atomic():
            try:
                mass_notification = MassNotification.objects.select_for_update().get(
                    pk=mass_notification_id,
                    status=STATUS_WAITING
                )
            except MassNotification.DoesNotExist:
                return
            else:
                mass_notification.status = STATUS_PROCESSING
                mass_notification.save()

        if mass_notification:
            mass_notification = mass_notification.type_cast()

            try:
                mass_notification.prepare()
            except Exception as e:
                exc_type, exc_value, _ = sys.exc_info()

                logger.error(
                    'Error sending mass notification: id %s (%s)',
                    mass_notification_id, e, exc_info=True, extra={'stack': True}
                )

                mass_notification.status = STATUS_ERROR

            mass_notification.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(SendMassNotificationTask, self).on_failure(exc, task_id, args, kwargs, einfo)

        mass_notification_id = args[0]

        logger.error(
            'Error sending mass notification: id %s (%s %s)', mass_notification_id,
            einfo.type.__name__, einfo.traceback
        )

        with transaction.atomic():
            try:
                mass_notification = MassNotification.objects.select_for_update().get(
                    pk=mass_notification_id,
                    status=STATUS_PROCESSING
                )
            except MassNotification.DoesNotExist:
                return
            else:
                mass_notification.status = STATUS_ERROR
                mass_notification.save()