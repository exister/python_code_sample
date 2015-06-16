# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import logging

from django.conf import settings
from django.core.exceptions import FieldError, ValidationError
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext as _
from jsonfield import JSONField
from django.db import models

from .notifications import Notification, MassNotification
from ..signals.push import device_created
from .enums import *


logger = logging.getLogger('pl_app')


OS_ALL, OS_IOS, OS_ANDROID = ('all', 'ios', 'android')
OS_CHOICES = (
    (OS_ALL, _('All')),
    (OS_IOS, _('iOS')),
    (OS_ANDROID, _('Android')),
)


class Device(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('User'), null=True, blank=True,
        related_name='mobile_devices'
    )

    device_id = models.TextField(verbose_name=_('Device ID'), db_index=True)
    push_id = models.TextField(verbose_name=_('Push ID'), default='')

    os = models.CharField(verbose_name=_('Device OS'), max_length=255)
    os_version = models.CharField(verbose_name=_('OS Version'), max_length=50)

    model = models.CharField(verbose_name=_('Device Model'), max_length=255)
    screen_size = models.CharField(verbose_name=_('Screen Size'), max_length=9, default='')

    badge = models.PositiveIntegerField(verbose_name=_('Badge'), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'{device_id} (OS: {os} {os_version}, Model: {model})'.format(**self.__dict__)

    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
        app_label = 'pl_notifications'

    def get_screen_size(self):
        if not self.screen_size or 'x' not in self.screen_size:
            return None
        try:
            width, height = map(int, self.screen_size.split('x'))
        except ValueError:
            return None
        return width, height

    @classmethod
    def delete_inactive_tokens(cls, inactive_devices):
        """
        Removes inactive push ids

        :param inactive_devices: list of inactive devices from APNS feedback loop
        :return:
        """
        for expire_date, device_sign in inactive_devices:
            logger.info('Expired token %s at %s', device_sign, expire_date)

            devices = cls.objects.filter(os__istartswith='ios', push_id=device_sign)

            for device in devices:
                if device.updated <= datetime.datetime.strptime(expire_date.value, "%Y%m%dT%H:%M:%S").date():
                    device.push_id = ''
                    device.save()

    @classmethod
    def _convert_field_name(cls, name):
        name = name.replace('HTTP_X_', '').replace('HTTP_', '').lower()
        if 'id' not in name:
            name = name.replace('device_', '')
        return name

    @classmethod
    def _get_device_data_from_request(cls, request):
        """
        Extracts device info from request headers.

        :param request:
        :return: Dict with device info
        """
        headers = (
            'HTTP_DEVICE_ID',
            'HTTP_PUSH_ID',
            'HTTP_DEVICE_OS',
            'HTTP_DEVICE_OS_VERSION',
            'HTTP_DEVICE_MODEL',
            'HTTP_DEVICE_SCREEN_SIZE'
        )
        allow_empty = (cls._convert_field_name('HTTP_PUSH_ID'), cls._convert_field_name('HTTP_DEVICE_SCREEN_SIZE'))
        data = dict(
            zip(
                map(cls._convert_field_name, headers),
                map(lambda x: request.META.get(x, request.META.get(x.replace('HTTP_', 'HTTP_X_'), None)), headers)
            )
        )

        for empty_key in allow_empty:
            if data.get(empty_key) is None:
                data[empty_key] = ''

        if not all(map(lambda (k, v): bool(v.strip() if v else v) if k not in allow_empty else (v is not None), data.items())):
            return None
        return data

    @classmethod
    def get_device_from_request(cls, request):
        """
        Finds :py:mod:`Device` using info from HTTP Headers.
        In case of device_id collision, recreates device, deleting all other duplicates.

        :param request:
        :return: :py:mod:`Device` or None
        """
        device = None

        device_data = cls._get_device_data_from_request(request)
        if device_data:
            push_id, os_version, screen_size = device_data.pop('push_id', ''), device_data.pop('os_version', ''), device_data.pop('screen_size', '')
            try:
                device = cls.objects.get(**device_data)
            except (FieldError, ValidationError, cls.DoesNotExist), e:
                logger.debug(e.message)
            except cls.MultipleObjectsReturned, e:
                cls.objects.filter(**device_data).delete()
                device_data['push_id'] = push_id
                device_data['os_version'] = os_version
                device_data['screen_size'] = screen_size
                device = cls.objects.create(**device_data)

        return device

    @classmethod
    def create_device_from_request(cls, request):
        """
        Uses device_id for lookup. Push_id and os_version are updated each time. Other parameters are used only
        upon first creation.

        Sends `device_created` only after first registration.

        :param request:
        :return: :py:class:`Device` or None, created or not
        """
        device = None
        created = False

        device_data = cls._get_device_data_from_request(request)
        if device_data:
            parameters_to_update = ('push_id', 'os_version', 'screen_size')
            device_data['defaults'] = {}
            for key in parameters_to_update:
                device_data['defaults'][key] = device_data.pop(key, '')

            try:
                device, created = cls.objects.get_or_create(**device_data)
            except (FieldError, ValidationError), e:
                logger.debug(e.message)

            if not created and device_data['defaults']:
                for key in parameters_to_update:
                    if device_data['defaults'].get(key, None) is not None:
                        setattr(device, key, device_data['defaults'][key])
                device.save()

        if created:
            device_created.send(sender=cls, device=device)

        return device, created


class PushNotificationMixin(models.Model):
    notification_type_slug = 'push'

    os = models.CharField(verbose_name=_('OS'), choices=OS_CHOICES, default=OS_ALL, max_length=50)

    text = models.CharField(verbose_name='Текст', max_length=80)

    class Meta:
        abstract = True

    @property
    def text_preview(self):
        return Truncator(self.text).chars(50)

    @property
    def notification_type_name(self):
        return 'Push'


class PushNotification(PushNotificationMixin, Notification):
    devices = models.ManyToManyField(
        to=Device, verbose_name=_('Devices'), blank=True, related_name='devices+'
    )
    processed_devices = models.ManyToManyField(
        to=Device, verbose_name=_('Devices'), blank=True, related_name='processed_devices+'
    )

    apns_alert_data = JSONField(null=True, blank=True)
    gcm_alert_data = JSONField(null=True, blank=True)
    extra = JSONField(default={}, blank=True)

    class Meta:
        app_label = 'pl_notifications'

    @property
    def text_preview(self):
        if self.text:
            return Truncator(self.text).chars(50)
        return 'Системное уведомление'

    def save(self, *args, **kwargs):
        if not self.text and not self.apns_alert_data and not self.gcm_alert_data:
            raise ValueError('set text or apns_alert_data or gcm_alert_data')
        super(PushNotification, self).save(*args, **kwargs)

    def get_alert_data(self, provider_key):
        if self.text:
            return self.text
        else:
            return getattr(self, '{0}_alert_data'.format(provider_key.lower()), None)

    def send(self):
        """
        Caller should catch all exceptions
        :return:
        """
        from pl_notifications.backends.push.sender import PushSender
        providers = PushSender.get_providers_keys_and_os()
        alert = dict((key, self.get_alert_data(key)) for key in providers.keys())
        if not alert or not all(alert.values()):
            return

        # device_tokens = {
        #    'APNS': set(),
        #    'GCM': set()
        # }
        device_tokens = {}

        # badges = {
        #    'push_id': 1,
        # }
        badges = {}
        processed_devices = []

        devices = self.devices.exclude(model__icontains='simulator')
        # filter by os
        if self.os != OS_ALL:
            devices = devices.filter(os__icontains=self.os)

        # exclude devices from previous attempts
        if self.processed_devices.all().count() > 0:
            devices = devices.exclude(pk__in=self.processed_devices.all())

        devices_count = devices.count()

        if devices_count == 0:
            return

        for device in devices:
            processed_devices.append(device)

            # tokens = {
            #    'APNS': set(),
            #    'GCM': set()
            # }
            tokens = dict((key, set([])) for key in providers.keys())

            if device.push_id is not None and device.push_id != "" and device.push_id:
                for provider, device_os in providers.iteritems():
                    if device.os.startswith(device_os):
                        tokens[provider].add(device.push_id)
                        device.badge = models.F('badge') + 1
                        device.save()
                        device = Device.objects.get(pk=device.pk)
                        badges[device.push_id] = device.badge

            # aggregate tokens
            for os_type, tokens_set in tokens.iteritems():
                if os_type in device_tokens:
                    device_tokens[os_type] = device_tokens[os_type].union(tokens_set)
                else:
                    device_tokens[os_type] = tokens_set

        # send message to aggregated tokens
        PushSender.send_notifications(
            device_tokens,
            alert=alert,
            badge=badges,
            sound='default',
            extra=self.extra,
            fail_silently=False
        )
        self.processed_devices.add(*processed_devices)

        self.status = STATUS_SENT
        self.sent_at = timezone.now()


class MassPushNotification(PushNotificationMixin, MassNotification):
    notification_class = PushNotification

    class Meta:
        app_label = 'pl_notifications'

    def get_initial_data(self):
        initial_data = super(MassPushNotification, self).get_initial_data()
        initial_data.update({
            'os': self.os,
            'text': self.text,
        })
        return initial_data

    def filter_users(self, users):
        users = super(MassPushNotification, self).filter_users(users)
        users = users.filter(
            models.Q(
                notifications_settings__is_channel_enabled_push=True,
            )
        )
        condition = """
            (
                SELECT COUNT(*) FROM "pl_notifications_device"
                WHERE
                    "pl_notifications_device"."user_id" = "pl_users_pluser"."id"
                    AND "pl_notifications_device"."push_id" != ''
            ) > 0
        """
        users = users.extra(where=[condition])
        return users

    def make_notification(self, user):
        notification = super(MassPushNotification, self).make_notification(user)

        notification.to = user.email
        notification.os = self.os
        notification.text = self.text

        notification.save()

        for device in user.mobile_devices.all():
            notification.devices.add(device)

        return notification
