# -*- coding: utf-8 -*-
import logging
import time
import signal

from django.core.management import BaseCommand
from django.utils import timezone
from lockfile import FileLock, AlreadyLocked, LockTimeout

from pl_notifications.models.enums import *
from pl_notifications.models import Notification
from pl_notifications.tasks import SendNotificationTask
from pl_notifications.utils.notifications import enabled_notification_subclasses


logger = logging.getLogger('pl_app')


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()
        self.options = None
        self.is_running = False

        signal.signal(signal.SIGTERM, self.signal_term_handler)

    def signal_term_handler(self, signal, frame):
        print 'got SIGTERM'
        self.is_running = False

    def run_locked(self):
        lock = FileLock('/tmp/send_notifications')
        try:
            logger.debug('Trying to acquire lock')
            lock.acquire(3)
            self.run()
        except AlreadyLocked:
            logger.debug('Lock already in place. Quitting')
            return
        except LockTimeout as e:
            logger.debug('%s', e)
            return
        finally:
            if lock.is_locked():
                lock.release()

    def handle(self, *args, **options):
        self.options = options
        self.run_locked()

    def run(self):
        logger.debug('Running')
        self.is_running = True

        try:
            self.process_items()
        except KeyboardInterrupt:
            logger.debug('Will stop running')
            self.is_running = False

    def process_items(self):
        logger.debug('Processing items')

        subclasses = enabled_notification_subclasses()

        if not subclasses:
            self.is_running = False
            return

        while self.is_running:
            notifications = Notification.objects.filter(
                status=STATUS_WAITING,
                scheduled_at__lte=timezone.now()
            ).select_subclasses(*subclasses).order_by('created_at')[:10]

            for notification in notifications:
                task = SendNotificationTask()
                task.apply_async(args=[notification.pk])

            logger.debug('Sleeping before next run')
            time.sleep(2)