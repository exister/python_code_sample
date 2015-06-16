# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('pl_notifications.views.notifications',
    url(
        r'^mass-notifications/$',
        'mass_notifications_list_view',
        name='dashboard-mass-notifications-list'
    ),
    url(
        r'^mass-notifications/(?P<notification_type>\w+)/add/$',
        'mass_notification_create_view',
        name='dashboard-mass-notification-add'
    ),
    url(
        r'^mass-notifications/(?P<notification_type>\w+)/(?P<pk>\d+)/edit/$',
        'mass_notification_update_view',
        name='dashboard-mass-notification-edit'
    ),
    url(
        r'^mass-notifications/(?P<pk>\d+)/delete/$',
        'mass_notification_delete_view',
        name='dashboard-mass-notification-delete'
    ),
    url(
        r'^mass-notifications/(?P<pk>\d+)/$',
        'mass_notification_details_view',
        name='dashboard-mass-notification-details'
    ),
)