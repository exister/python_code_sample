# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.db import models
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.text import Truncator

from .notifications import Notification, MassNotification
from ..utils.email import get_email_backend
from .enums import *


class EmailNotificationMixin(models.Model):
    notification_type_slug = 'email'

    subject = models.CharField(verbose_name='Тема', max_length=255, default='', blank=True)
    message = models.TextField(verbose_name='Текст', blank=True, default='')
    html_message = models.TextField(verbose_name='HTML-текст', blank=True, default='')

    class Meta:
        abstract = True

    @property
    def text_preview(self):
        return Truncator(self.message).chars(50)

    @property
    def notification_type_name(self):
        return 'Email'


class EmailNotification(EmailNotificationMixin, Notification):
    to = models.EmailField()

    class Meta:
        app_label = 'pl_notifications'

    def email_message(self, connection=None):
        """
        Returns a django ``EmailMessage`` or ``EmailMultiAlternatives`` object
        depending on whether html_message is empty.
        """
        subject = smart_text(self.subject)
        message = self.message
        html_message = self.html_message

        if html_message:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.to],
                connection=connection
            )
            msg.attach_alternative(html_message, "text/html")
        else:
            msg = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.to],
                connection=connection
            )

        return msg

    def send(self):
        """
        Caller should catch all exceptions
        :return:
        """
        connection = get_connection(get_email_backend())
        connection.open()
        self.email_message(connection=connection).send()
        connection.close()

        self.status = STATUS_SENT
        self.sent_at = timezone.now()


class MassEmailNotification(EmailNotificationMixin, MassNotification):
    notification_class = EmailNotification

    class Meta:
        app_label = 'pl_notifications'

    def get_initial_data(self):
        initial_data = super(MassEmailNotification, self).get_initial_data()
        initial_data.update({
            'subject': self.subject,
            'message': self.message,
            'html_message': self.html_message,
        })
        return initial_data

    def filter_users(self, users):
        from pl_users.models import PLUser

        users = super(MassEmailNotification, self).filter_users(users)
        return users.filter(
            models.Q(
                confirmed_contacts=PLUser.confirmed_contacts.email,
                notifications_settings__is_channel_enabled_email=True,
            )
        )

    def make_notification(self, user):
        notification = super(MassEmailNotification, self).make_notification(user)

        notification.to = user.email
        notification.subject = self.subject
        notification.message = self.message
        notification.html_message = self.html_message

        notification.save()

        return notification