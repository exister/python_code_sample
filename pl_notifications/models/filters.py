# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType

from polymodels.models import PolymorphicModel
from django.db import models

from pl_users._models.enums import GENDER_CHOICES, GENDER_NOT_SET, GENDER_MALE, GENDER_FEMALE


class MassNotificationFilter(PolymorphicModel):

    class Meta:
        app_label = 'pl_notifications'

    @property
    def mass_notification_filter_type_class(self):
        return ContentType.objects.get_for_id(self.content_type_id).model_class()

    @property
    def concrete_mass_notification_filter(self):
        return self.type_cast(to=self.mass_notification_filter_type_class)

    def get_initial_data(self):
        return {}


class MassNotificationFilterAgeAndGender(MassNotificationFilter):
    gender = models.IntegerField(verbose_name='Пол', choices=GENDER_CHOICES, default=GENDER_NOT_SET)
    age_from = models.IntegerField(verbose_name='Возраст от', null=True, blank=True)
    age_to = models.IntegerField(verbose_name='Возраст до', null=True, blank=True)

    class Meta:
        app_label = 'pl_notifications'

    def filter_users(self, users):
        filters = models.Q()

        if self.gender in (GENDER_MALE, GENDER_FEMALE):
            filters &= models.Q(gender=self.gender)

        if self.age_from is not None:
            date = datetime.date.today() - relativedelta(years=self.age_from)

            filters &= models.Q(birthday__lte=date) | models.Q(birthday__isnull=True)

        if self.age_to is not None:
            date = datetime.date.today() - relativedelta(years=self.age_to)

            filters &= models.Q(birthday__gte=date) | models.Q(birthday__isnull=True)

        return users.filter(filters)

    def get_initial_data(self):
        initial_data = super(MassNotificationFilterAgeAndGender, self).get_initial_data()
        initial_data.update({
            'gender': self.gender,
            'age_from': self.age_from,
            'age_to': self.age_to
        })
        return initial_data
