# -*- coding: utf-8 -*-


class PushSenderProvider(object):
    """
    Base class for push providers
    """

    @classmethod
    def get_key(cls):
        """
        Unique provider key

        :return:
        """
        raise NotImplementedError()

    @classmethod
    def get_os(cls):
        """
        OS pattern to determine if this provider matches user device

        :return:
        """
        raise NotImplementedError()

    def __init__(self, config=None):
        """

        :param config: Provider configuration dict
        :return:
        """
        self.config = config

    def _preprocess_tokens(self, tokens):
        """
        Normalize and validate list of tokens

        :param tokens: list of tokens
        :return:
        """
        return tokens

    def _check_arguments(self, *args, **kwargs):
        """
        Check presence of all required arguments

        :param args:
        :param kwargs:
        :raises: Exception if args are invalid
        :return:
        """
        pass

    def _setup_notifier(self):
        """
        Prepare actual sender

        :return:
        """
        pass

    def _prepare_payload(self, tokens, *args, **kwargs):
        """
        Generate data in suitable format

        :param args:
        :param kwargs:
        :return: data
        """
        raise NotImplementedError()

    def _validate_payload(self, payload):
        """
        Check payload prepared in `_prepare_payload` for maximum length, etc.

        :param payload: payload from `_prepare_payload`
        :raises: ValueError
        :return:
        """
        return payload

    def _send_notification(self, tokens, payload, **kwargs):
        """
        Send notification using concrete provider

        :param tokens: list of tokens
        :param payload: payload from `_prepare_payload`
        :param kwargs:
        :return: True if notification was successfully sent, False if failed
        """
        raise NotImplementedError()

    def _request_done(self, *args, **kwargs):
        """
        Called after notification was successfully sent

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def _request_failed(self, *args, **kwargs):
        """
        Called if notification failed

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def notify(self, tokens, **kwargs):
        """
        General workflow for sending notification

        :param list tokens: list of tokens
        :param str alert: message
        :param bool unique: each message has different content
        :param int badge: badge counter
        :param dict badge: badge counters
        :param str sound: sound name
        :param dict extra: extra params
        :return:
        """

        if not isinstance(tokens, (list, tuple)):
            raise TypeError('Tokens parameter should be a list or tuple')

        self._check_arguments(**kwargs)

        tokens = self._preprocess_tokens(tokens)

        if not tokens:
            return

        self._setup_notifier()

        payload = self._prepare_payload(tokens, **kwargs)
        payload = self._validate_payload(payload)

        done = self._send_notification(tokens, payload, **kwargs)
        if self.config.get('USE_REQUEST_STATUS_CALLBACKS', True):
            if done:
                self._request_done(**kwargs)
            else:
                self._request_failed(**kwargs)
