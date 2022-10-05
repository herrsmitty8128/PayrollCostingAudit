
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
    def build(csv_row: dict, element_table: Element.ElementTable, name_substitutions: dict) -> tuple:

        # retrieve and convert all the values that we need
        try:
            emp_id = int(csv_row['Employee Number'].strip())
            element = csv_row['Element'].strip()
            company = int(csv_row['Company_PC'].strip())
            department = int(csv_row['Department_PC'].strip())
            account = int(csv_row['Account_PC'].strip())
            uom = csv_row['Unit of Measure'].strip()
            dr = float(csv_row['Debit Amount'].strip())
            cr = float(csv_row['Credit Amount'].strip())
            amount = round(dr - cr, 2)
        except Exception as err:
            raise ValueError(f'An error was encountered while building a CostingTransaction object: {err}')

        # filter-out hours and zero dollar amounts

        if uom != 'Money' or (dr == 0.0 and cr == 0.0):
            return (None, None, None)

        # make any required element name substitutions

        for name, substitution in name_substitutions.items():
            if name.casefold() in element.casefold():
                element = substitution
                break

        # lookup the element and verify its values

        element = element_table.find_by_costing_name(element)

        if element is None:
            raise ValueError(f'{csv_row["Element"]} on the costing files does not exist in the element lookup table.')

        if not element.should_cost:
            return (None, None, None)

        if account not in element.debit_accounts and account not in element.credit_accounts:
            raise ValueError(f'{account} for element {element.costing_name} does not exist in the element lookup table')

        if emp_id == 0:
            raise ValueError('Employee ID can not be zero.')

        if company == 0:
            raise ValueError('Company number can not be zero.')

        if department == 0:
            raise ValueError('Department number can not be zero.')

        if account == 0:
            raise ValueError('Account number can not be zero.')

        return (Employee.Employee(emp_id), element, Costing(company, department, account, amount))


class Payroll(Transaction):

    # the minimum fields that must be present in a payroll register file
    fieldnames = set([
        'Person Number',
        'Net Pay',
        'Balance Name',
        'Balance Category',
        'Current'
    ])

    def __init__(self, amount: float):
        super().__init__(amount)

    @staticmethod
    def build(csv_row: dict, element_table: Element.ElementTable, name_substitutions: dict) -> tuple:

        try:
            emp_id = int(csv_row['Person Number'].strip())
            element = csv_row['Balance Name'].strip()
            category = csv_row['Balance Category'].strip()
            amount = float(csv_row['Current'].replace(',', '').strip())
            net_pay = float(csv_row['Net Pay'].replace(',', '').strip())
        except Exception as err:
            raise ValueError(f'An error was encountered while building a Payroll Transaction object: {err}')

        # ignore rows in the csv file that are zero, imputed, or represent hours
        if amount == 0.0 or 'Imputed'.casefold() in category.casefold() or 'Hours'.casefold() in category.casefold():
            return (None, None, None)

        if emp_id == 0:
            raise ValueError('Employee ID can not be zero.')

        if element == 'Tuition Non Cash':
            return (None, None, None)

        # make any required element name substitutions

        for name, substitution in name_substitutions.items():
            if name.casefold() in element.casefold():
                element = substitution
                break

        element = element_table.find_by_payroll_name(element)

        if element is None:
            raise ValueError(f'{csv_row["Balance Name"]} on the payroll register does not exist in the element lookup table.')

        if not element.should_cost:
            return (None, None, None)

        return (Employee.Employee(emp_id, net_pay), element, Payroll(amount))
