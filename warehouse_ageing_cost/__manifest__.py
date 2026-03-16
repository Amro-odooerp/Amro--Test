# -*- coding: utf-8 -*-
{
    'name': 'Warehouse Ageing Cost',
    'version': '19.0.1.0',
    'category': 'Inventory',
    'summary': 'Daily storage charges from GRN to dispatch',
    'description': """
Warehouse Ageing Cost
=====================
* Daily storage charge: auto-calculate from GRN date to delivery/dispatch
* Formula: Ageing Cost = Daily Storage Rate × Days Stored + Handling Fee
* Configurable rate per product category or warehouse zone
* Optional handling/dispatch fee
* COGS integration configurable per category
* Ageing cost and inventory ageing reports
    """,
    'author': '3Stars Consulting',
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'views/product_category_views.xml',
        'views/stock_views.xml',
        'reports/ageing_cost_report.xml',
        'reports/inventory_ageing_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
