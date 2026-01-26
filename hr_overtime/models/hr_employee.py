# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    overtime_ids = fields.One2many(
        'hr.overtime',
        'employee_id',
        string='Overtime Records',
    )
    overtime_count = fields.Integer(
        string='Overtime Count',
        compute='_compute_overtime_count',
    )
    total_overtime_hours = fields.Float(
        string='Total Overtime Hours',
        compute='_compute_overtime_stats',
    )
    total_overtime_amount = fields.Float(
        string='Total Overtime Amount',
        compute='_compute_overtime_stats',
    )

    def _compute_overtime_count(self):
        for employee in self:
            employee.overtime_count = self.env['hr.overtime'].search_count([
                ('employee_id', '=', employee.id),
            ])

    def _compute_overtime_stats(self):
        for employee in self:
            approved_overtime = self.env['hr.overtime'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'approved'),
            ])
            employee.total_overtime_hours = sum(approved_overtime.mapped('duration'))
            employee.total_overtime_amount = sum(approved_overtime.mapped('overtime_amount'))

    def action_view_overtime(self):
        self.ensure_one()
        return {
            'name': 'Overtime Records',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.overtime',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
