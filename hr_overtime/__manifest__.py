# -*- coding: utf-8 -*-
{
    'name': 'HR Overtime Wage Calculation',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Calculate overtime wages based on employee salary',
    'description': """
HR Overtime Wage Calculation
============================
This module provides functionality to:
- Record employee overtime hours
- Calculate overtime wages based on employee's contract wage
- Support different overtime rates (regular, weekend, holiday)
- Track and manage overtime requests and approvals
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['hr', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_overtime_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
