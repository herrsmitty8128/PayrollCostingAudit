
import csv
import Element
import Employee


class Transaction:

    def __init__(self, amount: float):
        if not isinstance(amount, float):
            raise ValueError('Amount must be a float type.')
        self.amount = round(amount, 2)

    def __str__(self):
        s = str(self.amount)
        return s

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            raise ValueError('Transaction.__eq__() can only be called for another Transaction')
        return self.amount == other.amount

    def __gt__(self, other):
        if not isinstance(other, Transaction):
            raise ValueError('Transaction.__gt__() can only be called for another Transaction')
        return self.amount > other.amount

    def __lt__(self, other):
        if not isinstance(other, Transaction):
            raise ValueError('Transaction.__lt__() can only be called for another Transaction')
        return self.amount < other.amount


class Costing(Transaction):

    # the minimum fields that must be present in a costing file
    fieldnames = set([
        'Employee Number',
        'Element',
        'Company_PC',
        'Department_PC',
        'Account_PC',
        'Debit Amount',
        'Credit Amount',
        'Unit of Measure'
    ])

    def __init__(self, company: int, department: int, account: int, amount: float):
        super().__init__(amount)
        self.company = company
        self.department = department
        self.account = account

    def __str__(self):
        s = str(self.company) + '\t'
        s += str(self.department) + '\t'
        s += str(self.account) + '\t'
        s += str(self.amount)
        return s

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Costing):
            return False
        return self.company == other.company and self.department == other.department and self.account == other.account and self.amount == other.amount

    @staticmethod
    def build(csv_row: dict, element_table: Element.ElementTable) -> tuple:

        try:
            uom = csv_row['Unit of Measure'].strip()
            dr = float(csv_row['Debit Amount'].strip())
            cr = float(csv_row['Credit Amount'].strip())
        except BaseException:
            return (None, None, None)

        if uom != 'Money' or (dr == 0.0 and cr == 0.0):
            return (None, None, None)

        # parse the employee id
        emp_id = int(csv_row['Employee Number'].strip())
        if emp_id == 0:
            raise ValueError('Employee ID can not be zero.')

        # parse the element
        if 'Work State Income Tax' in csv_row['Element']:
            element = 'Residence State Income Tax'
        elif 'Residence State Supplemental Income Tax' in csv_row['Element']:
            element = 'Residence State Income Tax'
        elif 'Federal Income Tax Not Taken' in csv_row['Element']:
            element = 'Federal Income Tax'
        elif 'Residence State Income Tax Not Taken' in csv_row['Element']:
            element = 'Residence State Income Tax'
        elif 'Medicare Employee Tax Not Taken' in csv_row['Element']:
            element = 'Medicare Employee Tax'
        elif 'Social Security Employee Tax Not Taken' in csv_row['Element']:
            element = 'Social Security Employee Tax'
        elif 'Work City Income Tax' in csv_row['Element']:
            element = 'Residence City Income Tax'
        else:
            element = csv_row['Element'].strip()

        element = element_table.find_by_costing_name(element)

        if element is None:
            raise ValueError(f'{csv_row["Element"]} on the costing files does not exist in the element lookup table.')

        # parse the company number
        company = int(csv_row['Company_PC'].strip())
        if company == 0:
            raise ValueError('Company number can not be zero.')

        # parse the department number
        department = int(csv_row['Department_PC'].strip())
        if department == 0:
            raise ValueError('Department number can not be zero.')

        # parse the account number
        account = int(csv_row['Account_PC'].strip())
        if account == 0:
            raise ValueError('Account number can not be zero.')

        # calculate the amount
        amount = round(dr - cr, 2)
        if account not in element.debit_accounts and account not in element.credit_accounts:
            raise ValueError(f'{account} for element {element.costing_name} does not exist in the element lookup table')
        return (Employee.Employee(emp_id), element, Costing(company, department, account, amount))


class Payroll(Transaction):

    # the minimum fields that must be present in a payroll register file
    fieldnames = set([
        'Person Number',
        'Gross Pay',
        'Net Pay',
        'Balance Name',
        'Current'
    ])

    def __init__(self, amount: float):
        super().__init__(amount)

    @staticmethod
    def build(csv_row: dict, element_table: Element.ElementTable) -> tuple:

        try:
            category = csv_row['Balance Category'].strip()
            amount = float(csv_row['Current'].replace(',', '').strip())
        except BaseException:
            return (None, None, None)

        if amount == 0.0 or 'Imputed' in category or 'Hours' in category:
            return (None, None, None)

        # parse the employee id
        emp_id = int(csv_row['Person Number'].strip())
        if emp_id == 0:
            raise ValueError('Employee ID can not be zero.')

        # parse the element
        element = csv_row['Balance Name'].strip()

        # if element == 'Bonus Day Off With Pay':

        #    element = 'Regular'

        if element == 'Tuition Non Cash':
            return (None, None, None)

        element = element_table.find_by_payroll_name(element)
        if element is None:
            raise ValueError(f'{csv_row["Balance Name"]} on the payroll register does not exist in the element lookup table.')

        gross_pay = float(csv_row['Gross Pay'].replace(',', '').strip())

        net_pay = float(csv_row['Net Pay'].replace(',', '').strip())

        return (Employee.Employee(emp_id, net_pay), element, Payroll(amount))
