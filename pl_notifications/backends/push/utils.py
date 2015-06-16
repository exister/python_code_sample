# -*- coding: utf-8 -*-
from .sender import PushSender


def get_token_groups(user):
    '''
    Get sets of tokens grouped by OS type

    :param user: User instance
    :return: {'os': tokens}
    '''
    providers = PushSender.get_providers_keys_and_os()
    tokens = dict((key, set([])) for key in providers.keys())

    for device in user.mobile_devices.all():
        if device.push_id is not None and device.push_id != "" and device.push_id:
            for provider, device_os in providers.iteritems():
                if device.os.startswith(device_os):
                    tokens[provider].add(device.push_id)
    return tokens
