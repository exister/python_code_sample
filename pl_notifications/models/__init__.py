# -*- coding: utf-8 -*-
from .notifications import *
from .smses import *
from .push import *
from .emails import *

MASS_NOTIFICATION_CLASS_FOR_SLUG = {
    'email': MassEmailNotification,
    'sms': MassSMSNotification,
    'push': MassPushNotification,
}

NOTIFICATION_CLASS_FOR_SLUG = {
    'email': EmailNotification,
    'sms': SMSNotification,
    'push': PushNotification,
}