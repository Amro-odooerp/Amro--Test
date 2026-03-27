# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrOvertimeType(models.Model):
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
        help='Multiplier applied to the base hourly rate. '
             'For example, 1.5 means 150% of the base rate.',
    )
    description = fields.Text(
        string='Description',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    color = fields.Integer(
        string='Color',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    
    # Constraints
    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 
         'The overtime type code must be unique per company!'),
    ]

    @api.constrains('rate')
    def _check_rate(self):
        for record in self:
            if record.rate <= 0:
                raise ValidationError(_('Rate multiplier must be greater than 0.'))
