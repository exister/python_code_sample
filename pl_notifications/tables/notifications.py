# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import django_tables2 as tables
from pl_core.tables import BaseTable
from ..models.notifications import MassNotification, Notification
from pl_users.models import PLUser


class MassNotificationsTable(BaseTable):
    pk = tables.LinkColumn(
        'dashboard-mass-notification-details',
        kwargs={'pk': tables.A('pk')},
        verbose_name='#'
    )
    notification_type_name = tables.Column(verbose_name='Тип')
    text_preview = tables.Column(verbose_name='Текст')

    class Meta(BaseTable.Meta):
        model = MassNotification
        fields = ('pk', 'status', 'text_preview', 'notification_type_name', 'scheduled_at', 'created_at')


class NotificationsTable(BaseTable):
    full_name = tables.LinkColumn(
        'dashboard-clients-details', args=[tables.A('user.client_profile.pk')], verbose_name='Клиент',
        order_by='user.last_name', accessor='user.client_profile.get_client_full_name'
    )

    class Meta(BaseTable.Meta):
        model = Notification
        fields = ('status', 'full_name', 'sent_at')


class MassNotificationUsersTable(BaseTable):
    full_name = tables.LinkColumn(
        'dashboard-clients-details', args=[tables.A('client_profile.pk')], verbose_name='Клиент',
        order_by='user.last_name', accessor='client_profile.get_client_full_name'
    )

    class Meta(BaseTable.Meta):
        model = PLUser
        fields = ('full_name',)