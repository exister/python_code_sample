# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_by_path
from django.utils.text import Truncator

from phonenumber_field.modelfields import PhoneNumberField
from django.db import models

from .notifications import Notification, MassNotification
from ..conf import sms
from .enums import *

import logging

logger = logging.getLogger('pl_app')


CHARSET_ASCII, CHARSET_CYRILLIC = range(2)
CHARSET_CHOICES = (
    (CHARSET_ASCII, 'Латинская'),
    (CHARSET_CYRILLIC, 'Кириллица')
)


class SMSNotificationMixin(models.Model):
    notification_type_slug = 'sms'

    sender = models.CharField(max_length=255, default=settings.PL_SMS_SENDER)
    text = models.TextField(verbose_name='Текст')
    charset = models.IntegerField(verbose_name='Кодировка', choices=CHARSET_CHOICES, default=CHARSET_ASCII)

    class Meta:
        abstract = True

    @property
    def text_preview(self):
        return Truncator(self.text).chars(50)

    @property
    def notification_type_name(self):
        return 'SMS'


class SMSNotification(SMSNotificationMixin, Notification):
    phone = PhoneNumberField()

    class Meta:
        app_label = 'pl_notifications'

    def send(self):
        """
        Caller should catch all exceptions
        :return:
        """
        backend_class = import_by_path(sms.PL_SMS_BACKEND)
        backend = backend_class(**sms.PL_SMS_BACKEND_PARAMS)
        backend.send(self)

        self.status = STATUS_SENT
        self.sent_at = timezone.now()


class MassSMSNotification(SMSNotificationMixin, MassNotification):
    notification_class = SMSNotification

    class Meta:
        app_label = 'pl_notifications'

    def get_initial_data(self):
        initial_data = super(MassSMSNotification, self).get_initial_data()
        initial_data.update({
            'os': self.sender,
            'text': self.text,
            'charset': self.charset,
        })
        return initial_data

    def filter_users(self, users):
        from pl_users.models import PLUser

        users = super(MassSMSNotification, self).filter_users(users)
        users = users.filter(
            models.Q(
                confirmed_contacts=PLUser.confirmed_contacts.phone,
                notifications_settings__is_channel_enabled_sms=True,
            )
        )
        return users

    def make_notification(self, user):
        notification = super(MassSMSNotification, self).make_notification(user)

        notification.phone = user.phone
        notification.sender = self.sender
        notification.text = self.text
        notification.charset = self.charset

        notification.save()

        return notification