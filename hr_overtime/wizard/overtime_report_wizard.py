# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OvertimeReportWizard(models.TransientModel):
    _name = 'overtime.report.wizard'
    _description = 'Overtime Report Wizard'

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.today,
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees',
        help='Leave empty to include all employees.',
    )
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
        help='Leave empty to include all departments.',
    )
    overtime_type_ids = fields.Many2many(
        'hr.overtime.type',
        string='Overtime Types',
        help='Leave empty to include all types.',
    )
    state_filter = fields.Selection([
        ('all', 'All'),
        ('approved', 'Approved Only'),
        ('pending', 'Pending Only'),
    ], string='Status Filter',
        default='approved',
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise UserError(_('Date From cannot be after Date To.'))

    def action_generate_report(self):
        self.ensure_one()
        
        # Build domain
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        
        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))
        
        if self.overtime_type_ids:
            domain.append(('overtime_type_id', 'in', self.overtime_type_ids.ids))
        
        if self.state_filter == 'approved':
            domain.append(('state', '=', 'approved'))
        elif self.state_filter == 'pending':
            domain.append(('state', 'in', ['draft', 'submitted']))
        
        return {
            'name': _('Overtime Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.overtime',
            'view_mode': 'tree,form,pivot,graph',
            'domain': domain,
            'context': {
                'search_default_group_employee': 1,
            },
        }

    def action_export_report(self):
        """Export overtime report to Excel/CSV."""
        self.ensure_one()
        # This would typically generate an Excel report
        # For now, we redirect to the tree view with export capability
        return self.action_generate_report()
