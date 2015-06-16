# -*- coding: utf-8 -*-
from django.conf import settings


PL_SMS_SENDER = getattr(settings, 'PL_SMS_SENDER', 'PL_SMS_SENDER')
PL_SMS_BACKEND = getattr(settings, 'PL_SMS_BACKEND', 'pl_notifications.backends.sms.console.ConsoleBackend')
PL_SMS_BACKEND_PARAMS = getattr(settings, 'PL_SMS_BACKEND_PARAMS', {})
PL_SMS_BATCH_SIZE = getattr(settings, 'PL_SMS_BATCH_SIZE', 1)
PL_SMS_DEFAULT_TIMEOUT = getattr(settings, 'PL_SMS_DEFAULT_TIMEOUT', 5)
PL_SMS_MAX_TIMEOUT = getattr(settings, 'PL_SMS_MAX_TIMEOUT', 60)
PL_SMS_TIMEOUT_MULTIPLIER = getattr(settings, 'PL_SMS_TIMEOUT_MULTIPLIER', 2)
PL_SMS_MAX_ATTEMPTS = getattr(settings, 'PL_SMS_MAX_ATTEMPTS', 3)