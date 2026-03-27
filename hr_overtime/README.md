# HR Overtime Management Module for Odoo

A comprehensive Odoo module for tracking and calculating employee overtime.

## Features

- **Overtime Tracking**: Record employee overtime with start/end times
- **Multiple Overtime Types**: Configure different overtime types with custom rates
  - Regular Overtime (1.5x default)
  - Weekend Overtime (2.0x default)
  - Holiday Overtime (2.5x default)
  - Night Shift Overtime (1.75x default)
  - Emergency Overtime (2.0x default)
- **Automatic Calculations**: 
  - Duration calculated from start/end times
  - Hourly rate derived from employee contract
  - Overtime pay = Duration × Hourly Rate × Rate Multiplier
- **Approval Workflow**: Draft → Submitted → Approved/Refused
- **Employee Integration**: View overtime statistics on employee profiles
- **Reporting**: Generate overtime reports and analytics

## Installation

1. Copy the `hr_overtime` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "HR Overtime Management" module

## Dependencies

- `hr` (Human Resources)
- `hr_contract` (Employee Contracts)

## Configuration

### Overtime Types

Navigate to **Overtime > Configuration > Overtime Types** to:
- Create custom overtime types
- Set rate multipliers
- Configure maximum hours per day/month
- Enable/disable approval requirements

### Security Groups

- **Overtime User**: Can create and view overtime records
- **Overtime Manager**: Full access to manage overtime, approve requests, and configure settings

## Usage

### Creating Overtime Records

1. Go to **Overtime > Overtime > My Overtime**
2. Click "Create"
3. Select employee, overtime type, and enter start/end times
4. Submit for approval

### Approving Overtime

1. Go to **Overtime > Overtime > To Approve**
2. Review overtime requests
3. Click "Approve" or "Refuse"

### Viewing Employee Overtime

1. Go to **Employees > Employees**
2. Open an employee record
3. Click the "Overtime" smart button or view the "Overtime" tab

## Overtime Calculation Formula

```
Overtime Amount = Duration (hours) × Hourly Rate × Rate Multiplier
```

Where:
- **Duration**: Automatically calculated from start/end times
- **Hourly Rate**: Derived from employee's contract (Monthly Wage / Monthly Working Hours)
- **Rate Multiplier**: Defined per overtime type (e.g., 1.5x, 2.0x)

## License

LGPL-3

## Author

Your Company
