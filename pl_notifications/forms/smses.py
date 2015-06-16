# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from .notifications import MassNotificationForm, NotificationForm
from ..models.smses import MassSMSNotification, SMSNotification, CHARSET_ASCII, CHARSET_CYRILLIC


class SMSNotificationFormMixin(object):
    def clean(self):
        data = super(SMSNotificationFormMixin, self).clean()

        charset = data.get('charset', 0)
        text = data.get('text', '')

        if charset == CHARSET_ASCII:
            if len(text) > 160:
                raise forms.ValidationError('Превышен лимит текста')
        elif charset == CHARSET_CYRILLIC:
            if len(text) > 70:
                raise forms.ValidationError('Превышен лимит текста')

        return data


class MassSMSNotificationForm(SMSNotificationFormMixin, MassNotificationForm):
    class Meta(MassNotificationForm.Meta):
        model = MassSMSNotification
        fields = MassNotificationForm.Meta.fields + (
            'text', 'charset'
        )


class SMSNotificationForm(SMSNotificationFormMixin, NotificationForm):
    class Meta(NotificationForm.Meta):
        model = SMSNotification
        fields = NotificationForm.Meta.fields + (
            'text', 'charset'
        )