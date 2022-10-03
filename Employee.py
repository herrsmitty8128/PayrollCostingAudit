

class Employee:

    def __init__(self, number: int, net_pay: float = 0.0):
        if not isinstance(number, int):
            raise ValueError('Employee number must be an interger type.')
        if not isinstance(net_pay, float):
            raise ValueError('Net pay must be a float type.')
        self.number = number
        self.net_pays = set([round(net_pay, 2)])

    def add_net_pay(self, other) -> None:
        if not isinstance(other, Employee):
            raise ValueError('add_net_pay() can only be called for another Employee')
        self.net_pays.update(other.net_pays)

    def total_net_pay(self):
        return round(sum(x for x in self.net_pays), 2)

    def __hash__(self):
        return self.number

    def __eq__(self, other):
        if not isinstance(other, Employee):
            raise ValueError('Employee.__eq__() can only be called for another Employee')
        return self.number == other.number

    def __gt__(self, other):
        if not isinstance(other, Employee):
            raise ValueError('Employee.__gt__() can only be called for another Employee')
        return self.number > other.number

    def __lt__(self, other):
        if not isinstance(other, Employee):
            raise ValueError('Employee.__lt__() can only be called for another Employee')
        return self.number < other.number

    def __str__(self):
        return str(self.number)

    def __repr__(self):
        return self.__str__()
