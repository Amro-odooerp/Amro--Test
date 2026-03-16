# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    daily_storage_rate = fields.Float(
        string='Daily Storage Rate',
        digits='Product Price',
        default=0.0,
        help='Daily storage cost per unit. Used in Ageing Cost = Rate × Days Stored.',
    )
    handling_dispatch_fee = fields.Float(
        string='Handling/Dispatch Fee',
        digits='Product Price',
        default=0.0,
        help='Optional fee applied at dispatch.',
    )
    ageing_in_cogs = fields.Boolean(
        string='Ageing in COGS',
        default=False,
        help='Include ageing cost in Cost of Goods Sold.',
    )

    @api.constrains('daily_storage_rate')
    def _check_daily_storage_rate(self):
        for record in self:
            if record.daily_storage_rate < 0:
                raise ValidationError(
                    'Daily Storage Rate cannot be negative.'
                )
