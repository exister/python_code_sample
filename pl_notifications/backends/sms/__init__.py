# -*- coding: utf-8 -*-


class SMSBackend(object):
    def __init__(self, **kwargs):
        super(SMSBackend, self).__init__()

    def send(self, sms_notification):
        raise NotImplementedError()