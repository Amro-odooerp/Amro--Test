# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class HrOvertime(models.Model):
    """Model for tracking and calculating employee overtime"""
    _name = 'hr.overtime'
    _description = 'Employee Overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True,
        index=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        related='employee_id.parent_id',
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='employee_id.company_id',
        store=True,
        readonly=True,
    )
    contract_id = fields.Many2one(
        'hr.contract',
        string='Contract',
        compute='_compute_contract_id',
        store=True,
    )

    # Time tracking
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        index=True,
    )
    date_start = fields.Datetime(
        string='Start Time',
        required=True,
        tracking=True,
    )
    date_end = fields.Datetime(
        string='End Time',
        required=True,
        tracking=True,
    )
    duration = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration',
        store=True,
        readonly=True,
    )

    # Overtime classification
    overtime_type_id = fields.Many2one(
        'hr.overtime.type',
        string='Overtime Type',
        required=True,
        tracking=True,
    )
    rate = fields.Float(
        string='Rate Multiplier',
        related='overtime_type_id.rate',
        store=True,
        readonly=True,
    )

    # Financial calculation
    hourly_rate = fields.Float(
        string='Hourly Rate',
        compute='_compute_hourly_rate',
        store=True,
        readonly=True,
        help='Base hourly rate from employee contract.',
    )
    overtime_amount = fields.Float(
        string='Overtime Amount',
        compute='_compute_overtime_amount',
        store=True,
        readonly=True,
        help='Total overtime pay: Duration × Hourly Rate × Rate Multiplier',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )

    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)

    # Additional info
    description = fields.Text(
        string='Description',
        help='Reason or description for the overtime work.',
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
    )
    approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        copy=False,
    )

    # Related documents
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        help='Related project for this overtime (if applicable).',
    )

    _sql_constraints = [
        ('date_check', 'CHECK(date_end > date_start)',
         'End time must be after start time!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.overtime') or _('New')
        return super(HrOvertime, self).create(vals)

    @api.depends('employee_id', 'date')
    def _compute_contract_id(self):
        """Get the active contract for the employee on the overtime date"""
        for record in self:
            if record.employee_id and record.date:
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('state', '=', 'open'),
                    ('date_start', '<=', record.date),
                    '|',
                    ('date_end', '=', False),
                    ('date_end', '>=', record.date),
                ], limit=1)
                record.contract_id = contract
            else:
                record.contract_id = False

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        """Calculate duration in hours between start and end time"""
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0

    @api.depends('contract_id', 'contract_id.wage')
    def _compute_hourly_rate(self):
        """Calculate hourly rate from contract wage"""
        for record in self:
            if record.contract_id and record.contract_id.wage:
                # Assuming monthly wage and standard 160 working hours/month
                # This can be customized based on company policy
                monthly_hours = record.employee_id.resource_calendar_id.hours_per_day * 20 if record.employee_id.resource_calendar_id else 160
                record.hourly_rate = record.contract_id.wage / monthly_hours
            else:
                record.hourly_rate = 0.0

    @api.depends('duration', 'hourly_rate', 'rate')
    def _compute_overtime_amount(self):
        """Calculate total overtime pay"""
        for record in self:
            record.overtime_amount = record.duration * record.hourly_rate * record.rate

    @api.onchange('date_start')
    def _onchange_date_start(self):
        """Set date based on start datetime"""
        if self.date_start:
            self.date = self.date_start.date()

    @api.constrains('date_start', 'date_end', 'employee_id')
    def _check_overlap(self):
        """Check for overlapping overtime records"""
        for record in self:
            if record.date_start and record.date_end and record.employee_id:
                domain = [
                    ('id', '!=', record.id),
                    ('employee_id', '=', record.employee_id.id),
                    ('state', 'not in', ['refused', 'cancelled']),
                    '|',
                    '&', ('date_start', '<=', record.date_start), ('date_end', '>', record.date_start),
                    '&', ('date_start', '<', record.date_end), ('date_end', '>=', record.date_end),
                ]
                if self.search_count(domain):
                    raise ValidationError(_(
                        'Overlapping overtime records are not allowed for the same employee.'
                    ))

    @api.constrains('duration', 'overtime_type_id')
    def _check_max_hours(self):
        """Check maximum hours limits"""
        for record in self:
            if record.overtime_type_id and record.duration:
                ot_type = record.overtime_type_id
                # Check daily limit
                if ot_type.max_hours_per_day and record.duration > ot_type.max_hours_per_day:
                    raise ValidationError(_(
                        'Duration (%(duration).2f hours) exceeds maximum allowed per day '
                        '(%(max).2f hours) for overtime type "%(type)s".',
                        duration=record.duration,
                        max=ot_type.max_hours_per_day,
                        type=ot_type.name,
                    ))

    def action_submit(self):
        """Submit overtime for approval"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft overtime can be submitted.'))
            if not record.overtime_type_id.requires_approval:
                record.write({
                    'state': 'approved',
                    'approved_by': self.env.user.id,
                    'approved_date': fields.Datetime.now(),
                })
            else:
                record.write({'state': 'submitted'})
        return True

    def action_approve(self):
        """Approve overtime request"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted overtime can be approved.'))
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
        return True

    def action_refuse(self):
        """Refuse overtime request"""
        for record in self:
            if record.state not in ['draft', 'submitted']:
                raise UserError(_('Only draft or submitted overtime can be refused.'))
            record.write({'state': 'refused'})
        return True

    def action_cancel(self):
        """Cancel overtime request"""
        for record in self:
            if record.state == 'approved':
                raise UserError(_('Approved overtime cannot be cancelled. Please contact HR.'))
            record.write({'state': 'cancelled'})
        return True

    def action_draft(self):
        """Reset to draft state"""
        for record in self:
            if record.state in ['approved']:
                raise UserError(_('Approved overtime cannot be reset to draft.'))
            record.write({'state': 'draft'})
        return True

    @api.model
    def get_employee_overtime_summary(self, employee_id, date_from, date_to):
        """Get overtime summary for an employee within a date range"""
        domain = [
            ('employee_id', '=', employee_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'approved'),
        ]
        records = self.search(domain)
        
        summary = {
            'total_hours': sum(records.mapped('duration')),
            'total_amount': sum(records.mapped('overtime_amount')),
            'by_type': {},
        }
        
        for record in records:
            type_name = record.overtime_type_id.name
            if type_name not in summary['by_type']:
                summary['by_type'][type_name] = {
                    'hours': 0,
                    'amount': 0,
                }
            summary['by_type'][type_name]['hours'] += record.duration
            summary['by_type'][type_name]['amount'] += record.overtime_amount
        
        return summary
