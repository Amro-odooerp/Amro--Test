# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = 'stock.move'

    days_stored = fields.Integer(
        string='Days Stored',
        compute='_compute_ageing_cost',
        store=True,
    )
    ageing_cost = fields.Float(
        string='Ageing Cost',
        compute='_compute_ageing_cost',
        store=True,
        digits='Product Price',
    )

    @api.depends('product_id', 'product_id.categ_id', 'date', 'state', 'picking_id')
    def _compute_ageing_cost(self):
        for move in self:
            if not move.product_id or move.state != 'done':
                move.days_stored = 0
                move.ageing_cost = 0.0
                continue

            grn_date = move._get_grn_date()
            if not grn_date:
                move.days_stored = 0
                move.ageing_cost = 0.0
                continue

            dispatch_date = move.date or datetime.now()
            if isinstance(dispatch_date, str):
                dispatch_date = fields.Datetime.from_string(dispatch_date)
            if isinstance(grn_date, str):
                grn_date = fields.Datetime.from_string(grn_date)

            days = (dispatch_date - grn_date).days
            move.days_stored = max(0, days)

            rate = move._get_daily_storage_rate()
            handling_fee = move._get_handling_fee() if move._is_outgoing() else 0.0
            qty = move.product_uom_qty or 0.0
            move.ageing_cost = float_round(
                (rate * move.days_stored * qty) + (handling_fee * qty),
                precision_digits=move.company_id.currency_id.decimal_places
            )

    def _get_grn_date(self):
        """Get GRN (Goods Received) date from incoming move or picking."""
        self.ensure_one()
        if self._is_outgoing():
            # For outgoing: find source move (incoming) for this product
            return self._get_incoming_date_for_product()
        # For incoming move, use move date
        return self.date

    def _get_incoming_date_for_product(self):
        """Find last incoming move date for this product/lot."""
        self.ensure_one()
        domain = [
            ('product_id', '=', self.product_id.id),
            ('state', '=', 'done'),
            ('location_dest_id.usage', '=', 'internal'),
            ('date', '<=', self.date or fields.Datetime.now()),
        ]
        if self.lot_id:
            domain.append(('lot_id', '=', self.lot_id.id))

        incoming = self.env['stock.move'].search(
            domain,
            order='date desc',
            limit=1
        )
        return incoming.date if incoming else None

    def _is_outgoing(self):
        self.ensure_one()
        return self.location_dest_id.usage in ('customer', 'supplier', 'inventory')

    def _get_daily_storage_rate(self):
        self.ensure_one()
        if not self.product_id:
            return 0.0
        categ = self.product_id.categ_id
        warehouse = self.picking_id.picking_type_id.warehouse_id if self.picking_id else None
        if warehouse and warehouse.daily_storage_rate > 0:
            return warehouse.daily_storage_rate
        return categ.daily_storage_rate if categ else 0.0

    def _get_handling_fee(self):
        self.ensure_one()
        if not self.product_id or not self.product_id.categ_id:
            return 0.0
        return self.product_id.categ_id.handling_dispatch_fee or 0.0
