# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.tools import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_ageing_cost_for_so_line(self, quantity, reference_date=None):
        """
        Compute ageing cost for a given quantity at a reference date.
        Used by sale_msp when computing MSP on sale.order.line.
        Formula: (Daily Rate × Days Stored + Handling Fee) × qty
        """
        self.ensure_one()
        if not quantity or quantity <= 0:
            return 0.0

        reference_date = reference_date or fields.Datetime.now()
        if isinstance(reference_date, str):
            reference_date = fields.Datetime.from_string(reference_date)

        categ = self.categ_id
        rate = categ.daily_storage_rate if categ else 0.0
        handling_fee = categ.handling_dispatch_fee if categ else 0.0

        grn_date = self._get_earliest_receipt_date()
        if not grn_date:
            return 0.0

        if isinstance(grn_date, str):
            grn_date = fields.Datetime.from_string(grn_date)
        days = (reference_date - grn_date).days
        days = max(0, days)

        cost_per_unit = (rate * days) + handling_fee
        company = self.env.company
        return float_round(
            cost_per_unit * quantity,
            precision_digits=company.currency_id.decimal_places
        )

    def _get_earliest_receipt_date(self):
        """Get earliest incoming move date for this product."""
        self.ensure_one()
        move = self.env['stock.move'].search([
            ('product_id', '=', self.id),
            ('state', '=', 'done'),
            ('location_dest_id.usage', '=', 'internal'),
        ], order='date asc', limit=1)
        return move.date if move else None
