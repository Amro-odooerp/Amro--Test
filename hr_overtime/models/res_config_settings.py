# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    overtime_monthly_hours = fields.Float(
        string='Monthly Working Hours',
        default=173.33,
        help='Standard monthly working hours used to calculate hourly rate from monthly wage.',
    )
    overtime_max_hours = fields.Float(
        string='Maximum Overtime Hours',
        default=12.0,
        help='Maximum allowed overtime hours per single request.',
    )
    overtime_approval_required = fields.Boolean(
        string='Overtime Approval Required',
        default=True,
        help='If enabled, overtime requests require manager approval.',
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    overtime_monthly_hours = fields.Float(
        related='company_id.overtime_monthly_hours',
        readonly=False,
        string='Monthly Working Hours',
    )
    overtime_max_hours = fields.Float(
        related='company_id.overtime_max_hours',
        readonly=False,
        string='Maximum Overtime Hours',
    )
    overtime_approval_required = fields.Boolean(
        related='company_id.overtime_approval_required',
        readonly=False,
        string='Overtime Approval Required',
    )
