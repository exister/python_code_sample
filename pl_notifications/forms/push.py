# -*- coding: utf-8 -*-
from .notifications import MassNotificationForm, NotificationForm
from ..models.push import MassPushNotification, PushNotification


class MassPushNotificationForm(MassNotificationForm):
    class Meta(MassNotificationForm.Meta):
        model = MassPushNotification
        fields = MassNotificationForm.Meta.fields + (
            'os', 'text'
        )


class PushNotificationForm(NotificationForm):
    class Meta(NotificationForm.Meta):
        model = PushNotification
        fields = NotificationForm.Meta.fields + (
            'os', 'text'
        )