# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import importlib


USER_SETTINGS = getattr(settings, 'PUSH_SENDER', None)

DEFAULTS = {
    'PROVIDERS': (
        'pl_notifications.backends.push.providers.apns_provider.APNSPushSenderProvider',
        'pl_notifications.backends.push.providers.gcm_provider.GCMPushSenderProvider',
    ),
    'APNS_PROVIDER_CONFIG': {
        'HOST': 'http://localhost:7077/',
        'TIMEOUT': 15,
        'INITIAL': [
            # EXAMPLE
            # ('app_name', '/path/to/cert.pem', 'sandbox or production'),
        ],
        'USE_REQUEST_STATUS_CALLBACKS': False,
        'MESSAGE_LENGTH': 80,
        'APPLICATION': {
            # EXAMPLE
            # 'NAME': 'app_name',
            # 'CERT': '/path/to/cert.pem',
            # 'ENV': 'sandbox or production'
        },
    },
    'GCM_PROVIDER_CONFIG': {
        # Example
        'API_KEY': ''
    },
    'USER_GENDER_FILTER': lambda devices_qs: devices_qs,
}

IMPORT_STRINGS = (
    'PROVIDERS',
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, basestring):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class PushSenderSettings(object):
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.import_strings = import_strings or ()

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid API setting: '%s'" % attr)

        val = self.defaults[attr]

        if attr in self.user_settings:
            user_val = self.user_settings[attr]
            if isinstance(val, dict) and isinstance(user_val, dict):
                val.update(user_val)
            else:
                val = user_val

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        setattr(self, attr, val)
        return val

push_sender_settings = PushSenderSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)