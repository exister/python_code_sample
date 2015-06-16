# -*- coding: utf-8 -*-
import copy

from django.utils.encoding import smart_unicode
import requests

from . import SMSBackend
from pl_notifications.models.smses import CHARSET_ASCII, CHARSET_CYRILLIC


class KannelBadStatusException(Exception):
    pass


class KannelBackend(SMSBackend):
    def __init__(self, sendsms_host='http://127.0.0.1', sendsms_port='13013', sendsms_params=None, charset=None,
                 coding=None, encode_errors=None, delivery_report_url=None, **kwargs):
        super(KannelBackend, self).__init__(**kwargs)

        self.sendsms_url = '{0}:{1}/cgi-bin/sendsms'.format(sendsms_host, sendsms_port)
        self.sendsms_params = sendsms_params or {}
        self.charset = charset or 'utf-16'
        self.coding = coding or 2
        self.encode_errors = encode_errors or 'ignore'
        self.delivery_report_url = delivery_report_url

    def charset_for_sms(self, sms):
        if sms.charset == CHARSET_ASCII:
            return 'utf-8'
        elif sms.charset == CHARSET_CYRILLIC:
            return 'utf-16'
        return None

    def coding_for_sms(self, sms):
        if sms.charset == CHARSET_ASCII:
            return 0
        elif sms.charset == CHARSET_CYRILLIC:
            return 2
        return None

    def prepare_request(self, text, identities, sender, charset=None, coding=None):
        kwargs = {'url': self.sendsms_url}
        query = copy.copy(self.sendsms_params)
        query['to'] = ' '.join(identities)
        query['from'] = sender
        query['text'] = text.encode(charset or self.charset, self.encode_errors)
        query['coding'] = coding or self.coding
        query['charset'] = self.charset
        kwargs['params'] = query
        return kwargs

    def send(self, sms_notification):
        """
        Caller should catch all exceptions
        :param sms_notification:
        :return:
        """

        phones = [smart_unicode(sms_notification.phone.as_e164)]

        kwargs = self.prepare_request(
            sms_notification.text,
            phones,
            sms_notification.sender,
            charset=self.charset_for_sms(sms_notification),
            coding=self.coding_for_sms(sms_notification),
        )

        r = requests.get(**kwargs)
        if r.status_code != requests.codes.accepted:
            raise KannelBadStatusException('Bad status code: {0}'.format(r.status_code))
