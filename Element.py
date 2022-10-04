
import csv


class Element:

    def __init__(self, csvrow: dict):
        self.payroll_name = csvrow['Payroll Name'].strip()
        self.costing_name = csvrow['Costing Name'].strip()
        self.payroll_category = csvrow['Payroll Category'].strip()
        self.costing_category = csvrow['Costing Category'].strip()
        self.debit_accounts = [int(x.strip()) for x in csvrow['Debit Account'].split(';')]
        self.credit_accounts = [int(x.strip()) for x in csvrow['Credit Account'].split(';')]
        self.should_cost = True if csvrow['Should Cost'].strip() == 'TRUE' else False

    def __eq__(self, other) -> bool:
        return True if isinstance(other, Element) and self.payroll_name == other.payroll_name else False

    def __hash__(self):
        return hash(self.payroll_name)

    def __str__(self):
        s = self.payroll_category + '\t'
        s += self.payroll_name + '\t'
        s += self.costing_category + '\t'
        s += self.costing_name + '\t'
        s += str(self.debit_accounts) + '\t'
        s += str(self.credit_accounts)
        return s

    def __repr__(self):
        return self.__str__()


class ElementTable:

    def __init__(self):
        self.elements = set()
        self.__payroll_name_lookup__ = dict()
        self.__costing_name_lookup__ = dict()

    def __iter__(self):
        return iter(self.elements)

    def add(self, element: Element) -> None:
        if not isinstance(element, Element):
            raise TypeError('Arg passed to ElementTable.add() is not an Element object.')
        self.elements.add(element)
        self.__payroll_name_lookup__[element.payroll_name] = element
        self.__costing_name_lookup__[element.costing_name] = element

    def find_by_payroll_name(self, name: str) -> Element:
        return self.__payroll_name_lookup__.get(name, None)

    def find_by_costing_name(self, name: str) -> Element:
        return self.__costing_name_lookup__.get(name, None)

    def __getitem__(self, name: str):
        element = self.__payroll_name_lookup__.get(name, None)
        return element if element else self.__costing_name_lookup__.get(name, None)


class Parser:

    fieldnames = set([
        'Costing Category',
        'Costing Name',
        'Payroll Category',
        'Payroll Name',
        'Debit Account',
        'Credit Account'
    ])

    #input_file = r'\\ihsnas1.net.inova.org\smitchris\MYDOCS\Projects\Payroll costing audit\config files\elements.csv'

    @staticmethod
    def parse(filename: str) -> dict:
        elements = ElementTable()
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if not Parser.fieldnames.issubset(set(reader.fieldnames)):
                raise SyntaxError('Elements input file does not contain the correct headers.')
            for row in reader:
                elements.add(Element(row))
        return elements
