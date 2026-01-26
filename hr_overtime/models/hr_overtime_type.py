# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrOvertimeType(models.Model):
    """Model for different types of overtime with their rates"""
    _name = 'hr.overtime.type'
    _description = 'Overtime Type'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    rate = fields.Float(
        string='Rate Multiplier',
        required=True,
        default=1.5,
        help='Multiplier applied to hourly rate. E.g., 1.5 means 150% of normal rate.',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    color = fields.Integer(
        string='Color',
    )
    description = fields.Text(
        string='Description',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    # Configuration options
    requires_approval = fields.Boolean(
        string='Requires Approval',
        default=True,
        help='If checked, overtime of this type requires manager approval.',
    )
    max_hours_per_day = fields.Float(
        string='Max Hours Per Day',
        default=4.0,
        help='Maximum overtime hours allowed per day for this type.',
    )
    max_hours_per_month = fields.Float(
        string='Max Hours Per Month',
        default=40.0,
        help='Maximum overtime hours allowed per month for this type.',
    )

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)',
         'The code must be unique per company!'),
        ('rate_positive', 'CHECK(rate > 0)',
         'Rate multiplier must be positive!'),
    ]

    @api.constrains('max_hours_per_day', 'max_hours_per_month')
    def _check_max_hours(self):
        for record in self:
            if record.max_hours_per_day < 0:
                raise ValidationError(_('Max hours per day cannot be negative.'))
            if record.max_hours_per_month < 0:
                raise ValidationError(_('Max hours per month cannot be negative.'))
            if record.max_hours_per_day > 24:
                raise ValidationError(_('Max hours per day cannot exceed 24 hours.'))
