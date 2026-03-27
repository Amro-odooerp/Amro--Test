# -*- coding: utf-8 -*-
{
    'name': 'HR Overtime Management',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage and calculate employee overtime',
    'description': """
HR Overtime Management
======================
This module provides functionality to:
- Track employee overtime hours
- Calculate overtime pay based on configurable rates
- Support different overtime types (regular, weekend, holiday)
- Approval workflow for overtime requests
- Integration with HR and Payroll modules
- Reporting and analytics for overtime data
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
        'data/hr_overtime_data.xml',
        'views/hr_overtime_views.xml',
        'views/hr_overtime_type_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_overtime_menu.xml',
        'report/hr_overtime_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
