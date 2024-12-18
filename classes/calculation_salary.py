import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

class CalculationSalary:
    def calculation_salary(self, month, year, premium=0, employee_position_info = None, employee_leaves_info = None):
        salary_month = f"{year}-{month:02d}"
        month_days = calendar.monthrange(year, month)[1]
        employee = employee_position_info

        full_name = employee['full_name']
        base_salary = Decimal(employee['salary_amount'])
        experience = int(employee['total_experience'])

        experience_bonus = (base_salary * Decimal(experience) / Decimal(100)).quantize(Decimal('0.01'),
                                                                                       rounding=ROUND_HALF_UP)
        gross_salary = base_salary + experience_bonus

        leaves = employee_leaves_info

        sick_days = 0
        vacation_days = 0

        for leave in leaves:
            if leave['leave_type'] == 'Sick':
                sick_days += leave['duration']
            elif leave['leave_type'] == 'Vacation':
                vacation_days += leave['duration']

        if not leaves:
            net_salary = self.calculate_net_salary(gross_salary, premium)
            return net_salary

        if sick_days:
            net_salary = self.calculate_sick_leave_salary(gross_salary, sick_days, experience, month_days, premium)
            return net_salary

        if vacation_days:
            net_salary = self.calculate_vacation_salary(gross_salary, vacation_days, month_days, premium)
            return net_salary

    def calculate_net_salary(self, gross_salary, premium):
        tax_pdf = (gross_salary * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tax_military = (gross_salary * Decimal('0.05')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        net_salary = (gross_salary - tax_pdf - tax_military + Decimal(premium)).quantize(Decimal('0.01'),
                                                                                         rounding=ROUND_HALF_UP)
        return net_salary

    def calculate_sick_leave_salary(self, gross_salary, sick_days, experience, month_days, premium):
        daily_rate = gross_salary / month_days
        if experience < 2:
            sick_pay_rate = Decimal('0.5')
        elif 2 <= experience <= 4:
            sick_pay_rate = Decimal('0.8')
        else:
            sick_pay_rate = Decimal('1.0')

        deduction = (daily_rate * sick_days * (1 - sick_pay_rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        adjusted_gross_salary = gross_salary - deduction
        return self.calculate_net_salary(adjusted_gross_salary, premium)

    def calculate_vacation_salary(self, gross_salary, vacation_days, month_days, premium):
        worked_days = month_days - vacation_days
        adjusted_gross_salary = (gross_salary / month_days * worked_days).quantize(Decimal('0.01'),
                                                                                   rounding=ROUND_HALF_UP)
        return self.calculate_net_salary(adjusted_gross_salary, premium)
