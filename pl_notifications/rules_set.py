# -*- coding: utf-8 -*-
import rules
from pl_core.permissions.rules import is_group_member

##########################################
# CLINIC RULES
#
# rule name pattern:
# module.objects.action::role
##########################################

rules.add_perm(
    'pl_notifications.notifications.view::clinic_dashboard',
    is_group_member('clinic_operators', 'clinic_doctors', must_include_all=False)
)
rules.add_perm(
    'pl_notifications.notifications.add::clinic_dashboard',
    is_group_member('clinic_operators', 'clinic_doctors', must_include_all=False)
)
rules.add_perm(
    'pl_notifications.notifications.edit::clinic_dashboard',
    is_group_member('clinic_operators', 'clinic_doctors', must_include_all=False)
)
rules.add_perm(
    'pl_notifications.notifications.delete::clinic_dashboard',
    is_group_member('clinic_admins')
)

rules.add_perm('pl_notifications.mass_notifications.view::clinic_dashboard', is_group_member('clinic_admins'))
rules.add_perm('pl_notifications.mass_notifications.add::clinic_dashboard', is_group_member('clinic_admins'))
rules.add_perm('pl_notifications.mass_notifications.edit::clinic_dashboard', is_group_member('clinic_admins'))
rules.add_perm('pl_notifications.mass_notifications.delete::clinic_dashboard', is_group_member('clinic_admins'))