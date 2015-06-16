# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils import timezone
from polymodels.managers import PolymorphicManager
from polymodels.models import PolymorphicModel

from .enums import *
from .filters import MassNotificationFilter
from pl_core.models import Timestampable, IterableQuerySet


class MassNotification(Timestampable, PolymorphicModel):
    notification_class = None
    notification_type_slug = None

    status = models.PositiveSmallIntegerField(
        verbose_name='Статус', choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    mass_notification_filter = models.ForeignKey(MassNotificationFilter, null=True, blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='MassNotificationUsers')

    scheduled_at = models.DateTimeField('Отправить в', default=timezone.now)

    class Meta:
        app_label = 'pl_notifications'

    @property
    def text_preview(self):
        return ''

    @property
    def notification_type_name(self):
        return 'Уведомление'

    @property
    def mass_notification_type_class(self):
        return ContentType.objects.get_for_id(self.content_type_id).model_class()

    @property
    def concrete_mass_notification(self):
        return self.type_cast(to=self.mass_notification_type_class)

    @property
    def concrete_mass_notification_filter(self):
        return self.mass_notification_filter.concrete_mass_notification_filter

    @property
    def is_editable(self):
        if self.status in (STATUS_DRAFT, STATUS_WAITING):
            return True
        return False

    def get_initial_data(self):
        initial_data = {}
        initial_data.update(self.concrete_mass_notification_filter.get_initial_data())
        return initial_data

    def prepare(self):
        users = self.filtered_users()

        for user in IterableQuerySet(users, batch=50):
            self.make_notification(user)
            self.create_user_relation(user)
        self.status = STATUS_SENT

    def filter_users(self, users):
        return users.filter(
            models.Q(
                is_active=True,
                notifications_settings__other=True
            )
        )

    def filtered_users(self):
        from pl_users.models import PLUser

        users = self.filter_users(PLUser.objects.clients().distinct())
        users = self.concrete_mass_notification_filter.filter_users(users)
        return users

    def make_notification(self, user):
        """
        Subclasses should return saved instance
        :param user:
        :return:
        """
        assert self.notification_class

        notification = self.notification_class()
        notification.user = user
        notification.mass_notification = self
        notification.information_type = INFORMATION_TYPE_MASS_NOTIFICATION
        notification.status = STATUS_WAITING
        return notification

    def create_user_relation(self, user):
        relation = MassNotificationUsers(
            user=user,
            mass_notification=self,
            relation_type=MassNotificationUsers.RELATION_TYPE_FROM_FILTER
        )
        relation.save()
        return relation


class MassNotificationUsers(models.Model):
    RELATION_TYPE_NONE, RELATION_TYPE_FROM_FILTER, RELATION_TYPE_MANUAL = range(3)
    RELATION_TYPE_CHOICES = (
        (RELATION_TYPE_NONE, 'NONE'),
        (RELATION_TYPE_FROM_FILTER, 'FROM FILTER'),
        (RELATION_TYPE_MANUAL, 'MANUAL'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    mass_notification = models.ForeignKey(MassNotification)
    relation_type = models.PositiveSmallIntegerField(
        choices=RELATION_TYPE_CHOICES,
        default=RELATION_TYPE_NONE
    )

    class Meta:
        app_label = 'pl_notifications'


class NotificationManager(PolymorphicManager):
    def non_private(self):
        return self.filter(
            information_type__in=[
                INFORMATION_TYPE_APPLICATION_NOTIFICATION,
                INFORMATION_TYPE_MASS_NOTIFICATION,
                INFORMATION_TYPE_MANUAL_NOTIFICATION
            ]
        )


class Notification(Timestampable, PolymorphicModel):
    notification_type_slug = None

    status = models.PositiveSmallIntegerField(
        verbose_name='Статус', choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    information_type = models.PositiveSmallIntegerField(
        choices=INFORMATION_TYPE_CHOICES, default=INFORMATION_TYPE_APPLICATION_NOTIFICATION
    )
    mass_notification = models.ForeignKey(
        MassNotification, null=True, blank=True, related_name='notifications'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_notifications')

    sent_at = models.DateTimeField(verbose_name='Отправлено в', null=True, blank=True, editable=False)
    scheduled_at = models.DateTimeField('Отправить в', default=timezone.now)

    objects = NotificationManager()

    class Meta:
        app_label = 'pl_notifications'
        ordering = ('-created_at',)

    @property
    def is_editable(self):
        if self.status in (STATUS_DRAFT, STATUS_WAITING):
            return True
        return False

    @property
    def is_mass_notification(self):
        return self.mass_notification is not None

    @property
    def notification_type_name(self):
        return 'Уведомление'

    @property
    def text_preview(self):
        return ''

    def send(self):
        pass


class NotificationSendingAttempt(PolymorphicModel):
    ATTEMPT_STATUS_PROCESSING, ATTEMPT_STATUS_SENT, ATTEMPT_STATUS_ERROR = range(3)
    ATTEMPT_STATUS_CHOICES = (
        (ATTEMPT_STATUS_PROCESSING, 'Обрабатывается'),
        (ATTEMPT_STATUS_SENT, 'Отправлено'),
        (ATTEMPT_STATUS_ERROR, 'Ошибка'),
    )

    notification = models.ForeignKey(Notification, related_name='attempts')
    status = models.PositiveSmallIntegerField(choices=ATTEMPT_STATUS_CHOICES, default=ATTEMPT_STATUS_PROCESSING)

    traceback = models.TextField(default='', blank=True)
    error = models.TextField(default='', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'pl_notifications'
