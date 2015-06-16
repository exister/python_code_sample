# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import SMSNotification, EmailNotification, PushNotification


def object_link(obj, model, title=None):
    return '<a href="{0}">{1}</a>'.format(
        reverse('admin:%s_%s_change' % (model._meta.app_label, model._meta.module_name), args=[obj.pk]),
        title or obj
    ) if obj else 'N/A'


class BaseNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'preview', 'status', 'information_type', 'mass_notification', 'user', 'sent_at',
        'scheduled_at', 'created_at'
    )
    list_filter = ('status', 'mass_notification')
    date_hierarchy = 'created_at'
    exclude = ('content_type',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

    def preview(self, obj):
        return obj.text_preview
    preview.short_description = 'Текст'


class SMSNotificationAdmin(BaseNotificationAdmin):
    search_fields = BaseNotificationAdmin.search_fields + ('text', 'phone', )

admin.site.register(SMSNotification, SMSNotificationAdmin)


class EmailNotificationAdmin(BaseNotificationAdmin):
    search_fields = BaseNotificationAdmin.search_fields + ('to', 'subject', 'message')

admin.site.register(EmailNotification, EmailNotificationAdmin)


class PushNotificationAdmin(BaseNotificationAdmin):
    search_fields = BaseNotificationAdmin.search_fields + ('to', 'subject', 'message')

admin.site.register(PushNotification, PushNotificationAdmin)