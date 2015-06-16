# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from ..models.filters import MassNotificationFilterAgeAndGender
from pl_core.forms.mixins import DefaultFormLayoutHelperMixin


class MassNotificationFilterAgeAndGenderForm(DefaultFormLayoutHelperMixin, forms.ModelForm):
    age_from = forms.IntegerField(label=u'Возраст от', min_value=0, max_value=100, required=False)
    age_to = forms.IntegerField(label=u'Возраст до', min_value=0, max_value=100, required=False)

    class Meta:
        model = MassNotificationFilterAgeAndGender
        fields = ('gender', 'age_from', 'age_to')

    def __init__(self, *args, **kwargs):
        super(MassNotificationFilterAgeAndGenderForm, self).__init__(*args, **kwargs)

        self.setup_form_helper()

    def clean(self):
        data = self.cleaned_data

        age_from = data.get('age_from')
        age_to = data.get('age_to')

        if age_from and age_to:
            if age_to < age_from:
                raise forms.ValidationError('Неверные возрастные границы')

        return data