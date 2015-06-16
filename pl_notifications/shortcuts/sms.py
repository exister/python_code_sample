# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.loader import render_to_string
from ..conf import sms
from ..models.smses import CHARSET_CYRILLIC, CHARSET_ASCII, SMSNotification
from ..models.enums import *


class SMSNotificationHelper(object):
    @classmethod
    def send_sms(cls, user, phone, text, sender=sms.PL_SMS_SENDER, charset=CHARSET_CYRILLIC,
                 scheduled_at=None, information_type=INFORMATION_TYPE_APPLICATION_NOTIFICATION):
        """

        :param user:
        :param phone:
        :param text:
        :param sender:
        :param charset:
        :param scheduled_at:
        :return:
        """
        if not phone or not user:
            return None

        sms_notification = SMSNotification()
        sms_notification.sender = sender
        sms_notification.text = text
        sms_notification.charset = charset
        sms_notification.user = user
        sms_notification.phone = phone
        if scheduled_at is not None:
            sms_notification.scheduled_at = scheduled_at

        sms_notification.status = STATUS_WAITING
        sms_notification.information_type = information_type
        sms_notification.save()

        return sms_notification

    @classmethod
    def send_code(cls, user, code, is_change_contact=False):
        sms_template = 'notifications/notification_templates/sms/contact_confirmation_sms.txt'

        action = code.field

        if is_change_contact:
            action = 'change_contact'

        cls.send_sms(
            user=user,
            phone=user.phone,
            text=render_to_string(
                sms_template, {'code': code.code, 'action': action}
            ),
            information_type=INFORMATION_TYPE_PASSWORD_NOTIFICATION
        )