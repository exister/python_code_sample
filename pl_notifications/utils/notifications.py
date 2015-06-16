# -*- coding: utf-8 -*-
from ..conf.notifications import SEND_NOTIFICATION_OF_TYPES
from ..models import MASS_NOTIFICATION_CLASS_FOR_SLUG, NOTIFICATION_CLASS_FOR_SLUG


def enabled_notification_slugs():
    if isinstance(SEND_NOTIFICATION_OF_TYPES, (basestring, unicode)):
        return SEND_NOTIFICATION_OF_TYPES.split('__')
    elif isinstance(SEND_NOTIFICATION_OF_TYPES, (list, tuple)):
        return SEND_NOTIFICATION_OF_TYPES
    return []


def enabled_mass_notification_subclasses():
    mass_notification_subclasses = []
    for slug in enabled_notification_slugs():
        subclass = MASS_NOTIFICATION_CLASS_FOR_SLUG.get(slug, None)
        if subclass:
            mass_notification_subclasses.append(subclass)
    return mass_notification_subclasses


def enabled_notification_subclasses():
    notification_subclasses = []
    for slug in enabled_notification_slugs():
        subclass = NOTIFICATION_CLASS_FOR_SLUG.get(slug, None)
        if subclass:
            notification_subclasses.append(subclass)
    return notification_subclasses