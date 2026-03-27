# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    """Extend employee model with overtime-related fields"""
    _inherit = 'hr.employee'

    overtime_ids = fields.One2many(
        'hr.overtime',
        'employee_id',
        string='Overtime Records',
    )
    overtime_count = fields.Integer(
        string='Overtime Count',
        compute='_compute_overtime_stats',
    )
    total_overtime_hours = fields.Float(
        string='Total Overtime Hours (This Month)',
        compute='_compute_overtime_stats',
        help='Total approved overtime hours for current month.',
    )
    total_overtime_amount = fields.Float(
        string='Total Overtime Amount (This Month)',
        compute='_compute_overtime_stats',
        help='Total approved overtime amount for current month.',
    )
    pending_overtime_count = fields.Integer(
        string='Pending Overtime Requests',
        compute='_compute_overtime_stats',
    )

    def _compute_overtime_stats(self):
        """Compute overtime statistics for employees"""
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        for employee in self:
            # All overtime records count
            employee.overtime_count = self.env['hr.overtime'].search_count([
                ('employee_id', '=', employee.id),
            ])
            
            # Current month approved overtime
            month_overtime = self.env['hr.overtime'].search([
                ('employee_id', '=', employee.id),
                ('date', '>=', first_day_of_month),
                ('date', '<=', today),
                ('state', '=', 'approved'),
            ])
            employee.total_overtime_hours = sum(month_overtime.mapped('duration'))
            employee.total_overtime_amount = sum(month_overtime.mapped('overtime_amount'))
            
            # Pending requests
            employee.pending_overtime_count = self.env['hr.overtime'].search_count([
                ('employee_id', '=', employee.id),
                ('state', '=', 'submitted'),
            ])

    def action_view_overtime(self):
        """Open overtime records for this employee"""
        self.ensure_one()
        return {
            'name': _('Overtime Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.overtime',
            'view_mode': 'tree,form,calendar,pivot',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
            },
        }

    def get_overtime_summary(self, date_from=None, date_to=None):
        """Get detailed overtime summary for the employee"""
        self.ensure_one()
        if not date_from:
            date_from = date.today().replace(day=1)
        if not date_to:
            date_to = date.today()
        
        return self.env['hr.overtime'].get_employee_overtime_summary(
            self.id, date_from, date_to
        )


class HrEmployeePublic(models.Model):
    """Extend public employee model"""
    _inherit = 'hr.employee.public'

    overtime_count = fields.Integer(
        string='Overtime Count',
        compute='_compute_overtime_count',
    )

    def _compute_overtime_count(self):
        for employee in self:
            employee.overtime_count = self.env['hr.overtime'].sudo().search_count([
                ('employee_id', '=', employee.id),
            ])
