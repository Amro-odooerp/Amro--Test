# HR Overtime Management Module for Odoo

A comprehensive Odoo module for managing employee overtime hours and calculating overtime payments.

## Features

### Overtime Types
- **Regular Overtime** (1.5x rate) - Standard overtime on working days
- **Weekend Overtime** (2.0x rate) - Work on Saturdays/Sundays
- **Holiday Overtime** (2.5x rate) - Work on public holidays
- **Night Shift Overtime** (1.75x rate) - Night hours (10 PM - 6 AM)
- **Emergency Overtime** (2.0x rate) - Urgent/emergency work
- Create custom overtime types with configurable rate multipliers

### Workflow Management
- Complete approval workflow: Draft → Submitted → Approved/Rejected
- Manager notifications and activity scheduling
- Rejection reason tracking
- Reset to draft functionality for rejected/cancelled requests

### Automatic Calculations
- **Duration**: Automatically calculated from start and end times
- **Hourly Rate**: Computed from employee's contract wage
- **Overtime Amount**: Duration × Hourly Rate × Rate Multiplier

### Views & Reports
- Tree view with color-coded status badges
- Form view with full details and chatter
- Calendar view for visual scheduling
- Pivot view for analysis
- Graph view for statistics
- Report wizard with multiple filters

### Security
- User and Manager permission groups
- Record rules for data privacy:
  - Employees see their own records
  - Managers see their team's records
  - HR Managers have full access
- Multi-company support

## Installation

1. Copy the `hr_overtime` folder to your Odoo addons directory
2. Update the apps list: Apps → Update Apps List
3. Search for "HR Overtime Management" and click Install

## Dependencies

- `hr` - Human Resources
- `hr_contract` - HR Contracts

## Configuration

Navigate to **Settings → HR → Overtime Settings** to configure:

| Setting | Default | Description |
|---------|---------|-------------|
| Monthly Working Hours | 173.33 | Standard hours used to calculate hourly rate |
| Maximum Overtime Hours | 12 | Max hours allowed per single request |
| Approval Required | Yes | Whether overtime needs manager approval |

## Usage

### For Employees
1. Go to **Overtime → My Overtime**
2. Click **Create** to submit a new overtime request
3. Fill in the details (date, times, type, reason)
4. Click **Submit** to send for approval

### For Managers
1. Go to **Overtime → To Approve**
2. Review pending requests from your team
3. Click **Approve** or **Reject** with reason

### For HR Managers
1. Go to **Overtime → All Overtime** for full overview
2. Use **Reports → Overtime Report** for analysis
3. Configure overtime types in **Configuration → Overtime Types**

## Module Structure

```
hr_overtime/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── hr_overtime.py          # Main overtime model
│   ├── hr_overtime_type.py     # Overtime type configuration
│   ├── hr_employee.py          # Employee extensions
│   └── res_config_settings.py  # Company settings
├── views/
│   ├── hr_overtime_views.xml
│   ├── hr_overtime_type_views.xml
│   ├── hr_employee_views.xml
│   ├── res_config_settings_views.xml
│   └── menu_views.xml
├── wizard/
│   ├── __init__.py
│   ├── overtime_report_wizard.py
│   └── overtime_report_wizard_views.xml
├── security/
│   ├── hr_overtime_security.xml
│   └── ir.model.access.csv
├── data/
│   └── hr_overtime_type_data.xml
├── static/
│   └── description/
│       ├── icon.svg
│       └── index.html
└── README.md
```

## License

LGPL-3

## Author

Your Company
