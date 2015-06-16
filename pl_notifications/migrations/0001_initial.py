# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("pl_users", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'MassNotificationFilter'
        db.create_table(u'pl_notifications_massnotificationfilter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal(u'pl_notifications', ['MassNotificationFilter'])

        # Adding model 'MassNotificationFilterAgeAndGender'
        db.create_table(u'pl_notifications_massnotificationfilterageandgender', (
            (u'massnotificationfilter_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pl_notifications.MassNotificationFilter'], unique=True, primary_key=True)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('age_from', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('age_to', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'pl_notifications', ['MassNotificationFilterAgeAndGender'])

        # Adding model 'MassNotification'
        db.create_table(u'pl_notifications_massnotification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', to=orm['contenttypes.ContentType'])),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('mass_notification_filter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pl_notifications.MassNotificationFilter'], null=True, blank=True)),
            ('scheduled_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 4, 17, 0, 0))),
        ))
        db.send_create_signal(u'pl_notifications', ['MassNotification'])

        # Adding model 'MassNotificationUsers'
        db.create_table(u'pl_notifications_massnotificationusers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pl_users.PLUser'])),
            ('mass_notification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pl_notifications.MassNotification'])),
            ('relation_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'pl_notifications', ['MassNotificationUsers'])

        # Adding model 'Notification'
        db.create_table(u'pl_notifications_notification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', to=orm['contenttypes.ContentType'])),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('information_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('mass_notification', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'notifications', null=True, to=orm['pl_notifications.MassNotification'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'user_notifications', to=orm['pl_users.PLUser'])),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('scheduled_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 4, 17, 0, 0))),
        ))
        db.send_create_signal(u'pl_notifications', ['Notification'])

        # Adding model 'NotificationSendingAttempt'
        db.create_table(u'pl_notifications_notificationsendingattempt', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', to=orm['contenttypes.ContentType'])),
            ('notification', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'attempts', to=orm['pl_notifications.Notification'])),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('traceback', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('error', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'pl_notifications', ['NotificationSendingAttempt'])

        # Adding model 'SMSNotification'
        db.create_table(u'pl_notifications_smsnotification', (
            (u'notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pl_notifications.Notification'], unique=True, primary_key=True)),
            ('sender', self.gf('django.db.models.fields.CharField')(default='PatientCard', max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('charset', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('phone', self.gf('phonenumber_field.modelfields.PhoneNumberField')(max_length=128)),
        ))
        db.send_create_signal(u'pl_notifications', ['SMSNotification'])

        # Adding model 'MassSMSNotification'
        db.create_table(u'pl_notifications_masssmsnotification', (
            (u'massnotification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pl_notifications.MassNotification'], unique=True, primary_key=True)),
            ('sender', self.gf('django.db.models.fields.CharField')(default='PatientCard', max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('charset', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'pl_notifications', ['MassSMSNotification'])

        # Adding model 'Device'
        db.create_table(u'pl_notifications_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mobile_devices', null=True, to=orm['pl_users.PLUser'])),
            ('device_id', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('push_id', self.gf('django.db.models.fields.TextField')(default=u'')),
            ('os', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('os_version', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('screen_size', self.gf('django.db.models.fields.CharField')(default=u'', max_length=9)),
            ('badge', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'pl_notifications', ['Device'])

        # Adding model 'PushNotification'
        db.create_table(u'pl_notifications_pushnotification', (
            (u'notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pl_notifications.Notification'], unique=True, primary_key=True)),
            ('os', self.gf('django.db.models.fields.CharField')(default=u'all', max_length=50)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('apns_alert_data', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('gcm_alert_data', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('extra', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
        ))
        db.send_create_signal(u'pl_notifications', ['PushNotification'])

        # Adding M2M table for field devices on 'PushNotification'
        m2m_table_name = db.shorten_name(u'pl_notifications_pushnotification_devices')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pushnotification', models.ForeignKey(orm[u'pl_notifications.pushnotification'], null=False)),
            ('device', models.ForeignKey(orm[u'pl_notifications.device'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pushnotification_id', 'device_id'])

        # Adding M2M table for field processed_devices on 'PushNotification'
        m2m_table_name = db.shorten_name(u'pl_notifications_pushnotification_processed_devices')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pushnotification', models.ForeignKey(orm[u'pl_notifications.pushnotification'], null=False)),
            ('device', models.ForeignKey(orm[u'pl_notifications.device'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pushnotification_id', 'device_id'])

        # Adding model 'MassPushNotification'
        db.create_table(u'pl_notifications_masspushnotification', (
            (u'massnotification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pl_notifications.MassNotification'], unique=True, primary_key=True)),
            ('os', self.gf('django.db.models.fields.CharField')(default=u'all', max_length=50)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal(u'pl_notifications', ['MassPushNotification'])

        # Adding model 'EmailNotification'
        db.create_table(u'pl_notifications_emailnotification', (
            (u'notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pl_notifications.Notification'], unique=True, primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('html_message', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('to', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal(u'pl_notifications', ['EmailNotification'])

        # Adding model 'MassEmailNotification'
        db.create_table(u'pl_notifications_massemailnotification', (
            (u'massnotification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pl_notifications.MassNotification'], unique=True, primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('html_message', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal(u'pl_notifications', ['MassEmailNotification'])


    def backwards(self, orm):
        # Deleting model 'MassNotificationFilter'
        db.delete_table(u'pl_notifications_massnotificationfilter')

        # Deleting model 'MassNotificationFilterAgeAndGender'
        db.delete_table(u'pl_notifications_massnotificationfilterageandgender')

        # Deleting model 'MassNotification'
        db.delete_table(u'pl_notifications_massnotification')

        # Deleting model 'MassNotificationUsers'
        db.delete_table(u'pl_notifications_massnotificationusers')

        # Deleting model 'Notification'
        db.delete_table(u'pl_notifications_notification')

        # Deleting model 'NotificationSendingAttempt'
        db.delete_table(u'pl_notifications_notificationsendingattempt')

        # Deleting model 'SMSNotification'
        db.delete_table(u'pl_notifications_smsnotification')

        # Deleting model 'MassSMSNotification'
        db.delete_table(u'pl_notifications_masssmsnotification')

        # Deleting model 'Device'
        db.delete_table(u'pl_notifications_device')

        # Deleting model 'PushNotification'
        db.delete_table(u'pl_notifications_pushnotification')

        # Removing M2M table for field devices on 'PushNotification'
        db.delete_table(db.shorten_name(u'pl_notifications_pushnotification_devices'))

        # Removing M2M table for field processed_devices on 'PushNotification'
        db.delete_table(db.shorten_name(u'pl_notifications_pushnotification_processed_devices'))

        # Deleting model 'MassPushNotification'
        db.delete_table(u'pl_notifications_masspushnotification')

        # Deleting model 'EmailNotification'
        db.delete_table(u'pl_notifications_emailnotification')

        # Deleting model 'MassEmailNotification'
        db.delete_table(u'pl_notifications_massemailnotification')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['auth.Group']"}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pl_notifications.device': {
            'Meta': {'object_name': 'Device'},
            'badge': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'os': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'os_version': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'push_id': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'screen_size': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '9'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mobile_devices'", 'null': 'True', 'to': u"orm['pl_users.PLUser']"})
        },
        u'pl_notifications.emailnotification': {
            'Meta': {'object_name': 'EmailNotification', '_ormbases': [u'pl_notifications.Notification']},
            'html_message': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'notification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pl_notifications.Notification']", 'unique': 'True', 'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'to': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        u'pl_notifications.massemailnotification': {
            'Meta': {'object_name': 'MassEmailNotification', '_ormbases': [u'pl_notifications.MassNotification']},
            'html_message': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'massnotification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pl_notifications.MassNotification']", 'unique': 'True', 'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'})
        },
        u'pl_notifications.massnotification': {
            'Meta': {'object_name': 'MassNotification'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'to': u"orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mass_notification_filter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pl_notifications.MassNotificationFilter']", 'null': 'True', 'blank': 'True'}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 4, 17, 0, 0)'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pl_users.PLUser']", 'through': u"orm['pl_notifications.MassNotificationUsers']", 'symmetrical': 'False'})
        },
        u'pl_notifications.massnotificationfilter': {
            'Meta': {'object_name': 'MassNotificationFilter'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pl_notifications.massnotificationfilterageandgender': {
            'Meta': {'object_name': 'MassNotificationFilterAgeAndGender', '_ormbases': [u'pl_notifications.MassNotificationFilter']},
            'age_from': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'age_to': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'massnotificationfilter_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pl_notifications.MassNotificationFilter']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'pl_notifications.massnotificationusers': {
            'Meta': {'object_name': 'MassNotificationUsers'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mass_notification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pl_notifications.MassNotification']"}),
            'relation_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pl_users.PLUser']"})
        },
        u'pl_notifications.masspushnotification': {
            'Meta': {'object_name': 'MassPushNotification', '_ormbases': [u'pl_notifications.MassNotification']},
            u'massnotification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pl_notifications.MassNotification']", 'unique': 'True', 'primary_key': 'True'}),
            'os': ('django.db.models.fields.CharField', [], {'default': "u'all'", 'max_length': '50'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'pl_notifications.masssmsnotification': {
            'Meta': {'object_name': 'MassSMSNotification', '_ormbases': [u'pl_notifications.MassNotification']},
            'charset': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'massnotification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pl_notifications.MassNotification']", 'unique': 'True', 'primary_key': 'True'}),
            'sender': ('django.db.models.fields.CharField', [], {'default': "'PatientCard'", 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'pl_notifications.notification': {
            'Meta': {'ordering': "(u'-created_at',)", 'object_name': 'Notification'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'to': u"orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'mass_notification': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'notifications'", 'null': 'True', 'to': u"orm['pl_notifications.MassNotification']"}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 4, 17, 0, 0)'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'user_notifications'", 'to': u"orm['pl_users.PLUser']"})
        },
        u'pl_notifications.notificationsendingattempt': {
            'Meta': {'object_name': 'NotificationSendingAttempt'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'to': u"orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'attempts'", 'to': u"orm['pl_notifications.Notification']"}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'traceback': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'pl_notifications.pushnotification': {
            'Meta': {'object_name': 'PushNotification', '_ormbases': [u'pl_notifications.Notification']},
            'apns_alert_data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'devices+'", 'blank': 'True', 'to': u"orm['pl_notifications.Device']"}),
            'extra': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'gcm_alert_data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            u'notification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pl_notifications.Notification']", 'unique': 'True', 'primary_key': 'True'}),
            'os': ('django.db.models.fields.CharField', [], {'default': "u'all'", 'max_length': '50'}),
            'processed_devices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'processed_devices+'", 'blank': 'True', 'to': u"orm['pl_notifications.Device']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'pl_notifications.smsnotification': {
            'Meta': {'object_name': 'SMSNotification', '_ormbases': [u'pl_notifications.Notification']},
            'charset': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'notification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pl_notifications.Notification']", 'unique': 'True', 'primary_key': 'True'}),
            'phone': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128'}),
            'sender': ('django.db.models.fields.CharField', [], {'default': "'PatientCard'", 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'pl_users.pluser': {
            'Meta': {'object_name': 'PLUser'},
            'birthday': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'confirmed_contacts': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('versatileimagefield.fields.VersatileImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['pl_notifications']