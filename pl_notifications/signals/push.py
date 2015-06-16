# -*- coding: utf-8 -*-
from django.dispatch import Signal


device_created = Signal(providing_args=['device'])