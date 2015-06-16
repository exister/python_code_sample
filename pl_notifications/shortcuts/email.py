# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils.http import urlquote
from ..models.emails import EmailNotification
from ..models.enums import *


class EmailNotificationHelper(object):
    @classmethod
    def send(cls, to=None, user=None, subject='', message='', html_message='',
             scheduled_at=None, information_type=INFORMATION_TYPE_APPLICATION_NOTIFICATION):
        if not to or not user:
            return None

        try:
            validate_email(to)
        except ValidationError:
            raise ValidationError('%s is not a valid email address' % to)

        email_notification = EmailNotification(
            user=user,
            to=to,
            subject=subject,
            message=message,
            html_message=html_message,
            information_type=information_type,
            status=STATUS_WAITING
        )
        if scheduled_at:
            email_notification.scheduled_at = scheduled_at
        email_notification.save()

        return email_notification

    @classmethod
    def check_email(cls, user):
        from pl_users.models import PLUser
        return PLUser.objects.has_real_email(user)

    @classmethod
    def mail_email_confirmation(cls, user, code):
        context = {
            'link': 'http://{0}{1}'.format(
                Site.objects.get_current().domain,
                reverse('users-auth-confirm-email-client', kwargs={'code': urlquote(code)})
            )
        }

        cls.send(
            user=user,
            to=user.email,
            subject='Подтверждение email',
            message=render_to_string(
                'notifications/notification_templates/email/email_confirmation.txt', context
            ),
            html_message=render_to_string(
                'notifications/notification_templates/email/email_confirmation.html', context
            ),
            information_type=INFORMATION_TYPE_PASSWORD_NOTIFICATION
        )