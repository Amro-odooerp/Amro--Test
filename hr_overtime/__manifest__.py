# -*- coding: utf-8 -*-
{
    'name': 'HR Overtime Management',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage and calculate employee overtime hours and payments',
    'description': """
HR Overtime Management Module
=============================

This module allows you to:
- Track employee overtime hours
- Define multiple overtime types with different rates
- Calculate overtime payments automatically
- Generate overtime reports
- Manage overtime approval workflow
- Configure company-wide overtime settings

Features:
---------
* Multiple overtime types (Regular, Weekend, Holiday, Night Shift)
* Configurable overtime rates per type
* Approval workflow (Draft -> Submitted -> Approved/Rejected)
* Integration with HR Employee module
* Overtime reports and analytics
* Monthly overtime summaries
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'hr',
        'hr_contract',
    ],
    'data': [
        'security/hr_overtime_security.xml',
        'security/ir.model.access.csv',
        'data/hr_overtime_type_data.xml',
        'views/hr_overtime_type_views.xml',
        'views/hr_overtime_views.xml',
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/overtime_report_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
