# -*- coding: utf-8 -*-
from .notifications import MassNotificationForm, NotificationForm
from ..models.emails import MassEmailNotification, EmailNotification


class MassEmailNotificationForm(MassNotificationForm):
    class Meta(MassNotificationForm.Meta):
        model = MassEmailNotification
        fields = MassNotificationForm.Meta.fields + (
            'subject', 'message', 'html_message'
        )


class EmailNotificationForm(NotificationForm):
    class Meta(NotificationForm.Meta):
        model = EmailNotification
        fields = NotificationForm.Meta.fields + (
            'subject', 'message', 'html_message'
        )