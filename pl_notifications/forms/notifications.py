# -*- coding: utf-8 -*-
from django import forms
from ..models.notifications import MassNotification, Notification
from ..models.enums import STATUS_DRAFT, STATUS_WAITING
from pl_core.forms.mixins import DefaultFormLayoutHelperMixin


class MassNotificationForm(DefaultFormLayoutHelperMixin, forms.ModelForm):
    class Meta:
        model = MassNotification
        fields = ('scheduled_at',)

    def __init__(self, *args, **kwargs):
        super(MassNotificationForm, self).__init__(*args, **kwargs)

        self.setup_form_helper()

    def save(self, commit=True):
        if self.instance.status == STATUS_DRAFT:
            self.instance.status = STATUS_WAITING
        return super(MassNotificationForm, self).save(commit)


class NotificationForm(DefaultFormLayoutHelperMixin, forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('scheduled_at',)

    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)

        self.setup_form_helper()

    def save(self, commit=True):
        if self.instance.status == STATUS_DRAFT:
            self.instance.status = STATUS_WAITING
        return super(NotificationForm, self).save(commit)