# -*- coding: utf-8 -*-
from django.conf import settings
from ..conf import email


def get_email_backend():
    backend = email.EMAIL_NOTIFICATION_CONFIG.get('EMAIL_BACKEND')

    if not backend:
        backend = getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    return backend