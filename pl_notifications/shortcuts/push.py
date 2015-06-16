# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ..models.push import PushNotification
from ..models.enums import *
from pl_notifications.backends.push.providers.apns_provider import APNSPushSenderProvider


class PushNotificationHelper(object):
    @classmethod
    def send_push(cls, user, text='', apns_alert_data=None, gcm_alert_data=None,
                  extra=None, scheduled_at=None,
                  information_type=INFORMATION_TYPE_APPLICATION_NOTIFICATION):
        """

        :type text: str
        :type apns_alert_data: dict
        :type user: PLUser
        :type devices: QuerySet
        :return: PushMailerItem
        """
        assert user

        if user.mobile_devices.all().count() == 0:
            return

        push_notification = PushNotification()
        if scheduled_at:
            push_notification.scheduled_at = scheduled_at

        push_notification.user = user
        push_notification.text = text
        push_notification.apns_alert_data = apns_alert_data
        push_notification.gcm_alert_data = gcm_alert_data
        push_notification.extra = extra
        push_notification.information_type = information_type

        push_notification.save()

        push_notification.devices.add(*list(user.mobile_devices.all()))

        push_notification.status = STATUS_WAITING
        push_notification.save()

        return push_notification

    @classmethod
    def push_appointment_confirmed(cls, appointment):
        if not appointment.client.is_push_enabled('appointment_confirmed'):
            return

        date = appointment.start.strftime('%d.%m.%Y')
        time = appointment.start.strftime('%H:%M')
        doctor = appointment.doctor.user.get_last_name_with_initials()
        clinic = appointment.clinic.title
        address = appointment.clinic.address

        apns_alert_data = APNSPushSenderProvider.make_embedded_alert(
            'APPOINTMENT_CONFIRMED',
            appointment.pk,
            date,
            time,
            doctor,
            clinic,
            address
        )
        gcm_alert_data = {
            'msg_type': 'APPOINTMENT_CONFIRMED',
            'date': date,
            'time': time,
            'doctor': doctor,
            'clinic': clinic,
            'address': address
        }
        extra = {
            'id': appointment.pk
        }

        cls.send_push(
            apns_alert_data=apns_alert_data,
            gcm_alert_data=gcm_alert_data,
            user=appointment.client.user,
            extra=extra
        )