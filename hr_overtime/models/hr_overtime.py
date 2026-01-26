# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _description = 'Employee Overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: 'New'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True
    )
    contract_id = fields.Many2one(
        'hr.contract',
        string='Contract',
        compute='_compute_contract_id',
        store=True,
        readonly=False
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    # Time fields
    hours = fields.Float(
        string='Overtime Hours',
        required=True,
        tracking=True
    )
    
    # Overtime type and rate
    overtime_type = fields.Selection([
        ('regular', 'Regular Overtime (1.5x)'),
        ('weekend', 'Weekend Overtime (2x)'),
        ('holiday', 'Holiday Overtime (2.5x)'),
        ('night', 'Night Shift Overtime (1.75x)'),
    ], string='Overtime Type', required=True, default='regular', tracking=True)
    
    overtime_rate = fields.Float(
        string='Overtime Rate Multiplier',
        compute='_compute_overtime_rate',
        store=True
    )
    
    # Wage and calculation fields
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='contract_id.currency_id',
        store=True
    )
    employee_wage = fields.Monetary(
        string='Monthly Wage',
        compute='_compute_employee_wage',
        store=True,
        currency_field='currency_id'
    )
    hourly_rate = fields.Monetary(
        string='Hourly Rate',
        compute='_compute_hourly_rate',
        store=True,
        currency_field='currency_id',
        help='Calculated as: Monthly Wage / (Working Days per Month * Working Hours per Day)'
    )
    overtime_hourly_rate = fields.Monetary(
        string='Overtime Hourly Rate',
        compute='_compute_overtime_amount',
        store=True,
        currency_field='currency_id',
        help='Hourly Rate * Overtime Rate Multiplier'
    )
    overtime_amount = fields.Monetary(
        string='Overtime Amount',
        compute='_compute_overtime_amount',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    
    # Configuration fields
    working_days_per_month = fields.Float(
        string='Working Days/Month',
        default=22.0,
        help='Number of working days per month used for hourly rate calculation'
    )
    working_hours_per_day = fields.Float(
        string='Working Hours/Day',
        default=8.0,
        help='Number of working hours per day used for hourly rate calculation'
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)
    
    # Additional info
    description = fields.Text(string='Description')
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.overtime') or 'New'
        return super().create(vals_list)

    @api.depends('employee_id')
    def _compute_contract_id(self):
        """Get the current active contract for the employee"""
        for record in self:
            if record.employee_id:
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('state', '=', 'open')
                ], limit=1)
                record.contract_id = contract
            else:
                record.contract_id = False

    @api.depends('contract_id', 'contract_id.wage')
    def _compute_employee_wage(self):
        """Get the wage from employee's contract"""
        for record in self:
            if record.contract_id:
                record.employee_wage = record.contract_id.wage
            else:
                record.employee_wage = 0.0

    @api.depends('employee_wage', 'working_days_per_month', 'working_hours_per_day')
    def _compute_hourly_rate(self):
        """Calculate hourly rate from monthly wage"""
        for record in self:
            if record.working_days_per_month and record.working_hours_per_day:
                total_hours = record.working_days_per_month * record.working_hours_per_day
                record.hourly_rate = record.employee_wage / total_hours if total_hours else 0.0
            else:
                record.hourly_rate = 0.0

    @api.depends('overtime_type')
    def _compute_overtime_rate(self):
        """Get the overtime rate multiplier based on overtime type"""
        rate_mapping = {
            'regular': 1.5,
            'weekend': 2.0,
            'holiday': 2.5,
            'night': 1.75,
        }
        for record in self:
            record.overtime_rate = rate_mapping.get(record.overtime_type, 1.5)

    @api.depends('hourly_rate', 'overtime_rate', 'hours')
    def _compute_overtime_amount(self):
        """Calculate the overtime amount"""
        for record in self:
            record.overtime_hourly_rate = record.hourly_rate * record.overtime_rate
            record.overtime_amount = record.overtime_hourly_rate * record.hours

    @api.constrains('hours')
    def _check_hours(self):
        """Validate overtime hours"""
        for record in self:
            if record.hours <= 0:
                raise ValidationError("Overtime hours must be greater than zero.")
            if record.hours > 24:
                raise ValidationError("Overtime hours cannot exceed 24 hours per day.")

    def action_submit(self):
        """Submit overtime request for approval"""
        self.write({'state': 'submitted'})

    def action_approve(self):
        """Approve the overtime request"""
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now()
        })

    def action_refuse(self):
        """Refuse the overtime request"""
        self.write({'state': 'refused'})

    def action_cancel(self):
        """Cancel the overtime request"""
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.write({
            'state': 'draft',
            'approved_by': False,
            'approved_date': False
        })

    def unlink(self):
        """Only allow deletion of draft or cancelled records"""
        for record in self:
            if record.state not in ('draft', 'cancelled'):
                raise ValidationError(
                    "You cannot delete an overtime record that is not in Draft or Cancelled state."
                )
        return super().unlink()


class HrOvertimeSequence(models.Model):
    """Create sequence on module installation"""
    _inherit = 'ir.sequence'

    @api.model
    def _create_overtime_sequence(self):
        """Create overtime sequence if it doesn't exist"""
        if not self.search([('code', '=', 'hr.overtime')]):
            self.create({
                'name': 'HR Overtime Sequence',
                'code': 'hr.overtime',
                'prefix': 'OT/',
                'padding': 5,
                'company_id': False,
            })
