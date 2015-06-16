# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from pl_core.permissions.views import dashboard_access
from pl_core.responses import JsonResponse
from pl_core.tables import TableViewMixin
from ..models.notifications import MassNotification, Notification
from ..tables.notifications import MassNotificationsTable, MassNotificationUsersTable, NotificationsTable
from ..forms.filters import MassNotificationFilterAgeAndGenderForm
from ..forms.emails import MassEmailNotificationForm, EmailNotificationForm
from ..forms.smses import MassSMSNotificationForm, SMSNotificationForm
from ..forms.push import MassPushNotificationForm, PushNotificationForm
from ..models.enums import *


class BaseNotificationViewMixin(object):
    def get_queryset(self):
        return self.model.objects.select_subclasses()


class MassNotificationViewMixin(BaseNotificationViewMixin):
    model = MassNotification

    def get_success_url(self):
        return reverse('dashboard-mass-notifications-list')


class NotificationViewMixin(BaseNotificationViewMixin):
    model = Notification

    def get_success_url(self):
        return reverse('dashboard-mass-notifications-list')


class BaseNotificationCreateUpdateViewMixin(object):
    notification_types = [
        'sms',
        'email',
        'push'
    ]
    notification_form_classes = {}

    def get_notification_type(self):
        notification_type = self.kwargs.get('notification_type')
        if notification_type not in self.notification_types:
            raise Http404
        return notification_type

    def get_form_class(self):
        return self.notification_form_classes.get(self.get_notification_type())

    def get_context_data(self, **kwargs):
        ctx = super(BaseNotificationCreateUpdateViewMixin, self).get_context_data(**kwargs)

        ctx['notification_type'] = self.get_notification_type()

        return ctx


class NotificationCreateUpdateViewMixin(BaseNotificationCreateUpdateViewMixin):
    notification_form_classes = {
        'sms': SMSNotificationForm,
        'email': EmailNotificationForm,
        'push': PushNotificationForm,
    }


class MassNotificationCreateUpdateViewMixin(BaseNotificationCreateUpdateViewMixin):
    notification_form_classes = {
        'sms': MassSMSNotificationForm,
        'email': MassEmailNotificationForm,
        'push': MassPushNotificationForm,
    }
    notification_filter_form_classes = {
        'sms': MassNotificationFilterAgeAndGenderForm,
        'email': MassNotificationFilterAgeAndGenderForm,
        'push': MassNotificationFilterAgeAndGenderForm,
    }

    def get_filter_form_class(self):
        return self.notification_filter_form_classes.get(self.get_notification_type())

    def get_filter_form(self, form_class):
        return form_class(**self.get_filter_form_kwargs())

    def get_filter_form_kwargs(self):
        kwargs = super(MassNotificationCreateUpdateViewMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.filter_object})
        return kwargs

    def get_initial(self):
        if not hasattr(self, '_initial'):
            if self.object is None:
                self._initial = {}

                template_id = self.request.GET.get('template', None)
                if template_id:
                    try:
                        mass_notification = self.get_queryset().get(pk=template_id)
                    except self.model.DoesNotExist:
                        mass_notification = None

                    if mass_notification:
                        self._initial = mass_notification.get_initial_data()
            else:
                self._initial = super(MassNotificationCreateUpdateViewMixin, self).get_initial()
        return self._initial

    def _get(self):
        form_class = self.get_form_class()
        filter_form_class = self.get_filter_form_class()

        form = self.get_form(form_class)
        filter_form = self.get_filter_form(filter_form_class)

        return self.render_to_response(self.get_context_data(form=form, filter_form=filter_form))

    def _post(self):
        form_class = self.get_form_class()
        filter_form_class = self.get_filter_form_class()

        form = self.get_form(form_class)
        filter_form = self.get_filter_form(filter_form_class)

        if form.is_valid() and filter_form.is_valid():
            return self.forms_valid(form, filter_form)
        else:
            return self.forms_invalid(form, filter_form)

    def forms_valid(self, form, filter_form):
        filter_obj = filter_form.save()
        form.instance.mass_notification_filter = filter_obj

        if self.request.GET.get('counter'):
            return self.counter_response(form)

        obj = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, filter_form):
        filter_obj = filter_form.instance
        form.instance.mass_notification_filter = filter_obj

        if self.request.GET.get('counter'):
            return self.counter_response(form)

        return self.render_to_response(self.get_context_data(form=form, filter_form=filter_form))

    def counter_response(self, form):
        return JsonResponse({
            'users_count': form.instance.filtered_users().count()
        })


class MassNotificationsListView(MassNotificationViewMixin, TableViewMixin, ListView):
    template_name = 'notifications/dashboard/mass_notification/list.html'
    table_class = MassNotificationsTable

    def get_context_data(self, **kwargs):
        ctx = super(MassNotificationsListView, self).get_context_data(**kwargs)

        ctx['objects_table'] = self.get_table(self.object_list, self.request)

        return ctx

mass_notifications_list_view = dashboard_access(
    'pl_notifications.mass_notifications.view::clinic_dashboard',
    MassNotificationsListView
)


class MassNotificationCreateView(MassNotificationViewMixin, MassNotificationCreateUpdateViewMixin, CreateView):
    template_name = 'notifications/dashboard/mass_notification/add.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        self.filter_object = None
        return self._get()

    def post(self, request, *args, **kwargs):
        self.object = None
        self.filter_object = None

        with transaction.atomic():
            return self._post()

mass_notification_create_view = dashboard_access(
    'pl_notifications.mass_notifications.add::clinic_dashboard',
    MassNotificationCreateView
)


class MassNotificationUpdateView(MassNotificationViewMixin, MassNotificationCreateUpdateViewMixin, UpdateView):
    template_name = 'notifications/dashboard/mass_notification/edit.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.filter_object = self.object.mass_notification_filter.concrete_mass_notification_filter

        if not self.object.is_editable:
            messages.warning(request, 'Запись недоступна для редактирования')
            return redirect(reverse('dashboard-mass-notification-details', kwargs=kwargs))

        return self._get()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.filter_object = self.object.mass_notification_filter.concrete_mass_notification_filter

        if not self.object.is_editable:
            messages.warning(request, 'Запись недоступна для редактирования')
            return redirect(reverse('dashboard-mass-notification-details', kwargs=kwargs))

        with transaction.atomic():
            return self._post()

mass_notification_update_view = dashboard_access(
    'pl_notifications.mass_notifications.edit::clinic_dashboard',
    MassNotificationUpdateView
)


class MassNotificationDeleteView(MassNotificationViewMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            self.object = self.get_object()

            if self.object.is_editable:
                self.object.delete()
                return JsonResponse({'url': self.get_success_url()})
            raise Http404

mass_notification_delete_view = dashboard_access(
    'pl_notifications.mass_notifications.delete::clinic_dashboard',
    MassNotificationDeleteView
)


class MassNotificationDetailsView(TableViewMixin, MassNotificationViewMixin, DetailView):
    template_name = 'notifications/dashboard/mass_notification/details.html'

    def get_details_table(self):
        if self.object.status in (STATUS_DRAFT, STATUS_WAITING):
            users = self.object.filtered_users().select_related('client_profile')
            return self.get_table(users, self.request, MassNotificationUsersTable)
        else:
            notifications = self.object.notifications.all().select_subclasses()
            return self.get_table(notifications, self.request, NotificationsTable)

    def get_details_table_label(self):
        if self.object.status in (STATUS_DRAFT, STATUS_WAITING):
            return 'Будет отправлено клиентам'
        else:
            return 'Статус отправки клиентам'

    def get_context_data(self, **kwargs):
        ctx = super(MassNotificationDetailsView, self).get_context_data(**kwargs)

        ctx['details_inc_name'] = 'notifications/dashboard/inc.details.{0}.html'.format(
            self.object.notification_type_slug
        )
        ctx['details_table'] = self.get_details_table()
        ctx['details_table_label'] = self.get_details_table_label()

        return ctx


mass_notification_details_view = dashboard_access(
    'pl_notifications.mass_notifications.view::clinic_dashboard',
    MassNotificationDetailsView
)


class NotificationCreateView(NotificationCreateUpdateViewMixin, CreateView):
    template_name = 'notifications/dashboard/notification/add.html'

    def post(self, request, *args, **kwargs):

        with transaction.atomic():
            return super(NotificationCreateView, self).post(request, *args, **kwargs)


class NotificationUpdateView(NotificationViewMixin, NotificationCreateUpdateViewMixin, UpdateView):
    template_name = 'notifications/dashboard/notification/edit.html'

    def get_non_editable_redirect_url(self):
        return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.is_editable:
            messages.warning(request, 'Запись недоступна для редактирования')
            return redirect(self.get_non_editable_redirect_url())

        return super(NotificationUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.is_editable:
            messages.warning(request, 'Запись недоступна для редактирования')
            return redirect(self.get_non_editable_redirect_url())

        with transaction.atomic():
            return super(NotificationUpdateView, self).post(request, *args, **kwargs)


class NotificationDetailsView(NotificationViewMixin, DetailView):
    template_name = 'notifications/dashboard/notification/details.html'

    def get_context_data(self, **kwargs):
        ctx = super(NotificationDetailsView, self).get_context_data(**kwargs)

        ctx['details_inc_name'] = 'notifications/dashboard/inc.details.{0}.html'.format(
            self.object.notification_type_slug
        )

        return ctx


class NotificationDeleteView(NotificationViewMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            self.object = self.get_object()

            if self.object.is_editable:
                self.object.delete()
                return JsonResponse({'url': self.get_success_url()})
            raise Http404
