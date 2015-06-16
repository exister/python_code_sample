# -*- coding: utf-8 -*-
from . import SMSBackend


class ConsoleBackend(SMSBackend):
    def send(self, sms_notification):
        print 'Sending sms %s to %s' % (sms_notification, sms_notification.phone)
