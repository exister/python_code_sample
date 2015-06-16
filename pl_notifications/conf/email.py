# -*- coding: utf-8 -*-
from django.conf import settings

EMAIL_NOTIFICATION_CONFIG = getattr(settings, 'EMAIL_NOTIFICATION_CONFIG', {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend'
})