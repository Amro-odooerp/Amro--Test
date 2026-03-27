# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


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
    contract_id = fields.Many2one(
        'hr.contract',
        string='Contract',
        compute='_compute_contract_id',
        store=True,
    )
    overtime_type_id = fields.Many2one(
        'hr.overtime.type',
        string='Overtime Type',
        required=True,
        tracking=True,
    )
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
    hourly_rate = fields.Float(
        string='Hourly Rate',
        compute='_compute_hourly_rate',
        store=True,
        help='Base hourly rate from employee contract.',
    )
    rate_multiplier = fields.Float(
        string='Rate Multiplier',
        related='overtime_type_id.rate',
        store=True,
        readonly=True,
    )
    overtime_amount = fields.Float(
        string='Overtime Amount',
        compute='_compute_overtime_amount',
        store=True,
        tracking=True,
    )
    description = fields.Text(
        string='Description/Reason',
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status',
        default='draft',
        tracking=True,
        required=True,
        copy=False,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
    )
    approved_date = fields.Datetime(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )

    # SQL Constraints
    _sql_constraints = [
        ('date_check', 'CHECK(date_end > date_start)',
         'End time must be after start time!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.overtime') or _('New')
        return super(HrOvertime, self).create(vals)

    @api.depends('employee_id')
    def _compute_contract_id(self):
        for record in self:
            if record.employee_id:
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('state', '=', 'open'),
                ], limit=1)
                record.contract_id = contract
            else:
                record.contract_id = False

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0

    @api.depends('contract_id', 'contract_id.wage')
    def _compute_hourly_rate(self):
        for record in self:
            if record.contract_id and record.contract_id.wage:
                # Assuming monthly wage and standard 40 hours/week, ~173.33 hours/month
                monthly_hours = record.company_id.overtime_monthly_hours or 173.33
                record.hourly_rate = record.contract_id.wage / monthly_hours
            else:
                record.hourly_rate = 0.0

    @api.depends('duration', 'hourly_rate', 'rate_multiplier')
    def _compute_overtime_amount(self):
        for record in self:
            record.overtime_amount = record.duration * record.hourly_rate * record.rate_multiplier

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_end <= record.date_start:
                    raise ValidationError(_('End time must be after start time.'))
                # Check for maximum overtime duration (e.g., 12 hours)
                max_hours = record.company_id.overtime_max_hours or 12
                if record.duration > max_hours:
                    raise ValidationError(
                        _('Overtime duration cannot exceed %s hours.') % max_hours
                    )

    @api.constrains('employee_id', 'date_start', 'date_end')
    def _check_overlap(self):
        for record in self:
            if record.employee_id and record.date_start and record.date_end:
                overlapping = self.search([
                    ('id', '!=', record.id),
                    ('employee_id', '=', record.employee_id.id),
                    ('state', 'not in', ['rejected', 'cancelled']),
                    '|',
                    '&', ('date_start', '<=', record.date_start),
                         ('date_end', '>', record.date_start),
                    '&', ('date_start', '<', record.date_end),
                         ('date_end', '>=', record.date_end),
                ])
                if overlapping:
                    raise ValidationError(
                        _('Overtime period overlaps with existing overtime record: %s') 
                        % overlapping[0].name
                    )

    @api.onchange('date')
    def _onchange_date(self):
        if self.date:
            # Set default start time to end of business hours (e.g., 18:00)
            self.date_start = datetime.combine(self.date, datetime.min.time()) + timedelta(hours=18)
            self.date_end = datetime.combine(self.date, datetime.min.time()) + timedelta(hours=20)

    def action_submit(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft overtime requests can be submitted.'))
            record.state = 'submitted'
            # Send notification to manager
            if record.manager_id and record.manager_id.user_id:
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=record.manager_id.user_id.id,
                    summary=_('Overtime Request to Approve'),
                    note=_('Please review overtime request %s from %s.') % (record.name, record.employee_id.name),
                )

    def action_approve(self):
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted overtime requests can be approved.'))
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
            # Mark activities as done
            record.activity_feedback(['mail.mail_activity_data_todo'])

    def action_reject(self):
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted overtime requests can be rejected.'))
            record.state = 'rejected'
            record.activity_feedback(['mail.mail_activity_data_todo'])

    def action_cancel(self):
        for record in self:
            if record.state in ['approved']:
                raise UserError(_('Approved overtime cannot be cancelled. Please contact HR.'))
            record.state = 'cancelled'

    def action_reset_draft(self):
        for record in self:
            if record.state not in ['rejected', 'cancelled']:
                raise UserError(_('Only rejected or cancelled records can be reset to draft.'))
            record.write({
                'state': 'draft',
                'rejection_reason': False,
            })

    def unlink(self):
        for record in self:
            if record.state not in ['draft', 'cancelled']:
                raise UserError(_('You can only delete draft or cancelled overtime records.'))
        return super(HrOvertime, self).unlink()

    @api.model
    def get_employee_overtime_summary(self, employee_id, date_from, date_to):
        """Get overtime summary for an employee within a date range."""
        domain = [
            ('employee_id', '=', employee_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'approved'),
        ]
        records = self.search(domain)
        return {
            'total_hours': sum(records.mapped('duration')),
            'total_amount': sum(records.mapped('overtime_amount')),
            'records_count': len(records),
        }
