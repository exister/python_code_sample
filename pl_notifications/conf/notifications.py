# -*- coding: utf-8 -*-
from django.conf import settings

SEND_NOTIFICATION_OF_TYPES = getattr(settings, 'SEND_NOTIFICATION_OF_TYPES', [
    'sms',
    'email',
    'push'
])