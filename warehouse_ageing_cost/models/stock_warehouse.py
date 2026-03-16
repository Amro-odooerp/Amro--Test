# -*- coding: utf-8 -*-
from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    daily_storage_rate = fields.Float(
        string='Daily Storage Rate (Override)',
        digits='Product Price',
        default=0.0,
        help='Override product category rate. 0 means use category rate.',
    )
