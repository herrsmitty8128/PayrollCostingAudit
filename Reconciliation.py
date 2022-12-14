
import csv
import Element
import Transaction
import Employee
from collections import Counter
from itertools import combinations


####################################################################
# The structure of the reconciliation tree is as follows:
#
#                tree
#                  |
#              employees
#                  |
#               elements
#               /     \
#      reconciled     unreconciled
#
####################################################################


class Tree:

    def __init__(self):
        self.tree = {}

    def build_summary_table(self) -> list:
        '''
        This function productes a table with one row for each element.
        '''

        def calc_diff(element: Element.Element, unreconciled: list) -> float:
            '''
            This nested function calculates the difference between the unreconciled payroll
            and unreconciled costing elements.
            '''
            pr = sum(x.amount for x in unreconciled if isinstance(x, Transaction.Payroll))
            cost = sum(x.amount for x in unreconciled if isinstance(x, Transaction.Costing) and x.account in element.debit_accounts)
            return round(pr - cost, 2)

        summary_table = []
        summary = {}
        account_numbers = set()

        for _, elements in self.tree.items():
            for element, pair_of_lists in elements.items():

                reconciled, unreconciled = pair_of_lists

                ctr = summary.get(element, None)
                if ctr is None:
                    ctr = Counter()
                    summary[element] = ctr

                ctr['Payroll Total'] += sum(r.amount for r in reconciled if isinstance(r, Transaction.Payroll))
                ctr['Payroll Total'] += sum(r.amount for r in unreconciled if isinstance(r, Transaction.Payroll))

                for r in [x for x in reconciled if isinstance(x, Transaction.Costing)]:
                    acct = str(r.account)
                    account_numbers.add(acct)
                    ctr[acct] += r.amount

                for r in [x for x in unreconciled if isinstance(x, Transaction.Costing)]:
                    acct = str(r.account)
                    account_numbers.add(acct)
                    ctr[acct] += r.amount

                ctr['Difference'] += calc_diff(element, unreconciled)

        column_names = ['Category', 'Element', 'Payroll Total', 'Difference']
        column_names.extend(sorted(account_numbers))
        default_values = {name: 0.0 for name in column_names}

        for element, counter in summary.items():
            row = dict(default_values)
            row['Category'] = element.payroll_category
            row['Element'] = element.payroll_name
            row.update(counter)
            summary_table.append(row)

        return (summary_table, column_names)

    def build_correcting_je(self) -> tuple:
        '''
        This function builds a correcting journal entry for all unreconciled transactions and
        returns them in a tuple containing a list of the debits and credits and the list headers.
        '''
        entries = []
        fields = ['Category', 'Element', 'Employee', 'Company', 'Department', 'Account', 'Amount', 'Description']

        def post(je, category, element, employee, company, dept, acct, amt, msg):
            je.append({'Category': category,
                       'Element': element,
                       'Employee': employee,
                       'Company': company,
                       'Department': dept,
                       'Account': acct,
                       'Amount': round(amt, 2),
                       'Description': msg})

        for employee, elements in self.tree.items():
            for element, pair_of_lists in elements.items():

                _, unreconciled = pair_of_lists

                je = []

                # Iterate over all the unreconciled transactions.
                for t in unreconciled:
                    # Reverse the costing transactions
                    if isinstance(t, Transaction.Costing):
                        msg = f'Rev cost err for {employee.number}'
                        post(je, element.payroll_category, element.payroll_name, employee.number, t.company, t.department, t.account, -t.amount, msg)
                    # Post the payroll transactions
                    if isinstance(t, Transaction.Payroll):
                        dr_acct = element.debit_accounts[0]
                        cr_acct = element.credit_accounts[0]
                        dr_dept = 90000 if dr_acct < 400000 else 700001
                        cr_dept = 90000 if cr_acct < 400000 else 700001
                        msg = f'Fix cost err for {employee.number}'
                        post(je, element.payroll_category, element.payroll_name, employee.number, 1100, dr_dept, dr_acct, t.amount, msg)
                        post(je, element.payroll_category, element.payroll_name, employee.number, 1100, cr_dept, cr_acct, -t.amount, msg)

                # Raise an excpetion if the debits and credits in the JE do not balance
                if round(sum(t['Amount'] for t in je), 2) != 0.0:
                    raise ValueError(f'Unable to calculate correcting je for {element.payroll_name} for employee {employee.number}')

                # Add the JE to the larger JE
                entries.extend(je)

        return (entries, fields)

    def build_unreconciled_entries(self) -> tuple:
        '''
        This fuction iterates over all unreconciled elements and produces a list of the reasons
        that those elements were not able to be reconciled. It returns a tuple containing a list
        of the entries and a list of the corresponding header values.
        '''
        entries = []
        fields = ['Source', 'Category', 'Element', 'Employee', 'Company', 'Department', 'Account', 'Amount', 'Description']

        def post(source, category, element, employee, company, department, account, amount, note):
            entries.append({'Source': source,
                            'Category': category,
                            'Element': element,
                            'Employee': employee.number,
                            'Company': company,
                            'Department': department,
                            'Account': account,
                            'Amount': round(amount, 2),
                            'Description': note})

        for employee, elements in self.tree.items():
            for element, pair_of_lists in elements.items():

                _, unreconciled = pair_of_lists

                note = ''
                c = 0
                p = 0

                for t in unreconciled:
                    if isinstance(t, Transaction.Costing):
                        c += 1
                    if isinstance(t, Transaction.Payroll):
                        p += 1

                if c > 0 and p > 0:
                    note = 'Costing and payroll dollar amounts are different'
                elif c > 0 and p == 0:
                    note = 'Costing file entry does not have a corresponding payroll register entry'
                elif c == 0 and p > 0:
                    note = 'Payroll register entry was not costed'

                for t in unreconciled:
                    if isinstance(t, Transaction.Costing):
                        post('Costing files', element.costing_category, element.costing_name, employee, t.company, t.department, t.account, t.amount, note)
                    elif isinstance(t, Transaction.Payroll):
                        post('Payroll register', element.payroll_category, element.payroll_name, employee, 'n/a', 'n/a', 'n/a', t.amount, note)

        return (entries, fields)

    def reconcile(self) -> list:
        '''
        This nested function attempts to reconcile all payroll and costing entries. It also validates
        the reconciled entries after they are reconciled for each element and employee. It does not do
        anything with unreconciled entries after the reconciliation process is completed.
        '''

        def net_pay_recalculates(employee: Employee.Employee, elements: dict) -> bool:
            '''
            This function recalculates the total net pay for an employee's payroll elements
            and compares it to the net pay in the employee object. If the two are different,
            then it indicates a technical issue with the original data file.
            '''
            counter = Counter()
            for element, pair_of_lists in elements.items():
                reconciled, unreconciled = pair_of_lists
                counter[element.payroll_category] += sum(x.amount for x in reconciled if isinstance(x, Transaction.Payroll))
                counter[element.payroll_category] += sum(x.amount for x in unreconciled if isinstance(x, Transaction.Payroll))
            total = counter['Standard Earnings']
            total += counter['Supplemental Earnings']
            total -= counter['Employee Tax Deductions']
            total -= counter['Involuntary Deductions']
            total -= counter['Pretax Deductions']
            total -= counter['Voluntary Deductions']
            return True if round(total, 2) == employee.total_net_pay() else False

        def normal_costing_entry(element: Element.Element, reconciled: list, unreconciled: list) -> None:
            '''
            This nested function determines if the sum of the payroll entries is equal to
            both the sum of all debits and the sum of all credits for all costing entries.
            If so, then it moves all the entries from the unreconciled list to the reconciled list.
            '''
            pr = round(sum(x.amount for x in unreconciled if isinstance(x, Transaction.Payroll)), 2)
            dr = round(sum(x.amount for x in unreconciled if isinstance(x, Transaction.Costing) and x.account in element.debit_accounts), 2)
            cr = round(sum(x.amount for x in unreconciled if isinstance(x, Transaction.Costing) and x.account in element.credit_accounts), 2)
            if dr == pr and cr == -pr:
                reconciled.extend(unreconciled)
                unreconciled.clear()

        def departmental_reclass(reconciled: list, unreconciled: list) -> None:
            '''
            This nested function looks for unreconciled costing entries that have no impact on the GL
            account balances. When found, it moves them from the unreconciled list to the reconciled list.
            '''
            costing_entries = [x for x in unreconciled if isinstance(x, Transaction.Costing)]
            balances = Counter()
            for entry in costing_entries:
                balances[entry.account] += entry.amount
            for acct, balance in balances.items():
                if round(balance, 2) == 0.0:
                    reclassifications = [x for x in costing_entries if x.account == acct]
                    reconciled.extend(reclassifications)
                    for r in reclassifications:
                        unreconciled.remove(r)

        def brute_force_method(element: Element.Element, reconciled: list, unreconciled: list) -> list:
            '''
            This nested function tries the remaining combinations.
            '''
            def find_combo(records: list, total: float) -> tuple:
                if len(records) < 20:
                    for n in range(1, len(records) + 1):
                        for combo in combinations(records, n):
                            if round(abs(sum(x.amount for x in combo)), 2) == round(abs(total), 2):
                                return combo
                return ()

            for pr in [x for x in unreconciled if isinstance(x, Transaction.Payroll)]:
                temp = []
                dr = [x for x in unreconciled if isinstance(x, Transaction.Costing) and x.account in element.debit_accounts]
                temp.extend(find_combo(dr, pr.amount))
                cr = [x for x in unreconciled if isinstance(x, Transaction.Costing) and x.account in element.credit_accounts]
                temp.extend(find_combo(cr, pr.amount))
                if len(temp) > 0 and round(abs(sum(x.amount for x in temp)), 2) == 0.0:
                    reconciled.append(pr)
                    unreconciled.remove(pr)
                    reconciled.extend(temp)
                    for t in temp:
                        unreconciled.remove(t)

        errors = []

        for employee, elements in self.tree.items():

            # Net pay must recalculate for all employees, otherwise a reconciliation
            # can not be reliably performed. This typically indicates a technical issue
            # with the dataset and probably the original input file.
            if not net_pay_recalculates(employee, elements):
                raise ValueError(f'Net pay does not recalculate for employee {employee.number}.')

            for element, pair_of_lists in elements.items():

                reconciled, unreconciled = pair_of_lists

                # The unreconciled debits and credits must balance. Otherwise a reconciliation
                # can not be reliably performed. This typically indicates a technical issue
                # with the dataset and probably the original input file.
                if round(sum(entry.amount for entry in unreconciled if isinstance(entry, Transaction.Costing)), 2) != 0.0:
                    raise ValueError(f'Reconciliation can not be performed because unreconciled debits do not equal unreconciled credits for "{element.costing_name}" for employee {employee.number}.')

                # Try different methods to reconcile the payroll and costing entries.
                normal_costing_entry(element, reconciled, unreconciled)
                departmental_reclass(reconciled, unreconciled)
                brute_force_method(element, reconciled, unreconciled)

                # If any unreconciled transactions remain, then log an error.
                if len(unreconciled) > 0:
                    errors.append({'Description': f'Reconciliation could not be completed for "{element.payroll_name}"', 'Employee': employee.number})

                # If the reconciled debits and credits do not balance, then log an error.
                if round(sum(trans.amount for trans in reconciled if isinstance(trans, Transaction.Costing)), 2) != 0.0:
                    raise ValueError(f'Reconciled debits do not equal reconciled credits for "{element.payroll_name}" for employee {employee.number}.')

                # If there is a difference between the payroll transaction(s) and the costing transactions, then log an error.
                p = sum(trans.amount for trans in reconciled if isinstance(trans, Transaction.Payroll))
                c = sum(trans.amount for trans in reconciled if isinstance(trans, Transaction.Costing) and trans.account in element.debit_accounts)
                diff = round(p - c, 2)
                if diff != 0.0:
                    errors.append({'Description': f'Unreconciled difference of ${diff} between payroll and costing elements was detected for "{element.payroll_name}"', 'Employee': employee.number})

        return errors

    @staticmethod
    def build(input_files: list, element_table: Element.ElementTable, name_substitutions: dict) -> tuple:

        def update_ee(employee: Employee.Employee, employees: dict) -> Employee.Employee:
            ee = employees.get(employee.number, None)
            if ee:
                ee.add_net_pay(employee)
                return ee
            else:
                employees[employee.number] = employee
            return employee

        def add_unreconciled(tree, employee: Employee.Employee, element: Element.Element, transaction: Transaction.Transaction) -> None:
            elements = tree.get(employee, None)
            if elements:
                records_tup = elements.get(element, None)
                if records_tup:
                    records_tup[1].append(transaction)
                else:
                    elements[element] = ([], [transaction])
            else:
                tree[employee] = {element: ([], [transaction])}

        tree = Tree()
        errors = []
        employees = {}

        for f in input_files:
            with open(f, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                if Transaction.Costing.fieldnames.issubset(set(reader.fieldnames)):
                    build_transaction = Transaction.Costing.build
                elif Transaction.Payroll.fieldnames.issubset(set(reader.fieldnames)):
                    build_transaction = Transaction.Payroll.build
                else:
                    raise SyntaxError(f'{csvfile.name} does not contain the correct headers for a payroll register or costing file.')
                print('Parsing file', csvfile.name)
                for row in reader:
                    try:
                        employee, element, transaction = build_transaction(row, element_table, name_substitutions)
                        if isinstance(employee, Employee.Employee):
                            employee = update_ee(employee, employees)
                            add_unreconciled(tree.tree, employee, element, transaction)
                    except Exception as e:
                        errors.append(str(e))
        return (tree, errors)
