# -*- coding: utf-8 -*-
import logging

from .settings import push_sender_settings


logger = logging.getLogger('pl_app')


class PushSender(object):
    settings = push_sender_settings

    #Dict of providers loaded from settings {'provider_key': {'provider': ProviderClass, 'os': 'os_pattern'}}
    providers = dict((provider.get_key(), {'provider': provider, 'os': provider.get_os()}) for provider in push_sender_settings.PROVIDERS)

    @classmethod
    def get_providers_keys(cls):
        """
        Keys for all loaded providers

        :return: list of keys
        """
        return cls.providers.keys()

    @classmethod
    def get_providers_keys_and_os(cls):
        """
        Pairs of provider key and os pattern

        :return: {'APNS': 'iOS', ...}
        """
        return dict((key, cls.providers[key]['os']) for key in cls.providers.keys())

    @classmethod
    def get_provider(cls, name):
        """
        Get provider instance.

        :param name: provider key
        :return: provider instance with loaded configuration
        """
        provider = cls.providers.get(name)
        if provider:
            return provider['provider'](getattr(cls.settings, '{name}_PROVIDER_CONFIG'.format(name=name), {}))
        return None

    @classmethod
    def send_notifications(cls, tokens, alert=None, badge=None, sound=None, extra=None, fail_silently=True):
        """
        Send text notification to all devices with given tokens

        Could be used like this:

        >>> from pl_notifications.backends.push.utils import get_token_groups
        >>> tokens = get_token_groups(user)
        >>> PushSender.send_notifications(tokens, alert=text, badge=badge, extra={})

        :param tokens: Tokens dict {'service_type': [token, token, ...]}
        :param alert: Message (str)
        :param badge: Badge counter (int)
        :param sound: (str)
        :param extra: Extra parameters (dict)
        :param from_user: (object)
        :param to_user: (object)
        :return:
        """
        for key, devices in tokens.iteritems():
            if devices:
                provider = cls.get_provider(key)
                if provider:
                    try:
                        provider.notify(
                            tokens=list(devices),
                            alert=alert,
                            badge=badge,
                            sound=sound,
                            extra=extra,
                        )
                    except TypeError, e:
                        logger.error(
                            "Can not sent notification to devices %s, (Exception: %s)" %
                            (devices, unicode(e)),
                            exc_info=True,
                            extra={'stack': True}
                        )
                        if not fail_silently:
                            raise e
                    except Exception, e:
                        logger.error(
                            "Can not sent notification to devices %s, (Exception: %s)" %
                            (devices, unicode(e)),
                            exc_info=True,
                            extra={'stack': True}
                        )
                        if not fail_silently:
                            raise e
